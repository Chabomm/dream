from fastapi import Request
from inspect import currentframe as frame
from app.core.database import format_sql
from sqlalchemy import func, select, update, delete, Table, MetaData, and_, or_, literal_column
from app.core import util
import math
import random

from app.schemas.schema import *
from app.schemas.front.point import *
from app.models.member import *
from app.models.point.point import *
from app.models.point.sikwon import *
from app.service.log_service import *


# 회원 정보 from user_id
def get_user_info(request: Request, user_id: str):
    request.state.inspect = frame()
    db = request.state.db
    return db.query(T_MEMBER).filter(T_MEMBER.user_id == user_id).first()

# 현재 잔액
def get_my_point(request: Request, user_id: str, with_sikwon: bool) :
    request.state.inspect = frame()
    db = request.state.db

    bokji_point_saved = 0
    bokji_point_avail = 0
    sikwon_point_saved = 0
    sikwon_point_avail = 0

    res_bokji_point = ( 
        db.query(
             func.sum(func.ifnull(T_POINT.saved_point, 0)).label('saved_welfare_point') # 지급 완료 포인트
            ,func.sum(func.ifnull(T_POINT.point, 0)).label('avail_welfare_point') # 미사용 포인트
        )
        .filter(
            T_POINT.user_id == user_id,
            or_(
                T_POINT.expiration_date == None,
                T_POINT.expiration_date > func.now(),
            )
        )
        .group_by(T_POINT.user_id)
    ).first()

    if res_bokji_point != None :
        bokji_point_saved = res_bokji_point.saved_welfare_point
        bokji_point_avail = res_bokji_point.avail_welfare_point

    if with_sikwon :
        res_sikwon_point = ( 
            db.query(
                func.sum(func.ifnull(T_SIKWON.saved_point, 0)).label('saved_welfare_point') # 지급 완료 포인트
                ,func.sum(func.ifnull(T_SIKWON.point, 0)).label('avail_welfare_point') # 미사용 포인트
            )
            .filter(
                T_SIKWON.user_id == user_id,
                or_(
                    T_SIKWON.expiration_date == None,
                    T_SIKWON.expiration_date > func.now(),
                )
            )
            .group_by(T_SIKWON.user_id)
        ).first()
        
        if res_sikwon_point != None :
            sikwon_point_saved = res_sikwon_point.saved_welfare_point
            sikwon_point_avail = res_sikwon_point.avail_welfare_point

    jsondata = {}
    jsondata.update({"bokji_point_saved": util.checkNumeric(bokji_point_saved)})
    jsondata.update({"bokji_point_avail": util.checkNumeric(bokji_point_avail)})
    jsondata.update({"sikwon_point_saved": util.checkNumeric(sikwon_point_saved)})
    jsondata.update({"sikwon_point_avail": util.checkNumeric(sikwon_point_avail)})

    return jsondata

# 복지포인트 사용처리
def use_point(request: Request, pointUse: PointUse, user: any) :
    request.state.inspect = frame()
    db = request.state.db

    user_id = util.null2Blank(pointUse.user_id)
    use_point = util.checkNumeric(pointUse.use_point)
    order_uid = util.checkNumeric(pointUse.order_uid)
    order_no = util.null2Blank(pointUse.order_no) # "C" + str(random.randrange(1111111, 9999999))
    used_type = "1" # 1:사용, 2:환불, 3:차감
    reason = util.null2Blank(pointUse.reason)
    partner_uid = util.checkNumeric(user.partner_uid)
    partner_id = util.null2Blank(user.partner_id)

    res_point = (
        db.query(T_POINT)
        .filter(
            T_POINT.user_id == user_id,
            T_POINT.point > 0,
            or_(
                T_POINT.expiration_date == None,
                T_POINT.expiration_date > func.now(),
            )
        )
    )
    format_sql(res_point)

    my_spare_point = 0 # 처리 후 최종 잔액
    for c in res_point.all() :
        my_spare_point = my_spare_point + c.point

    if my_spare_point < use_point : # 사용할 금액보다 잔액이 부족할때
        return my_spare_point - use_point

    for c in res_point.all() :
        if use_point > 0 :
            if c.point >= use_point : # 잔여포인트 >= 사용할포인트 : 전액사용 끝
                before_point = c.point 
                c.point = c.point-use_point
                create_log (
                     request
                    ,c.uid
                    ,"T_POINT"
                    ,"point"
                    ,"복지포인트 사용"
                    ,str(before_point)
                    ,str(c.point)
                    ,user.user_id
                )
                request.state.inspect = frame()

                db_item = T_POINT_USED (
                     point_id = c.uid
                    ,used_type = used_type
                    ,used_point = use_point
                    ,order_uid = order_uid
                    ,order_no = order_no
                    ,reason = reason
                    ,user_id = user_id
                    ,partner_uid = partner_uid
                    ,partner_id = partner_id
                )
                db.add(db_item)
                db.flush()

                my_spare_point = my_spare_point - use_point
                use_point = 0

            else : # 잔여포인트 < 사용할포인트 : 사용할포인트 spare로 남기고 다음 포인트 보러감
                before_point = c.point
                use_point = use_point - c.point
                db_item = T_POINT_USED (
                     point_id = c.uid
                    ,used_type = used_type
                    ,used_point = c.point
                    ,order_uid = order_uid
                    ,order_no = order_no
                    ,reason = reason
                    ,user_id = user_id
                    ,partner_uid = partner_uid
                    ,partner_id = partner_id
                )
                db.add(db_item)
                db.flush()
                
                my_spare_point = my_spare_point - c.point
                c.point = 0
                create_log (
                     request
                    ,c.uid
                    ,"T_POINT"
                    ,"point"
                    ,"복지포인트 사용"
                    ,str(before_point)
                    ,str(c.point)
                    ,user.user_id
                )
                request.state.inspect = frame()
    
    # 음수이면 잔액이 부족한거, router가 따로 에러처리
    return my_spare_point 





# 복지포인트 취소처리
def cancel_point(request: Request, pointCancel: PointCancel, user: any) :
    request.state.inspect = frame()
    db = request.state.db

    user_id = util.null2Blank(pointCancel.user_id)
    cancel_point = util.checkNumeric(pointCancel.cancel_point)
    order_uid = util.checkNumeric(pointCancel.order_uid)
    order_no = util.null2Blank(pointCancel.order_no) # "C" + str(random.randrange(1111111, 9999999))
    used_type = "2" # 1:사용, 2:환불, 3:차감
    reason = util.null2Blank(pointCancel.reason)
    partner_uid = util.checkNumeric(user.partner_uid)
    partner_id = util.null2Blank(user.partner_id)

    _sql_remaining_stmt = (
        db.query(
            T_POINT_USED.point_id
            ,(
                func.sum(func.ifnull(T_POINT_USED.used_point, 0))-func.sum(func.ifnull(T_POINT_USED.remaining_point, 0))
            ).label('sum_of_spare_used')
        )
        .filter(
            T_POINT_USED.user_id == user_id,
            T_POINT_USED.order_no == order_no,
            T_POINT_USED.order_uid == order_uid
        )
        .group_by(T_POINT_USED.point_id)
    )
    format_sql(_sql_remaining_stmt)
    
    pointid_of_used = [] # 환불할 point id 들
    poss_remaining_point = 0 # 환불가능한 금액
    for c in _sql_remaining_stmt.all() : # 취소가능한지 검사
        if c.sum_of_spare_used > 0 :
            print(c.sum_of_spare_used, c.point_id)
            poss_remaining_point = poss_remaining_point + c.sum_of_spare_used
            pointid_of_used.append(c.point_id)

    # 환불가능한금액 보다 취소요청한금액이 더 클때
    if poss_remaining_point < cancel_point :
        return util.checkNumeric(poss_remaining_point-cancel_point) 

    sql = (
        db.query(
             T_POINT_USED.point_id
            ,T_POINT_USED.used_point
        )
        .filter(
            T_POINT_USED.user_id == user_id,
            T_POINT_USED.order_no == order_no,
            T_POINT_USED.order_uid == order_uid,
            T_POINT_USED.used_type == "1",
            T_POINT_USED.point_id.in_(pointid_of_used)
        )
    )
    format_sql(sql)

    for c in sql.all() :
        if cancel_point > 0 :
            if c.used_point >= cancel_point : # 환불가능포인트 >= 환불할포인트 : 전액환불 끝
                db_item = T_POINT_USED (
                     point_id = c.point_id
                    ,used_type = used_type
                    ,remaining_point = cancel_point
                    ,order_uid = order_uid
                    ,order_no = order_no
                    ,reason = reason
                    ,user_id = user_id
                    ,partner_uid = partner_uid
                    ,partner_id = partner_id
                )
                db.add(db_item)
                db.flush()
            
                res_point = db.query(T_POINT).filter(T_POINT.uid == c.point_id).first()
                before_point = res_point.point
                res_point.point = res_point.point + cancel_point
                create_log (
                     request
                    ,res_point.uid
                    ,"T_POINT"
                    ,"point"
                    ,"복지포인트 환불"
                    ,str(before_point)
                    ,str(res_point.point)
                    ,user.user_id
                )
                request.state.inspect = frame()

                poss_remaining_point = poss_remaining_point - cancel_point
                cancel_point = 0
            
            else : # 환불가능포인트 < 환불할포인트 : 환불할포인트 spare로 남기고 다음 포인트 보러감
                db_item = T_POINT_USED (
                     point_id = c.point_id
                    ,used_type = used_type
                    ,remaining_point = c.used_point
                    ,order_uid = order_uid
                    ,order_no = order_no
                    ,reason = reason
                    ,user_id = user_id
                    ,partner_uid = partner_uid
                    ,partner_id = partner_id
                )
                db.add(db_item)
                db.flush()

                res_point = db.query(T_POINT).filter(T_POINT.uid == c.point_id).first()
                before_point = res_point.point
                res_point.point = res_point.point + c.used_point
                create_log (
                     request
                    ,res_point.uid
                    ,"T_POINT"
                    ,"point"
                    ,"복지포인트 환불"
                    ,str(before_point)
                    ,str(res_point.point)
                    ,user.user_id
                )
                request.state.inspect = frame()

                cancel_point = cancel_point - c.used_point
                poss_remaining_point = poss_remaining_point - c.used_point

    # 환불요청 후 더 환불 가능한 포인트
    # 음수이면 환불가능금액보다 큰 금액을 요청한거
    return util.checkNumeric(poss_remaining_point)
