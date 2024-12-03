from fastapi import Request
from inspect import currentframe as frame
from app.core.database import format_sql
from sqlalchemy import func, select, update, delete, Table, MetaData, and_
from app.core import util
import math

from app.schemas.schema import *
from app.models.point.point import *
from app.models.point.sikwon import *
from app.models.member import *
from app.models.manager import *
from app.service.log_service import *

# 복지포인트 지급 - 리스트
def assign_list(request: Request, page_param: PPage_param, fullsearch:bool=False):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user
           
    offsets = 0
    if fullsearch == False :
        offsets = (page_param.page-1)*page_param.page_view_size

    limits = None
    if fullsearch == False :
        limits = page_param.page_view_size

    member_stmt = (
        db.query(
             T_MEMBER_INFO.uid
            ,T_MEMBER_INFO.user_id
            ,T_MEMBER_INFO.login_id
            ,T_MEMBER_INFO.user_name
            ,T_MEMBER_INFO.partner_uid
            ,T_MEMBER_INFO.partner_id
            ,T_MEMBER_INFO.depart
            ,T_MEMBER_INFO.position
            ,T_MEMBER_INFO.position2
        )
        .filter(T_MEMBER_INFO.delete_at == None)
        .subquery()
    )

    filters = []
    filters.append(getattr(T_POINT, "delete_at") == None)
    filters.append(getattr(T_POINT, "partner_uid") == user.partner_uid)

    # [ S ] search filter start
    if page_param.filters :
        if page_param.filters["skeyword"] :
            if page_param.filters["skeyword_type"] != "" :
                if page_param.filters["skeyword_type"] == "user_name" :
                    print('user_name')
                    filters.append(member_stmt.c.user_name.like("%"+page_param.filters["skeyword"]+"%"))
                elif page_param.filters["skeyword_type"] == "position" :
                    filters.append(member_stmt.c.position.like("%"+page_param.filters["skeyword"]+"%"))
                elif page_param.filters["skeyword_type"] == "depart" :
                    filters.append(member_stmt.c.depart.like("%"+page_param.filters["skeyword"]+"%"))
                elif page_param.filters["skeyword_type"] == "admin_name" :
                    filters.append(T_MANAGER.name.like("%"+page_param.filters["skeyword"]+"%"))
                else :
                    filters.append(getattr(T_POINT, page_param.filters["skeyword_type"]).like("%"+page_param.filters["skeyword"]+"%"))
            else : 
                filters.append(
                      T_POINT.reason.like("%"+page_param.filters["skeyword"]+"%")
                    | T_POINT.user_id.like("%"+page_param.filters["skeyword"]+"%")
                    | T_POINT.admin_memo.like("%"+page_param.filters["skeyword"]+"%")
                    | member_stmt.c.user_name.like("%"+page_param.filters["skeyword"]+"%")
                    | member_stmt.c.depart.like("%"+page_param.filters["skeyword"]+"%")
                    | member_stmt.c.position.like("%"+page_param.filters["skeyword"]+"%")
                    | T_MANAGER.name.like("%"+page_param.filters["skeyword"]+"%")
                )

        if page_param.filters["create_at"]["startDate"] and page_param.filters["create_at"]["endDate"] :
            filters.append(
                and_(
                    T_POINT.create_at >= page_param.filters["create_at"]["startDate"]
                    ,T_POINT.create_at <= page_param.filters["create_at"]["endDate"] + " 23:59:59"
                )
            )

        if page_param.filters["saved_type"]  :
            filters.append(T_POINT.saved_type == page_param.filters["saved_type"])
    # [ E ] search filter end

    sql = (
        db.query(
             T_POINT.uid
            ,T_POINT.group_id
            ,case(
                [
                    (T_POINT.saved_type == '1', "대량지급")
                    ,(T_POINT.saved_type == '2', "개별지급")
                    ,(T_POINT.saved_type == '3', "회수")
                ]
            ).label('saved_type')
            ,T_POINT.point
            ,T_POINT.saved_point
            ,func.date_format(T_POINT.expiration_date, '%Y-%m-%d').label('expiration_date')
            ,T_POINT.user_id
            ,T_POINT.manager_id
            ,T_POINT.partner_uid
            ,T_POINT.partner_id
            ,T_POINT.reason
            ,T_POINT.admin_memo
            ,func.date_format(T_POINT.create_at, '%Y-%m-%d').label('create_at')
            ,member_stmt.c.user_name
            ,member_stmt.c.depart
            ,member_stmt.c.position
            ,member_stmt.c.position2
            ,T_MANAGER.name.label('admin_name')
        )
        .join (
            member_stmt, 
            member_stmt.c.user_id == T_POINT.user_id,
            isouter = True # LEFT JOIN
        )
        .join (
            T_MANAGER, 
            T_MANAGER.user_id == T_POINT.manager_id,
            isouter = True # LEFT JOIN
        )
        .filter(*filters)
        .order_by(T_POINT.uid.desc())
        .offset(offsets)
        .limit(limits)
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    # [ S ] 페이징 처리
    page_param.page_total = (
         db.query(T_POINT)
        .join (
            member_stmt, 
            member_stmt.c.user_id == T_POINT.user_id,
            isouter = True # LEFT JOIN
        )
        .join (
            T_MANAGER, 
            T_MANAGER.user_id == T_POINT.manager_id,
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

# 식권포인트 지급 - 리스트
def assign_sikwon_list(request: Request, page_param: PPage_param, fullsearch:bool=False):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    offsets = 0
    if fullsearch == False :
        offsets = (page_param.page-1)*page_param.page_view_size

    limits = None
    if fullsearch == False :
        limits = page_param.page_view_size

    member_stmt = (
        db.query(
             T_MEMBER_INFO.uid
            ,T_MEMBER_INFO.user_id
            ,T_MEMBER_INFO.login_id
            ,T_MEMBER_INFO.user_name
            ,T_MEMBER_INFO.partner_uid
            ,T_MEMBER_INFO.partner_id
            ,T_MEMBER_INFO.depart
            ,T_MEMBER_INFO.position
            ,T_MEMBER_INFO.position2
        )
        .filter(T_MEMBER_INFO.delete_at == None)
        .subquery()
    )

    filters = []
    filters.append(getattr(T_SIKWON, "delete_at") == None)
    filters.append(getattr(T_SIKWON, "partner_uid") == user.partner_uid)

    # [ S ] search filter start
    if page_param.filters :
        if page_param.filters["skeyword"] :
            if page_param.filters["skeyword_type"] != "" :
                if page_param.filters["skeyword_type"] == "user_name" :
                    print('user_name')
                    filters.append(member_stmt.c.user_name.like("%"+page_param.filters["skeyword"]+"%"))
                elif page_param.filters["skeyword_type"] == "position" :
                    filters.append(member_stmt.c.position.like("%"+page_param.filters["skeyword"]+"%"))
                elif page_param.filters["skeyword_type"] == "depart" :
                    filters.append(member_stmt.c.depart.like("%"+page_param.filters["skeyword"]+"%"))
                elif page_param.filters["skeyword_type"] == "admin_name" :
                    filters.append(T_MANAGER.name.like("%"+page_param.filters["skeyword"]+"%"))
                else :
                    filters.append(getattr(T_SIKWON, page_param.filters["skeyword_type"]).like("%"+page_param.filters["skeyword"]+"%"))
            else : 
                filters.append(
                      T_SIKWON.reason.like("%"+page_param.filters["skeyword"]+"%")
                    | T_SIKWON.user_id.like("%"+page_param.filters["skeyword"]+"%")
                    | T_SIKWON.admin_memo.like("%"+page_param.filters["skeyword"]+"%")
                    | member_stmt.c.user_name.like("%"+page_param.filters["skeyword"]+"%")
                    | member_stmt.c.depart.like("%"+page_param.filters["skeyword"]+"%")
                    | member_stmt.c.position.like("%"+page_param.filters["skeyword"]+"%")
                    | T_MANAGER.name.like("%"+page_param.filters["skeyword"]+"%")
                )

        if page_param.filters["create_at"]["startDate"] and page_param.filters["create_at"]["endDate"] :
            filters.append(
                and_(
                    T_SIKWON.create_at >= page_param.filters["create_at"]["startDate"]
                    ,T_SIKWON.create_at <= page_param.filters["create_at"]["endDate"] + " 23:59:59"
                )
            )

        if page_param.filters["saved_type"]  :
            filters.append(T_SIKWON.saved_type == page_param.filters["saved_type"])
    # [ E ] search filter end
           
    sql = (
        db.query(
             T_SIKWON.uid
            ,T_SIKWON.group_id
            ,case(
                [
                    (T_SIKWON.saved_type == '1', "대량지급")
                    ,(T_SIKWON.saved_type == '2', "개별지급")
                    ,(T_SIKWON.saved_type == '3', "회수")
                ]
            ).label('saved_type')
            ,T_SIKWON.point
            ,T_SIKWON.saved_point
            ,func.date_format(T_SIKWON.expiration_date, '%Y-%m-%d').label('expiration_date')
            ,T_SIKWON.user_id
            ,T_SIKWON.manager_id
            ,T_SIKWON.partner_uid
            ,T_SIKWON.partner_id
            ,T_SIKWON.reason
            ,T_SIKWON.admin_memo
            ,func.date_format(T_SIKWON.create_at, '%Y-%m-%d').label('create_at')
            ,member_stmt.c.user_name
            ,member_stmt.c.depart
            ,member_stmt.c.position
            ,member_stmt.c.position2
            ,T_MANAGER.name.label('admin_name')
        )
        .join (
            member_stmt, 
            member_stmt.c.user_id == T_SIKWON.user_id,
            isouter = True # LEFT JOIN
        )
        .join (
            T_MANAGER, 
            T_MANAGER.user_id == T_SIKWON.manager_id,
            isouter = True # LEFT JOIN
        )
        .filter(*filters)
        .order_by(T_SIKWON.uid.desc())
        .offset(offsets)
        .limit(limits)
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    # [ S ] 페이징 처리
    page_param.page_total = (
         db.query(T_SIKWON)
        .join (
            member_stmt, 
            member_stmt.c.user_id == T_SIKWON.user_id,
            isouter = True # LEFT JOIN
        )
        .join (
            T_MANAGER, 
            T_MANAGER.user_id == T_SIKWON.manager_id,
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
