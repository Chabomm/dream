from fastapi import Request
from inspect import currentframe as frame
from app.core.database import format_sql
from sqlalchemy import func, select, update, delete, Table, MetaData, and_
from app.core import util
import math
from app.core import exceptions as ex

from app.schemas.schema import *
from app.schemas.manager.point.exuse.confirm import *
from app.models.point.confirm import *
from app.service.log_service import *

# 소명신청 - 리스트
def confirm_list(request: Request, page_param: PPage_param, fullsearch:bool=False):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    offsets = 0
    if fullsearch == False :
        offsets = (page_param.page-1)*page_param.page_view_size

    limits = None
    if fullsearch == False :
        limits = page_param.page_view_size

    filters = []
    filters.append(getattr(T_EXUSE, "delete_at") == None)
    filters.append(getattr(T_EXUSE, "partner_uid") == user.partner_uid)

    # [ S ] search filter start
    if page_param.filters :
        if page_param.filters["skeyword"] :
            if page_param.filters["skeyword_type"] != "" :
                filters.append(getattr(T_EXUSE, page_param.filters["skeyword_type"]).like("%"+page_param.filters["skeyword"]+"%"))
            else : 
                filters.append(
                      T_EXUSE.user_name.like("%"+page_param.filters["skeyword"]+"%")
                    | T_EXUSE.birth.like("%"+page_param.filters["skeyword"]+"%")
                    | T_EXUSE.depart.like("%"+page_param.filters["skeyword"]+"%")
                )

        if page_param.filters["create_at"]["startDate"] and page_param.filters["create_at"]["endDate"] :
            filters.append(
                and_(
                    T_EXUSE.create_at >= page_param.filters["create_at"]["startDate"]
                    ,T_EXUSE.create_at <= page_param.filters["create_at"]["endDate"] + " 23:59:59"
                )
            )

        if page_param.filters["pay_at"]["startDate"] and page_param.filters["pay_at"]["endDate"] :
            filters.append(
                and_(
                    T_EXUSE.pay_at >= page_param.filters["pay_at"]["startDate"]
                    ,T_EXUSE.pay_at <= page_param.filters["pay_at"]["endDate"] + " 23:59:59"
                )
            )

        if page_param.filters["pay_cancel_at"]["startDate"] and page_param.filters["pay_cancel_at"]["endDate"] :
            filters.append(
                and_(
                    T_EXUSE.pay_cancel_at >= page_param.filters["pay_cancel_at"]["startDate"]
                    ,T_EXUSE.pay_cancel_at <= page_param.filters["pay_cancel_at"]["endDate"] + " 23:59:59"
                )
            )

        if page_param.filters["confirm_at"]["startDate"] and page_param.filters["confirm_at"]["endDate"] :
            filters.append(
                and_(
                    T_EXUSE.confirm_at >= page_param.filters["confirm_at"]["startDate"]
                    ,T_EXUSE.confirm_at <= page_param.filters["confirm_at"]["endDate"] + " 23:59:59"
                )
            )
        
        if page_param.filters["state"] :
            filters.append(T_EXUSE.state == page_param.filters["state"])
        
    # [ E ] search filter end
            
    sql = (
        db.query(
             T_EXUSE.uid
            ,T_EXUSE.partner_uid
            ,T_EXUSE.partner_id
            ,T_EXUSE.user_uid
            ,T_EXUSE.user_id
            ,T_EXUSE.user_name
            ,T_EXUSE.birth
            ,T_EXUSE.depart
            ,T_EXUSE.position
            ,func.date_format(T_EXUSE.pay_at, '%Y-%m-%d').label('pay_at')
            ,func.date_format(T_EXUSE.pay_cancel_at, '%Y-%m-%d').label('pay_cancel_at')
            ,T_EXUSE.biz_item
            ,T_EXUSE.detail
            ,T_EXUSE.pay_amount
            ,T_EXUSE.exuse_amount
            ,T_EXUSE.state
            ,func.date_format(T_EXUSE.confirm_at, '%Y-%m-%d').label('confirm_at')
            ,func.date_format(T_EXUSE.create_at, '%Y-%m-%d %T').label('create_at')
            ,T_EXUSE.point_type
        )
        .filter(*filters)
        .order_by(T_EXUSE.uid.desc())
        .offset(offsets)
        .limit(limits)
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    # [ S ] 페이징 처리
    page_param.page_total = (
        db.query(T_EXUSE)
        .filter(*filters)
        .count()
    )
    page_param.page_last = math.ceil(
        page_param.page_total / page_param.page_view_size)
    page_param.page_size = len(rows)  # 현재 페이지에 검색된 수
    # [ E ] 페이징 처리

    jsondata = {}
    jsondata.update({"params":page_param})
    jsondata.update({"list": rows})

    return jsondata

# 소명신청_상태_편집 - 수정
def confirm_update_state(request: Request, confirmStateInput: ConfirmStateInput) :
    request.state.inspect = frame()
    db = request.state.db 
    user = request.state.user

    for uid in confirmStateInput.uid :

        # 기존 등록된 item select 
        res_exuse = db.query(T_EXUSE).filter(T_EXUSE.uid == uid).first()
        
        if res_exuse is None :
            raise ex.NotFoundUser

        if confirmStateInput.state is not None and res_exuse.state != confirmStateInput.state : 
            create_log(request, uid, "T_EXUSE", "state", "소명신청 상태", res_exuse.state, confirmStateInput.state, user.user_id)
            request.state.inspect = frame()
            res_exuse.state = confirmStateInput.state
        
        res_exuse.update_at = util.getNow()
    return 

# 소명신청 - 상세
def confirm_read(request: Request, uid: int):
    request.state.inspect = frame()
    db = request.state.db

    sql = ( 
        db.query(
             T_EXUSE.uid
            ,T_EXUSE.card_used_uid
            ,T_EXUSE.biz_item
            ,T_EXUSE.exuse_amount
            ,T_EXUSE.state
            ,T_EXUSE.point_type
            ,T_EXUSE.welfare_type
            ,T_EXUSE.exuse_detail
            ,T_EXUSE.attch_file
        )
        .filter(
            T_EXUSE.uid == uid
            ,T_EXUSE.delete_at == None
        )
    )
    # format_sql(sql)
    return sql.first()

# 소명신청내역 - 수정
def confirm_update(request: Request, confirmInput: ConfirmInput):
    request.state.inspect = frame()
    db = request.state.db 
    user = request.state.user

    res_exuse = (db.query(T_EXUSE).filter(T_EXUSE.uid == confirmInput.uid).first())

    if res_exuse is None :
        raise ex.NotFoundUser
    
    if confirmInput.memo is not None and confirmInput.memo != "" : 
        # insert
        create_memo(request, res_exuse.uid, "T_EXUSE", confirmInput.memo, user.user_id)
        request.state.inspect = frame()

    if confirmInput.exuse_amount is not None and res_exuse.exuse_amount != confirmInput.exuse_amount : 
        create_log(request, res_exuse.uid, "T_EXUSE", "exuse_amount", "소명신청금액 수정", res_exuse.exuse_amount, confirmInput.exuse_amount, user.user_id)
        request.state.inspect = frame()
        res_exuse.exuse_amount = confirmInput.exuse_amount

    if confirmInput.state is not None and res_exuse.state != confirmInput.state : 
            create_log(request, res_exuse.uid, "T_EXUSE", "state", "소명신청 상태 수정", res_exuse.state, confirmInput.state, user.user_id)
            request.state.inspect = frame()
            res_exuse.state = confirmInput.state

    res_exuse.update_at = util.getNow()

    return res_exuse