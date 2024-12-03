from fastapi import Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Optional
from inspect import currentframe as frame
from sqlalchemy.dialects import mysql as mysql_dialetct
from pymysql.converters import conversions, escape_item, encoders
from sqlalchemy import func, select, update, delete, Table, MetaData, and_
import math

from app.core import exceptions as ex
from app.core import util
from app.core.database import format_sql
from app.models.member import *
from app.models.device import *
from app.models.partner import *
from app.schemas.admin.member import *
from app.service.log_service import *

# 회원 list 
def list(request: Request, page_param: PPage_param):
    request.state.inspect = frame()
    db = request.state.db

    
    partner_stmt = (
        db.query(
            T_PARTNER.mall_name
            ,T_PARTNER.company_name
            ,T_PARTNER.partner_code
            ,T_PARTNER.uid.label("partner_uid")
        )
        .subquery()
    )

    filters = []
    filters.append(getattr(T_MEMBER, "delete_at") == None)

    # [ S ] search filter start
    if page_param.filters :
        if page_param.filters["skeyword"] :
            if page_param.filters["skeyword_type"] != "" :
                if page_param.filters["skeyword_type"] == "mall_name" :
                    filters.append(partner_stmt.c.mall_name.like("%"+page_param.filters["skeyword"]+"%"))
                elif page_param.filters["skeyword_type"] == "partner_code" :
                    filters.append(partner_stmt.c.partner_code.like("%"+page_param.filters["skeyword"]+"%"))
                else :
                    filters.append(getattr(T_MEMBER, page_param.filters["skeyword_type"]).like("%"+page_param.filters["skeyword"]   +"%"))
            else : 
                filters.append(
                    T_MEMBER.partner_id.like("%"+page_param.filters["skeyword"]+"%") 
                    | partner_stmt.c.mall_name.like("%"+page_param.filters["skeyword"]+"%") 
                    | partner_stmt.c.partner_code.like("%"+page_param.filters["skeyword"]+"%") 
                    | T_MEMBER.user_id.like("%"+page_param.filters["skeyword"]+"%") 
                    | T_MEMBER.user_name.like("%"+page_param.filters["skeyword"]+"%") 
                )

        if page_param.filters["create_at"]["startDate"] and page_param.filters["create_at"]["endDate"] :
            filters.append(
                and_(
                    T_MEMBER.create_at >= page_param.filters["create_at"]["startDate"]
                    ,T_MEMBER.create_at <= page_param.filters["create_at"]["endDate"] + " 23:59:59"
                )
            )

        if page_param.filters["serve"] :
            filters.append(T_MEMBER_INFO.serve == page_param.filters["serve"])

        if page_param.filters["partner_uid"] > 0 :
            filters.append(T_MEMBER.partner_uid == page_param.filters["partner_uid"])
    # [ E ] search filter end


    sql = (
        db.query(
             T_MEMBER.uid
            ,T_MEMBER.site_id
            ,T_MEMBER.login_id
            ,T_MEMBER.user_id
            ,T_MEMBER.partner_uid
            ,T_MEMBER.partner_id
            ,T_MEMBER.prefix
            ,T_MEMBER.user_name
            ,T_MEMBER.mobile
            ,T_MEMBER.email
            ,T_MEMBER.aff_uid
            ,T_MEMBER.user_ci
            ,func.date_format(T_MEMBER.create_at, '%Y-%m-%d').label('create_at')
            ,func.date_format(T_MEMBER.update_at, '%Y-%m-%d %T').label('update_at')
            ,func.date_format(T_MEMBER.delete_at, '%Y-%m-%d %T').label('delete_at')
            ,T_MEMBER_INFO.serve
            ,T_MEMBER_INFO.is_pw_reset
            ,T_MEMBER_INFO.is_login
            ,T_MEMBER_INFO.is_point
            ,T_MEMBER_INFO.post
            ,T_MEMBER_INFO.addr
            ,T_MEMBER_INFO.addr_detail
            ,T_MEMBER_INFO.state
            ,T_MEMBER_INFO.depart
            ,partner_stmt.c.company_name
            ,partner_stmt.c.mall_name
            ,partner_stmt.c.partner_code
        )
        .join(T_MEMBER_INFO,T_MEMBER_INFO.user_id == T_MEMBER.user_id)
        .join(
            partner_stmt, 
            T_MEMBER.partner_uid == partner_stmt.c.partner_uid,
            isouter = True 
        )
        .filter(*filters)
        .order_by(T_MEMBER.uid.desc())
        .offset((page_param.page-1)*page_param.page_view_size)
        .limit(page_param.page_view_size)
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    # [ S ] 페이징 처리
    page_param.page_total = (
        db.query(T_MEMBER)
        .join(T_MEMBER_INFO,T_MEMBER_INFO.user_id == T_MEMBER.user_id)
        .join(
            partner_stmt, 
            T_MEMBER.partner_uid == partner_stmt.c.partner_uid,
            isouter = True 
        )
        .filter(*filters)
        .count()
    )
    page_param.page_last = math.ceil(
        page_param.page_total / page_param.page_view_size)
    page_param.page_size = len(rows)  # 현재 페이지에 검색된 수
    # [ E ] 페이징 처리

    jsondata = {}
    jsondata.update(page_param)
    jsondata.update({"list": rows})

    return jsondata

# 회원 상세 
def read(request: Request, uid: int):
    request.state.inspect = frame()
    db = request.state.db

    partner_stmt = (
        db.query(
            T_PARTNER.mall_name
            ,T_PARTNER.partner_code
            ,T_PARTNER.uid.label("partner_uid")
        )
        .subquery()
    )

    sql = ( 
        db.query(
             T_MEMBER.uid
            ,T_MEMBER.site_id
            ,T_MEMBER.login_id
            ,T_MEMBER.user_id
            ,T_MEMBER.partner_uid
            ,T_MEMBER.partner_id
            ,T_MEMBER.prefix
            ,T_MEMBER.user_name
            ,T_MEMBER.mobile
            ,T_MEMBER.email
            ,T_MEMBER.aff_uid
            ,T_MEMBER.user_ci
            ,func.date_format(T_MEMBER.create_at, '%Y-%m-%d %T').label('create_at')
            ,func.date_format(T_MEMBER.update_at, '%Y-%m-%d %T').label('update_at')
            ,func.date_format(T_MEMBER.delete_at, '%Y-%m-%d %T').label('delete_at')
            ,T_MEMBER_INFO.serve
            ,T_MEMBER_INFO.is_pw_reset
            ,T_MEMBER_INFO.is_login
            ,T_MEMBER_INFO.is_point
            ,T_MEMBER_INFO.state
            ,T_MEMBER_INFO.birth
            ,T_MEMBER_INFO.gender
            ,T_MEMBER_INFO.anniversary
            ,T_MEMBER_INFO.emp_no
            ,T_MEMBER_INFO.position
            ,T_MEMBER_INFO.position2
            ,T_MEMBER_INFO.join_com
            ,T_MEMBER_INFO.post
            ,T_MEMBER_INFO.addr
            ,T_MEMBER_INFO.addr_detail
            ,T_MEMBER_INFO.depart
            ,partner_stmt.c.mall_name
            ,partner_stmt.c.partner_code
        )
        .join(T_MEMBER_INFO,T_MEMBER_INFO.user_id == T_MEMBER.user_id)
        .join(
            partner_stmt, 
            T_MEMBER.partner_uid == partner_stmt.c.partner_uid,
            isouter = True 
        )
        .filter(
            T_MEMBER.uid == uid
            ,T_MEMBER.delete_at == None
        )
    )
    format_sql(sql)
    return sql.first()

# 회원 수정
def update(request: Request, memberInput: MemberInput):
    request.state.inspect = frame()
    db = request.state.db 
    user = request.state.user

    member_res = db.query(T_MEMBER).filter(T_MEMBER.user_id == memberInput.user_id).first()
    member_info_res = db.query(T_MEMBER_INFO).filter(T_MEMBER_INFO.user_id == memberInput.user_id).first()

    if member_res is None :
        return ex.ReturnOK(404, "문제가 발생되었습니다.", request)
    if member_info_res is None :
        return ex.ReturnOK(405, "문제가 발생되었습니다.", request)

    if memberInput.user_name is not None and member_res.user_name != memberInput.user_name:
        create_log(request, member_res.uid, "T_MEMBER", "user_name", "이름", member_res.user_name, memberInput.user_name, user.user_id)
        request.state.inspect = frame()

        member_res.user_name = memberInput.user_name
        member_res.update_at = util.getNow()
    
    if memberInput.mobile is not None and member_res.mobile != memberInput.mobile:
        create_log(request, member_res.uid, "T_MEMBER", "mobile", "휴대전화", member_res.mobile, memberInput.mobile, user.user_id)
        request.state.inspect = frame()

        member_res.mobile = memberInput.mobile
        member_res.update_at = util.getNow()

    if memberInput.email is not None and member_res.email != memberInput.email:
        create_log(request, member_res.uid, "T_MEMBER", "email", "이메일", member_res.email, memberInput.email, user.user_id)
        request.state.inspect = frame()

        member_res.email = memberInput.email
        member_res.update_at = util.getNow()

    if memberInput.state is not None and member_info_res.state != memberInput.state:
        create_log(request, member_info_res.uid, "T_MEMBER_INFO", "state", "회원상태", member_info_res.state, memberInput.state, user.user_id)
        request.state.inspect = frame()

        member_info_res.state = memberInput.state
        member_info_res.update_at = util.getNow()

    if memberInput.gender is not None and member_info_res.gender != memberInput.gender:
        create_log(request, member_info_res.uid, "T_MEMBER_INFO", "gender", "성별", member_info_res.gender, memberInput.gender, user.user_id)
        request.state.inspect = frame()
        
        member_info_res.gender = memberInput.gender
        member_info_res.update_at = util.getNow()

    if memberInput.is_login is not None and member_info_res.is_login != memberInput.is_login:
        create_log(request, member_info_res.uid, "T_MEMBER_INFO", "is_login", "복지몰로그인", member_info_res.is_login, memberInput.is_login, user.user_id)
        request.state.inspect = frame()
        
        member_info_res.is_login = memberInput.is_login
        member_info_res.update_at = util.getNow()

    if memberInput.is_point is not None and member_info_res.is_point != memberInput.is_point:
        create_log(request, member_info_res.uid, "T_MEMBER_INFO", "is_point", "포인트사용", member_info_res.is_point, memberInput.is_point, user.user_id)
        request.state.inspect = frame()
        
        member_info_res.is_point = memberInput.is_point
        member_info_res.update_at = util.getNow()

    if memberInput.post is not None and member_info_res.post != memberInput.post:
        create_log(request, memberInput.uid, "T_MEMBER_INFO", "post", "우편번호", member_info_res.post, memberInput.post, user.user_id)
        request.state.inspect = frame()
        member_info_res.post = memberInput.post
        member_info_res.update_at = util.getNow()

    if memberInput.addr is not None and member_info_res.addr != memberInput.addr:
        create_log(request, memberInput.uid, "T_MEMBER_INFO", "addr", "주소", member_info_res.addr, memberInput.addr, user.user_id)
        request.state.inspect = frame()
        member_info_res.addr = memberInput.addr
        member_info_res.update_at = util.getNow()

    if memberInput.addr_detail is not None and member_info_res.addr_detail != memberInput.addr_detail:
        create_log(request, memberInput.uid, "T_MEMBER_INFO", "addr_detail", "주소상세", member_info_res.addr_detail, memberInput.addr_detail, user.user_id)
        request.state.inspect = frame()
        member_info_res.addr_detail = memberInput.addr_detail
        member_info_res.update_at = util.getNow()

    if memberInput.birth is not None and member_info_res.birth != memberInput.birth:
        create_log(request, memberInput.uid, "T_MEMBER_INFO", "birth", "생년월일", member_info_res.birth, memberInput.birth, user.user_id)
        request.state.inspect = frame()
        member_info_res.birth = memberInput.birth
        member_info_res.update_at = util.getNow()

    if memberInput.anniversary is not None and member_info_res.anniversary != memberInput.anniversary:
        create_log(request, memberInput.uid, "T_MEMBER_INFO", "anniversary", "기념일", member_info_res.anniversary, memberInput.anniversary, user.user_id)
        request.state.inspect = frame()
        member_info_res.anniversary = memberInput.anniversary
        member_info_res.update_at = util.getNow()

    if memberInput.serve is not None and member_info_res.serve != memberInput.serve:
        create_log(request, memberInput.uid, "T_MEMBER_INFO", "serve", "재직여부", member_info_res.serve, memberInput.serve, user.user_id)
        request.state.inspect = frame()
        member_info_res.serve = memberInput.serve
        member_info_res.update_at = util.getNow()

    if memberInput.emp_no is not None and member_info_res.emp_no != memberInput.emp_no:
        create_log(request, memberInput.uid, "T_MEMBER_INFO", "emp_no", "사번", member_info_res.emp_no, memberInput.emp_no, user.user_id)
        request.state.inspect = frame()
        member_info_res.emp_no = memberInput.emp_no
        member_info_res.update_at = util.getNow()

    if memberInput.depart is not None and member_info_res.depart != memberInput.depart:
        create_log(request, memberInput.uid, "T_MEMBER_INFO", "depart", "부서", member_info_res.depart, memberInput.depart, user.user_id)
        request.state.inspect = frame()
        member_info_res.depart = memberInput.depart
        member_info_res.update_at = util.getNow()

    if memberInput.join_com is not None and member_info_res.join_com != memberInput.join_com:
        create_log(request, memberInput.uid, "T_MEMBER_INFO", "join_com", "입사일", member_info_res.join_com, memberInput.join_com, user.user_id)
        request.state.inspect = frame()
        member_info_res.join_com = memberInput.join_com
        member_info_res.update_at = util.getNow()

    if memberInput.position is not None and member_info_res.position != memberInput.position:
        create_log(request, memberInput.uid, "T_MEMBER_INFO", "position", "직급", member_info_res.position, memberInput.position, user.user_id)
        request.state.inspect = frame()
        member_info_res.position = memberInput.position
        member_info_res.update_at = util.getNow()

    if memberInput.position2 is not None and member_info_res.position2 != memberInput.position2:
        create_log(request, memberInput.uid, "T_MEMBER_INFO", "position2", "직책", member_info_res.position2, memberInput.position2, user.user_id)
        request.state.inspect = frame()
        member_info_res.position2 = memberInput.position2
        member_info_res.update_at = util.getNow()

    return {"member_res":member_res, "member_info_res": member_info_res}


# 파트너리스트
def partner_list(request: Request, partnerSearchInput: PartnerSearchInput):
    request.state.inspect = frame()
    db = request.state.db

    filters = []
    filters.append(getattr(T_PARTNER, "delete_at") == None)
    filters.append(
        T_PARTNER.partner_id.like("%"+partnerSearchInput.partner_name+"%") 
        | T_PARTNER.company_name.like("%"+partnerSearchInput.partner_name+"%")
        | T_PARTNER.mall_name.like("%"+partnerSearchInput.partner_name+"%")
    )

    sql = (
        db.query(
             T_PARTNER.uid
            ,T_PARTNER.partner_id
            ,T_PARTNER.company_name
            ,T_PARTNER.mall_name
        )
        .filter(*filters)
        .order_by(T_PARTNER.uid.desc())
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    jsondata = {}
    jsondata.update({"list": rows})

    return jsondata

# ---------------------- [ S ] APP list(device)
# APP list 
def app_list(request: Request, page_param: PPage_param):
    request.state.inspect = frame()
    db = request.state.db


    partner_stmt = (
        db.query(
            T_PARTNER.mall_name
            ,T_PARTNER.company_name
            ,T_PARTNER.partner_id
            ,T_PARTNER.uid.label("partner_uid")
        )
        .subquery()
    )

    filters = []
    filters.append(getattr(T_APP_DEVICE, "delete_at") == None)
    # [ S ] search filter start
    if page_param.filters :
        if page_param.filters["skeyword"] :
            if page_param.filters["skeyword_type"] != "" :
                if page_param.filters["skeyword_type"] == "mall_name" :
                    filters.append(partner_stmt.c.mall_name.like("%"+page_param.filters["skeyword"]+"%"))
                if page_param.filters["skeyword_type"] == "company_name" :
                    filters.append(partner_stmt.c.company_name.like("%"+page_param.filters["skeyword"]+"%"))
                elif page_param.filters["skeyword_type"] == "partner_id" :
                    filters.append(partner_stmt.c.partner_id.like("%"+page_param.filters["skeyword"]+"%"))
                else :
                    filters.append(getattr(T_APP_DEVICE, page_param.filters["skeyword_type"]).like("%"+page_param.filters["skeyword"]   +"%"))
            else : 
                filters.append(
                    T_APP_DEVICE.user_id.like("%"+page_param.filters["skeyword"]+"%") 
                    | partner_stmt.c.mall_name.like("%"+page_param.filters["skeyword"]+"%") 
                    | partner_stmt.c.company_name.like("%"+page_param.filters["skeyword"]+"%") 
                    | partner_stmt.c.partner_id.like("%"+page_param.filters["skeyword"]+"%") 
                )

        if page_param.filters["create_at"]["startDate"] and page_param.filters["create_at"]["endDate"] :
            filters.append(
                and_(
                    T_APP_DEVICE.create_at >= page_param.filters["create_at"]["startDate"]
                    ,T_APP_DEVICE.create_at <= page_param.filters["create_at"]["endDate"] + " 23:59:59"
                )
            )
        if page_param.filters["update_at"]["startDate"] and page_param.filters["update_at"]["endDate"] :
            filters.append(
                and_(
                    T_APP_DEVICE.update_at >= page_param.filters["update_at"]["startDate"]
                    ,T_APP_DEVICE.update_at <= page_param.filters["update_at"]["endDate"] + " 23:59:59"
                )
            )

        if page_param.filters["is_sms"] :
            filters.append(T_APP_DEVICE.is_sms == page_param.filters["is_sms"])
        if page_param.filters["is_mailing"] :
            filters.append(T_APP_DEVICE.is_mailing == page_param.filters["is_mailing"])
        if page_param.filters["is_push"] :
            filters.append(T_APP_DEVICE.is_push == page_param.filters["is_push"])

        if page_param.filters["partner_uid"] > 0 :
            filters.append(partner_stmt.c.partner_uid == page_param.filters["partner_uid"])
    # [ E ] search filter end

    sql = (
        db.query(
             T_APP_DEVICE.uid
            ,T_APP_DEVICE.user_id
            ,T_APP_DEVICE.partner_id
            ,T_APP_DEVICE.bars_uuid
            ,T_APP_DEVICE.device_os
            ,T_APP_DEVICE.gender
            ,T_APP_DEVICE.birth
            ,T_APP_DEVICE.mobile
            ,T_APP_DEVICE.email
            ,T_APP_DEVICE.is_sms
            ,T_APP_DEVICE.is_mailing
            ,T_APP_DEVICE.is_push
            ,func.date_format(T_APP_DEVICE.create_at, '%Y-%m-%d').label('create_at')
            ,func.date_format(T_APP_DEVICE.update_at, '%Y-%m-%d').label('update_at')
            ,func.date_format(T_APP_DEVICE.delete_at, '%Y-%m-%d').label('delete_at')
            ,partner_stmt.c.company_name
            ,partner_stmt.c.mall_name
        ) 
        .join(
            partner_stmt, 
            T_APP_DEVICE.partner_id == partner_stmt.c.partner_id,
            isouter = True 
        )
        .filter(*filters)
        .order_by(T_APP_DEVICE.uid.desc())
        .offset((page_param.page-1)*page_param.page_view_size)
        .limit(page_param.page_view_size)
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    # [ S ] 페이징 처리
    page_param.page_total = (
        db.query(T_APP_DEVICE)
        .filter(*filters)
        .count()
    )
    page_param.page_last = math.ceil(
        page_param.page_total / page_param.page_view_size)
    page_param.page_size = len(rows)  # 현재 페이지에 검색된 수
    # [ E ] 페이징 처리

    jsondata = {}
    jsondata.update(page_param)
    jsondata.update({"list": rows})

    return jsondata