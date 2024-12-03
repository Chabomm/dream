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

from app.core import exceptions as ex
from app.core import util
from app.core.database import format_sql
from app.models.partner import *
from app.models.session import *
from app.schemas.schema import *
from app.service.log_service import *

# 복지드림 inbound 고객사 정보 편집
def partner_edit(request: Request, info: Dict) :
    request.state.inspect = frame()
    db = request.state.db 

    res = db.query(T_PARTNER).filter(T_PARTNER.uid == info["uid"]).first()

    if res is None : # 없는 사용자면 INSERT
        db_item = T_PARTNER (
             uid = info["uid"]
            ,partner_type = info["partner_type"]
            ,partner_id = info["partner_id"]
            ,mall_name = info["mall_name"]
            ,company_name = info["company_name"]
            ,sponsor = info["sponsor"]
            ,partner_code = info["partner_code"]
            ,prefix = info["prefix"]
            ,logo = info["logo"]
            ,state = info["state"]
            ,mem_type = info["mem_type"]
            ,is_welfare = info["is_welfare"]
            ,is_dream = info["is_dream"]
            ,mall_type = info["mall_type"]
        )
        db.add(db_item)
        db.flush()
        create_log(request, db_item.uid, "T_PARTNER", "INSERT", "고객사 등록", "", info["partner_id"], info["partner_id"])
        request.state.inspect = frame()
        return 1

    else :  # 있는 사용자면 UPDATE
        if "partner_type" in info and res.partner_type != info["partner_type"] :
            create_log(request, res.uid, "T_PARTNER", "partner_type", "복지몰 로그인 타입", res.partner_type, info["partner_type"], info["partner_id"])
            request.state.inspect = frame()
            res.partner_type = info["partner_type"]
            
        if "partner_id" in info and res.partner_id != info["partner_id"] :
            create_log(request, res.uid, "T_PARTNER", "partner_id", "고객사 아이디", res.partner_id, info["partner_id"], info["partner_id"])
            request.state.inspect = frame()
            res.partner_id = info["partner_id"]
            
        if "mall_name" in info and res.mall_name != info["mall_name"] :
            create_log(request, res.uid, "T_PARTNER", "mall_name", "고객사 복지몰명", res.mall_name, info["mall_name"], info["partner_id"])
            request.state.inspect = frame()
            res.mall_name = info["mall_name"]
            
        if "company_name" in info and res.company_name != info["company_name"] :
            create_log(request, res.uid, "T_PARTNER", "company_name", "고객사 회사명", res.company_name, info["company_name"], info["partner_id"])
            request.state.inspect = frame()
            res.company_name = info["company_name"]
            
        if "sponsor" in info and res.sponsor != info["sponsor"] :
            create_log(request, res.uid, "T_PARTNER", "sponsor", "스폰서", res.sponsor, info["sponsor"], info["partner_id"])
            request.state.inspect = frame()
            res.sponsor = info["sponsor"]
            
        if "partner_code" in info and res.partner_code != info["partner_code"] :
            create_log(request, res.uid, "T_PARTNER", "partner_code", "고객사 코드", res.partner_code, info["partner_code"], info["partner_id"])
            request.state.inspect = frame()
            res.partner_code = info["partner_code"]
            
        if "prefix" in info and res.prefix != info["prefix"] :
            create_log(request, res.uid, "T_PARTNER", "prefix", "아이디 프리픽스", res.prefix, info["prefix"], info["partner_id"])
            request.state.inspect = frame()
            res.prefix = info["prefix"]
            
        if "logo" in info and res.logo != info["logo"] :
            create_log(request, res.uid, "T_PARTNER", "logo", "로고 이미지", res.logo, info["logo"], info["partner_id"])
            request.state.inspect = frame()
            res.logo = info["logo"]

        if "state" in info and res.state != info["state"] :
            create_log(request, res.uid, "T_PARTNER", "state", "복지몰 상태", res.state, info["state"], info["partner_id"])
            request.state.inspect = frame()
            res.state = info["state"]

        if "mem_type" in info and res.mem_type != info["mem_type"] :
            create_log(request, res.uid, "T_PARTNER", "mem_type", "복지몰 상태", res.mem_type, info["mem_type"], info["partner_id"])
            request.state.inspect = frame()
            res.mem_type = info["mem_type"]
            
        if "is_welfare" in info and res.is_welfare != info["is_welfare"] :
            create_log(request, res.uid, "T_PARTNER", "is_welfare", "복지포인트 사용여부", res.is_welfare, info["is_welfare"], info["partner_id"])
            request.state.inspect = frame()
            res.is_welfare = info["is_welfare"]
            
        if "is_dream" in info and res.is_dream != info["is_dream"] :
            create_log(request, res.uid, "T_PARTNER", "is_dream", "드림포인트 사용여부", res.is_dream, info["is_dream"], info["partner_id"])
            request.state.inspect = frame()
            res.is_dream = info["is_dream"]
            
        if "mall_type" in info and res.mall_type != info["mall_type"] :
            create_log(request, res.uid, "T_PARTNER", "mall_type", "몰타입", res.mall_type, info["mall_type"], info["partner_id"])
            request.state.inspect = frame()
            res.mall_type = info["mall_type"]

        res.update_at = util.getNow()
        return 2