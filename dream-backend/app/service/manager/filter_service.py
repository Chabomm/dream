from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, select, column, table, case, or_
from fastapi import Request
from inspect import currentframe as frame
from fastapi.encoders import jsonable_encoder
import math

from app.core import util
from app.core.database import format_sql

from app.models.menu import *
from app.models.partner import *

# 관리자 역할
def roles(request: Request) :
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    sql = (
        db.query(T_ADMIN_ROLE.uid.label("key"), T_ADMIN_ROLE.name.label("text"))
        .filter(
            T_ADMIN_ROLE.partner_uid == user.partner_uid
            ,T_ADMIN_ROLE.site_id == "manager"
        )
        .order_by(T_ADMIN_ROLE.uid.asc())
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    jsondata = {}
    jsondata.update({"list": rows})
    
    return jsondata

# 전체 메뉴 리스트 (고객사_관리자_역할_필터조건)
def menu_list_for_roles(request: Request):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    jsondata = {}
    sql1 = (
        db.query(
             T_ADMIN_MENU.uid
            ,T_ADMIN_MENU.name
            ,T_ADMIN_MENU.depth
            ,T_ADMIN_MENU.parent
        )
        .filter(
            T_ADMIN_MENU.site_id == "manager"
            ,T_ADMIN_MENU.depth == 1
        )
        .order_by(T_ADMIN_MENU.sort.asc())
    )
    depth1 = []
    for c in sql1.all() :
        depth1.append(dict(zip(c.keys(), c)))
    jsondata.update({"depth1": depth1})

    partner_roles = db.query(T_PARTNER.roles).filter(T_PARTNER.uid == user.partner_uid).first()
    sql_menus_by_roles = db.query(T_ADMIN_ROLE.menus).filter(T_ADMIN_ROLE.uid.in_(partner_roles.roles))
    
    menus_by_roles = []
    for c in sql_menus_by_roles.all():
        menus_by_roles = menus_by_roles + c.menus # 검색할 메뉴 합치기

    menus_by_roles = list(set(menus_by_roles)) # 중복 제거
    menus_by_roles.sort() # 걍 오름차순 정렬 굳이 할필욘없긴함

    sql2 = (
        db.query(
             T_ADMIN_MENU.uid
            ,T_ADMIN_MENU.name
            ,T_ADMIN_MENU.depth
            ,T_ADMIN_MENU.parent
        )
        .filter(
            T_ADMIN_MENU.site_id == "manager"
            ,T_ADMIN_MENU.depth == 2
            ,T_ADMIN_MENU.uid.in_(menus_by_roles)
        )
        .order_by(T_ADMIN_MENU.sort.asc())
    )
    depth2 = []
    for c in sql2.all() :
        depth2.append(dict(zip(c.keys(), c)))
    jsondata.update({"depth2": depth2})

    menus_list = []
    
    for d1 in depth1 :
        d1["sub"] = []
        for d2 in depth2 :
            if util.checkNumeric(d2["parent"]) == util.checkNumeric(d1["uid"]) :
                d1["sub"].append(d2)
    
    return jsondata



