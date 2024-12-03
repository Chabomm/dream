from fastapi import Request
from inspect import currentframe as frame
from app.core.database import format_sql
from sqlalchemy import func, select, update, delete, Table, MetaData, and_
from app.core import util
import math
from app.core import exceptions as ex

from app.schemas.schema import *
from app.schemas.manager.point.exuse.confirm import *
from app.models.point.remaining import *
from app.service.log_service import *

# 환급내역 - 리스트
def remaining_list(request: Request, page_param: PPage_param, fullsearch:bool=False):
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
    filters.append(getattr(T_CARD_USED_REMAINING, "delete_at") == None)
    filters.append(getattr(T_CARD_USED_REMAINING, "partner_uid") == user.partner_uid)

    # [ S ] search filter start
    if page_param.filters :
        if page_param.filters["skeyword"] :
            if page_param.filters["skeyword_type"] != "" :
                filters.append(getattr(T_CARD_USED_REMAINING, page_param.filters["skeyword_type"]).like("%"+page_param.filters["skeyword"]+"%"))
            else :
                filters.append(
                      T_CARD_USED_REMAINING.user_name.like("%"+page_param.filters["skeyword"]+"%")
                    | T_CARD_USED_REMAINING.birth.like("%"+page_param.filters["skeyword"]+"%")
                    | T_CARD_USED_REMAINING.depart.like("%"+page_param.filters["skeyword"]+"%")
                )

        if page_param.filters["remaining_at"]["startDate"] and page_param.filters["remaining_at"]["endDate"] :
            filters.append(
                and_(
                    T_CARD_USED_REMAINING.remaining_at >= page_param.filters["remaining_at"]["startDate"]
                    ,T_CARD_USED_REMAINING.remaining_at <= page_param.filters["remaining_at"]["endDate"] + " 23:59:59"
                )
            )

        if page_param.filters["confirm_at"]["startDate"] and page_param.filters["confirm_at"]["endDate"] :
            filters.append(
                and_(
                    T_CARD_USED_REMAINING.confirm_at >= page_param.filters["confirm_at"]["startDate"]
                    ,T_CARD_USED_REMAINING.confirm_at <= page_param.filters["confirm_at"]["endDate"] + " 23:59:59"
                )
            )
        
        if page_param.filters["state"] :
            filters.append(T_CARD_USED_REMAINING.state == page_param.filters["state"])
    # [ E ] search filter end
            
    sql = (
        db.query(
             T_CARD_USED_REMAINING.uid
            ,T_CARD_USED_REMAINING.card_used_uid
            ,T_CARD_USED_REMAINING.partner_uid
            ,T_CARD_USED_REMAINING.partner_id
            ,T_CARD_USED_REMAINING.user_uid
            ,T_CARD_USED_REMAINING.user_id
            ,T_CARD_USED_REMAINING.user_name
            ,T_CARD_USED_REMAINING.birth
            ,T_CARD_USED_REMAINING.depart
            ,T_CARD_USED_REMAINING.position
            ,T_CARD_USED_REMAINING.biz_item
            ,T_CARD_USED_REMAINING.detail
            ,func.date_format(T_CARD_USED_REMAINING.confirm_at, '%Y-%m-%d').label('confirm_at')
            ,func.date_format(T_CARD_USED_REMAINING.remaining_at, '%Y-%m-%d').label('remaining_at')
            ,T_CARD_USED_REMAINING.input_amount
            ,T_CARD_USED_REMAINING.card
            ,T_CARD_USED_REMAINING.input_bank
            ,T_CARD_USED_REMAINING.input_name
            ,T_CARD_USED_REMAINING.input_bank_num
            ,T_CARD_USED_REMAINING.state
            ,func.date_format(T_CARD_USED_REMAINING.create_at, '%Y-%m-%d %T').label('create_at')
        )
        .filter(*filters)
        .order_by(T_CARD_USED_REMAINING.uid.desc())
        .offset(offsets)
        .limit(limits)
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    # [ S ] 페이징 처리
    page_param.page_total = (
        db.query(T_CARD_USED_REMAINING)
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
