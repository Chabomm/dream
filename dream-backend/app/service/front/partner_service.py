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
from app.models.partner import *
from app.schemas.front.auth import *

# 파트너 list
def list(request: Request, uid:int):
    request.state.inspect = frame()
    db = request.state.db 

    filters = []
    filters.append(T_PARTNER.uid.in_(uid))
        
    sql = (
        db.query(
             T_PARTNER.uid
            ,T_PARTNER.logo
            ,T_PARTNER.company_name
            ,T_PARTNER.mall_name
            ,T_PARTNER.partner_id
        )
        .filter(*filters)
    )

    rows = []
    for c in sql.all():
        list = dict(zip(c.keys(), c))
        rows.append(list)
        
    return rows



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