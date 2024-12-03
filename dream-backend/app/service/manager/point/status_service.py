import json
from fastapi import Request
from inspect import currentframe as frame
from app.core.database import format_sql
from sqlalchemy import func, select, update, delete, Table, MetaData, and_
from app.core import util
import math

from app.schemas.schema import *
from app.schemas.manager.point.assign.balance import *
from app.models.point.balance import *
from app.models.point.point import *
from app.models.point.sikwon import *
from app.service.log_service import *

# -- 총 충전 예치금 
# select sum(save_point) From T_BALANCE where partner_uid = 115 and input_state = '입금완료'

# -- 지급완료 복지포인트
# select sum(saved_point) From T_POINT where partner_uid = 115 and saved_type in ('1', '2') 

# -- 잔여 예치금 
# select sum(point) From T_BALANCE where partner_uid = 115 and input_state = '입금완료'

# -- 사용완료 복지포인트
# select sum(used_point) - sum(remaining_point)  from dream.T_POINT_USED where partner_uid = 115 

# -- 미사용 복지포인트 
# select sum(point) From T_POINT where partner_uid = 115 and saved_type in ('1', '2')

# 복지포인트 충전 현황
def status_point_read(request: Request, partner_uid: int):
    request.state.inspect = frame()
    db = request.state.db

    # [ S ] 총 충전 예치금, 잔여 예치금
    sql_balance = ( 
        db.query(
             T_BALANCE.partner_uid
            ,func.sum(func.ifnull(T_BALANCE.save_point, 0)).label('total_charge_balance') # 총 충전 예치금
            ,func.sum(func.ifnull(T_BALANCE.point, 0)).label('avail_charge_balance') # 잔여 예치금
        )
        .filter(
            T_BALANCE.partner_uid == partner_uid
            ,T_BALANCE.input_state == "입금완료"
            ,T_BALANCE.delete_at == None
        )
        .group_by(T_BALANCE.partner_uid)
    )
    format_sql(sql_balance)
    res_balance = sql_balance.first()
    # [ E ] 총 충전 예치금, 잔여 예치금


    # [ S ] 지급 완료 포인트, 미사용 포인트
    sql_point = ( 
        db.query(
             T_POINT.partner_uid
            ,func.sum(func.ifnull(T_POINT.saved_point, 0)).label('saved_welfare_point') # 지급 완료 포인트
            ,func.sum(func.ifnull(T_POINT.point, 0)).label('avail_welfare_point') # 미사용 포인트
        )
        .filter(
            T_POINT.partner_uid == partner_uid
            ,T_POINT.delete_at == None
        )
        .group_by(T_POINT.partner_uid)
    )
    # format_sql(sql_point)
    res_point = sql_point.first()
    # [ E ] 지급 완료 포인트, 사용 예치금 , 미사용 포인트

    # [ S ] 사용완료 포인트
    sql_point_used = (
        db.query(
            T_POINT_USED.partner_uid
            ,(func.sum(func.ifnull(T_POINT_USED.used_point, 0)) - func.sum(func.ifnull(T_POINT_USED.remaining_point, 0))).label('used_welfare_point') # 사용완료 포인트
        )
        .filter(
            T_POINT_USED.partner_uid == partner_uid
            ,T_POINT_USED.delete_at == None
        )
        .group_by(T_POINT_USED.partner_uid)
    )
    format_sql(sql_point_used)
    res_point_used = sql_point_used.first()
    # [ E ] 사용완료 포인트

    # [ S ] 회수 포인트
    sql_point_collect = (
        db.query(
            T_POINT.partner_uid
            ,func.sum(func.ifnull(T_POINT.saved_point, 0)).label('return_point')
        )
        .filter(
            T_POINT.partner_uid == partner_uid
            ,T_POINT.saved_type == "3"
            ,T_POINT.delete_at == None
        )
        .group_by(T_POINT.partner_uid)
    )
    format_sql(sql_point_collect)
    res_point_collect = sql_point_collect.first()
    # [ E ] 회수 포인트

    # [ S ] 만료 포인트
    sql_point_exp = ( 
        db.query(
             T_POINT_EXP.partner_uid
            ,func.sum(func.ifnull(T_POINT_EXP.exp_point, 0)).label('exp_welfare_point') # 미사용 포인트
        )
        .filter(
            T_POINT_EXP.partner_uid == partner_uid
            ,T_POINT_EXP.exp_type == '1'
            ,T_POINT_EXP.delete_at == None
        )
        .group_by(T_POINT_EXP.partner_uid)
    )
    # format_sql(sql_point)
    res_point_exp = sql_point_exp.first()
    # [ E ] 만료 포인트

    # total_charge_balance 총 충전 예치금
    # avail_charge_balance 잔여 예치금
    # saved_welfare_point 지급 완료 포인트
    # avail_welfare_point 미사용 포인트
    # used_welfare_point 사용완료 포인트
    # used_charge_balance 사용 예치금

    if res_balance == None :
        res_balance = {
            "total_charge_balance" : 0,
            "avail_charge_balance" : 0
        }
    else :   
        res_balance = dict(zip(res_balance.keys(), res_balance))
        res_balance["total_charge_balance"] = int(res_balance["total_charge_balance"])
        res_balance["avail_charge_balance"] = int(res_balance["avail_charge_balance"])
        res_balance["used_charge_balance"] = int(res_balance["total_charge_balance"]) - int(res_balance["avail_charge_balance"])

    if res_point == None :
        res_point = {
            "saved_welfare_point" : 0,
            "avail_welfare_point" : 0
        }
    else :   
        res_point = dict(zip(res_point.keys(), res_point))
        res_point["saved_welfare_point"] = int(res_point["saved_welfare_point"])
        res_point["avail_welfare_point"] = int(res_point["avail_welfare_point"])

    if res_point_used == None :
        res_point_used = {
            "used_welfare_point" : 0,
        }
    else :   
        res_point_used = dict(zip(res_point_used.keys(), res_point_used))
        res_point_used["used_welfare_point"] = int(res_point_used["used_welfare_point"])

    if res_point_collect == None :
        res_point_collect = {
            "return_point" : 0,
        }
    else :   
        res_point_collect = dict(zip(res_point_collect.keys(), res_point_collect))
        res_point_collect["return_point"] = int(res_point_collect["return_point"])

    if res_point_exp == None :
        res_point_exp = {
            "exp_welfare_point" : 0,
        }
    else :   
        res_point_exp = dict(zip(res_point_exp.keys(), res_point_exp))
        res_point_exp["exp_welfare_point"] = int(res_point_exp["exp_welfare_point"])

    jsondata = {}
    jsondata.update(res_balance)
    jsondata.update(res_point)
    jsondata.update(res_point_used)
    jsondata.update(res_point_collect)
    jsondata.update(res_point_exp)

    return jsondata

# 식권포인트 충전 현황
def status_sikwon_read(request: Request, partner_uid: int):
    request.state.inspect = frame()
    db = request.state.db

    # [ S ] 총 충전 예치금, 잔여 예치금
    sql_balance = ( 
        db.query(
             T_BALANCE.partner_uid
            ,func.sum(func.ifnull(T_BALANCE.save_point, 0)).label('total_charge_balance') # 총 충전 예치금
            ,func.sum(func.ifnull(T_BALANCE.point, 0)).label('avail_charge_balance') # 잔여 예치금
        )
        .filter(
            T_BALANCE.partner_uid == partner_uid
            ,T_BALANCE.input_state == "입금완료"
            ,T_BALANCE.delete_at == None
        )
        .group_by(T_BALANCE.partner_uid)
    )
    # format_sql(sql_balance)
    res_balance = sql_balance.first()
    # [ E ] 총 충전 예치금, 잔여 예치금

    # [ S ] 지급 완료 포인트, 사용 예치금 , 미사용 포인트
    sql_point = ( 
        db.query(
             T_SIKWON.partner_uid
            ,func.sum(func.ifnull(T_SIKWON.saved_point, 0)).label('saved_welfare_point') # 지급 완료 포인트, 사용 예치금
            ,func.sum(func.ifnull(T_SIKWON.point, 0)).label('avail_welfare_point') # 미사용 포인트
        )
        .filter(
            T_SIKWON.partner_uid == partner_uid
            ,T_SIKWON.delete_at == None
        )
        .group_by(T_SIKWON.partner_uid)
    )
    # format_sql(sql_point)
    res_point = sql_point.first()
    # [ E ] 지급 완료 포인트, 사용 예치금 , 미사용 포인트

    # [ S ] 사용완료 포인트
    sql_point_used = (
        db.query(
            T_SIKWON_USED.partner_uid
            ,(func.sum(func.ifnull(T_SIKWON_USED.used_point, 0)) - func.sum(func.ifnull(T_SIKWON_USED.remaining_point, 0))).label('used_welfare_point') # 사용완료 포인트
        )
        .filter(
            T_SIKWON_USED.partner_uid == partner_uid
            ,T_SIKWON_USED.delete_at == None
        )
        .group_by(T_SIKWON_USED.partner_uid)
    )
    format_sql(sql_point_used)
    res_point_used = sql_point_used.first()
    # [ E ] 사용완료 포인트

    # [ S ] 회수 포인트
    sql_point_collect = (
        db.query(
            T_SIKWON.partner_uid
            ,func.sum(func.ifnull(T_SIKWON.saved_point, 0)).label('return_point')
        )
        .filter(
            T_SIKWON.partner_uid == partner_uid
            ,T_SIKWON.saved_type == "3"
            ,T_SIKWON.delete_at == None
        )
        .group_by(T_SIKWON.partner_uid)
    )
    format_sql(sql_point_collect)
    res_point_collect = sql_point_collect.first()
    # [ E ] 회수 포인트

    # total_charge_balance
    # avail_charge_balance
    # saved_welfare_point
    # avail_welfare_point
    # used_welfare_point

    if res_balance == None :
        res_balance = {
            "total_charge_balance" : 0,
            "avail_charge_balance" : 0
        }
    else :   
        res_balance = dict(zip(res_balance.keys(), res_balance))
        res_balance["total_charge_balance"] = int(res_balance["total_charge_balance"])
        res_balance["avail_charge_balance"] = int(res_balance["avail_charge_balance"])
        res_balance["used_charge_balance"] = int(res_balance["total_charge_balance"]) - int(res_balance["avail_charge_balance"])

    if res_point == None :
        res_point = {
            "saved_welfare_point" : 0,
            "avail_welfare_point" : 0
        }
    else :   
        res_point = dict(zip(res_point.keys(), res_point))
        res_point["saved_welfare_point"] = int(res_point["saved_welfare_point"])
        res_point["avail_welfare_point"] = int(res_point["avail_welfare_point"])

    if res_point_used == None :
        res_point_used = {
            "used_welfare_point" : 0,
        }
    else :   
        res_point_used = dict(zip(res_point_used.keys(), res_point_used))
        res_point_used["used_welfare_point"] = int(res_point_used["used_welfare_point"])

    if res_point_collect == None :
        res_point_collect = {
            "return_point" : 0,
        }
    else :   
        res_point_collect = dict(zip(res_point_collect.keys(), res_point_collect))
        res_point_collect["return_point"] = int(res_point_collect["return_point"])

    jsondata = {}
    jsondata.update(res_balance)
    jsondata.update(res_point)
    jsondata.update(res_point_used)
    jsondata.update(res_point_collect)

    return jsondata