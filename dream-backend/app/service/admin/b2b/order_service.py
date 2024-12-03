from fastapi import Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Optional
from inspect import currentframe as frame
from sqlalchemy.dialects import mysql as mysql_dialetct
from pymysql.converters import conversions, escape_item, encoders
from sqlalchemy import func, select, update, delete, Table, MetaData, and_
import math

from app.core import exceptions as ex
from app.core import util

from app.core.database import format_sql
from app.models.scm.b2b.order import *
from app.models.scm.b2b.goods import *
from app.models.scm.b2b.seller import *
from app.service.log_service import *
from app.service.admin.b2b import order_service
from app.schemas.admin.b2b.order import *


def order_list(request: Request, page_param: PPage_param):
    request.state.inspect = frame()
    db_scm = request.state.db_scm

    seller_stmt = (
        db_scm.query(
             T_B2B_SELLER.seller_id
            ,T_B2B_SELLER.seller_name
            ,T_B2B_SELLER.indend_md
            ,T_B2B_SELLER.indend_md_name
        )
        .subquery()
    )

    filters = []
    filters.append(getattr(T_B2B_ORDER, "delete_at") == None)

    # [ S ] search filter start
    if page_param.filters :
        if page_param.filters["skeyword"] :
            if page_param.filters["skeyword_type"] != "" :
                if page_param.filters["skeyword_type"] == "seller_id" or page_param.filters["skeyword_type"] == "seller_name" or page_param.filters["skeyword_type"] == "indend_md" or page_param.filters["skeyword_type"] == "indend_md_name" :
                    filters.append(getattr(seller_stmt.c, page_param.filters["skeyword_type"]).like("%"+page_param.filters["skeyword"]   +"%"))
                else :
                    filters.append(getattr(T_B2B_ORDER, page_param.filters["skeyword_type"]).like("%"+page_param.filters["skeyword"]   +"%"))
            else : 
                filters.append(
                    T_B2B_ORDER.title.like("%"+page_param.filters["skeyword"]+"%") 
                )

        if page_param.filters["create_at"]["startDate"] and page_param.filters["create_at"]["endDate"] :
            filters.append(
                and_(
                    T_B2B_ORDER.create_at >= page_param.filters["create_at"]["startDate"]
                    ,T_B2B_ORDER.create_at <= page_param.filters["create_at"]["endDate"] + " 23:59:59"
                )
            )

        if page_param.filters["state"] != '' :
            filters.append(T_B2B_ORDER.state == page_param.filters["state"])

    # [ E ] search filter end


    sql = (
        db_scm.query(
             T_B2B_ORDER.uid
            ,T_B2B_ORDER.guid
            ,T_B2B_ORDER.seller_id
            ,T_B2B_ORDER.service_type
            ,T_B2B_ORDER.category
            ,T_B2B_ORDER.title
            ,T_B2B_ORDER.state
            ,T_B2B_ORDER.commission_type
            ,T_B2B_ORDER.commission
            ,T_B2B_ORDER.token_name
            ,T_B2B_ORDER.sosok_uid
            ,T_B2B_ORDER.sosok_id
            ,T_B2B_ORDER.apply_user_uid
            ,T_B2B_ORDER.apply_user_id
            ,T_B2B_ORDER.apply_company
            ,T_B2B_ORDER.apply_name
            ,T_B2B_ORDER.apply_depart
            ,T_B2B_ORDER.apply_position
            ,T_B2B_ORDER.apply_phone
            ,T_B2B_ORDER.apply_email
            ,func.date_format(T_B2B_ORDER.create_at, '%Y-%m-%d').label('create_at')
            ,seller_stmt.c.seller_name
            ,seller_stmt.c.indend_md
            ,seller_stmt.c.indend_md_name
        )
        .join(
            seller_stmt, 
            T_B2B_ORDER.seller_id == seller_stmt.c.seller_id,
            isouter = True 
        )
        .filter(*filters)
        .order_by(T_B2B_ORDER.uid.desc())
        .offset((page_param.page-1)*page_param.page_view_size)
        .limit(page_param.page_view_size)
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    # [ S ] 페이징 처리
    page_param.page_total = (
        db_scm.query(T_B2B_ORDER)
        .join(
            seller_stmt, 
            T_B2B_ORDER.seller_id == seller_stmt.c.seller_id,
            isouter = True 
        )
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

# 신청내역 상세
def order_read(request: Request, uid: int):
    request.state.inspect = frame()
    db_scm = request.state.db_scm

    sql = ( 
        db_scm.query(
             T_B2B_ORDER.uid
            ,T_B2B_ORDER.guid
            ,T_B2B_ORDER.seller_id
            ,T_B2B_ORDER.service_type
            ,T_B2B_ORDER.category
            ,T_B2B_ORDER.title
            ,T_B2B_ORDER.state
            ,T_B2B_ORDER.commission_type
            ,T_B2B_ORDER.commission
            ,T_B2B_ORDER.token_name
            ,T_B2B_ORDER.sosok_uid
            ,T_B2B_ORDER.sosok_id
            ,T_B2B_ORDER.apply_user_uid
            ,T_B2B_ORDER.apply_user_id
            ,T_B2B_ORDER.apply_company
            ,T_B2B_ORDER.apply_name
            ,T_B2B_ORDER.apply_depart
            ,T_B2B_ORDER.apply_position
            ,T_B2B_ORDER.apply_phone
            ,T_B2B_ORDER.apply_email
            ,func.date_format(T_B2B_ORDER.create_at, '%Y-%m-%d %T').label('create_at')
            ,func.date_format(T_B2B_ORDER.update_at, '%Y-%m-%d %T').label('update_at')
            ,func.date_format(T_B2B_ORDER.delete_at, '%Y-%m-%d %T').label('delete_at')
        )
        .filter(
            T_B2B_ORDER.uid == uid
            ,T_B2B_ORDER.delete_at == None
        )
    )
    format_sql(sql)
    res = sql.first()

    if res == None :
        return ex.ReturnOK(404, "신청내역을 찾을 수 없습니다.", request)
    else :
        res = dict(zip(res.keys(), res))

    info_list = order_service.info_list(request, uid, res["guid"])
    request.state.inspect = frame()
    res.update({"info_list" : info_list})

    return res

def info_list(request: Request, uid: int, guid:int):
    request.state.inspect = frame()
    db_scm = request.state.db_scm
    
    sql = (
        db_scm.query(
             T_B2B_ORDER_INFO.uid
            ,T_B2B_ORDER_INFO.ouid
            ,T_B2B_ORDER_INFO.guid
            ,T_B2B_ORDER_INFO.option_title
            ,T_B2B_ORDER_INFO.option_num
            ,T_B2B_ORDER_INFO.option_type
            ,T_B2B_ORDER_INFO.placeholder
            ,T_B2B_ORDER_INFO.option_yn
            ,T_B2B_ORDER_INFO.apply_value
            ,T_B2B_ORDER_INFO.file_name
        )
        .filter(T_B2B_ORDER_INFO.ouid == uid, T_B2B_ORDER_INFO.guid == guid)
        .order_by(T_B2B_ORDER_INFO.option_num.asc())
    )

    rows = []
    for c in sql.all():
        list = dict(zip(c.keys(), c))
        rows.append(list)
    return rows