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
from app.deps import auth
from app.models.session import *
from app.models.menu import *
from app.models.admin import *
from app.schemas.admin.auth import *

from app.models.manager import * # .admin 으로 변경해야됨

# 유저 정보 by user_id
def read_by_userid(request: Request, user_id:str):
    request.state.inspect = frame()
    db = request.state.db 
    sql = db.query(T_ADMIN).filter(T_ADMIN.user_id == user_id, T_ADMIN.state == "200")
    format_sql(sql)
    return sql.first()
