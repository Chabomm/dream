
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Optional
from inspect import currentframe as frame
from sqlalchemy.dialects import mysql as mysql_dialetct
from pymysql.converters import conversions, escape_item, encoders
from sqlalchemy import func, select, update, delete, Table, MetaData
import math

from app.models.session import *
from app.models.manager import *
from app.models.menu import *
from app.models.partner import *
from app.schemas.schema import *
from app.core import util
from app.core.database import format_sql
from app.deps import auth
from app.schemas.manager.auth import *

# 세선 select
def read_session(request: Request, session_uid: Optional[int] = None, access_token: Optional[str] = None):
    request.state.inspect = frame()
    db = request.state.db 

    filters = []
    if session_uid is not None and session_uid > 0 :
        filters.append(getattr(T_SESSION, "uid") == session_uid)
    elif access_token is not None and access_token != "" :
        filters.append(getattr(T_SESSION, "access_token") == access_token)

    if len(filters) == 0 :
        return None

    sql = db.query(T_SESSION).filter(*filters)
    return sql.first()

# 세션 insert
def create_session(request: Request, session_param: T_SESSION, token_data={}):
    request.state.inspect = frame()
    db = request.state.db 

    delete_session(request, session_param.user_uid)
    request.state.inspect = frame()
    
    db_item = session_param 
    db.add(db_item)
    db.flush()

    db_item_history = T_SESSION_HISTORY (
         site_id = session_param.site_id
        ,user_uid = session_param.user_uid
        ,user_id = session_param.user_id
        ,partner_uid = token_data["partner_uid"] if "partner_uid" in token_data else 0
        ,partner_id = token_data["partner_id"] if "partner_id" in token_data else ""
        ,ip = session_param.ip
        ,create_date = session_param.create_date
        ,profile = session_param.profile
        ,is_fail = 0
    )
    db.add(db_item_history)
    db.flush()

    return db_item

# 세션 delete
def delete_session(request: Request, user_uid: int):
    request.state.inspect = frame()
    db = request.state.db 
    return db.query(T_SESSION).filter(T_SESSION.user_uid == user_uid).delete()

# 세션 fail_session_history
def fail_session_history(request: Request, session_param: T_SESSION_HISTORY):
    request.state.inspect = frame()
    db = request.state.db 

    db_item = T_SESSION_HISTORY (
         site_id = session_param.site_id
        ,user_uid = session_param.user_uid
        ,user_id = session_param.user_id
        ,partner_uid = session_param.partner_uid
        ,partner_id = session_param.partner_id
        ,ip = session_param.ip
        ,profile = session_param.profile
        ,is_fail = 1
    )
    db.add(db_item)
    db.flush()

    return db_item