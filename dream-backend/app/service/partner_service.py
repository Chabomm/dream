
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Optional
from inspect import currentframe as frame
from sqlalchemy.dialects import mysql as mysql_dialetct
from pymysql.converters import conversions, escape_item, encoders
from sqlalchemy import func, select, update, delete, Table, MetaData
import math

from app.core import exceptions as ex
from app.core import util
from app.core.database import format_sql
from app.models.partner import *
from app.schemas.schema import *
from app.schemas.manager.member import *
from app.service.log_service import *
from app.schemas.manager.partner import *



# partner_uid로 고객사정보 select
def read_partner_by_puid(request: Request, partner_uid: int):
    request.state.inspect = frame()
    db = request.state.db 

    sql = db.query(T_PARTNER).filter(T_PARTNER.uid == partner_uid)
    return sql.first()

# 고객사 등록
def partner_create(request: Request, partnerInput: PartnerInput):
    request.state.inspect = frame()
    db = request.state.db 

    db_item = T_PARTNER (
         partner_type = partnerInput.partner_type
        ,partner_id = partnerInput.partner_id
        ,mall_name = partnerInput.mall_name
        ,company_name = partnerInput.company_name
        ,sponsor = partnerInput.sponsor
        ,partner_code = partnerInput.partner_code
        ,prefix = partnerInput.prefix
        ,logo = partnerInput.logo
        ,is_welfare = partnerInput.is_welfare
        ,is_dream = partnerInput.is_dream
        ,state = partnerInput.state
        ,mem_type = partnerInput.mem_type
    )
    db.add(db_item)
    db.flush()

    create_log(request, db_item.uid, "T_PARTNER", "INSERT", "고객사 등록", 0, db_item.uid, partnerInput.in_user_id)
    request.state.inspect = frame()

    return db_item

# 고객사 수정
def partner_update(request: Request, partnerInput: PartnerInput):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user
    
    # 기존 등록된 고객사 select 
    res = db.query(T_PARTNER).filter(T_PARTNER.partner_id == partnerInput.partner_id).first()

    if res is None:
        raise ex.NotFoundUser

    if partnerInput.partner_type is not None and res.partner_type != partnerInput.partner_type:
        create_log(request, res.uid, "T_PARTNER", "partner_type", "회원가입 유형",
                    res.partner_type, partnerInput.partner_type, partnerInput.in_user_id)
        request.state.inspect = frame()
        res.partner_type = partnerInput.partner_type

    if partnerInput.mall_name is not None and res.mall_name != partnerInput.mall_name:
        create_log(request, res.uid, "T_PARTNER", "mall_name", "복지몰명",
                    res.mall_name, partnerInput.mall_name, partnerInput.in_user_id)
        request.state.inspect = frame()
        res.mall_name = partnerInput.mall_name

    if partnerInput.company_name is not None and res.company_name != partnerInput.company_name:
        create_log(request, res.uid, "T_PARTNER", "company_name", "고객사명",
                    res.company_name, partnerInput.company_name, partnerInput.in_user_id)
        request.state.inspect = frame()
        res.company_name = partnerInput.company_name

    if partnerInput.sponsor is not None and res.sponsor != partnerInput.sponsor:
        create_log(request, res.uid, "T_PARTNER", "sponsor", "스폰서",
                    res.sponsor, partnerInput.sponsor, partnerInput.in_user_id)
        request.state.inspect = frame()
        res.sponsor = partnerInput.sponsor

    if partnerInput.logo is not None and res.logo != partnerInput.logo:
        create_log(request, res.uid, "T_PARTNER", "logo", "로고",
                    res.logo, partnerInput.logo, partnerInput.in_user_id)
        request.state.inspect = frame()
        res.logo = partnerInput.logo

    if partnerInput.is_welfare is not None and res.is_welfare != partnerInput.is_welfare:
        create_log(request, res.uid, "T_PARTNER", "is_welfare", "복지포인트 사용유무",
                    res.is_welfare, partnerInput.is_welfare, partnerInput.in_user_id)
        request.state.inspect = frame()
        res.is_welfare = partnerInput.is_welfare

    if partnerInput.is_dream is not None and res.is_dream != partnerInput.is_dream:
        create_log(request, res.uid, "T_PARTNER", "is_dream", "드림포인트 사용유무",
                    res.is_dream, partnerInput.is_dream, partnerInput.in_user_id)
        request.state.inspect = frame()
        res.is_dream = partnerInput.is_dream

    if partnerInput.state is not None and res.state != partnerInput.state:
        create_log(request, res.uid, "T_PARTNER", "state", "복지몰 상태",
                    res.state, partnerInput.state, partnerInput.in_user_id)
        request.state.inspect = frame()
        res.state = partnerInput.state

    if partnerInput.mem_type is not None and res.mem_type != partnerInput.mem_type:
        create_log(request, res.uid, "T_PARTNER", "mem_type", "회원유형",
                    res.mem_type, partnerInput.mem_type, partnerInput.in_user_id)
        request.state.inspect = frame()
        res.mem_type = partnerInput.mem_type

    res.update_at = util.getNow()
    return res
    
