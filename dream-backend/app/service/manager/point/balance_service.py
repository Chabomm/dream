from fastapi import Request
from inspect import currentframe as frame
from app.core.database import format_sql
from sqlalchemy import func, select, update, delete, Table, MetaData, and_
from app.core import util
import math

from app.schemas.schema import *
from app.schemas.manager.point.assign.balance import *
from app.models.point.balance import *
from app.service.log_service import *

def balance_list(request: Request, page_param: PPage_param, fullsearch:bool=False):
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
    filters.append(getattr(T_BALANCE, "delete_at") == None)
    filters.append(getattr(T_BALANCE, "partner_uid") == user.partner_uid)

    # [ S ] search filter start
    if page_param.filters :
        if page_param.filters["skeyword"] :
            if page_param.filters["skeyword_type"] != "" :
                filters.append(getattr(T_BALANCE, page_param.filters["skeyword_type"]).like("%"+page_param.filters["skeyword"]+"%"))
            else : 
                filters.append(
                      T_BALANCE.reason.like("%"+page_param.filters["skeyword"]+"%")
                    | T_BALANCE.input_bank.like("%"+page_param.filters["skeyword"]+"%")
                    | T_BALANCE.input_name.like("%"+page_param.filters["skeyword"]+"%")
                )

        if page_param.filters["create_at"]["startDate"] and page_param.filters["create_at"]["endDate"] :
            filters.append(
                and_(
                    T_BALANCE.create_at >= page_param.filters["create_at"]["startDate"]
                    ,T_BALANCE.create_at <= page_param.filters["create_at"]["endDate"] + " 23:59:59"
                )
            )
        
        if page_param.filters["input_state"] :
            filters.append(T_BALANCE.input_state == page_param.filters["input_state"])
    # [ E ] search filter end
            
    rtpay_stmt = (
        db.query(
            T_BALANCE_RTPAY.balance_uid
            ,func.sum(T_BALANCE_RTPAY.pmoney).label('sum_of_pmoney')
            ,func.max(T_BALANCE_RTPAY.create_at).label('max_of_at')
        )
        .filter(T_BALANCE_RTPAY.rt_code == "200")
        .group_by(T_BALANCE_RTPAY.balance_uid)
        .subquery()
    )

    sql = (
        db.query(
             T_BALANCE.uid
            ,T_BALANCE.point
            ,T_BALANCE.save_point
            ,T_BALANCE.reason
            ,T_BALANCE.order_no
            ,T_BALANCE.input_bank
            ,T_BALANCE.input_name
            ,T_BALANCE.input_state
            ,func.date_format(T_BALANCE.create_at, '%Y-%m-%d %T').label('create_at')
            ,rtpay_stmt.c.sum_of_pmoney
            ,func.date_format(rtpay_stmt.c.max_of_at, '%Y-%m-%d %T').label('max_of_at')
        )
        .join (
            rtpay_stmt, 
            T_BALANCE.uid == rtpay_stmt.c.balance_uid,
            isouter = True # LEFT JOIN
        )
        .filter(*filters)
        .order_by(T_BALANCE.uid.desc())
        .offset(offsets)
        .limit(limits)
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    # [ S ] 페이징 처리
    page_param.page_total = (
         db.query(T_BALANCE)
        .filter(*filters)
        .count()
    )
    page_param.page_last = math.ceil(page_param.page_total / page_param.page_view_size)
    page_param.page_size = len(rows) # 현재 페이지에 검색된 수
    # [ E ] 페이징 처리

    jsondata = {}
    jsondata.update({"params" : page_param})
    jsondata.update({"list": rows})

    return jsondata


def rpay_checkpay(request: Request, res: dict):
    request.state.inspect = frame()
    db = request.state.db   

    rt_code = res['RCODE']  # 결과
    pmoney = res['RPAY']	# 입금금액
    pbank = res['RBANK']	# 은행명
    pname = res['RNAME']	# 입금자명
    tall = res['RTEXT']		# 전송 데이터 전문
    pnum = res['RNUMBER']	# 계좌번호

    if util.checkNumeric(rt_code) == 200 :
        sql = (
            db.query(T_BALANCE)
            .filter(
                T_BALANCE.input_state.in_(['입금전', '입금중'])
                ,T_BALANCE.input_bank == pbank
                ,T_BALANCE.input_name == pname
            )
        )
        res_balance = sql.first()

    balance_uid = 0
    partner_uid = 0
    partner_id = ""

    if res_balance != None :
        balance_uid = res_balance.uid
        partner_uid = res_balance.partner_uid
        partner_id = res_balance.partner_id
    
    db_item = T_BALANCE_RTPAY (
         balance_uid = balance_uid
        ,partner_uid = partner_uid
        ,partner_id = partner_id
        ,pmoney = util.checkNumeric(pmoney) 
        ,rt_code = rt_code
        ,tall = tall
        ,pbank = pbank
        ,pname = pname
        ,pnum = pnum
    )
    db.add(db_item)
    db.flush()

    if res_balance != None :
        sql = (
            db.query(
                 T_BALANCE_RTPAY.balance_uid
                ,func.sum(T_BALANCE_RTPAY.pmoney).label('sum_of_pmoney')
            )
            .filter(T_BALANCE_RTPAY.rt_code == "200")
            .group_by(T_BALANCE_RTPAY.balance_uid)
        )
        res_balance_rtpay = sql.first()

        if res_balance_rtpay.sum_of_pmoney >= res_balance.save_point :
            res_balance.input_state = "입금완료"
        else :
            res_balance.input_state = "입금중"
        res_balance.update_at = util.getNow()

    print("resresres", res)


# 예치금 충전_등록
def balance_create(request: Request, assignBalanceInput: AssignBalanceInput):
    request.state.inspect = frame()
    db = request.state.db 
    user = request.state.user

    db_item = T_BALANCE (
         partner_uid = user.partner_uid
        ,partner_id = user.partner_id
        ,point = util.checkNumeric(assignBalanceInput.save_point) 
        ,save_point = util.checkNumeric(assignBalanceInput.save_point) 
        ,reason = assignBalanceInput.reason
        ,input_bank = assignBalanceInput.input_bank
        ,input_name = assignBalanceInput.input_name
        ,input_state = "입금완료" if user.partner_id == "indend" else "입금전"
    )
    db.add(db_item)
    
    create_log(request, db_item.uid, "T_BALANCE", "INSERT", "예치금충전 등록", 0, db_item.uid, user.user_id)
    request.state.inspect = frame()

    return db_item

# 잔여 예치금 조회 by partner_uid
def balance_read_partner_id(request: Request, partner_uid: int):
    request.state.inspect = frame()
    db = request.state.db

    point_stmt = (
        db.query(
             T_BALANCE.partner_uid
            ,func.sum(T_BALANCE.point).label('spare_point')
        )
        .filter(
            T_BALANCE.partner_uid == partner_uid
            ,T_BALANCE.input_state == "입금완료"
            ,T_BALANCE.delete_at == None
        )
        .group_by(T_BALANCE.partner_uid)
        .subquery()
    )

    sql = ( 
        db.query(
             T_BALANCE.uid
            ,T_BALANCE.partner_uid
            ,T_BALANCE.partner_id
            ,point_stmt.c.spare_point
        )
        .join (
            point_stmt, 
            T_BALANCE.partner_uid == point_stmt.c.partner_uid,
            isouter = True # LEFT JOIN
        )
    )
    # format_sql(sql)
    return sql.first()
