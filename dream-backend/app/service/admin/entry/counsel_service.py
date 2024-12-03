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
# from app.models.dream import *
from app.models.member import *
from app.models.partner import *
from app.models.manager import *
from app.schemas.admin.entry.counsel import *

from app.schemas.schema import *
from app.models.scm.entry.counsel import *
from app.service import log_scm_service

# 상담 신청 list 
def counsel_list(request: Request, page_param: PPage_param):
    request.state.inspect = frame()
    db_scm = request.state.db_scm

    filters = []
    filters.append(getattr(T_DREAM_COUNSEL, "delete_at") == None)

    # [ S ] search filter start
    if page_param.filters :
        if page_param.filters["skeyword"] :
            if page_param.filters["skeyword_type"] != "" :
                filters.append(getattr(T_DREAM_COUNSEL, page_param.filters["skeyword_type"]).like("%"+page_param.filters["skeyword"]+"%"))
            else : 
                filters.append(
                    T_DREAM_COUNSEL.company_name.like("%"+page_param.filters["skeyword"]+"%") 
                    | T_DREAM_COUNSEL.staff_name.like("%"+page_param.filters["skeyword"]+"%")
                )

        if page_param.filters["create_at"]["startDate"] and page_param.filters["create_at"]["endDate"] :
            filters.append(
                and_(
                    T_DREAM_COUNSEL.create_at >= page_param.filters["create_at"]["startDate"]
                    ,T_DREAM_COUNSEL.create_at <= page_param.filters["create_at"]["endDate"] + " 23:59:59"
                )
            )

        if page_param.filters["state"] :
            filters.append(T_DREAM_COUNSEL.state.in_(page_param.filters["state"]))
    # [ E ] search filter end

    sql = (
        db_scm.query(
             T_DREAM_COUNSEL.uid
            ,T_DREAM_COUNSEL.company_name
            ,T_DREAM_COUNSEL.homepage_url
            ,T_DREAM_COUNSEL.staff_count
            ,T_DREAM_COUNSEL.wish_build_at
            ,T_DREAM_COUNSEL.staff_name
            ,T_DREAM_COUNSEL.staff_dept
            ,T_DREAM_COUNSEL.staff_position
            ,T_DREAM_COUNSEL.staff_position2
            ,T_DREAM_COUNSEL.staff_mobile
            ,T_DREAM_COUNSEL.staff_email
            ,T_DREAM_COUNSEL.contents
            ,T_DREAM_COUNSEL.state
            ,func.date_format(T_DREAM_COUNSEL.create_at, '%Y-%m-%d %T').label('create_at')
            ,func.date_format(T_DREAM_COUNSEL.update_at, '%Y-%m-%d %T').label('update_at')
        )
        .filter(*filters)
        .order_by(T_DREAM_COUNSEL.uid.desc())
        .offset((page_param.page-1)*page_param.page_view_size)
        .limit(page_param.page_view_size)
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    # [ S ] 페이징 처리
    page_param.page_total = (
        db_scm.query(T_DREAM_COUNSEL)
        .filter(*filters)
        .count()
    )
    page_param.page_last = math.ceil(page_param.page_total / page_param.page_view_size)
    page_param.page_size = len(rows)  # 현재 페이지에 검색된 수
    # [ E ] 페이징 처리

    jsondata = {}
    jsondata.update({"params":page_param})
    jsondata.update({"list": rows})

    return jsondata


# 상담정보 상세보기
def consel_read(request: Request, uid: int):
    request.state.inspect = frame()
    db_scm = request.state.db_scm

    sql = ( 
        db_scm.query(
             T_DREAM_COUNSEL.uid
            ,T_DREAM_COUNSEL.company_name
            ,T_DREAM_COUNSEL.homepage_url
            ,T_DREAM_COUNSEL.staff_count
            ,func.date_format(T_DREAM_COUNSEL.wish_build_at, '%Y-%m-%d').label('wish_build_at')
            ,T_DREAM_COUNSEL.staff_name
            ,T_DREAM_COUNSEL.staff_dept
            ,T_DREAM_COUNSEL.staff_position
            ,T_DREAM_COUNSEL.staff_position2
            ,T_DREAM_COUNSEL.staff_mobile
            ,T_DREAM_COUNSEL.staff_email
            ,T_DREAM_COUNSEL.contents
            ,T_DREAM_COUNSEL.state
            ,func.date_format(T_DREAM_COUNSEL.create_at, '%Y-%m-%d %T').label('create_at')
            ,func.date_format(T_DREAM_COUNSEL.update_at, '%Y-%m-%d %T').label('update_at')
        )
        .filter(
            T_DREAM_COUNSEL.uid == uid
            ,T_DREAM_COUNSEL.delete_at == None
        )
    )
    format_sql(sql)
    return sql.first()


# 상담_등록
def counsel_create(request: Request, dreamCounsel: DreamCounsel):
    request.state.inspect = frame()
    db_scm = request.state.db_scm 
    user = request.state.user

    db_item = T_DREAM_COUNSEL (
         company_name = dreamCounsel.company_name
        ,homepage_url = dreamCounsel.homepage_url
        ,staff_count = dreamCounsel.staff_count
        ,wish_build_at = dreamCounsel.wish_build_at
        ,staff_name = dreamCounsel.staff_name
        ,staff_dept = dreamCounsel.staff_dept
        ,staff_position = dreamCounsel.staff_position
        ,staff_position2 = dreamCounsel.staff_position2
        ,staff_mobile = dreamCounsel.staff_mobile
        ,staff_email = dreamCounsel.staff_email
        ,contents = dreamCounsel.contents
        ,state = dreamCounsel.state
    )
    db_scm.add(db_item)
    db_scm.flush()

    if dreamCounsel.memo is not None and dreamCounsel.memo != "" : 
        # insert
        log_scm_service.create_memo(request, db_item.uid, "T_DREAM_COUNSEL", dreamCounsel.memo, user.user_id, user.token_name, 'ADMIN', None)
        request.state.inspect = frame()
    
    log_scm_service.create_log(request, db_item.uid, "T_DREAM_COUNSEL", "INSERT", "복지드림 상담 수기 등록", 0, db_item.uid, user.user_id)
    request.state.inspect = frame()

    return db_item

# 상담 신청 수정
def counsel_update(request: Request, dreamCounsel: DreamCounsel):
    request.state.inspect = frame()
    db_scm = request.state.db_scm 
    user = request.state.user

    res = db_scm.query(T_DREAM_COUNSEL).filter(T_DREAM_COUNSEL.uid == dreamCounsel.uid).first()

    if res is None :
        raise ex.NotFoundUser

    if dreamCounsel.memo is not None and dreamCounsel.memo != "" : 
        # insert
        log_scm_service.create_memo(request, res.uid, "T_DREAM_COUNSEL", dreamCounsel.memo, user.user_id, user.token_name, 'ADMIN', None)
        request.state.inspect = frame()

    if dreamCounsel.company_name is not None and res.company_name != dreamCounsel.company_name:
        log_scm_service.create_log(request, res.uid, "T_DREAM_COUNSEL", "company_name", "기업명",
                    res.company_name, dreamCounsel.company_name, user.user_id)
        request.state.inspect = frame()
        res.company_name = dreamCounsel.company_name

    if dreamCounsel.homepage_url is not None and res.homepage_url != dreamCounsel.homepage_url:
        log_scm_service.create_log(request, res.uid, "T_DREAM_COUNSEL", "homepage_url", "홈페이지url",
                    res.homepage_url, dreamCounsel.homepage_url, user.user_id)
        request.state.inspect = frame()
        res.homepage_url = dreamCounsel.homepage_url
    
    if dreamCounsel.staff_count is not None and res.staff_count != dreamCounsel.staff_count:
        log_scm_service.create_log(request, res.uid, "T_DREAM_COUNSEL", "staff_count", "직원수",
                    res.staff_count, dreamCounsel.staff_count, user.user_id)
        request.state.inspect = frame()
        res.staff_count = dreamCounsel.staff_count
    
    if dreamCounsel.wish_build_at is not None and res.wish_build_at != dreamCounsel.wish_build_at:
        log_scm_service.create_log(request, res.uid, "T_DREAM_COUNSEL", "wish_build_at", "구축희망일",
                    res.wish_build_at, dreamCounsel.wish_build_at, user.user_id)
        request.state.inspect = frame()
        res.wish_build_at = dreamCounsel.wish_build_at
     
    if dreamCounsel.staff_name is not None and res.staff_name != dreamCounsel.staff_name:
        log_scm_service.create_log(request, res.uid, "T_DREAM_COUNSEL", "staff_name", "담당자명",
                    res.staff_name, dreamCounsel.staff_name, user.user_id)
        request.state.inspect = frame()
        res.staff_name = dreamCounsel.staff_name

    if dreamCounsel.staff_dept is not None and res.staff_dept != dreamCounsel.staff_dept:
        log_scm_service.create_log(request, res.uid, "T_DREAM_COUNSEL", "staff_dept", "담당자 부서",
                    res.staff_dept, dreamCounsel.staff_dept, user.user_id)
        request.state.inspect = frame()
        res.staff_dept = dreamCounsel.staff_dept

    if dreamCounsel.staff_position is not None and res.staff_position != dreamCounsel.staff_position:
        log_scm_service.create_log(request, res.uid, "T_DREAM_COUNSEL", "staff_position", "담당자 직급",
                    res.staff_position, dreamCounsel.staff_position, user.user_id)
        request.state.inspect = frame()
        res.staff_position = dreamCounsel.staff_position

    if dreamCounsel.staff_position2 is not None and res.staff_position2 != dreamCounsel.staff_position2:
        log_scm_service.create_log(request, res.uid, "T_DREAM_COUNSEL", "staff_position2", "담당자 직책",
                    res.staff_position2, dreamCounsel.staff_position2, user.user_id)
        request.state.inspect = frame()
        res.staff_position2 = dreamCounsel.staff_position2
    
    if dreamCounsel.staff_mobile is not None and res.staff_mobile != dreamCounsel.staff_mobile:
        log_scm_service.create_log(request, res.uid, "T_DREAM_COUNSEL", "staff_mobile", "담당자 핸드폰 번호",
                    res.staff_mobile, dreamCounsel.staff_mobile, user.user_id)
        request.state.inspect = frame()
        res.staff_mobile = dreamCounsel.staff_mobile
    
    if dreamCounsel.staff_email is not None and res.staff_email != dreamCounsel.staff_email:
        log_scm_service.create_log(request, res.uid, "T_DREAM_COUNSEL", "staff_email", "담당자 이메일",
                    res.staff_email, dreamCounsel.staff_email, user.user_id)
        request.state.inspect = frame()
        res.staff_email = dreamCounsel.staff_email
    
    if dreamCounsel.contents is not None and res.contents != dreamCounsel.contents:
        log_scm_service.create_log(request, res.uid, "T_DREAM_COUNSEL", "contents", "상담문의 & 요청내용",
                    res.contents, dreamCounsel.contents, user.user_id)
        request.state.inspect = frame()
        res.contents = dreamCounsel.contents
    
    if dreamCounsel.state is not None and res.state != dreamCounsel.state:
        log_scm_service.create_log(request, res.uid, "T_DREAM_COUNSEL", "state", "진행상태",
                    res.state, dreamCounsel.state, user.user_id)
        request.state.inspect = frame()
        res.state = dreamCounsel.state

    res.update_at = util.getNow()
    return res
