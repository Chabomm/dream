from fastapi import Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Optional
from inspect import currentframe as frame
from sqlalchemy.dialects import mysql as mysql_dialetct
from pymysql.converters import conversions, escape_item, encoders
from sqlalchemy import func, select, update, delete, Table, MetaData
import math

from app.core import exceptions as ex
from app.core import util
from app.core.database import format_sql
from app.deps import auth
from app.models.session import *
from app.models.manager import *
from app.models.menu import *
from app.models.partner import *
from app.schemas.schema import *
from app.schemas.manager.auth import *
from app.schemas.manager.manager import *
from app.service import log_service

# 고객사 관리자 역할 전체 리스트
def admin_rols_list(request: Request, page_param: PPage_param):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    where = ""
    where = where + "WHERE site_id = 'manager' "
    where = where + "AND partner_uid = " + str(user.partner_uid) + " "

    # [ S ] search filter start
    if not util.isEmptyObject(page_param.filters, "skeyword") :
        if not util.isEmptyObject(page_param.filters, "skeyword_type") :
            where = where + "AND "+page_param.filters["skeyword_type"]+" like '%"+page_param.filters["skeyword"]+"%' "
        else : 
            where = where + "AND ("
            where = where + "   name like '%"+page_param.filters["skeyword"]+"%'"
            where = where + ") "
    # [ E ] search filter end

    sql = """
        SELECT 
            uid
            ,name
            ,menus
            ,( 
                select GROUP_CONCAT(name SEPARATOR ', ') AS result  
                From T_ADMIN_MENU 
                where uid MEMBER OF(menus->>'$')
            ) as roles_txt 
        FROM T_ADMIN_ROLE
        {where}
        ORDER BY uid DESC
    """.format(where=where, user=user)

    res = db.execute(text(sql)).fetchall()

    rows = []
    for c in res :
        rows.append(dict(zip(c.keys(), c)))

    # 페이징이 없어서
    page_param.page_total = len(rows)

    jsondata = {}
    jsondata.update({"params": page_param})
    jsondata.update({"list": rows})

    return jsondata

# 고객사 관리자 역할관리 - 상세
def admin_roles_read(request: Request, uid: int):
    db = request.state.db
    user = request.state.user

    sql = (
        db.query(
             T_ADMIN_ROLE.uid
            ,T_ADMIN_ROLE.name
            ,T_ADMIN_ROLE.menus
        )
        .filter(T_ADMIN_ROLE.uid == uid)
    )
    # format_sql(sql)
    res = sql.first()
    if res is not None:
        res = dict(zip(res.keys(), res))
    return res

# 고객사 관리자 역할관리_편집 - 등록
def admin_roles_create(request: Request, adminRolesInput: AdminRolesInput) :
    request.state.inspect = frame()
    db = request.state.db 
    user = request.state.user

    db_item = T_ADMIN_ROLE (
         name = adminRolesInput.name
        ,menus = adminRolesInput.menus
        ,partner_uid = user.partner_uid
        ,site_id = "manager"
    )
    db.add(db_item)
    db.flush()

    log_service.create_log(request, db_item.uid, "T_ADMIN_ROLE", "INSERT", "관리자 역할관리 등록", 0, db_item.uid, user.user_id)
    request.state.inspect = frame()

    return db_item

# 고객사 관리자 역할관리_편집 - 수정
def admin_roles_update(request: Request, adminRolesInput: AdminRolesInput) :
    request.state.inspect = frame()
    db = request.state.db 
    user = request.state.user

    res = db.query(T_ADMIN_ROLE).filter(T_ADMIN_ROLE.uid == adminRolesInput.uid).first()

    if res is None :
        raise ex.NotFoundUser

    if adminRolesInput.name is not None and res.name != adminRolesInput.name : 
        log_service.create_log(request, adminRolesInput.uid, "T_ADMIN_ROLE", "name", "역할명 수정", res.name, adminRolesInput.name, user.user_id)
        request.state.inspect = frame()
        res.name = adminRolesInput.name

    if adminRolesInput.menus is not None and res.menus != adminRolesInput.menus : 
        log_service.create_log(request, adminRolesInput.uid, "T_ADMIN_ROLE", "menus", "배정된 메뉴 수정", res.menus, adminRolesInput.menus, user.user_id)
        request.state.inspect = frame()
        res.menus = adminRolesInput.menus

    return res

# 고객사 관리자 역할관리_편집 - 삭제  
def admin_roles_delete(request: Request, uid: int):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user
    
    db.query(T_ADMIN_ROLE).filter(T_ADMIN_ROLE.uid == uid).delete()
    
    log_service.create_log(request, uid, "T_ADMIN_ROLE", "DELETE", "관리자 역할관리 삭제", uid, '', user.user_id)
    request.state.inspect = frame()

    return






