from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, select, column, table, case, or_
from fastapi import Request
from inspect import currentframe as frame
from fastapi.encoders import jsonable_encoder
import math

from app.core import util
from app.core.database import format_sql

from app.models.menu import *

# 관리자 역할
def roles(request: Request, site_id : str) :
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    sql = (
        db.query(T_ADMIN_ROLE.uid.label("key"), T_ADMIN_ROLE.name.label("text"))
        .filter(
            T_ADMIN_ROLE.site_id == site_id
            ,T_ADMIN_ROLE.partner_uid == 0
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
def menu_list_for_roles(request: Request, site_id: any):
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
             T_ADMIN_MENU.site_id == site_id
            ,T_ADMIN_MENU.depth == 1)
        .order_by(T_ADMIN_MENU.sort.asc())
    )
    depth1 = []
    for c in sql1.all() :
        depth1.append(dict(zip(c.keys(), c)))
    jsondata.update({"depth1": depth1})

    sql2 = (
        db.query(
             T_ADMIN_MENU.uid
            ,T_ADMIN_MENU.name
            ,T_ADMIN_MENU.depth
            ,T_ADMIN_MENU.parent
        )
        .filter(
             T_ADMIN_MENU.site_id == site_id
            ,T_ADMIN_MENU.depth == 2
        )
        .order_by(T_ADMIN_MENU.sort.asc())
    )
    depth2 = []
    for c in sql2.all() :
        depth2.append(dict(zip(c.keys(), c)))
    jsondata.update({"depth2": depth2})
    
    return jsondata



