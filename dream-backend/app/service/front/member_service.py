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
from app.models.session import *
from app.models.member import *
from app.models.partner import *
from app.schemas.front.auth import *

# 회원정보 list select (NoAuth)
# def read(request: Request, login_id :str):
#     request.state.inspect = frame()
#     db = request.state.db 

#     filters = []
#     filters.append(T_MEMBER.login_id == login_id)
        
#     sql = (
#         db.query(
#              T_MEMBER.uid
#             ,T_MEMBER.partner_uid
#             ,T_MEMBER.partner_id
#             ,T_MEMBER.user_id
#             ,T_MEMBER.login_id
#             ,T_MEMBER.user_name
#             ,T_MEMBER.prefix
#         )
#         .filter(*filters)
#     )


#     rows = []
#     for c in sql.all():
#         list = dict(zip(c.keys(), c))

#         rows.append(list)
#     return rows

# 회원정보 list select (Auth)
def read(request: Request, login_id :str, mobile:str):
    request.state.inspect = frame()
    db = request.state.db 

    filters = []
    filters.append(T_MEMBER.login_id == login_id)
    filters.append(T_MEMBER.mobile == mobile)
        
    sql = (
        db.query(
             T_MEMBER.uid
            ,T_MEMBER.partner_uid
            ,T_MEMBER.partner_id
            ,T_MEMBER.user_id
            ,T_MEMBER.login_id
            ,T_MEMBER.user_name
            ,T_MEMBER.prefix
        )
        .filter(*filters)
    )


    rows = []
    for c in sql.all():
        list = dict(zip(c.keys(), c))

        rows.append(list)
    return rows

# 회원정보 select
def login_read(request: Request, authNumInput: AuthNumInput):
    request.state.inspect = frame()
    db = request.state.db 

    filters = []
    filters.append(T_MEMBER.login_id == authNumInput["login_id"])
    filters.append(T_MEMBER.partner_uid == authNumInput["partner_uid"])
    # filters.append(T_MEMBER.mobile == authNumInput["mobile"])
        
    sql = (
        db.query(
             T_MEMBER.uid
            ,T_MEMBER.partner_id
            ,T_MEMBER.partner_uid
            ,T_MEMBER.login_id
            ,T_MEMBER.user_id
            ,T_MEMBER.user_name
            ,T_MEMBER.prefix
        )
        .join(T_PARTNER, T_PARTNER.uid == T_MEMBER.partner_uid)
        .filter(*filters)
    ).first()

    return sql


# 회원select 앱사용자_인증번호_발송
def member_read(request: Request, authNum: AuthNum):
    request.state.inspect = frame()
    db = request.state.db 

    filters = []
    filters.append(T_MEMBER.login_id == authNum.login_id)
    
    if authNum.send_type == 'email' :
        filters.append(T_MEMBER.email == authNum.value)

    if authNum.send_type == 'mobile' :
        filters.append(T_MEMBER.mobile == authNum.value)
        
    sql = (
        db.query(
             T_MEMBER.uid
            ,T_MEMBER.partner_id
            ,T_MEMBER.partner_uid
            ,T_MEMBER.login_id
            ,T_MEMBER.user_id
            ,T_MEMBER.user_name
        )
        .filter(*filters)
    ).first()

    return sql
