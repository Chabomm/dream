from fastapi import Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from dateutil.relativedelta import relativedelta
from inspect import currentframe as frame
from sqlalchemy.dialects import mysql as mysql_dialetct
from pymysql.converters import conversions, escape_item, encoders
from sqlalchemy import func, select, update, delete, Table, MetaData, and_, or_
import math

from app.core import exceptions as ex
from app.core import util
from app.core.database import format_sql
from app.deps import auth
from app.models.manager import *
from app.schemas.admin.entry.manager import *
from app.service.log_service import *

# 고객사관리자_내역
def manager_list(request: Request, page_param: PPage_param):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    where = ""
    where = where + "WHERE M.delete_at is NULL "

    # [ S ] search filter start
    if not util.isEmptyObject(page_param.filters, "role") :
            where = where + "AND M.role = '"+ str(page_param.filters["role"]) +"' "

    if page_param.filters["create_at"]["startDate"] and page_param.filters["create_at"]["endDate"] :
        where = where + "AND M.create_at >= '" +page_param.filters["create_at"]["startDate"]+ "' " 
        where = where + "AND M.create_at <= '" +page_param.filters["create_at"]["endDate"]+ "' " 

    if not util.isEmptyObject(page_param.filters, "skeyword") :
        if not util.isEmptyObject(page_param.filters, "skeyword_type") :
            if page_param.filters["skeyword_type"] == "P.company_name" or page_param.filters["skeyword_type"] == "P.mall_name" :
                where = where + "AND M.partner_uid in ("
                where = where + "    select uid from T_PARTNER as P "
                where = where + "    where P.company_name like '%"+page_param.filters["skeyword"]+"%' "
                where = where + "    or P.mall_name like '%"+page_param.filters["skeyword"]+"%' "
                where = where + ") "
            else : 
                where = where + "AND "+page_param.filters["skeyword_type"]+" like '%"+page_param.filters["skeyword"]+"%' "
        else : 
            where = where + "AND ("
            where = where + "   M.partner_id like '%"+page_param.filters["skeyword"]+"%'"
            where = where + "   or M.user_id like '%"+page_param.filters["skeyword"]+"%'"
            where = where + "   or M.name like '%"+page_param.filters["skeyword"]+"%'"
            where = where + "   or M.mobile like '%"+page_param.filters["skeyword"]+"%'"
            where = where + "   or M.email like '%"+page_param.filters["skeyword"]+"%'"
            where = where + ") "
            where = where + "AND M.partner_uid in ("
            where = where + "    select uid from T_PARTNER as P "
            where = where + "    where P.company_name like '%"+page_param.filters["skeyword"]+"%' "
            where = where + "    or P.mall_name like '%"+page_param.filters["skeyword"]+"%' "
            where = where + ") "
    # [ E ] search filter end
    
    sql = """
        SELECT 
             M.uid
            ,M.user_id
            ,M.login_id
            ,M.partner_uid
            ,M.partner_id
            ,M.name
            ,M.tel
            ,M.mobile
            ,M.email
            ,M.role
            ,M.roles
            ,M.state
            ,( 
                select GROUP_CONCAT(name SEPARATOR ', ') AS result  
                From T_ADMIN_ROLE 
                where uid MEMBER OF(M.roles->>'$')
            ) as roles_txt
            ,P.company_name
            ,P.mall_name
            ,date_format(M.create_at, '%Y.%m.%d') as create_at
        FROM T_MANAGER as M
        join T_PARTNER as P on M.partner_uid = P.uid
        {where}
        ORDER BY uid DESC
        LIMIT {start}, {end}
    """.format(where=where, start=(page_param.page-1)*page_param.page_view_size, end=page_param.page_view_size)

    res = db.execute(text(sql)).fetchall()

    rows = []
    for c in res :
        rows.append(dict(zip(c.keys(), c)))

    page_param.page_total = db.execute(text("select count(M.uid) as cnt FROM T_MANAGER as M join T_PARTNER as P on M.partner_uid = P.uid " + where)).scalar()
    page_param.page_last = math.ceil(page_param.page_total / page_param.page_view_size)
    page_param.page_size = len(rows) 

    jsondata = {}
    jsondata.update({"params" : page_param})
    jsondata.update({"list": rows})

    return jsondata




# T_PARTNER의 관리자 - 리스트
def manager_list_in_partner_read(request: Request, partner_uid: int):
    request.state.inspect = frame()
    db = request.state.db

    sql = f"""
        SELECT 
             uid
            ,login_id
            ,partner_uid
            ,partner_id
            ,name
            ,tel
            ,mobile
            ,email
            ,role
            ,roles
            ,state
            ,( 
                select GROUP_CONCAT(name SEPARATOR ', ') AS result  
                From T_ADMIN_ROLE 
                where uid MEMBER OF(roles->>'$')
            ) as roles_txt
        FROM T_MANAGER
        WHERE delete_at is NULL
        AND partner_uid = {partner_uid}
        ORDER BY uid DESC
    """
    
    res = db.execute(text(sql)).fetchall()

    rows = []
    for c in res :
        rows.append(dict(zip(c.keys(), c))) 

    jsondata = {}
    jsondata.update({"list": rows})

    return jsondata

    # sql = (
    #     db.query(
    #          T_MANAGER.uid
    #         ,T_MANAGER.partner_uid
    #         ,T_MANAGER.partner_id
    #         ,T_MANAGER.name
    #         ,T_MANAGER.tel
    #         ,T_MANAGER.mobile
    #         ,T_MANAGER.email
    #         ,T_MANAGER.role
    #         ,T_MANAGER.roles
    #         ,T_MANAGER.state
    #         ,func.date_format(T_MANAGER.create_at, '%Y-%m-%d %T').label('create_at')
    #     )
    #     .filter(
    #         T_MANAGER.partner_uid == partner_uid, T_MANAGER.delete_at == None
    #     )
    #     .order_by(T_MANAGER.uid.desc())
    # )

    # format_sql(sql)

    # rows = []
    # for c in sql.all():
    #     rows.append(dict(zip(c.keys(), c)))

    # jsondata = {}
    # jsondata.update({"list": rows})

    # return jsondata

# T_PARTNER의 관리자 - 상세
def manager_read(request: Request, uid: int = 0, login_id: str = ""):
    request.state.inspect = frame()
    db = request.state.db

    filters = []
    filters.append(getattr(T_MANAGER, "delete_at") == None)

    if uid > 0:
        filters.append(getattr(T_MANAGER, "uid") == uid)
    elif login_id != "":
        filters.append(getattr(T_MANAGER, "login_id") == login_id)
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

# T_PARTNER의 관리자 편집 - 등록
def manager_create(request: Request, managerInput: ManagerInput):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    # [ S ] 아이디 중복검사 
    user_data = db.query(
            T_MANAGER
        ).filter(
            T_MANAGER.partner_uid == managerInput.partner_uid
            ,T_MANAGER.login_id == managerInput.login_id
            ,T_MANAGER.delete_at == None
        ).first()

    if user_data is not None:
        return ex.ReturnOK(300, "해당 로그인 아이디는 중복된 아이디로 등록할 수 없습니다.", request)
    # [ E ] 아이디 중복검사 
    
    # [ S ] 기존 마스터 권한 null 처리 
    if managerInput.role == "master" :
        user_data = db.query(
            T_MANAGER
        ).filter(
            T_MANAGER.partner_uid == managerInput.partner_uid
            ,T_MANAGER.role == managerInput.role
            ,T_MANAGER.delete_at == None
        ).first()

        if user_data != None :
            user_data.role = None
    # [ E ] 기존 마스터 권한 null 처리 

    db_item = T_MANAGER(
         partner_uid = managerInput.partner_uid
        ,partner_id = managerInput.partner_id
        ,prefix = managerInput.prefix
        ,login_id = managerInput.login_id
        ,login_pw = auth.get_password_hash(managerInput.login_id)
        ,user_id = managerInput.prefix+managerInput.login_id
        ,name = managerInput.name
        ,tel = managerInput.tel
        ,mobile = managerInput.mobile
        ,email = managerInput.login_id
        ,role = managerInput.role
        ,position1 = managerInput.position1
        ,position2 = managerInput.position2
        ,depart = managerInput.depart
        ,roles = managerInput.roles
    )
    db.add(db_item)
    db.flush()
    
    create_log(request, db_item.uid, "T_MANAGER", "INSERT", "고객사 관리자 등록", 0, db_item.uid, user.user_id)
    request.state.inspect = frame()

    return db_item

# T_PARTNER의 관리자 - 수정
def manager_update(request: Request, managerInput: ManagerInput):
    request.state.inspect = frame()
    db = request.state.db 
    user = request.state.user

    res_manager = (db.query(T_MANAGER).filter(T_MANAGER.uid == managerInput.uid).first())

    if res_manager is None :
        raise ex.NotFoundUser
    
    if managerInput.mode == 'DEL' : 
        create_log(request, res_manager.uid, "T_MANAGER", "delete_at", "고객사 담당자 삭제", res_manager.delete_at, util.getNow(), user.user_id)
        request.state.inspect = frame()
        res_manager.delete_at = util.getNow()

    else :

        if managerInput.name is not None and res_manager.name != managerInput.name : 
            create_log(request, res_manager.uid, "T_MANAGER", "name", "담당자명 수정", res_manager.name, managerInput.name, user.user_id)
            request.state.inspect = frame()
            res_manager.name = managerInput.name

        if managerInput.tel is not None and res_manager.tel != managerInput.tel : 
            create_log(request, res_manager.uid, "T_MANAGER", "tel", "담당자 일반전화 수정", res_manager.tel, managerInput.tel, user.user_id)
            request.state.inspect = frame()
            res_manager.tel = managerInput.tel

        if managerInput.mobile is not None and res_manager.mobile != managerInput.mobile : 
            create_log(request, res_manager.uid, "T_MANAGER", "mobile", "담당자 휴대전화 수정", res_manager.mobile, managerInput.mobile, user.user_id)
            request.state.inspect = frame()
            res_manager.mobile = managerInput.mobile

        if managerInput.email is not None and res_manager.email != managerInput.email : 
            create_log(request, res_manager.uid, "T_MANAGER", "email", "담당자 이메일 수정", res_manager.email, managerInput.email, user.user_id)
            request.state.inspect = frame()
            res_manager.email = managerInput.email

        if managerInput.position1 is not None and res_manager.position1 != managerInput.position1 : 
            create_log(request, res_manager.uid, "T_MANAGER", "position1", "담당자 직급 수정", res_manager.position1, managerInput.position1, user.user_id)
            request.state.inspect = frame()
            res_manager.position1 = managerInput.position1

        if managerInput.position2 is not None and res_manager.position2 != managerInput.position2 : 
            create_log(request, res_manager.uid, "T_MANAGER", "position2", "담당자 직책 수정", res_manager.position2, managerInput.position2, user.user_id)
            request.state.inspect = frame()
            res_manager.position2 = managerInput.position2

        if managerInput.depart is not None and res_manager.depart != managerInput.depart : 
            create_log(request, res_manager.uid, "T_MANAGER", "depart", "담당자 부서 수정", res_manager.depart, managerInput.depart, user.user_id)
            request.state.inspect = frame()
            res_manager.depart = managerInput.depart

        if managerInput.roles is not None and res_manager.roles != managerInput.roles : 
            create_log(request, res_manager.uid, "T_MANAGER", "roles", "담당자 역할 수정", res_manager.roles, managerInput.roles, user.user_id)
            request.state.inspect = frame()
            res_manager.roles = managerInput.roles

        if managerInput.role is not None and res_manager.role != managerInput.role : 
            # [ S ] 기존 마스터 권한 null 처리 
            if managerInput.role == "master" :
                user_data = db.query(
                    T_MANAGER
                ).filter(
                    T_MANAGER.partner_uid == managerInput.partner_uid
                    ,T_MANAGER.role == managerInput.role
                    ,T_MANAGER.delete_at == None
                ).first()

                if user_data != None :
                    user_data.role = None
            # [ E ] 기존 마스터 권한 null 처리 
                      
            elif managerInput.role == "" or managerInput.role == None :
                managerInput.role = None

            create_log(request, res_manager.uid, "T_MANAGER", "role", "담당자 마스터권한 수정", res_manager.role, managerInput.role, user.user_id)
            request.state.inspect = frame()
            res_manager.role = managerInput.role

    res_manager.update_at = util.getNow()

    return res_manager

# T_PARTNER 담당자 비밀번호 초기화  
def partner_manager_pw_update(request: Request, uid : int):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    res = db.query(T_MANAGER).filter(T_MANAGER.uid == uid).first()

    if res is None :
        return ex.ReturnOK(404, "죄송합니다. 오류가 발생 하였습니다. 문제 지속시 개발자에게 접수 바랍니다.", request)
    
    if res.login_pw != res.login_id:
        create_log(request, res.uid, "T_MANAGER", "login_pw", "담당자 비밀번호 초기화", "", "", user.user_id)
        request.state.inspect = frame()
        res.login_pw = auth.get_password_hash(res.login_id)
        res.update_at = util.getNow()

    return res
