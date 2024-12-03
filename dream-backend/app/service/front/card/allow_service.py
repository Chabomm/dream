from fastapi import Request
from inspect import currentframe as frame
from app.core.database import format_sql
from sqlalchemy import func, select, update, delete, Table, MetaData, and_, literal_column
from app.core import util
import math
import random
from app.core import exceptions as ex

from app.schemas.schema import *
from app.schemas.manager.point.offcard.used import *
from app.models.offcard.used import *
from app.models.limit.industry import *
from app.models.member import *
from app.service.log_service import *
from app.models.point.point import *
from app.models.point.sikwon import *

# 회원 정보
def get_user_info(request: Request, user_id: str):
    request.state.inspect = frame()
    db = request.state.db
    return db.query(T_MEMBER).filter(T_MEMBER.user_id == user_id).first()

# 허용업종 리스트 bokji
def allow_bokji_list(request: Request, user:T_MEMBER):
    request.state.inspect = frame()
    db = request.state.db

    filters = []
    filters.append(getattr(T_INDUSTRY_OFFCARD, "delete_at") == None)
    filters.append(getattr(T_INDUSTRY_CODE, "delete_at") == None)
    filters.append(getattr(T_INDUSTRY_OFFCARD, "partner_uid") == user.partner_uid)

    sql = (
        db.query(
             T_INDUSTRY_OFFCARD.code
            ,T_INDUSTRY_OFFCARD.std_class
            ,T_INDUSTRY_CODE.card_name
            ,T_INDUSTRY_CODE.group
            ,T_INDUSTRY_CODE.code
            ,T_INDUSTRY_CODE.name
        )
        .join(T_INDUSTRY_CODE, T_INDUSTRY_CODE.uid == T_INDUSTRY_OFFCARD.indus_uid)
        .filter(*filters)
        .order_by(T_INDUSTRY_OFFCARD.uid.desc())
    ).all()

    # format_sql(sql)

    if sql is None:
        return ex.ReturnOK(404, "허용업종 리스트를 찾을 수 없습니다. 다시 확인해주세요.", request)

    rows = []
    for c in sql:
        rows.append(dict(zip(c.keys(), c)))

    jsondata = {}
    jsondata.update({"list": rows})

    return jsondata 
    

# 허용업종 리스트 sikwon
def allow_sikwon_list(request: Request, user:T_MEMBER):
    request.state.inspect = frame()
    db = request.state.db

    filters = []
    filters.append(getattr(T_INDUSTRY_SIKWON, "delete_at") == None)
    filters.append(getattr(T_INDUSTRY_CODE, "delete_at") == None)
    filters.append(getattr(T_INDUSTRY_SIKWON, "partner_uid") == user.partner_uid)

    sql = (
        db.query(
             T_INDUSTRY_SIKWON.uid
            ,T_INDUSTRY_SIKWON.code
            ,T_INDUSTRY_SIKWON.std_class
            ,T_INDUSTRY_CODE.card_name
            ,T_INDUSTRY_CODE.group
            ,T_INDUSTRY_CODE.code
            ,T_INDUSTRY_CODE.name
        )
        .join(T_INDUSTRY_CODE, T_INDUSTRY_CODE.uid == T_INDUSTRY_SIKWON.indus_uid)
        .filter(*filters)
        .order_by(T_INDUSTRY_SIKWON.uid.desc())
    ).all()

    if sql is None:
        return ex.ReturnOK(404, "허용업종 리스트를 찾을 수 없습니다. 다시 확인해주세요.", request)
    
    rows = []
    for c in sql:
        rows.append(dict(zip(c.keys(), c)))

    jsondata = {}
    jsondata.update({"list": rows})

    return jsondata 
    
