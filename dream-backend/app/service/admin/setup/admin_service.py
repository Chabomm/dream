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
from app.models.admin import *
from app.models.menu import *
from app.models.partner import *
from app.schemas.schema import *
from app.schemas.admin.auth import *
from app.schemas.admin.admin import *
from app.service import log_service

# 관리자 list 
def admin_user_list(request: Request, page_param: PPage_param):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    where = ""
    where = where + "WHERE delete_at is NULL "

    # [ S ] search filter start
    if not util.isEmptyObject(page_param.filters, "state") :
        where = where + "AND state = '" + page_param.filters["state"] + "' "

    if not util.isEmptyObject(page_param.filters, "roles") and len(page_param.filters["roles"]) > 0 :
        where = where + "AND json_contains(roles, '"+ str(page_param.filters["roles"]) +"') "

    if not util.isEmptyObject(page_param.filters, "skeyword") :
        if not util.isEmptyObject(page_param.filters, "skeyword_type") :
            where = where + "AND "+page_param.filters["skeyword_type"]+" like '%"+page_param.filters["skeyword"]+"%' "
        else : 
            where = where + "AND ("
            where = where + "   user_id like '%"+page_param.filters["skeyword"]+"%'"
            where = where + "   or user_name like '%"+page_param.filters["skeyword"]+"%'"
            where = where + "   or depart like '%"+page_param.filters["skeyword"]+"%'"
            where = where + ") "
    # [ E ] search filter end
    
    sql = """
        SELECT 
             uid
            ,user_id
            ,user_name
            ,tel
            ,mobile
            ,email
            ,role
            ,DATE_FORMAT(create_at, '%Y-%m-%d %T') as create_at
            ,DATE_FORMAT(last_at, '%Y-%m-%d %T') as last_at
            ,depart
            ,roles
            ,state
            ,( 
                select GROUP_CONCAT(name SEPARATOR ', ') AS result  
                From T_ADMIN_ROLE 
                where uid MEMBER OF(roles->>'$')
            ) as roles_txt
        FROM T_ADMIN
        {where}
        ORDER BY uid DESC
        LIMIT {start}, {end}
    """.format(where=where, start=(page_param.page-1)*page_param.page_view_size, end=page_param.page_view_size)

    res = db.execute(text(sql)).fetchall()

    rows = []
    for c in res :
        rows.append(dict(zip(c.keys(), c)))

    page_param.page_total = db.execute(text("select count(uid) as cnt from T_ADMIN " + where)).scalar()

    page_param.page_last = math.ceil(page_param.page_total / page_param.page_view_size)
    page_param.page_size = len(rows) 

    jsondata = {}
    jsondata.update({"params" : page_param})
    jsondata.update({"list": rows})

    return jsondata

# 고객사 관리자 상세보기
def admin_user_read(request: Request, uid: int = 0, user_id: str = ""):
    request.state.inspect = frame()
    db = request.state.db

    filters = []
    filters.append(getattr(T_ADMIN, "delete_at") == None)

    if uid > 0:
        filters.append(getattr(T_ADMIN, "uid") == uid)
    elif user_id != "":
        filters.append(getattr(T_ADMIN, "user_id") == user_id)
    else:
        return None
    
    sql = (
        db.query(
             T_ADMIN.uid
            ,T_ADMIN.user_id
            ,T_ADMIN.user_name
            ,T_ADMIN.tel
            ,T_ADMIN.mobile
            ,T_ADMIN.email
            ,T_ADMIN.role
            ,T_ADMIN.position1
            ,T_ADMIN.position2
            ,T_ADMIN.depart
            ,T_ADMIN.roles
            ,T_ADMIN.state
            ,func.date_format(T_ADMIN.create_at, '%Y-%m-%d %T').label('create_at')
        )
        .filter(*filters)
    )
    # format_sql(sql)
    res = sql.first()
    if res is not None:
        res = dict(zip(res.keys(), res))
    return res

# 고객사 관리자 편집 - 등록
def admin_user_create(request: Request, adminInput: AdminInput):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    user_data = admin_user_read(request, 0, adminInput.user_id)
    request.state.inspect = frame()

    if user_data is not None:
        return ex.ReturnOK(300, "이미 등록된 아이디 입니다.", request)

    db_item = T_ADMIN(
         user_id = adminInput.user_id
        ,user_name = adminInput.user_name
        ,tel = adminInput.tel
        ,mobile = adminInput.mobile
        ,email = adminInput.email
        ,role = adminInput.role
        ,position1 = adminInput.position1
        ,position2 = adminInput.position2
        ,depart = adminInput.depart
        ,roles = adminInput.roles
    )
    db.add(db_item)
    db.flush()
    
    log_service.create_log(request, db_item.uid, "T_ADMIN", "INSERT", "관리자 등록", 0, db_item.uid, user.user_id)
    request.state.inspect = frame()

    return db_item

# 고객사 관리자 편집 - 수정
def admin_user_edit(request: Request, adminInput: AdminInput):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    # 기존 등록된 관리자 select
    res = db.query(T_ADMIN).filter(T_ADMIN.uid == adminInput.uid).first()

    if res is None:
        return ex.ReturnOK(404, "관리자를 찾을 수 없습니다. 다시 확인해주세요.", request)

    if adminInput.state is not None and res.state != adminInput.state:
        log_service.create_log(request, adminInput.uid, "T_ADMIN", "state", "상태 수정", res.state, adminInput.state, user.user_id)
        request.state.inspect = frame()
        res.state = adminInput.state

    if adminInput.name is not None and res.name != adminInput.name:
        log_service.create_log(request, adminInput.uid, "T_ADMIN", "user_name", "이름 수정", res.user_name, adminInput.user_name, user.user_id)
        request.state.inspect = frame()
        res.name = adminInput.name

    if adminInput.tel is not None and res.tel != adminInput.tel:
        log_service.create_log(request, adminInput.uid, "T_ADMIN", "tel", "전화번호 수정", res.tel, adminInput.tel, user.user_id)
        request.state.inspect = frame()
        res.tel = adminInput.tel

    if adminInput.mobile is not None and res.mobile != adminInput.mobile:
        log_service.create_log(request, adminInput.uid, "T_ADMIN", "mobile", "휴대전화번호 수정", res.mobile, adminInput.mobile, user.user_id)
        request.state.inspect = frame()
        res.mobile = adminInput.mobile

    if adminInput.email is not None and res.email != adminInput.email:
        log_service.create_log(request, adminInput.uid, "T_ADMIN", "email", "이메일 수정", res.email, adminInput.email, user.user_id)
        request.state.inspect = frame()
        res.email = adminInput.email

    if adminInput.position1 is not None and res.position1 != adminInput.position1:
        log_service.create_log(request, adminInput.uid, "T_ADMIN", "position1", "직급 수정", res.position1, adminInput.position1, user.user_id)
        request.state.inspect = frame()
        res.position1 = adminInput.position1

    if adminInput.position2 is not None and res.position2 != adminInput.position2:
        log_service.create_log(request, adminInput.uid, "T_ADMIN", "position2", "직책 수정", res.position2, adminInput.position2, user.user_id)
        request.state.inspect = frame()
        res.position2 = adminInput.position2

    if adminInput.depart is not None and res.depart != adminInput.depart:
        log_service.create_log(request, adminInput.uid, "T_ADMIN", "depart", "부서 수정", res.depart, adminInput.depart, user.user_id)
        request.state.inspect = frame()
        res.depart = adminInput.depart

    if adminInput.roles is not None and res.roles != adminInput.roles:
        log_service.create_log(request, adminInput.uid, "T_ADMIN", "roles", "역할 수정", res.roles, adminInput.roles, user.user_id)
        request.state.inspect = frame()
        res.roles = adminInput.roles

    res.update_at = util.getNow()
    return res





