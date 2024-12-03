from fastapi import Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Optional
from inspect import currentframe as frame
from sqlalchemy.dialects import mysql as mysql_dialetct
from pymysql.converters import conversions, escape_item, encoders
from sqlalchemy import func, select, update, delete, Table, MetaData, and_, case
import math

from app.core import exceptions as ex
from app.core import util
from app.core.database import format_sql
from app.deps import auth

from app.schemas.schema import *

from app.models.manager import *
from app.models.member import *
from app.models.partner import *
from app.models.point.balance import *
from app.models.point.point import *

def user_info(request: Request):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    sql = (
        db.query(
             T_MANAGER.uid
            ,T_MANAGER.name
            ,T_MANAGER.depart
            ,T_PARTNER_INFO.file_logo
            ,T_PARTNER_INFO.file_mall_logo
            ,T_PARTNER_INFO.company_name
            ,T_PARTNER_INFO.mall_name
        )
        .join(T_PARTNER_INFO, T_PARTNER_INFO.partner_uid == user.partner_uid, isouter = True)
        .filter(T_MANAGER.user_id == user.user_id)
        .filter(T_MANAGER.partner_uid == user.partner_uid)
    )

    format_sql(sql)
    return sql.first()

def member_info(request: Request):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    sql = (
        db.query(
             T_MEMBER_INFO.serve
            ,func.count(T_MEMBER_INFO.uid).label('member_count')
        )
        .filter(T_MEMBER_INFO.partner_uid == user.partner_uid)
        .group_by(T_MEMBER_INFO.serve)
    )

    format_sql(sql)

    rows = []
    all_cnt = 0
    mem_재직 = 0
    mem_퇴직 = 0
    mem_휴직 = 0
    for c in sql.all():
        list = dict(zip(c.keys(), c))
        if list["serve"] == '재직' :
            mem_재직 = list["member_count"]
        elif list["serve"] == '퇴직' :
            mem_퇴직 = list["member_count"]
        elif list["serve"] == '휴직' :
            mem_휴직 = list["member_count"]
              
        all_cnt = all_cnt + int(list["member_count"])
        rows.append(list)
        
    jsondata = {}
    jsondata.update({"mem_재직":mem_재직})
    jsondata.update({"mem_퇴직":mem_퇴직})
    jsondata.update({"mem_휴직":mem_휴직})
    jsondata.update({"all_cnt":all_cnt})

    return jsondata

def balance_info(request: Request):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    sql = (
        db.query(
             T_BALANCE.uid
            ,T_BALANCE.save_point
            ,func.date_format(T_BALANCE.create_at, '%Y-%m-%d').label('create_at')
        )
        .filter(T_BALANCE.partner_uid == user.partner_uid)
        .filter(T_BALANCE.input_state == '입금완료')
        .filter(T_BALANCE.delete_at == None)
        .order_by(T_BALANCE.uid.desc())
        .limit(4)
    )

    format_sql(sql)
    return sql.all()

def assign_info(request:Request):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    sql = (
        db.query(
             T_POINT.uid
            ,case(
                [
                    (T_POINT.saved_type == '1', "대량지급")
                    ,(T_POINT.saved_type == '2', "개별지급")
                    ,(T_POINT.saved_type == '3', "회수")
                ]
            ).label('saved_type')
            ,T_POINT.saved_point
            ,func.date_format(T_POINT.create_at, '%Y-%m-%d').label('create_at')
        )
        .order_by(T_POINT.uid.desc())
        .limit(4)
    )

    format_sql(sql)

    return sql.all()

def day_point_info(request:Request):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    sql = (
        db.query(
             func.date(T_POINT_USED.create_at).label('create_at')
            ,func.sum(func.ifnull(T_POINT_USED.used_point, 0)).label('used_point')
        )
        .group_by(func.date(T_POINT_USED.create_at))
        .limit(4)
    )

    format_sql(sql)

    return sql.all()

