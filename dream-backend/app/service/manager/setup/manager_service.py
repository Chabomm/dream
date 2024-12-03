from fastapi import Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Optional
from inspect import currentframe as frame
from sqlalchemy.dialects import mysql as mysql_dialetct
from pymysql.converters import conversions, escape_item, encoders
from sqlalchemy import func, select, update, delete, Table, MetaData
import math
import re

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

# 고객사 관리자 list 
def admin_user_list(request: Request, page_param: PPage_param):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    where = ""
    where = where + "WHERE delete_at is NULL "
    where = where + "AND partner_uid = " + str(user.partner_uid) + " "

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
            where = where + "   login_id like '%"+page_param.filters["skeyword"]+"%'"
            where = where + "   or name like '%"+page_param.filters["skeyword"]+"%'"
            where = where + "   or depart like '%"+page_param.filters["skeyword"]+"%'"
            where = where + ") "
    # [ E ] search filter end
    
    sql = """
        SELECT 
             uid
            ,login_id
            ,name
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
        FROM T_MANAGER
        {where}
        ORDER BY uid DESC
        LIMIT {start}, {end}
    """.format(where=where, start=(page_param.page-1)*page_param.page_view_size, end=page_param.page_view_size)

    res = db.execute(text(sql)).fetchall()

    rows = []
    for c in res :
        rows.append(dict(zip(c.keys(), c)))

    page_param.page_total = db.execute(text("select count(uid) as cnt from T_MANAGER " + where)).scalar()

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
    filters.append(getattr(T_MANAGER, "delete_at") == None)

    if uid > 0:
        filters.append(getattr(T_MANAGER, "uid") == uid)
    elif user_id != "":
        filters.append(getattr(T_MANAGER, "user_id") == user_id)
    else:
        return None
    
    sql = (
        db.query(
             T_MANAGER.uid
            ,T_MANAGER.partner_uid
            ,T_MANAGER.partner_id
            ,T_MANAGER.prefix
            ,T_MANAGER.login_id
            ,T_MANAGER.login_pw
            ,T_MANAGER.user_id
            ,T_MANAGER.name
            ,T_MANAGER.tel
            ,T_MANAGER.mobile
            ,T_MANAGER.email
            ,T_MANAGER.role
            ,T_MANAGER.position1
            ,T_MANAGER.position2
            ,T_MANAGER.depart
            ,T_MANAGER.roles
            ,T_MANAGER.state
            ,func.date_format(T_MANAGER.create_at, '%Y-%m-%d %T').label('create_at')
        )
        .filter(*filters)
    )
    # format_sql(sql)
    res = sql.first()
    if res is not None:
        res = dict(zip(res.keys(), res))
    return res

# 고객사 관리자 편집 - 등록
def admin_user_create(request: Request, managerInput: ManagerInput):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    managerInput.user_id = user.prefix + managerInput.login_id

    user_data = admin_user_read(request, 0, managerInput.user_id)
    request.state.inspect = frame()

    if user_data is not None:
        return ex.ReturnOK(300, "이미 등록된 아이디 입니다.", request)
    
    arry_mobile = managerInput.mobile.split('-')
    reset_pw = managerInput.login_id + arry_mobile[2]
    

    db_item = T_MANAGER(
         partner_uid = user.partner_uid
        ,partner_id = user.partner_id
        ,prefix = user.prefix
        ,login_id = managerInput.login_id
        ,login_pw = auth.get_password_hash(reset_pw)
        ,user_id = managerInput.user_id
        ,name = managerInput.name
        ,tel = managerInput.tel
        ,mobile = managerInput.mobile
        ,email = managerInput.email
        ,role = managerInput.role
        ,position1 = managerInput.position1
        ,position2 = managerInput.position2
        ,depart = managerInput.depart
        ,roles = managerInput.roles
    )
    db.add(db_item)
    db.flush()
    
    log_service.create_log(request, db_item.uid, "T_MANAGER", "INSERT", "관리자 등록", 0, db_item.uid, user.user_id)
    request.state.inspect = frame()

    return db_item

# 고객사 관리자 편집 - 수정
def admin_user_edit(request: Request, managerInput: ManagerInput):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    # 기존 등록된 관리자 select
    res = db.query(T_MANAGER).filter(T_MANAGER.uid == managerInput.uid).first()

    if res is None:
        return ex.ReturnOK(404, "관리자를 찾을 수 없습니다. 다시 확인해주세요.", request)

    if managerInput.login_pw is not None and managerInput.login_pw != "":
        if (len(managerInput.login_pw) < 6 or len(managerInput.login_pw) > 20) or (not re.findall('[0-9]+', managerInput.login_pw)) or (not re.findall('[a-z]', managerInput.login_pw)) :
            return ex.ReturnOK(300, "비밀번호는 영문, 숫자 조합 6자 이상, 20자 이하여야 합니다.", request)
        else :
            log_service.create_log(request, managerInput.uid, "T_MANAGER", "login_pw", "비밀번호 수정",
                        res.login_pw, managerInput.login_pw, user.user_id)
            request.state.inspect = frame()
            res.login_pw = auth.get_password_hash(managerInput.login_pw)

    if managerInput.state is not None and res.state != managerInput.state:
        log_service.create_log(request, managerInput.uid, "T_MANAGER", "state", "상태 수정", res.state, managerInput.state, user.user_id)
        request.state.inspect = frame()
        res.state = managerInput.state

    if managerInput.name is not None and res.name != managerInput.name:
        log_service.create_log(request, managerInput.uid, "T_MANAGER", "name", "이름 수정", res.name, managerInput.name, user.user_id)
        request.state.inspect = frame()
        res.name = managerInput.name

    if managerInput.tel is not None and res.tel != managerInput.tel:
        log_service.create_log(request, managerInput.uid, "T_MANAGER", "tel", "전화번호 수정", res.tel, managerInput.tel, user.user_id)
        request.state.inspect = frame()
        res.tel = managerInput.tel

    if managerInput.mobile is not None and res.mobile != managerInput.mobile:
        log_service.create_log(request, managerInput.uid, "T_MANAGER", "mobile", "휴대전화번호 수정", res.mobile, managerInput.mobile, user.user_id)
        request.state.inspect = frame()
        res.mobile = managerInput.mobile

    if managerInput.email is not None and res.email != managerInput.email:
        log_service.create_log(request, managerInput.uid, "T_MANAGER", "email", "이메일 수정", res.email, managerInput.email, user.user_id)
        request.state.inspect = frame()
        res.email = managerInput.email

    if managerInput.position1 is not None and res.position1 != managerInput.position1:
        log_service.create_log(request, managerInput.uid, "T_MANAGER", "position1", "직급 수정", res.position1, managerInput.position1, user.user_id)
        request.state.inspect = frame()
        res.position1 = managerInput.position1

    if managerInput.position2 is not None and res.position2 != managerInput.position2:
        log_service.create_log(request, managerInput.uid, "T_MANAGER", "position2", "직책 수정", res.position2, managerInput.position2, user.user_id)
        request.state.inspect = frame()
        res.position2 = managerInput.position2

    if managerInput.depart is not None and res.depart != managerInput.depart:
        log_service.create_log(request, managerInput.uid, "T_MANAGER", "depart", "부서 수정", res.depart, managerInput.depart, user.user_id)
        request.state.inspect = frame()
        res.depart = managerInput.depart

    if managerInput.roles is not None and res.roles != managerInput.roles:
        log_service.create_log(request, managerInput.uid, "T_MANAGER", "roles", "역할 수정", res.roles, managerInput.roles, user.user_id)
        request.state.inspect = frame()
        res.roles = managerInput.roles

    res.update_at = util.getNow()
    return res


# 고객사 관리자 편집 - 비밀번호 초기화
def admin_user_reset_pw(request: Request, uid: int):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    # 기존 등록된 관리자 select
    res = db.query(T_MANAGER).filter(T_MANAGER.uid == uid, T_MANAGER.partner_uid == user.partner_uid).first()

    if res is None:
        return ex.ReturnOK(404, "관리자를 찾을 수 없습니다. 다시 확인해주세요.", request)
    
    arry_mobile = res.mobile.split('-')
    reset_pw = res.login_id + arry_mobile[2]
    
    if reset_pw is not None and reset_pw != "":
        log_service.create_log(request, res.uid, "T_MANAGER", "login_pw", "비밀번호 초기화",
                    res.login_pw, reset_pw, user.user_id)
        request.state.inspect = frame()
        res.login_pw = auth.get_password_hash(reset_pw)

    res.update_at = util.getNow()
    return res





