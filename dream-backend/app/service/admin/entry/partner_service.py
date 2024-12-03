from fastapi import Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from dateutil.relativedelta import relativedelta
from inspect import currentframe as frame
from sqlalchemy.dialects import mysql as mysql_dialetct
from pymysql.converters import conversions, escape_item, encoders
from sqlalchemy import func, select, update, delete, Table, MetaData, and_, or_
import math

from app.core import exceptions as ex
from app.core import util
from app.core.database import format_sql
from app.deps import auth
from app.models.member import *
from app.models.partner import *
from app.models.manager import *
from app.schemas.admin.entry.partner import *
from app.schemas.admin.entry.build import *
from app.service.log_service import *

# 고객사 list
def partner_list(request: Request, page_param: PPage_param):
    request.state.inspect = frame()
    db = request.state.db

    filters = []
    filters.append(getattr(T_PARTNER, "delete_at") == None)

    # [ S ] search filter start
    if page_param.filters :
        if page_param.filters["skeyword"] :
            if page_param.filters["skeyword_type"] != "" :
                filters.append(getattr(T_PARTNER, page_param.filters["skeyword_type"]).like("%"+page_param.filters["skeyword"]+"%"))
            else : 
                filters.append(
                    T_PARTNER.partner_id.like("%"+page_param.filters["skeyword"]+"%") 
                    | T_PARTNER.partner_code.like("%"+page_param.filters["skeyword"]+"%")
                    | T_PARTNER.company_name.like("%"+page_param.filters["skeyword"]+"%")
                    | T_PARTNER.mall_name.like("%"+page_param.filters["skeyword"]+"%")
                )

        if page_param.filters["create_at"]["startDate"] and page_param.filters["create_at"]["endDate"] :
            filters.append(
                and_(
                    T_PARTNER.create_at >= page_param.filters["create_at"]["startDate"]
                    ,T_PARTNER.create_at <= page_param.filters["create_at"]["endDate"] + " 23:59:59"
                )
            )

        if page_param.filters["state"] :
            filters.append(T_PARTNER.state == page_param.filters["state"])
    # [ E ] search filter end

    member_count_stmt = (
        db.query(
            T_MEMBER.partner_uid.label("partner_uid")
            ,func.count(T_MEMBER.uid).label('member_count')
        )
        .group_by(T_MEMBER.partner_uid)
        .subquery()
    )

    sql = (
        db.query(
             T_PARTNER.uid
            ,T_PARTNER.partner_type
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
            ,T_PARTNER.mem_type
            ,T_PARTNER.mall_type
            ,member_count_stmt.c.member_count
            ,T_PARTNER_INFO.staff_name
            ,T_PARTNER_INFO.staff_mobile
            ,T_PARTNER_INFO.staff_email
            ,func.date_format(T_PARTNER.create_at, '%Y-%m-%d %T').label('create_at')
            ,func.date_format(T_PARTNER.update_at, '%Y-%m-%d %T').label('update_at')
            ,func.date_format(T_PARTNER.delete_at, '%Y-%m-%d %T').label('delete_at')
        )
        .join(
            member_count_stmt, 
            T_PARTNER.uid == member_count_stmt.c.partner_uid,
            isouter = True 
        )
        .join(
            T_PARTNER_INFO ,
            T_PARTNER.uid == T_PARTNER_INFO.partner_uid,
            isouter = True 
        )
        .filter(*filters)
        .order_by(T_PARTNER.uid.desc())
        .offset((page_param.page-1)*page_param.page_view_size)
        .limit(page_param.page_view_size)
    )

    # format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    
    # [ S ] 페이징 처리
    page_param.page_total = (
        db.query(T_PARTNER)
        .filter(*filters)
        .count()
    )
    page_param.page_last = math.ceil(
        page_param.page_total / page_param.page_view_size)
    page_param.page_size = len(rows)  # 현재 페이지에 검색된 수
    # [ E ] 페이징 처리

    jsondata = {}
    jsondata.update({"params":page_param})
    jsondata.update({"list": rows})

    return jsondata

# 복지드림 구축신청완료 후 고객사 등록 또는 수정 (T_PARTNER)
def partner_create(request: Request, dreamBuild: DreamBuild):
    request.state.inspect = frame()
    db = request.state.db 
    user = request.state.user

    partner_code = dreamBuild.biz_item + "TEST"

    res_partner = db.query(T_PARTNER).filter(T_PARTNER.partner_id == dreamBuild.host).first()
    if res_partner == None :
        db_item = T_PARTNER (
             partner_type = "300"
            ,partner_id = dreamBuild.host 
            ,mall_name = dreamBuild.mall_name 
            ,company_name = dreamBuild.company_name 
            ,sponsor = "welfaredream"
            ,partner_code = partner_code
            ,prefix = partner_code + "_" 
            ,logo = dreamBuild.file_mall_logo 
        )
        db.add(db_item)
        db.flush()

        create_log(request, db_item.uid, "T_PARTNER", "INSERT", "복지드림 구축신청완료 후 고객사 등록", 0, db_item.uid, user.user_id)
        request.state.inspect = frame()

        return db_item
    
    else : 
        res_partner.partner_type = "300"
        res_partner.partner_id = dreamBuild.host 
        res_partner.mall_name = dreamBuild.mall_name 
        res_partner.company_name = dreamBuild.company_name 
        res_partner.sponsor = "welfaredream"
        res_partner.partner_code = partner_code
        res_partner.prefix = partner_code + "_" 
        res_partner.logo = dreamBuild.file_mall_logo 
        res_partner.update_at = util.getNow()
        create_log(request, res_partner.uid, "T_PARTNER", "UPDATE", "복지드림 구축신청완료 후 고객사 수정", 0, res_partner.uid, user.user_id)
        request.state.inspect = frame()
        return res_partner

# 복지드림 구축신청완료 후 고객사 정보 등록 또는 수정 (T_PARTNER_INFO)
def partner_info_create(request: Request, dreamBuild: DreamBuild, partner_uid: int):
    request.state.inspect = frame()
    db = request.state.db 
    user = request.state.user

    res_partner_info = db.query(T_PARTNER_INFO).filter(T_PARTNER_INFO.partner_uid == partner_uid).first()
    if res_partner_info == None :
        db_item = T_PARTNER_INFO (
            partner_uid = partner_uid
            ,counsel_uid = dreamBuild.counsel_uid
            ,build_uid = dreamBuild.uid
            ,company_name = dreamBuild.company_name
            ,ceo_name = dreamBuild.ceo_name
            ,staff_name = dreamBuild.staff_name
            ,staff_dept = dreamBuild.staff_dept
            ,staff_position = dreamBuild.staff_position
            ,staff_position2 = dreamBuild.staff_position2
            ,staff_mobile = dreamBuild.staff_mobile
            ,staff_email = dreamBuild.staff_email
            ,account_email = dreamBuild.account_email
            ,post = dreamBuild.post
            ,addr = dreamBuild.addr
            ,addr_detail = dreamBuild.addr_detail
            ,company_hp = dreamBuild.company_hp
            ,biz_kind = dreamBuild.biz_kind
            ,biz_item = dreamBuild.biz_item
            ,biz_no = dreamBuild.biz_no
            ,biz_service = dreamBuild.biz_service
            ,mall_name = dreamBuild.mall_name
            ,host = dreamBuild.host
            ,file_biz_no = dreamBuild.file_biz_no
            ,file_bank = dreamBuild.file_bank
            ,file_logo = dreamBuild.file_logo
            ,file_mall_logo = dreamBuild.file_mall_logo
        )
        db.add(db_item)
        db.flush()
        
        create_log(request, db_item.partner_uid, "T_PARTNER_INFO", "INSERT", "복지드림 구축신청완료 후 고객사 정보 등록", 0, db_item.partner_uid, user.user_id)
        request.state.inspect = frame()

        return db_item
    
    else : 
        res_partner_info.counsel_uid = dreamBuild.counsel_uid
        res_partner_info.build_uid = dreamBuild.uid
        res_partner_info.company_name = dreamBuild.company_name
        res_partner_info.ceo_name = dreamBuild.ceo_name
        res_partner_info.staff_name = dreamBuild.staff_name
        res_partner_info.staff_dept = dreamBuild.staff_dept
        res_partner_info.staff_position = dreamBuild.staff_position
        res_partner_info.staff_position2 = dreamBuild.staff_position2
        res_partner_info.staff_mobile = dreamBuild.staff_mobile
        res_partner_info.staff_email = dreamBuild.staff_email
        res_partner_info.account_email = dreamBuild.account_email
        res_partner_info.post = dreamBuild.post
        res_partner_info.addr = dreamBuild.addr
        res_partner_info.addr_detail = dreamBuild.addr_detail
        res_partner_info.company_hp = dreamBuild.company_hp
        res_partner_info.biz_kind = dreamBuild.biz_kind
        res_partner_info.biz_item = dreamBuild.biz_item
        res_partner_info.biz_no = dreamBuild.biz_no
        res_partner_info.biz_service = dreamBuild.biz_service
        res_partner_info.mall_name = dreamBuild.mall_name
        res_partner_info.host = dreamBuild.host
        res_partner_info.file_biz_no = dreamBuild.file_biz_no
        res_partner_info.file_bank = dreamBuild.file_bank
        res_partner_info.file_logo = dreamBuild.file_logo
        res_partner_info.file_mall_logo = dreamBuild.file_mall_logo
        res_partner_info.update_at = util.getNow()
        create_log(request, res_partner_info.partner_uid, "T_PARTNER_INFO", "UPDATE", "복지드림 구축신청완료 후 고객사 정보 수정", 0, res_partner_info.partner_uid, user.user_id)
        request.state.inspect = frame()
        return res_partner_info
    
# 고객사 정보 select partner_uid by partner_id
def read_partner_id(request: Request, partner_id: str):
    request.state.inspect = frame()
    db = request.state.db 
    filters = []
    filters.append(getattr(T_PARTNER, "partner_id") == partner_id)
    sql = db.query(T_PARTNER.uid).filter(*filters)
    return sql.first()

# 고객사 정보 select partner_uid by host
def read_partner_uid_for_build_uid(request: Request, build_uid: int):
    request.state.inspect = frame()
    db = request.state.db 
    filters = []
    filters.append(getattr(T_PARTNER_INFO, "build_uid") == build_uid)
    sql = db.query(T_PARTNER_INFO.partner_uid).filter(*filters)
    res = sql.first()
    if res == None :
        return 0
    else :
        return res.partner_uid

# 고객사 상세
def partner_read(request: Request, uid: int):
    request.state.inspect = frame()
    db = request.state.db

    sql = ( 
        db.query(
             T_PARTNER.uid
            ,T_PARTNER.partner_type
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
            ,T_PARTNER.mem_type
            ,T_PARTNER.mall_type
            ,T_PARTNER.roles
            ,func.date_format(T_PARTNER.create_at, '%Y-%m-%d %T').label('create_at')
            ,func.date_format(T_PARTNER.update_at, '%Y-%m-%d %T').label('update_at')
            ,func.date_format(T_PARTNER.delete_at, '%Y-%m-%d %T').label('delete_at')
        )
        .filter(
            T_PARTNER.uid == uid
            ,T_PARTNER.delete_at == None
        )
    )
    format_sql(sql)

    res = sql.first()

    if res == None :
        return {}
    else :
        return dict(zip(res.keys(), res))

def partner_info_read(request: Request, uid: int):
    request.state.inspect = frame()
    db = request.state.db

    sql = ( 
        db.query(
             T_PARTNER_INFO.partner_uid
            ,T_PARTNER_INFO.counsel_uid
            ,T_PARTNER_INFO.build_uid
            ,T_PARTNER_INFO.company_name
            ,T_PARTNER_INFO.ceo_name
            ,T_PARTNER_INFO.staff_name
            ,T_PARTNER_INFO.staff_dept
            ,T_PARTNER_INFO.staff_position
            ,T_PARTNER_INFO.staff_position2
            ,T_PARTNER_INFO.staff_mobile
            ,T_PARTNER_INFO.staff_email
            ,T_PARTNER_INFO.account_email
            ,T_PARTNER_INFO.post
            ,T_PARTNER_INFO.addr
            ,T_PARTNER_INFO.addr_detail
            ,T_PARTNER_INFO.company_hp
            ,T_PARTNER_INFO.biz_kind
            ,T_PARTNER_INFO.biz_item
            ,T_PARTNER_INFO.biz_no
            ,T_PARTNER_INFO.biz_service
            ,T_PARTNER_INFO.mall_name
            ,T_PARTNER_INFO.host
            ,T_PARTNER_INFO.file_biz_no
            ,T_PARTNER_INFO.file_bank
            ,T_PARTNER_INFO.file_logo
            ,T_PARTNER_INFO.file_mall_logo
        )
        .filter(
            T_PARTNER_INFO.partner_uid == uid
            ,T_PARTNER_INFO.delete_at == None
        )
    )
    format_sql(sql)

    res = sql.first()

    if res == None :
        return {}
    else :
        return dict(zip(res.keys(), res))

# 파트너 용어 상세
def partner_words_read(request: Request, uid: int, mall_type: str):
    request.state.inspect = frame()
    db = request.state.db

    sql = ( 
        db.query(
             T_PARTNER_WORDS.partner_uid.label('word_partner_uid')
            ,T_PARTNER_WORDS.partner_id.label('word_partner_id')
            ,T_PARTNER_WORDS.mall_type
            ,T_PARTNER_WORDS.mall_tltle
            ,T_PARTNER_WORDS.member_name
            ,T_PARTNER_WORDS.point_name
            ,T_PARTNER_WORDS.notice
            ,T_PARTNER_WORDS.intro
            ,T_PARTNER_WORDS.employee_card
            ,T_PARTNER_WORDS.benefit
            ,T_PARTNER_WORDS.b2b_goods
        )
        .filter(or_(
            (
            T_PARTNER_WORDS.partner_uid == uid
            ).self_group(),
            and_(
                T_PARTNER_WORDS.partner_id == None,
                T_PARTNER_WORDS.mall_type == mall_type,
            ).self_group()
        ))
        .order_by(T_PARTNER_WORDS.partner_uid.desc())
    )
    format_sql(sql)

    res = sql.first()

    if res == None :
        return {}
    else :
        return dict(zip(res.keys(), res))
    
# 파트너 드림포인트 상세
def dream_config_read(request: Request, uid: int):
    request.state.inspect = frame()
    db = request.state.db

    sql = ( 
        db.query(
             T_DREAM_CONFIG.partner_id
            ,T_DREAM_CONFIG.give_point
            ,T_DREAM_CONFIG.exp_date
            ,func.date_format(T_DREAM_CONFIG.end_date, '%Y-%m-%d').label('end_date')
            ,T_DREAM_CONFIG.memo
        )
        .filter(
            T_DREAM_CONFIG.partner_uid == uid
        )
    )
    format_sql(sql)

    res = sql.first()

    if res == None :
        return {}
    else :
        return dict(zip(res.keys(), res))
    
# 드림포인트 등록
def dream_config_create(request: Request, partner_id: str, partner_uid: int):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    res_dream_config = db.query(T_DREAM_CONFIG).filter(T_DREAM_CONFIG.partner_uid == partner_uid).first()
    if res_dream_config == None :
        db_item = T_DREAM_CONFIG (
            partner_uid = partner_uid
            ,partner_id = partner_id
            ,end_date = str(datetime.now().date() + relativedelta(months=+3))
        )
        db.add(db_item)
        db.flush()

        create_log(request, db_item.partner_uid, "T_DREAM_CONFIG", "INSERT", "복지드림 구축신청완료 후 복지포인트 등록", 0, db_item.partner_uid, user.user_id)
        request.state.inspect = frame()

    else : 
        res_dream_config.counsel_uid = partner_uid
        res_dream_config.partner_id = partner_id
        res_dream_config.end_date = str(datetime.now().date() + relativedelta(months=+3))

        create_log(request, res_dream_config.partner_uid, "T_DREAM_CONFIG", "UPDATE", "복지드림 구축신청완료 후 복지포인트 정보 수정", 0, res_dream_config.partner_uid, user.user_id)
        request.state.inspect = frame()
        return res_dream_config

    return db_item

# 고객사 - 수정
def partner_update(request: Request, partnerInput: PartnerInput):
    request.state.inspect = frame()
    db = request.state.db 
    user = request.state.user

    res_partner = (db.query(T_PARTNER).filter(T_PARTNER.uid == partnerInput.uid).first())

    if res_partner is None :
        raise ex.NotFoundUser

    if partnerInput.mall_name is not None and res_partner.mall_name != partnerInput.mall_name : 
        create_log(request, res_partner.uid, "T_PARTNER", "mall_name", "복지몰명 수정", res_partner.mall_name, partnerInput.mall_name, user.user_id)
        request.state.inspect = frame()
        res_partner.mall_name = partnerInput.mall_name

    if partnerInput.company_name is not None and res_partner.company_name != partnerInput.company_name : 
        create_log(request, res_partner.uid, "T_PARTNER", "company_name", "고객사명 수정", res_partner.company_name, partnerInput.company_name, user.user_id)
        request.state.inspect = frame()
        res_partner.company_name = partnerInput.company_name

    if partnerInput.state is not None and res_partner.state != partnerInput.state : 
        create_log(request, res_partner.uid, "T_PARTNER", "state", "복지몰 상태 수정", res_partner.state, partnerInput.state, user.user_id)
        request.state.inspect = frame()
        res_partner.state = partnerInput.state

    if partnerInput.sponsor is not None and res_partner.sponsor != partnerInput.sponsor : 
        create_log(request, res_partner.uid, "T_PARTNER", "sponsor", "SponsorID 수정", res_partner.sponsor, partnerInput.sponsor, user.user_id)
        request.state.inspect = frame()
        res_partner.sponsor = partnerInput.sponsor

    if partnerInput.partner_type is not None and res_partner.partner_type != partnerInput.partner_type : 
        create_log(request, res_partner.uid, "T_PARTNER", "partner_type", "회원가입유형 수정", res_partner.partner_type, partnerInput.partner_type, user.user_id)
        request.state.inspect = frame()
        res_partner.partner_type = partnerInput.partner_type

    if partnerInput.mem_type is not None and res_partner.mem_type != partnerInput.mem_type : 
        create_log(request, res_partner.uid, "T_PARTNER", "mem_type", "회원유형 수정", res_partner.mem_type, partnerInput.mem_type, user.user_id)
        request.state.inspect = frame()
        res_partner.mem_type = partnerInput.mem_type

    if partnerInput.mall_type is not None and res_partner.mall_type != partnerInput.mall_type : 
        create_log(request, res_partner.uid, "T_PARTNER", "mall_type", "몰유형 수정", res_partner.mall_type, partnerInput.mall_type, user.user_id)
        request.state.inspect = frame()
        res_partner.mall_type = partnerInput.mall_type

    if partnerInput.is_welfare is not None and res_partner.is_welfare != partnerInput.is_welfare : 
        create_log(request, res_partner.uid, "T_PARTNER", "is_welfare", "복지포인트 유무 수정", res_partner.is_welfare, partnerInput.is_welfare, user.user_id)
        request.state.inspect = frame()
        res_partner.is_welfare = partnerInput.is_welfare

    if partnerInput.is_dream is not None and res_partner.is_dream != partnerInput.is_dream : 
        create_log(request, res_partner.uid, "T_PARTNER", "is_dream", "드림포인트 유무 수정", res_partner.is_dream, partnerInput.is_dream, user.user_id)
        request.state.inspect = frame()
        res_partner.is_dream = partnerInput.is_dream

    if partnerInput.roles is not None and res_partner.roles != partnerInput.roles:
        create_log(request, partnerInput.uid, "T_PARTNER", "roles", "역할 수정", res_partner.roles, partnerInput.roles, user.user_id)
        request.state.inspect = frame()
        res_partner.roles = partnerInput.roles

    res_partner.update_at = util.getNow()

    return res_partner

# 고객사 계약 정보 - 수정
def partner_info_update(request: Request, partnerInput: PartnerInput):
    request.state.inspect = frame()
    db = request.state.db 
    user = request.state.user

    res_partner_info = (db.query(T_PARTNER_INFO).filter(T_PARTNER_INFO.partner_uid == partnerInput.uid).first())

    if res_partner_info is None :
        raise ex.NotFoundUser

    if partnerInput.company_name is not None and res_partner_info.company_name != partnerInput.company_name : 
        create_log(request, res_partner_info.partner_uid, "T_PARTNER_INFO", "company_name", "기업명 수정", res_partner_info.company_name, partnerInput.company_name, user.user_id)
        request.state.inspect = frame()
        res_partner_info.company_name = partnerInput.company_name

    if partnerInput.ceo_name is not None and res_partner_info.ceo_name != partnerInput.ceo_name : 
        create_log(request, res_partner_info.partner_uid, "T_PARTNER_INFO", "ceo_name", "대표자성함 수정", res_partner_info.ceo_name, partnerInput.ceo_name, user.user_id)
        request.state.inspect = frame()
        res_partner_info.ceo_name = partnerInput.ceo_name

    if partnerInput.staff_name is not None and res_partner_info.staff_name != partnerInput.staff_name : 
        create_log(request, res_partner_info.partner_uid, "T_PARTNER_INFO", "staff_name", "담당자 이름 수정", res_partner_info.staff_name, partnerInput.staff_name, user.user_id)
        request.state.inspect = frame()
        res_partner_info.staff_name = partnerInput.staff_name

    if partnerInput.staff_dept is not None and res_partner_info.staff_dept != partnerInput.staff_dept : 
        create_log(request, res_partner_info.partner_uid, "T_PARTNER_INFO", "staff_dept", "담당자 부서 수정", res_partner_info.staff_dept, partnerInput.staff_dept, user.user_id)
        request.state.inspect = frame()
        res_partner_info.staff_dept = partnerInput.staff_dept

    if partnerInput.staff_position is not None and res_partner_info.staff_position != partnerInput.staff_position : 
        create_log(request, res_partner_info.partner_uid, "T_PARTNER_INFO", "staff_position", "담당자 직급 수정", res_partner_info.staff_position, partnerInput.staff_position, user.user_id)
        request.state.inspect = frame()
        res_partner_info.staff_position = partnerInput.staff_position

    if partnerInput.staff_position2 is not None and res_partner_info.staff_position2 != partnerInput.staff_position2 : 
        create_log(request, res_partner_info.partner_uid, "T_PARTNER_INFO", "staff_position2", "담당자 직책 수정", res_partner_info.staff_position2, partnerInput.staff_position2, user.user_id)
        request.state.inspect = frame()
        res_partner_info.staff_position2 = partnerInput.staff_position2

    if partnerInput.staff_mobile is not None and res_partner_info.staff_mobile != partnerInput.staff_mobile : 
        create_log(request, res_partner_info.partner_uid, "T_PARTNER_INFO", "staff_mobile", "담당자 휴대전화 수정", res_partner_info.staff_mobile, partnerInput.staff_mobile, user.user_id)
        request.state.inspect = frame()
        res_partner_info.staff_mobile = partnerInput.staff_mobile

    if partnerInput.staff_email is not None and res_partner_info.staff_email != partnerInput.staff_email : 
        create_log(request, res_partner_info.partner_uid, "T_PARTNER_INFO", "staff_email", "담당자 이메일 수정", res_partner_info.staff_email, partnerInput.staff_email, user.user_id)
        request.state.inspect = frame()
        res_partner_info.staff_email = partnerInput.staff_email

    if partnerInput.account_email is not None and res_partner_info.account_email != partnerInput.account_email : 
        create_log(request, res_partner_info.partner_uid, "T_PARTNER_INFO", "account_email", "정산 이메일 수정", res_partner_info.account_email, partnerInput.account_email, user.user_id)
        request.state.inspect = frame()
        res_partner_info.account_email = partnerInput.account_email

    if partnerInput.post is not None and res_partner_info.post != partnerInput.post : 
        create_log(request, res_partner_info.partner_uid, "T_PARTNER_INFO", "post", "우편번호 수정", res_partner_info.post, partnerInput.post, user.user_id)
        request.state.inspect = frame()
        res_partner_info.post = partnerInput.post

    if partnerInput.addr is not None and res_partner_info.addr != partnerInput.addr : 
        create_log(request, res_partner_info.partner_uid, "T_PARTNER_INFO", "addr", "주소 수정", res_partner_info.addr, partnerInput.addr, user.user_id)
        request.state.inspect = frame()
        res_partner_info.addr = partnerInput.addr

    if partnerInput.addr_detail is not None and res_partner_info.addr_detail != partnerInput.addr_detail : 
        create_log(request, res_partner_info.partner_uid, "T_PARTNER_INFO", "addr_detail", "주소 상세 수정", res_partner_info.addr_detail, partnerInput.addr_detail, user.user_id)
        request.state.inspect = frame()
        res_partner_info.addr_detail = partnerInput.addr_detail

    if partnerInput.company_hp is not None and res_partner_info.company_hp != partnerInput.company_hp : 
        create_log(request, res_partner_info.partner_uid, "T_PARTNER_INFO", "company_hp", "일반전화(대표번호) 수정", res_partner_info.company_hp, partnerInput.company_hp, user.user_id)
        request.state.inspect = frame()
        res_partner_info.company_hp = partnerInput.company_hp

    if partnerInput.biz_kind is not None and res_partner_info.biz_kind != partnerInput.biz_kind : 
        create_log(request, res_partner_info.partner_uid, "T_PARTNER_INFO", "biz_kind", "사업자 분류 수정", res_partner_info.biz_kind, partnerInput.biz_kind, user.user_id)
        request.state.inspect = frame()
        res_partner_info.biz_kind = partnerInput.biz_kind

    if partnerInput.biz_item is not None and res_partner_info.biz_item != partnerInput.biz_item : 
        create_log(request, res_partner_info.partner_uid, "T_PARTNER_INFO", "biz_item", "업종 수정", res_partner_info.biz_item, partnerInput.biz_item, user.user_id)
        request.state.inspect = frame()
        res_partner_info.biz_item = partnerInput.biz_item

    if partnerInput.biz_no is not None and res_partner_info.biz_no != partnerInput.biz_no : 
        create_log(request, res_partner_info.partner_uid, "T_PARTNER_INFO", "biz_no", "사업자등록번호 수정", res_partner_info.biz_no, partnerInput.biz_no, user.user_id)
        request.state.inspect = frame()
        res_partner_info.biz_no = partnerInput.biz_no

    if partnerInput.file_biz_no is not None and res_partner_info.file_biz_no != partnerInput.file_biz_no : 
        create_log(request, res_partner_info.partner_uid, "T_PARTNER_INFO", "file_biz_no", "사업자등록증 수정", res_partner_info.file_biz_no, partnerInput.file_biz_no, user.user_id)
        request.state.inspect = frame()
        res_partner_info.file_biz_no = partnerInput.file_biz_no

    if partnerInput.file_bank is not None and res_partner_info.file_bank != partnerInput.file_bank : 
        create_log(request, res_partner_info.partner_uid, "T_PARTNER_INFO", "file_bank", "통장사본 수정", res_partner_info.file_bank, partnerInput.file_bank, user.user_id)
        request.state.inspect = frame()
        res_partner_info.file_bank = partnerInput.file_bank

    if partnerInput.file_logo is not None and res_partner_info.file_logo != partnerInput.file_logo : 
        create_log(request, res_partner_info.partner_uid, "T_PARTNER_INFO", "file_logo", "회사 로고 수정", res_partner_info.file_logo, partnerInput.file_logo, user.user_id)
        request.state.inspect = frame()
        res_partner_info.file_logo = partnerInput.file_logo

    if partnerInput.file_mall_logo is not None and res_partner_info.file_mall_logo != partnerInput.file_mall_logo : 
        create_log(request, res_partner_info.partner_uid, "T_PARTNER_INFO", "file_mall_logo", "복지몰 로고 수정", res_partner_info.file_mall_logo, partnerInput.file_mall_logo, user.user_id)
        request.state.inspect = frame()
        res_partner_info.file_mall_logo = partnerInput.file_mall_logo

    res_partner_info.update_at = util.getNow()

    return res_partner_info

# 고객사- 수정
def dream_config_update(request: Request, partnerInput: PartnerInput):
    request.state.inspect = frame()
    db = request.state.db 
    user = request.state.user

    res_dream_config = (db.query(T_DREAM_CONFIG).filter(T_DREAM_CONFIG.partner_uid == partnerInput.uid).first())

    if res_dream_config is None :
        return

    if partnerInput.give_point is not None and res_dream_config.give_point != partnerInput.give_point : 
        create_log(request, res_dream_config.partner_uid, "T_DREAM_CONFIG", "give_point", "포인트 금액 수정", res_dream_config.give_point, partnerInput.give_point, user.user_id)
        request.state.inspect = frame()
        res_dream_config.give_point = partnerInput.give_point

    if partnerInput.exp_date is not None and res_dream_config.exp_date != partnerInput.exp_date : 
        create_log(request, res_dream_config.partner_uid, "T_DREAM_CONFIG", "exp_date", "포인트 유효일 수정", res_dream_config.exp_date, partnerInput.exp_date, user.user_id)
        request.state.inspect = frame()
        res_dream_config.exp_date = partnerInput.exp_date

    if partnerInput.end_date is not None and res_dream_config.end_date != partnerInput.end_date : 
        create_log(request, res_dream_config.partner_uid, "T_DREAM_CONFIG", "end_date", "언제까지 지급할건지 수정", res_dream_config.end_date, partnerInput.end_date, user.user_id)
        request.state.inspect = frame()
        res_dream_config.end_date = partnerInput.end_date

    if partnerInput.memo is not None and res_dream_config.memo != partnerInput.memo : 
        create_log(request, res_dream_config.partner_uid, "T_DREAM_CONFIG", "memo", "관리자 특이사항 수정", res_dream_config.memo, partnerInput.memo, user.user_id)
        request.state.inspect = frame()
        res_dream_config.memo = partnerInput.memo

    return res_dream_config
