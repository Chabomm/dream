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
from app.deps import auth
from app.models.member import *
from app.models.partner import *
from app.models.manager import *
from app.schemas.admin.entry.build import *
# from app.service.log_service import *

from app.models.scm.entry.build import *
from app.models.scm.entry.counsel import *
from app.service import log_scm_service


# 구축 신청 list 
def build_list(request: Request, page_param: PPage_param):
    request.state.inspect = frame()
    db_scm = request.state.db_scm

    filters = []
    filters.append(getattr(T_DREAM_BUILD, "delete_at") == None)

    # [ S ] search filter start
    if page_param.filters :
        if page_param.filters["skeyword"] :
            if page_param.filters["skeyword_type"] != "" :
                filters.append(getattr(T_DREAM_BUILD, page_param.filters["skeyword_type"]).like("%"+page_param.filters["skeyword"]+"%"))
            else : 
                filters.append(
                    T_DREAM_BUILD.company_name.like("%"+page_param.filters["skeyword"]+"%") 
                    | T_DREAM_BUILD.mall_name.like("%"+page_param.filters["skeyword"]+"%")
                )

        if page_param.filters["create_at"]["startDate"] and page_param.filters["create_at"]["endDate"] :
            filters.append(
                and_(
                    T_DREAM_BUILD.create_at >= page_param.filters["create_at"]["startDate"]
                    ,T_DREAM_BUILD.create_at <= page_param.filters["create_at"]["endDate"] + " 23:59:59"
                )
            )

        if page_param.filters["state"] :
            filters.append(T_DREAM_BUILD.state.in_(page_param.filters["state"]))
    # [ E ] search filter end


    sql = (
        db_scm.query(
             T_DREAM_BUILD.uid
            ,T_DREAM_BUILD.company_name
            ,T_DREAM_BUILD.staff_name
            ,T_DREAM_BUILD.staff_mobile
            ,T_DREAM_BUILD.staff_email
            ,T_DREAM_BUILD.mall_name
            ,T_DREAM_BUILD.state
            ,T_DREAM_BUILD.counsel_uid
            ,func.date_format(T_DREAM_BUILD.create_at, '%Y-%m-%d %T').label('create_at')
            ,func.date_format(T_DREAM_BUILD.update_at, '%Y-%m-%d %T').label('update_at')
        )
        .filter(*filters)
        .order_by(T_DREAM_BUILD.uid.desc())
        .offset((page_param.page-1)*page_param.page_view_size)
        .limit(page_param.page_view_size)
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    # [ S ] 페이징 처리
    page_param.page_total = (
        db_scm.query(T_DREAM_BUILD)
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

# 구축정보 상세보기
def build_read(request: Request, uid: int):
    request.state.inspect = frame()
    db_scm = request.state.db_scm

    sql = ( 
        db_scm.query(
             T_DREAM_BUILD.uid
            ,T_DREAM_BUILD.company_name
            ,T_DREAM_BUILD.ceo_name
            ,T_DREAM_BUILD.staff_name
            ,T_DREAM_BUILD.staff_dept
            ,T_DREAM_BUILD.staff_position
            ,T_DREAM_BUILD.staff_position2
            ,T_DREAM_BUILD.staff_mobile
            ,T_DREAM_BUILD.staff_email
            ,T_DREAM_BUILD.account_email
            ,T_DREAM_BUILD.post
            ,T_DREAM_BUILD.addr
            ,T_DREAM_BUILD.addr_detail
            ,T_DREAM_BUILD.company_hp
            ,T_DREAM_BUILD.biz_kind
            ,T_DREAM_BUILD.biz_item
            ,T_DREAM_BUILD.biz_no
            ,T_DREAM_BUILD.biz_service
            ,T_DREAM_BUILD.mall_name
            ,T_DREAM_BUILD.host
            ,T_DREAM_BUILD.file_biz_no
            ,T_DREAM_BUILD.file_bank
            ,T_DREAM_BUILD.file_logo
            ,T_DREAM_BUILD.file_mall_logo
            ,T_DREAM_BUILD.state
            ,T_DREAM_BUILD.counsel_uid
            ,func.date_format(T_DREAM_BUILD.create_at, '%Y-%m-%d %T').label('create_at')
            ,func.date_format(T_DREAM_BUILD.update_at, '%Y-%m-%d %T').label('update_at')
        )
        .filter(
            T_DREAM_BUILD.uid == uid
            ,T_DREAM_BUILD.delete_at == None
        )
    )
    format_sql(sql)
    res = sql.first()
    if res is not None:
        res = dict(zip(res.keys(), res))
    
    jsondata = {}
    jsondata.update(res)

    return jsondata

# 구축신청 - 등록
def build_create(request: Request, dreamBuild: DreamBuild):
    request.state.inspect = frame()
    db_scm = request.state.db_scm
    user = request.state.user

    db_item = T_DREAM_BUILD (
         company_name = dreamBuild.company_name
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
        ,state = "100"
        ,counsel_uid = dreamBuild.counsel_uid
    )
    db_scm.add(db_item)
    db_scm.flush()

    log_scm_service.create_log(request, db_item.uid, "T_DREAM_BUILD", "INSERT", "파트너 구축 등록", 0, db_item.uid, request.state.user_ip)
    request.state.inspect = frame()

    # [ S ] T_DREAM_COUNSEL state 변경
    res = db_scm.query(T_DREAM_COUNSEL).filter(T_DREAM_COUNSEL.uid == dreamBuild.counsel_uid).first()

    if res.state != "502":
        log_scm_service.create_log(request, res.uid, "T_DREAM_COUNSEL", "state", "진행상태", res.state, "502", request.state.user_ip)
        request.state.inspect = frame()
        res.state = "502"

    res.update_at = util.getNow()

    if res is None :
        raise ex.NotFoundUser
    # [ E ] T_DREAM_COUNSEL state 변경

    return db_item

# 구축신청 - 수정
def build_update(request: Request, dreamBuild: DreamBuild):
    request.state.inspect = frame()
    db_scm = request.state.db_scm 
    user = request.state.user

    res_build = (db_scm.query(T_DREAM_BUILD).filter(T_DREAM_BUILD.counsel_uid == dreamBuild.counsel_uid).first())

    if res_build is None :
        raise ex.NotFoundUser
    
    if dreamBuild.memo is not None and dreamBuild.memo != "" : 
        # insert
        log_scm_service.create_memo(request, res_build.uid, "T_DREAM_BUILD", dreamBuild.memo, user.user_id, user.token_name, 'ADMIN', None)
        request.state.inspect = frame()

    if dreamBuild.company_name is not None and res_build.company_name != dreamBuild.company_name : 
        log_scm_service.create_log(request, res_build.uid, "T_DREAM_BUILD", "company_name", "기업명 수정", res_build.company_name, dreamBuild.company_name, user.user_id)
        request.state.inspect = frame()
        res_build.company_name = dreamBuild.company_name

    if dreamBuild.company_name is not None and res_build.company_name != dreamBuild.company_name : 
        log_scm_service.create_log(request, res_build.uid, "T_DREAM_BUILD", "company_name", "기업명 수정", res_build.company_name, dreamBuild.company_name, user.user_id)
        request.state.inspect = frame()
        res_build.company_name = dreamBuild.company_name

    if dreamBuild.staff_name is not None and res_build.staff_name != dreamBuild.staff_name : 
        log_scm_service.create_log(request, res_build.uid, "T_DREAM_BUILD", "staff_name", "담당자명 수정", res_build.staff_name, dreamBuild.staff_name, user.user_id)
        request.state.inspect = frame()
        res_build.staff_name = dreamBuild.staff_name

    if dreamBuild.staff_dept is not None and res_build.staff_dept != dreamBuild.staff_dept : 
        log_scm_service.create_log(request, res_build.uid, "T_DREAM_BUILD", "staff_dept", "담당자 부서 수정", res_build.staff_dept, dreamBuild.staff_dept, user.user_id)
        request.state.inspect = frame()
        res_build.staff_dept = dreamBuild.staff_dept

    if dreamBuild.staff_position is not None and res_build.staff_position != dreamBuild.staff_position : 
        log_scm_service.create_log(request, res_build.uid, "T_DREAM_BUILD", "staff_position", "담당자 직급 수정", res_build.staff_position, dreamBuild.staff_position, user.user_id)
        request.state.inspect = frame()
        res_build.staff_position = dreamBuild.staff_position

    if dreamBuild.staff_position2 is not None and res_build.staff_position2 != dreamBuild.staff_position2 : 
        log_scm_service.create_log(request, res_build.uid, "T_DREAM_BUILD", "staff_position2", "담당자 직책 수정", res_build.staff_position2, dreamBuild.staff_position2, user.user_id)
        request.state.inspect = frame()
        res_build.staff_position2 = dreamBuild.staff_position2

    if dreamBuild.staff_mobile is not None and res_build.staff_mobile != dreamBuild.staff_mobile : 
        log_scm_service.create_log(request, res_build.uid, "T_DREAM_BUILD", "staff_mobile", "담당자 연락처 수정", res_build.staff_mobile, dreamBuild.staff_mobile, user.user_id)
        request.state.inspect = frame()
        res_build.staff_mobile = dreamBuild.staff_mobile

    if dreamBuild.staff_email is not None and res_build.staff_email != dreamBuild.staff_email : 
        log_scm_service.create_log(request, res_build.uid, "T_DREAM_BUILD", "staff_email", "담당자 이메일 수정", res_build.staff_email, dreamBuild.staff_email, user.user_id)
        request.state.inspect = frame()
        res_build.staff_email = dreamBuild.staff_email

    if dreamBuild.ceo_name is not None and res_build.ceo_name != dreamBuild.ceo_name : 
        log_scm_service.create_log(request, res_build.uid, "T_DREAM_BUILD", "ceo_name", "대표자 성함", res_build.ceo_name, dreamBuild.ceo_name, user.user_id)
        request.state.inspect = frame()
        res_build.ceo_name = dreamBuild.ceo_name

    if dreamBuild.account_email is not None and res_build.account_email != dreamBuild.account_email : 
        log_scm_service.create_log(request, res_build.uid, "T_DREAM_BUILD", "account_email", "정산메일", res_build.account_email, dreamBuild.account_email, user.user_id)
        request.state.inspect = frame()
        res_build.account_email = dreamBuild.account_email

    if dreamBuild.post is not None and res_build.post != dreamBuild.post : 
        log_scm_service.create_log(request, res_build.uid, "T_DREAM_BUILD", "post", "우편번호", res_build.post, dreamBuild.post, user.user_id)
        request.state.inspect = frame()
        res_build.post = dreamBuild.post

    if dreamBuild.addr is not None and res_build.addr != dreamBuild.addr : 
        log_scm_service.create_log(request, res_build.uid, "T_DREAM_BUILD", "addr", "주소", res_build.addr, dreamBuild.addr, user.user_id)
        request.state.inspect = frame()
        res_build.addr = dreamBuild.addr

    if dreamBuild.addr_detail is not None and res_build.addr_detail != dreamBuild.addr_detail : 
        log_scm_service.create_log(request, res_build.uid, "T_DREAM_BUILD", "addr_detail", "주소상세", res_build.addr_detail, dreamBuild.addr_detail, user.user_id)
        request.state.inspect = frame()
        res_build.addr_detail = dreamBuild.addr_detail

    if dreamBuild.company_hp is not None and res_build.company_hp != dreamBuild.company_hp : 
        log_scm_service.create_log(request, res_build.uid, "T_DREAM_BUILD", "company_hp", "대표번호", res_build.company_hp, dreamBuild.company_hp, user.user_id)
        request.state.inspect = frame()
        res_build.company_hp = dreamBuild.company_hp

    if dreamBuild.biz_kind is not None and res_build.biz_kind != dreamBuild.biz_kind : 
        log_scm_service.create_log(request, res_build.uid, "T_DREAM_BUILD", "biz_kind", "사업자 분류", res_build.biz_kind, dreamBuild.biz_kind, user.user_id)
        request.state.inspect = frame()
        res_build.biz_kind = dreamBuild.biz_kind

    if dreamBuild.biz_item is not None and res_build.biz_item != dreamBuild.biz_item : 
        log_scm_service.create_log(request, res_build.uid, "T_DREAM_BUILD", "biz_item", "업종", res_build.biz_item, dreamBuild.biz_item, user.user_id)
        request.state.inspect = frame()
        res_build.biz_item = dreamBuild.biz_item

    if dreamBuild.biz_no is not None and res_build.biz_no != dreamBuild.biz_no : 
        log_scm_service.create_log(request, res_build.uid, "T_DREAM_BUILD", "biz_no", "사업자등록번호", res_build.biz_no, dreamBuild.biz_no, user.user_id)
        request.state.inspect = frame()
        res_build.biz_no = dreamBuild.biz_no

    if dreamBuild.mall_name is not None and res_build.mall_name != dreamBuild.mall_name : 
        log_scm_service.create_log(request, res_build.uid, "T_DREAM_BUILD", "mall_name", "복지몰명", res_build.mall_name, dreamBuild.mall_name, user.user_id)
        request.state.inspect = frame()
        res_build.mall_name = dreamBuild.mall_name

    if dreamBuild.mall_name is not None and res_build.mall_name != dreamBuild.mall_name : 
        log_scm_service.create_log(request, res_build.uid, "T_DREAM_BUILD", "mall_name", "복지몰명", res_build.mall_name, dreamBuild.mall_name, user.user_id)
        request.state.inspect = frame()
        res_build.mall_name = dreamBuild.mall_name

    if dreamBuild.host is not None and res_build.host != dreamBuild.host : 
        log_scm_service.create_log(request, res_build.uid, "T_DREAM_BUILD", "host", "도메인 및 대표관리자 아이디", res_build.host, dreamBuild.host, user.user_id)
        request.state.inspect = frame()
        res_build.host = dreamBuild.host

    if dreamBuild.file_biz_no is not None and res_build.file_biz_no != dreamBuild.file_biz_no : 
        log_scm_service.create_log(request, res_build.uid, "T_DREAM_BUILD", "file_biz_no", "사업자등록증", res_build.file_biz_no, dreamBuild.file_biz_no, user.user_id)
        request.state.inspect = frame()
        res_build.file_biz_no = dreamBuild.file_biz_no

    if dreamBuild.file_bank is not None and res_build.file_bank != dreamBuild.file_bank : 
        log_scm_service.create_log(request, res_build.uid, "T_DREAM_BUILD", "file_bank", "통장사본", res_build.file_bank, dreamBuild.file_bank, user.user_id)
        request.state.inspect = frame()
        res_build.file_bank = dreamBuild.file_bank

    if dreamBuild.file_logo is not None and res_build.file_logo != dreamBuild.file_logo : 
        log_scm_service.create_log(request, res_build.uid, "T_DREAM_BUILD", "file_logo", "회사로고", res_build.file_logo, dreamBuild.file_logo, user.user_id)
        request.state.inspect = frame()
        res_build.file_logo = dreamBuild.file_logo

    if dreamBuild.file_mall_logo is not None and res_build.file_mall_logo != dreamBuild.file_mall_logo : 
        log_scm_service.create_log(request, res_build.uid, "T_DREAM_BUILD", "file_mall_logo", "복지몰로고", res_build.file_mall_logo, dreamBuild.file_mall_logo, user.user_id)
        request.state.inspect = frame()
        res_build.file_mall_logo = dreamBuild.file_mall_logo

    if dreamBuild.state is not None and res_build.state != dreamBuild.state : 
        log_scm_service.create_log(request, res_build.uid, "T_DREAM_BUILD", "state", "상태", res_build.state, dreamBuild.state, user.user_id)
        request.state.inspect = frame()
        res_build.state = dreamBuild.state

    res_build.update_at = util.getNow()

    return res_build

# 구축 정보 - DELETE (이미 있는 신청서 삭제) 
def build_delete(request: Request, uid: int):
    request.state.inspect = frame()
    db_scm = request.state.db_scm
    user = request.state.user

    db_scm.query(T_DREAM_BUILD).filter(T_DREAM_BUILD.counsel_uid == uid).delete()

    log_scm_service.create_log(request, uid, "T_DREAM_BUILD", "DELETE", "구축정보 삭제", uid, '', user.user_id)
    request.state.inspect = frame()

    return





def com_item_list(request: Request) :
    return [
        {
            "key": "A",
            "text" : "농업, 임업 및 어업(01~03)"
        },
        {
            "key": "B",
            "text" : "광업(05~08)"
        },
        {
            "key": "C",
            "text" : "제조업(10~34)"
        },
        {
            "key": "D",
            "text" : "전기, 가스, 증기 및 공기 조절 "
        },
        {
            "key": "E",
            "text" : "수도, 하수 및 폐기물 처리, 원"
        },
        {
            "key": "F",
            "text" : "건설업(41~42)"
        },
        {
            "key": "G",
            "text" : "도매 및 소매업(45~47)"
        },
        {
            "key": "H",
            "text" : "운수 및 창고업(49~52)"
        },
        {
            "key": "I",
            "text" : "숙박 및 음식점업(55~56)"
        },
        {
            "key": "J",
            "text" : "정보통신업(58~63)"
        },
        {
            "key": "K",
            "text" : "금융 및 보험업(64~66)"
        },
        {
            "key": "L",
            "text" : "부동산업(68)"
        },
        {
            "key": "M",
            "text" : "전문, 과학 및 기술 서비스업(70)"
        },
        {
            "key": "N",
            "text" : "사업시설 관리, 사업 지원 및 임대 서비스업(74~76)"
        },
        {
            "key": "O",
            "text" : "공공 행정, 국방 및 사회보장 행정(84)"
        },
        {
            "key": "P",
            "text" : "교육 서비스업(85)"
        },
        {
            "key": "Q",
            "text" : "보건업 및 사회복지 서비스업(86~87)"
        },
        {
            "key": "R",
            "text" : "예술, 스포츠 및 여가관련 서비스업(90~91)"
        },
        {
            "key": "S",
            "text" : "협회 및 단체, 수리 및 기타 개인 서비스업(94~96)"
        },
        {
            "key": "T",
            "text" : "가구 내 고용활동 및 달리 분류되지 않은 자가 소비 생산활동(97~98)"
        },
    ]



