from fastapi import Request
from inspect import currentframe as frame
from app.core.database import format_sql
from sqlalchemy import func, select, update, delete, Table, MetaData, and_
from app.core import util
import math

from app.schemas.schema import *
# from app.schemas.manager.point.assign.balance import *
from app.models.point.point import *
from app.models.member import *
from app.service.log_service import *

def mall_list(request: Request, page_param: PPage_param, fullsearch:bool=False):
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
    filters.append(getattr(T_POINT_USED, "delete_at") == None)
    filters.append(getattr(T_MEMBER_INFO, "partner_uid") == user.partner_uid)

    # [ S ] search filter start
    if page_param.filters :
        if page_param.filters["skeyword"] :
            if page_param.filters["skeyword_type"] != "" :
                if page_param.filters["skeyword_type"] == "order_no" :
                    filters.append(getattr(T_POINT_USED, page_param.filters["skeyword_type"]).like("%"+page_param.filters["skeyword"]+"%"))
                else : 
                    filters.append(getattr(T_MEMBER_INFO, page_param.filters["skeyword_type"]).like("%"+page_param.filters["skeyword"]+"%"))
            else : 
                filters.append(
                      T_MEMBER_INFO.user_name.like("%"+page_param.filters["skeyword"]+"%")
                    | T_MEMBER_INFO.user_id.like("%"+page_param.filters["skeyword"]+"%")
                    | T_POINT_USED.order_no.like("%"+page_param.filters["skeyword"]+"%")
                )

        if page_param.filters["create_at"]["startDate"] and page_param.filters["create_at"]["endDate"] :
            filters.append(
                and_(
                    T_POINT_USED.create_at >= page_param.filters["create_at"]["startDate"]
                    ,T_POINT_USED.create_at <= page_param.filters["create_at"]["endDate"] + " 23:59:59"
                )
            )
        
        if page_param.filters["used_type"] :
            filters.append(T_POINT_USED.used_type == page_param.filters["used_type"])
    # [ E ] search filter end

    sql = (
        db.query(
             T_POINT_USED.uid
            ,T_POINT_USED.group_id
            ,T_POINT_USED.point_id
            ,case(
                [
                    (T_POINT_USED.used_type == '1', "사용")
                    ,(T_POINT_USED.used_type == '2', "차감")
                    ,(T_POINT_USED.used_type == '3', "환불")
                ]
            ).label('used_type')
            ,T_POINT_USED.used_point
            ,T_POINT_USED.remaining_point
            ,T_POINT_USED.order_no
            ,T_POINT_USED.order_uid
            ,T_POINT_USED.order_info_uid
            ,T_POINT_USED.reason
            ,T_POINT_USED.user_id
            ,T_POINT_USED.partner_uid
            ,T_POINT_USED.partner_id
            ,func.date_format(T_POINT_USED.create_at, '%Y-%m-%d %T').label('create_at')
            ,T_MEMBER_INFO.user_name
            ,T_MEMBER_INFO.user_id
        )
        .join (
            T_MEMBER_INFO, 
            T_MEMBER_INFO.user_id == T_POINT_USED.user_id,
            isouter = True # LEFT JOIN
        )
        .filter(*filters)
        .order_by(T_POINT_USED.uid.desc())
        .offset(offsets)
        .limit(limits)
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    # [ S ] 페이징 처리
    page_param.page_total = (
         db.query(T_POINT_USED)
        .join (
            T_MEMBER_INFO, 
            T_MEMBER_INFO.user_id == T_POINT_USED.user_id,
            isouter = True # LEFT JOIN
        )
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
