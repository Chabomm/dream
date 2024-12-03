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


# 계정관리_상세정보
def info_read(request: Request):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    sql = (
        db.query(
             T_MANAGER.uid
            ,T_MANAGER.login_id
            ,T_MANAGER.user_id
            ,T_MANAGER.name
            ,T_MANAGER.tel
            ,T_MANAGER.mobile
            ,T_MANAGER.email
            ,T_MANAGER.role
            ,T_MANAGER.position1
            ,T_MANAGER.position2
            ,T_MANAGER.depart
        )
        .filter(T_MANAGER.user_id == user.user_id)
        .filter(T_MANAGER.partner_uid == user.partner_uid)
    )

    format_sql(sql)
    return sql.first()

# 내 정보 보기 - 수정
def info_update(request: Request, myInfoInput: MyInfoInput) :
    request.state.inspect = frame()
    db = request.state.db 
    user = request.state.user

    res = db.query(T_MANAGER).filter(T_MANAGER.user_id == user.user_id, T_MANAGER.partner_uid == user.partner_uid).first()

    if res is None :
        return ex.ReturnOK(404, "정보를 찾을 수 없습니다. 아이디와 비밀번호를 다시 확인해 주세요", request)
    
    if myInfoInput.tel is not None and res.tel != myInfoInput.tel : 
        log_service.create_log(request, res.uid, "T_MANAGER", "tel", "일반전화번호", res.tel, myInfoInput.tel, user.user_id)
        request.state.inspect = frame()
        res.tel = myInfoInput.tel

    if myInfoInput.mobile is not None and res.mobile != myInfoInput.mobile : 
        log_service.create_log(request, res.uid, "T_MANAGER", "mobile", "핸드폰번호", res.mobile, myInfoInput.mobile, user.user_id)
        request.state.inspect = frame()
        res.mobile = myInfoInput.mobile

    if myInfoInput.login_pw is not None and res.login_pw != auth.get_password_hash(myInfoInput.login_pw):
        log_service.create_log(request, res.uid, "T_ADMIN", "login_pw", "비밀번호 변경", res.login_pw, auth.get_password_hash(myInfoInput.login_pw), user.user_id)
        request.state.inspect = frame()
        res.login_pw = auth.get_password_hash(myInfoInput.login_pw)

    res.update_at = util.getNow()

    return res

# 고객사 구축 정보
def partner_build_read(request: Request):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    sql = ( 
        db.query(
             T_PARTNER.uid
            ,T_PARTNER.partner_type
            ,T_PARTNER.partner_id
            ,T_PARTNER.mall_name
            ,T_PARTNER.company_name
            ,T_PARTNER.partner_code
            ,func.date_format(T_PARTNER.create_at, '%Y-%m-%d %T').label('create_at')
            ,T_PARTNER_INFO.ceo_name
            ,T_PARTNER_INFO.staff_name
            ,T_PARTNER_INFO.staff_dept
            ,T_PARTNER_INFO.staff_position
            ,T_PARTNER_INFO.staff_position2
            ,T_PARTNER_INFO.staff_mobile
            ,T_PARTNER_INFO.staff_email
            ,T_PARTNER_INFO.post
            ,T_PARTNER_INFO.addr
            ,T_PARTNER_INFO.addr_detail
            ,T_PARTNER_INFO.company_hp
            ,T_PARTNER_INFO.biz_no
            ,T_PARTNER_INFO.host
        )
        .join(
            T_PARTNER_INFO,
            T_PARTNER.uid == T_PARTNER_INFO.partner_uid,
            isouter = True
        )
        .filter(
            T_PARTNER.uid == user.partner_uid
            ,T_PARTNER.delete_at == None
        )
    )
    format_sql(sql)

    res = sql.first()

    if res == None :
        return {}
    else :
        return dict(zip(res.keys(), res))
