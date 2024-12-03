from fastapi import Request
from inspect import currentframe as frame
from app.core.database import format_sql
from sqlalchemy import func, select, update, delete, Table, MetaData, and_
import math
from app.core import exceptions as ex

from app.service.manager.b2b import goods_service
from app.schemas.schema import *
from app.schemas.manager.b2b.goods import *
from app.models.scm.b2b.goods import *


# 서비스리스트
def goods_list(request: Request, page_param: PPage_param):
    request.state.inspect = frame()
    db_scm = request.state.db_scm
    user = request.state.user

    filters = []
    filters.append(getattr(T_B2B_GOODS, "delete_at") == None)
    filters.append(getattr(T_B2B_GOODS, "is_display") == 'T')

    if page_param.filters :
        if page_param.filters["category"] != '' :
            filters.append(getattr(T_B2B_GOODS, "category") == page_param.filters["category"])

    sql = (
        db_scm.query(
             T_B2B_GOODS.uid
            ,T_B2B_GOODS.category
            ,T_B2B_GOODS.title
            ,T_B2B_GOODS.keyword
            ,T_B2B_GOODS.thumb
            ,T_B2B_GOODS.service_type
            ,func.date_format(T_B2B_GOODS.create_at, '%Y-%m-%d %T').label('create_at')
            ,func.date_format(T_B2B_GOODS.update_at, '%Y-%m-%d %T').label('update_at')
            ,func.date_format(T_B2B_GOODS.delete_at, '%Y-%m-%d %T').label('delete_at')
        )
        .filter(*filters)
        .order_by(T_B2B_GOODS.sort.asc(), T_B2B_GOODS.uid.desc())
        .offset((page_param.page-1)*page_param.page_view_size)
        .limit(page_param.page_view_size)
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        list = dict(zip(c.keys(), c))
        if list["keyword"] != '' and list["keyword"] != None :
            keyword = list["keyword"].split(',')
            list["keyword"] = keyword

        rows.append(list)


    # [ S ] 페이징 처리
    page_param.page_total = (
        db_scm.query(T_B2B_GOODS)
        .filter(*filters)
        .count()
    )
    page_param.page_last = math.ceil(page_param.page_total / page_param.page_view_size)
    page_param.page_size = len(rows)  # 현재 페이지에 검색된 수
    # [ E ] 페이징 처리

    jsondata = {}
    jsondata.update({"params" : page_param})
    jsondata.update({"list": rows})

    return jsondata

# 서비스_상세
def goods_read(request: Request, uid: int):
    request.state.inspect = frame()
    db_scm = request.state.db_scm
    user = request.state.user

    sql = ( 
        db_scm.query(
             T_B2B_GOODS.uid
            ,T_B2B_GOODS.service_type
            ,T_B2B_GOODS.category
            ,T_B2B_GOODS.seller_id
            ,T_B2B_GOODS.seller_name
            ,T_B2B_GOODS.title
            ,T_B2B_GOODS.sub_title
            ,T_B2B_GOODS.contents
            ,T_B2B_GOODS.benefit
            ,T_B2B_GOODS.attention
            ,T_B2B_GOODS.keyword
            ,T_B2B_GOODS.thumb
            ,T_B2B_GOODS.option_yn
            ,T_B2B_GOODS.option_value
            ,T_B2B_GOODS.option_cnt
            ,T_B2B_GOODS.market_price
            ,T_B2B_GOODS.price
            ,T_B2B_GOODS.str_sale_percent
            ,T_B2B_GOODS.str_market_price
            ,T_B2B_GOODS.str_price
            ,T_B2B_GOODS.commission_type
            ,T_B2B_GOODS.commission
            ,T_B2B_GOODS.other_service
            ,T_B2B_GOODS.sort
            ,T_B2B_GOODS.start_date
            ,T_B2B_GOODS.end_date
            ,T_B2B_GOODS.is_display
            ,T_B2B_GOODS.state
            ,func.date_format(T_B2B_GOODS.create_at, '%Y-%m-%d %T').label('create_at')
            ,func.date_format(T_B2B_GOODS.update_at, '%Y-%m-%d %T').label('update_at')
            ,func.date_format(T_B2B_GOODS.delete_at, '%Y-%m-%d %T').label('delete_at')
        )
        .filter(
            T_B2B_GOODS.uid == uid
            ,T_B2B_GOODS.is_display == 'T'
            ,T_B2B_GOODS.delete_at == None
        )
    )
    format_sql(sql)
    res = sql.first()

    if res == None :
        return ex.ReturnOK(404, "서비스를 찾을 수 없습니다.", request)
    else :
        res = dict(zip(res.keys(), res))

    image_list = goods_service.image_list(request, uid)
    request.state.inspect = frame()
    res.update({"etc_images" : image_list})

    other_service_list = goods_service.other_service_list(request, res["other_service"], res["service_type"])
    request.state.inspect = frame()
    res.update({"other_service_list" : other_service_list})

    return res

# 업체추가리스트
def other_service_list(request: Request, other_service:str, service_type:str):
    request.state.inspect = frame()
    db_scm = request.state.db_scm
    user = request.state.user

    if other_service != '' and other_service != None :
        other_service = other_service.split(',')
    else :
        return

    filters = []
    filters.append(getattr(T_B2B_GOODS, "delete_at") == None)
    filters.append(getattr(T_B2B_GOODS, "service_type") == service_type)
    filters.append(getattr(T_B2B_GOODS, "is_display") == 'T')
    filters.append(T_B2B_GOODS.uid.in_(other_service))

    sql = (
        db_scm.query(
             T_B2B_GOODS.uid
            ,T_B2B_GOODS.category
            ,T_B2B_GOODS.title
            ,T_B2B_GOODS.keyword
            ,T_B2B_GOODS.thumb
            ,T_B2B_GOODS.str_market_price
            ,T_B2B_GOODS.str_price
            ,func.date_format(T_B2B_GOODS.create_at, '%Y-%m-%d %T').label('create_at')
            ,func.date_format(T_B2B_GOODS.update_at, '%Y-%m-%d %T').label('update_at')
            ,func.date_format(T_B2B_GOODS.delete_at, '%Y-%m-%d %T').label('delete_at')
        )
        .filter(*filters)
        .order_by(T_B2B_GOODS.uid.desc())
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        list = dict(zip(c.keys(), c))
        if list["keyword"] != '' and list["keyword"] != None :
            keyword = list["keyword"].split(',')
            list["keyword"] = keyword

        rows.append(list)

    return rows


def image_list(request: Request, uid: int):
    request.state.inspect = frame()
    db_scm = request.state.db_scm
    db = request.state.db
    
    sql = (
        db_scm.query(
             T_B2B_GOODS_IMAGE.guid
            ,T_B2B_GOODS_IMAGE.img_url
            ,T_B2B_GOODS_IMAGE.sort
        )
        .filter(T_B2B_GOODS_IMAGE.guid == uid)
        .order_by(T_B2B_GOODS_IMAGE.sort.asc())
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    return rows
