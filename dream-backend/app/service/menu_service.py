from fastapi import Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Optional
from inspect import currentframe as frame
from sqlalchemy.dialects import mysql as mysql_dialetct
from pymysql.converters import conversions, escape_item, encoders
from sqlalchemy import func, select, update, delete, Table, MetaData
import math
from app.schemas.schema import *

from app.core import util
from app.core.database import format_sql

from app.models.menu import *
from app.models.manager import *
from app.models.admin import *
from app.models.partner import *

# 메뉴 select
def get_admin_menus(request: Request, partner_info:Optional[dict] = None) :
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user
    
    # [ S ] get roles
    if user.token_name == "DREAM" : # 일반회원
        user_roles == ()
    
    elif user.token_name == "DREAM-MANAGER" : # 고객사
        user_roles = (
            db.query(T_MANAGER.roles)
            .filter(T_MANAGER.uid == user.user_uid)
        ).first()

    elif user.token_name == "DREAM-ADMIN" : # 어드민
        user_roles = (
            db.query(T_ADMIN.roles)
            .filter(T_ADMIN.uid == user.user_uid)
        ).first()
    # [ E ] get roles

    
    dict_roles = dict(user_roles)
    if len(dict_roles["roles"]) > 0 :
        roles_to_menus = ( # 역할의 menus
            db.query(T_ADMIN_ROLE.menus)
            .filter(T_ADMIN_ROLE.uid.in_(user_roles.roles)) # user_roles.roles = [7]
        )

        my_menus = [] # 역할의 메뉴 리스트를 한 배열에 담기
        for c in roles_to_menus.all() :
            row = dict(zip(c.keys(), c))
            my_menus = my_menus + row["menus"]

        sql = (
            db.query(
                T_ADMIN_MENU.uid
                ,T_ADMIN_MENU.name
                ,T_ADMIN_MENU.icon
            )
            .filter(T_ADMIN_MENU.uid.in_(my_menus))
        )

    filters = []
    if user.token_name == "DREAM-MANAGER" :

        partner_roles = db.query(T_PARTNER.roles).filter(T_PARTNER.uid == user.partner_uid).first()
        sql_menus_by_roles = db.query(T_ADMIN_ROLE.menus).filter(T_ADMIN_ROLE.uid.in_(partner_roles.roles))
        
        menus_by_roles = []
        for c in sql_menus_by_roles.all():
            menus_by_roles = menus_by_roles + c.menus # 검색할 메뉴 합치기

        menus_by_roles = list(set(menus_by_roles)) # 중복 제거
        menus_by_roles.sort() # 걍 오름차순 정렬 굳이 할필욘없긴함

        filters.append(getattr(T_ADMIN_MENU, "site_id") == "manager")
        filters.append(getattr(T_ADMIN_MENU, "uid").in_(menus_by_roles))
        if user.role != "master" : # 고객사
            filters.append(getattr(T_ADMIN_MENU, "uid").in_(my_menus))

    elif user.token_name == "DREAM-ADMIN" :
        filters.append(getattr(T_ADMIN_MENU, "site_id") == "admin")
        if user.role != "admin" : # 어드민
            filters.append(getattr(T_ADMIN_MENU, "uid").in_(my_menus))
        
    if partner_info != None and partner_info["partner_type"] != "201" :
        filters.append(getattr(T_ADMIN_MENU, "uid") != 79)

    sql2 = (
        db.query(
             T_ADMIN_MENU.uid
            ,T_ADMIN_MENU.name
            ,T_ADMIN_MENU.to
            ,T_ADMIN_MENU.sort
            ,T_ADMIN_MENU.parent
        )
        .filter(*filters)
        .order_by(T_ADMIN_MENU.sort.asc())
    )
    format_sql(sql2)

    depth1s = []
    for c in sql2.all() :
        is_due = False # 중복이 안된다고 가정
        for d1 in depth1s :
            if d1 == c.parent :
                is_due =  True # 이미 추가된 1depth 메뉴
        if not is_due :
            depth1s.append(c.parent)

    sql = ( # 1depth menu
        db.query(
             T_ADMIN_MENU.uid
            ,T_ADMIN_MENU.name
            ,T_ADMIN_MENU.icon
            ,T_ADMIN_MENU.sort
        )
        .filter(T_ADMIN_MENU.uid.in_(depth1s))
        .order_by(T_ADMIN_MENU.sort.asc())
    )

    rows = []
    for c in sql.all():
        column_json = dict(zip(c.keys(), c))
        column_json["children"] = []

        for cc in sql2.all():
            if cc.parent == c.uid :
                d2_json = dict(zip(cc.keys(), cc))
                column_json["children"].append(d2_json)

        rows.append(column_json)
    
    jsondata = {}
    jsondata.update({"admin_menus": rows})

    return jsondata