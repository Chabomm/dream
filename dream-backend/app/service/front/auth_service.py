from fastapi import Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Optional
from inspect import currentframe as frame
from sqlalchemy.dialects import mysql as mysql_dialetct
from pymysql.converters import conversions, escape_item, encoders
from sqlalchemy import func, select, update, delete, Table, MetaData
import math
import datetime

from app.core import util
from app.core.database import format_sql
from app.models.session import *
from app.models.member import *
from app.models.device import *
from app.schemas.schema import *
from app.schemas.front.auth import *
from app.service.log_service import *

# app 핸드폰번호, 이메일 인증번호 insert
def auth_num_create(request: Request, random_num:int,authNum :AuthNum):
    request.state.inspect = frame()
    db = request.state.db 

    current =  datetime.datetime.now()
    five_minutes_later = current + datetime.timedelta(minutes=5)

    db_item = T_AUTH_CONFIRM (
         send_type = authNum.send_type
        ,value = authNum.value
        ,auth_num = random_num
        ,try_count = 0
        ,expiry_at = five_minutes_later
    )
    db.add(db_item)
    db.flush()

    return db_item


# 인증번호 확인
def auth_num_vaild(request: Request, authNumInput: AuthNumInput):
    request.state.inspect = frame()
    db = request.state.db 

    res = (
        db.query(T_AUTH_CONFIRM)
        .filter(
             T_AUTH_CONFIRM.uid == authNumInput.uid
        )
    ).first()

    result = {} 
    result["code"] = 200
    result["msg"] = ""


    # 매칭되는 uid로 일단은 무조건 데이터 가져와서
    # 1. 제한시간체크 3분 
    if res.expiry_at <= datetime.datetime.now() :
        result["code"] = 500
        result["msg"] = "제한 시간(5분)을 초과했습니다. 다시 시도하여 주십시오."
    
    # 2. try_count 회수체크 3회
    elif res.try_count >= 3 :
        result["code"] = 500
        result["msg"] = "제한 횟수(3회)를 초과했습니다. 다시 시도하여 주십시오."

    # 3. db auth_num 이랑 input auth_num 비교
    elif res.auth_num != authNumInput.auth_num :
        result["code"] = 300
        result["msg"] = "인증번호가 불일치 합니다. 인증번호를 다시 입력해 주세요."

    if result["code"] != 200 :
        res.try_count = res.try_count + 1

    return result

# 유저 정보 by user_id
def read_by_userid(request: Request, user_id:str):
    request.state.inspect = frame()
    db = request.state.db 
    sql = db.query(T_MEMBER).filter(T_MEMBER.user_id == user_id)
    format_sql(sql)
    return sql.first()


# 복지드림 앱 push uuid 등록 by.namgu
def device_update(request: Request, info: Dict) :
    request.state.inspect = frame()
    db = request.state.db 

    sql = db.query(T_APP_DEVICE).filter(T_APP_DEVICE.bars_uuid == info["bars_uuid"])
    format_sql(sql)
    res = sql.first()

    if res is None : # 없는 사용자면 INSERT
        db_item = T_APP_DEVICE (
             user_id = info["user_id"]
            ,partner_id = info["partner_id"]
            ,bars_uuid = info["bars_uuid"]
            ,device_os = info["device_os"]
            ,gender = info["gender"]
            ,birth = info["birth"]
            ,mobile = info["mobile"]
            ,email = info["email"]
            ,is_sms = info["is_sms"]
            ,is_mailing = info["is_mailing"]
            ,is_push = info["is_push"]
        )
        db.add(db_item)
        db.flush()
        create_log(request, db_item.uid, "T_APP_DEVICE", "INSERT", "디바이스 등록", "", info["user_id"], info["bars_uuid"])
        
        request.state.inspect = frame()
        return 1

    else :  # 있는 사용자면 UPDATE
        if "user_id" in info and res.user_id != info["user_id"] :
            create_log(request, res.uid, "T_APP_DEVICE", "user_id", "로그인ID", res.user_id, info["user_id"], info["bars_uuid"])
            request.state.inspect = frame()
            res.user_id = info["user_id"]

        if "partner_id" in info and res.partner_id != info["partner_id"] :
            create_log(request, res.uid, "T_APP_DEVICE", "partner_id", "고객사", res.partner_id, info["partner_id"], info["bars_uuid"])
            request.state.inspect = frame()
            res.partner_id = info["partner_id"]

        if "bars_uuid" in info and res.bars_uuid != info["bars_uuid"] :
            create_log(request, res.uid, "T_APP_DEVICE", "bars_uuid", "바이앱스uuid", res.bars_uuid, info["bars_uuid"], info["bars_uuid"])
            request.state.inspect = frame()
            res.bars_uuid = info["bars_uuid"]

        if "device_os" in info and res.device_os != info["device_os"] :
            create_log(request, res.uid, "T_APP_DEVICE", "device_os", "android/ios", res.device_os, info["device_os"], info["bars_uuid"])
            request.state.inspect = frame()
            res.device_os = info["device_os"]

        if "gender" in info and res.gender != info["gender"] :
            create_log(request, res.uid, "T_APP_DEVICE", "gender", "성별", res.gender, info["gender"], info["bars_uuid"])
            request.state.inspect = frame()
            res.gender = info["gender"]

        if "birth" in info and res.birth != info["birth"] :
            create_log(request, res.uid, "T_APP_DEVICE", "birth", "생년월일", res.birth, info["birth"], info["bars_uuid"])
            request.state.inspect = frame()
            res.birth = info["birth"]

        if "mobile" in info and res.mobile != info["mobile"] :
            create_log(request, res.uid, "T_APP_DEVICE", "mobile", "휴대전화", res.mobile, info["mobile"], info["bars_uuid"])
            request.state.inspect = frame()
            res.mobile = info["mobile"]

        if "email" in info and res.email != info["email"] :
            create_log(request, res.uid, "T_APP_DEVICE", "email", "이메일", res.email, info["email"], info["bars_uuid"])
            request.state.inspect = frame()
            res.email = info["email"]

        if "is_sms" in info and res.is_sms != info["is_sms"] :
            create_log(request, res.uid, "T_APP_DEVICE", "is_sms", "문자 수신여부", res.is_sms, info["is_sms"], info["bars_uuid"])
            request.state.inspect = frame()
            res.is_sms = info["is_sms"]

        if "is_mailing" in info and res.is_mailing != info["is_mailing"] :
            create_log(request, res.uid, "T_APP_DEVICE", "is_mailing", "이메일 수신여부", res.is_mailing, info["is_mailing"], info["bars_uuid"])
            request.state.inspect = frame()
            res.is_mailing = info["is_mailing"]

        if "is_push" in info and res.is_push != info["is_push"] :
            create_log(request, res.uid, "T_APP_DEVICE", "is_push", "푸시 수신여부", res.is_push, info["is_push"], info["bars_uuid"])
            request.state.inspect = frame()
            res.is_push = info["is_push"]

            

        res.update_at = util.getNow()
        return 2



