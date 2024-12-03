from fastapi import Request
from inspect import currentframe as frame
from app.core.database import format_sql
from sqlalchemy import func, select, update, delete, Table, MetaData, and_, literal_column
from app.core import util
import math
import random

from app.schemas.schema import *
from app.schemas.manager.point.offcard.remaining import *
from app.models.point.remaining import *
from app.models.member import *
from app.service.log_service import *
from app.core import exceptions as ex

# 환급금액합계
def get_my_remaining(request: Request, cardRemainingListInput: CardRemainingListInput, user: T_MEMBER) :
    request.state.inspect = frame()
    db = request.state.db
    
    filters = []
    filters.append(getattr(T_CARD_USED_REMAINING, "delete_at") == None)
    filters.append(getattr(T_CARD_USED_REMAINING, "user_id") == cardRemainingListInput.user_id)
    filters.append(getattr(T_CARD_USED_REMAINING, "partner_uid") == user.partner_uid)

    if cardRemainingListInput.filters :
        if cardRemainingListInput.filters["create_at"]["startDate"] and cardRemainingListInput.filters["create_at"]["endDate"] :
            filters.append(
                and_(
                    T_CARD_USED_REMAINING.remaining_at >= cardRemainingListInput.filters["create_at"]["startDate"]
                    ,T_CARD_USED_REMAINING.remaining_at <= cardRemainingListInput.filters["create_at"]["endDate"] + " 23:59:59"
                )
            )


    sum_price_data = 0
    remaining_price = ( 
        db.query(
            func.sum(func.ifnull(T_CARD_USED_REMAINING.input_amount, 0)).label('sum_price_data')
        )
        .filter(*filters)
        .group_by(T_CARD_USED_REMAINING.user_id)
    ).first()

    if remaining_price != None :
        sum_price_data = int(remaining_price.sum_price_data)
        
    return sum_price_data


# 환급 내역
def offcard_remaining_list(request: Request, cardRemainingListInput: CardRemainingListInput, user: T_MEMBER):
    request.state.inspect = frame()
    db = request.state.db

    filters = []
    filters.append(getattr(T_CARD_USED_REMAINING, "delete_at") == None)
    filters.append(getattr(T_CARD_USED_REMAINING, "user_id") == cardRemainingListInput.user_id)
    filters.append(getattr(T_CARD_USED_REMAINING, "partner_uid") == user.partner_uid)

    if cardRemainingListInput.filters :
        if cardRemainingListInput.filters["create_at"]["startDate"] and cardRemainingListInput.filters["create_at"]["endDate"] :
            filters.append(
                and_(
                    T_CARD_USED_REMAINING.remaining_at >= cardRemainingListInput.filters["create_at"]["startDate"]
                    ,T_CARD_USED_REMAINING.remaining_at <= cardRemainingListInput.filters["create_at"]["endDate"] + " 23:59:59"
                )
            )

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
        .offset((cardRemainingListInput.page-1)*cardRemainingListInput.page_view_size)
        .limit(cardRemainingListInput.page_view_size)
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    # [ S ] 페이징 처리
    cardRemainingListInput.page_total = (db.query(T_CARD_USED_REMAINING).filter(*filters).count())
    cardRemainingListInput.page_last = math.ceil(cardRemainingListInput.page_total / cardRemainingListInput.page_view_size)
    cardRemainingListInput.page_size = len(rows) # 현재 페이지에 검색된 수
    # [ E ] 페이징 처리

    jsondata = {}
    jsondata.update({"params" : cardRemainingListInput})
    jsondata.update({"list": rows})

    return jsondata

