import os
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

from app.core import exceptions as ex
from app.core import util
from app.core.database import format_sql
from app.deps import auth
from app.models.session import *
from app.models.manager import *
from app.models.menu import *
from app.models.partner import *
from app.schemas.manager.auth import *
from app.service.log_service import *
from app.service.session_service import *

# 어드민 id & pw로 로그인
def signin_manager(request: Request, signin_request :SignInRequest):
    request.state.inspect = frame()
    db = request.state.db 

    sql = (
        db.query(
             T_MANAGER.uid
            ,T_MANAGER.partner_uid
            ,T_MANAGER.partner_id
            ,T_MANAGER.user_id
            ,T_MANAGER.name
            ,T_MANAGER.depart
            ,T_MANAGER.role
            ,T_MANAGER.roles
            ,T_MANAGER.login_id
            ,T_MANAGER.login_pw
            ,T_MANAGER.mobile
            ,T_PARTNER.prefix
        )
        .join(
            T_PARTNER,
            T_PARTNER.uid == T_MANAGER.partner_uid
        )
        .filter(
            T_MANAGER.login_id == signin_request.user_id
            ,T_MANAGER.delete_at == None
            ,T_PARTNER.delete_at == None
            ,T_PARTNER.state == '200'
            ,T_PARTNER.partner_id == signin_request.partner_id
        )
    )
    user = sql.first()

    format_sql(sql)

    if not user:
        return None
    
    cbfp = check_block_fail_password(request, "T_MANAGER", user.uid)
    request.state.inspect = frame()
    if cbfp is not None and cbfp.fail_count >= 5 :
        if cbfp.ten_min >= 0 : # 10분 아직 안지남
            return ex.ReturnOK(300, "비밀번호를 5회연속 틀렸습니다.\n10분간 사용이 제한됩니다.", request)
        else : # 10분 지남
            reset_block_fail_password(request, "T_MANAGER", user.uid)
            request.state.inspect = frame()
    
    if not auth.verify_password(signin_request.user_pw, user.login_pw):
        fail_count = create_fail_password(request, "T_MANAGER", user.uid, signin_request.user_pw)
        request.state.inspect = frame()
        
        session_param = T_SESSION_HISTORY(
             site_id = 'DREAM-MANAGER'
            ,user_uid = user.uid
            ,user_id = user.user_id
            ,partner_uid = user.partner_uid
            ,partner_id = user.partner_id
            ,ip = request.state.user_ip
            ,profile = os.environ.get('PROFILE')
        )

        fail_session_history(request, session_param)
        request.state.inspect = frame()

        # log insert를 해야되서 200 code 리턴.
        return ex.ReturnOK(200, "비밀번호가 일치하지 않습니다. ("+str(fail_count)+"/5)\n5회 연속 다른 경우, 서비스 사용이 제한됩니다.", request)
    else :
        reset_block_fail_password(request, "T_MANAGER", user.uid)
        request.state.inspect = frame()
    
    return user

# 파트너 정보 select
def get_partner_read(request: Request):
    request.state.insfect = frame()
    db = request.state.db
    user = request.state.user

    sql = (
        db.query(
             T_PARTNER.partner_type
            ,T_PARTNER.partner_id
            ,T_PARTNER.mall_name
            ,T_PARTNER.company_name
            ,T_PARTNER.sponsor
            ,T_PARTNER.partner_code
            ,T_PARTNER.prefix
            ,T_PARTNER.logo
            ,T_PARTNER.is_welfare
            ,T_PARTNER.is_dream
            ,T_PARTNER.state
        )
        .filter(T_PARTNER.uid == user.partner_uid)
    )

    format_sql(sql)
    res = sql.first()
    if res is not None:
        res = dict(zip(res.keys(), res))
    return res

# 유저 정보 by user_id
def read_by_userid(request: Request, user_id:str):
    request.state.inspect = frame()
    db = request.state.db 
    sql = db.query(T_MANAGER).filter(T_MANAGER.user_id == user_id)
    format_sql(sql)
    return sql.first()

# 고객사 정보 by partner_id
def read_by_partnerid(request: Request, partner_id:str):
    request.state.inspect = frame()
    db = request.state.db 
    sql = db.query(
        T_PARTNER
    ).filter(
        T_PARTNER.partner_id == partner_id
        ,T_PARTNER.state == "200"
        ,T_PARTNER.delete_at == None
    )
    format_sql(sql)
    return sql.first()









# 임시로 비밀번호 발급, 강제로 비번 설정
# def temp_update(request: Request, signin_request:SignInRequest):
#     request.state.inspect = frame()
#     db = request.state.db 
#     res = db.query(T_MEMBER_ADMIN).filter(T_MEMBER_ADMIN.user_id == signin_request.user_id).first()
#     res.user_pw = auth.get_password_hash(signin_request.user_pw)

# 유저 정보 get
# def read(request: Request, site_id:str, user_idx: str, user_id: str):
#     request.state.inspect = frame()
#     db = request.state.db 
#     sql = (
#         db.query(T_MEMBER)
#         .filter(
#              T_MEMBER.user_id == user_id
#             ,T_MEMBER.user_idx == user_idx
#             ,T_MEMBER.site_id == site_id
#         )
#     )
#     format_sql(sql)
#     return sql.first()


