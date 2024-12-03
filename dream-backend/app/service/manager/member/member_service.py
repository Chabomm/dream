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
from app.schemas.schema import *
from app.schemas.manager.member import *
from app.service.log_service import *

# 임직원_리스트
def member_list(request: Request, page_param: PPage_param, fullsearch:bool=False):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    offsets = 0
    if fullsearch == False :
        offsets = (page_param.page-1)*page_param.page_view_size

    limits = None
    if fullsearch == False :
        limits = page_param.page_view_size


    filters = []
    filters.append(getattr(T_MEMBER, "delete_at") == None)
    filters.append(getattr(T_MEMBER, "partner_uid") == user.partner_uid)

    # [ S ] search filter start
    if page_param.filters :
        if page_param.filters["skeyword"] :
            if page_param.filters["skeyword_type"] != "" :
                if page_param.filters["skeyword_type"] == "depart" or page_param.filters["skeyword_type"] == "position" or page_param.filters["skeyword_type"] == "position2" :
                    filters.append(getattr(T_MEMBER_INFO, page_param.filters["skeyword_type"]).like("%"+page_param.filters["skeyword"]+"%"))
                else :
                    filters.append(getattr(T_MEMBER, page_param.filters["skeyword_type"]).like("%"+page_param.filters["skeyword"]+"%"))
            else : 
                filters.append(
                    T_MEMBER.user_name.like("%"+page_param.filters["skeyword"]+"%") 
                    | T_MEMBER.login_id.like("%"+page_param.filters["skeyword"]+"%")
                    | T_MEMBER_INFO.depart.like("%"+page_param.filters["skeyword"]+"%")
                    | T_MEMBER_INFO.position.like("%"+page_param.filters["skeyword"]+"%")
                    | T_MEMBER_INFO.position2.like("%"+page_param.filters["skeyword"]+"%")
                )

        if page_param.filters["create_at"]["startDate"] and page_param.filters["create_at"]["endDate"] :
            filters.append(
                and_(
                    T_MEMBER.create_at >= page_param.filters["create_at"]["startDate"]
                    ,T_MEMBER.create_at <= page_param.filters["create_at"]["endDate"] + " 23:59:59"
                )
            )
        
        if page_param.filters["birth_type"] :
            filters.append(func.substr(T_MEMBER_INFO.birth, 6, 2).like("%"+page_param.filters["birth_type"]+"%"))
            # filters.append(T_MEMBER_INFO.birth.like(func.substr(T_MEMBER_INFO.birth, 6, 2)))

        if page_param.filters["serve_type"] :
            filters.append(T_MEMBER_INFO.serve.in_(page_param.filters["serve_type"]))
    # [ E ] search filter end

    sql = (
        db.query(
             T_MEMBER.uid
            ,T_MEMBER.login_id
            ,T_MEMBER.user_id
            ,T_MEMBER.user_name
            ,T_MEMBER.mobile
            ,func.date_format(T_MEMBER.create_at, '%Y-%m-%d %T').label('create_at')
            ,func.date_format(T_MEMBER_INFO.birth, '%Y-%m-%d').label('birth')
            ,T_MEMBER_INFO.depart
            ,T_MEMBER_INFO.position
        )
        .join(
            T_MEMBER_INFO, 
            T_MEMBER_INFO.uid == T_MEMBER.uid,
        )
        .filter(*filters)
        .order_by(T_MEMBER.uid.desc())
        # .offset((page_param.page-1)*page_param.page_view_size)
        # .limit(page_param.page_view_size)
        .offset(offsets)
        .limit(limits)
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    # [ S ] 페이징 처리
    page_param.page_total = (
         db.query(T_MEMBER)
        .join(
            T_MEMBER_INFO, 
            T_MEMBER_INFO.uid == T_MEMBER.uid,
        )
        .filter(*filters)
        .count()
    )
    page_param.page_last = math.ceil(page_param.page_total / page_param.page_view_size)
    page_param.page_size = len(rows) # 현재 페이지에 검색된 수
    # [ E ] 페이징 처리

    jsondata = {}
    jsondata.update({"params": page_param})
    jsondata.update({"list": rows})

    return jsondata

# 임직원 - 상세
def member_read(request: Request, uid: int):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    sql = ( 
        db.query(
             T_MEMBER.uid
            ,T_MEMBER.login_id
            ,T_MEMBER.user_name
            ,T_MEMBER.mobile
            ,T_MEMBER.email
            ,T_MEMBER_INFO.serve
            ,T_MEMBER_INFO.birth
            ,T_MEMBER_INFO.gender
            ,T_MEMBER_INFO.anniversary
            ,T_MEMBER_INFO.emp_no
            ,T_MEMBER_INFO.depart
            ,T_MEMBER_INFO.position
            ,T_MEMBER_INFO.position2
            ,T_MEMBER_INFO.join_com
            ,T_MEMBER_INFO.post
            ,T_MEMBER_INFO.addr
            ,T_MEMBER_INFO.addr_detail
            ,T_MEMBER_INFO.tel
            ,T_MEMBER_INFO.affiliate
            ,T_MEMBER_INFO.state
            ,T_MEMBER_INFO.is_login
            ,T_MEMBER_INFO.is_point
            ,T_MEMBER_INFO.is_pw_reset
        )
        .join(
            T_MEMBER_INFO,
            T_MEMBER_INFO.uid == T_MEMBER.uid,
        )
        .filter(
            T_MEMBER.uid == uid
            ,T_MEMBER.partner_uid == user.partner_uid
            ,T_MEMBER.delete_at == None
        )
    )
    # format_sql(sql)
    return sql.first()

# 임직원 등록
def member_create(request: Request, memberInput: MemberInput):
    request.state.inspect = frame()
    db = request.state.db 
    user = request.state.user

    db_item = T_MEMBER (
         login_id = memberInput.login_id
        ,user_id = str(user.prefix) + str(memberInput.user_id)
        ,partner_uid = user.partner_uid
        ,partner_id = user.partner_id
        ,prefix = user.prefix
        ,user_name = memberInput.user_name
        ,mobile = memberInput.mobile
        ,email = memberInput.email
        ,aff_uid = memberInput.aff_uid
    )
    db.add(db_item)
    db.flush()

    create_log(request, db_item.uid, "T_MEMBER", "INSERT", "임직원 등록", 0, db_item.uid, user.user_id)
    request.state.inspect = frame()

    db_item2 = T_MEMBER_INFO (
         uid = db_item.uid
        ,user_id = str(user.prefix) + str(memberInput.user_id)
        ,login_id = memberInput.login_id
        ,prefix = user.prefix
        ,partner_uid = user.partner_uid
        ,partner_id = user.partner_id
        ,mem_uid = memberInput.mem_uid
        ,serve = memberInput.serve
        ,birth = memberInput.birth
        ,gender = memberInput.gender
        ,user_name = memberInput.user_name
        ,anniversary = memberInput.anniversary
        ,emp_no = memberInput.emp_no
        ,depart = memberInput.depart
        ,position = memberInput.position
        ,position2 = memberInput.position2
        ,join_com = memberInput.join_com
        ,post = memberInput.post
        ,addr = memberInput.addr
        ,addr_detail = memberInput.addr_detail
        ,tel = memberInput.tel
        ,affiliate = memberInput.affiliate
        ,state = memberInput.state
        ,is_login = memberInput.is_login
        ,is_point = memberInput.is_point
        ,is_pw_reset = memberInput.is_pw_reset
    )
    db.add(db_item2)
    db.flush()

    create_log(request, db_item2.uid, "T_MEMBER_INFO", "INSERT", "임직원 정보 등록", 0, db_item2.uid, user.user_id)
    request.state.inspect = frame()

    return db_item

def member_update(request: Request, memberInput: MemberInput):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user
    
    # 기존 등록된 임직원 select 
    res = db.query(T_MEMBER).filter(T_MEMBER.uid == memberInput.uid).first()
    res2 = db.query(T_MEMBER_INFO).filter(T_MEMBER_INFO.uid == memberInput.uid).first()

    if res is None:
        raise ex.NotFoundUser

    if memberInput.user_name is not None and res.user_name != memberInput.user_name:
        create_log(request, memberInput.uid, "T_MEMBER", "user_name", "임직원 이름",
                    res.user_name, memberInput.user_name, user.user_id)
        request.state.inspect = frame()
        res.user_name = memberInput.user_name

    if memberInput.mobile is not None and res.mobile != memberInput.mobile:
        create_log(request, memberInput.uid, "T_MEMBER", "mobile", "휴대전화번호",
                    res.mobile, memberInput.mobile, user.user_id)
        request.state.inspect = frame()
        res.mobile = memberInput.mobile

    if memberInput.email is not None and res.email != memberInput.email:
        create_log(request, memberInput.uid, "T_MEMBER", "email", "이메일",
                    res.email, memberInput.email, user.user_id)
        request.state.inspect = frame()
        res.email = memberInput.email

    if memberInput.serve is not None and res2.serve != memberInput.serve:
        create_log(request, memberInput.uid, "T_MEMBER_INFO", "serve", "재직여부",
                    res2.serve, memberInput.serve, user.user_id)
        request.state.inspect = frame()
        res2.serve = memberInput.serve

    if memberInput.birth is not None and res2.birth != memberInput.birth:
        create_log(request, memberInput.uid, "T_MEMBER_INFO", "birth", "생년월일",
                    res2.birth, memberInput.birth, user.user_id)
        request.state.inspect = frame()
        res2.birth = memberInput.birth

    if memberInput.gender is not None and res2.gender != memberInput.gender:
        create_log(request, memberInput.uid, "T_MEMBER_INFO", "gender", "성별",
                    res2.gender, memberInput.gender, user.user_id)
        request.state.inspect = frame()
        res2.gender = memberInput.gender

    if memberInput.anniversary is not None and res2.anniversary != memberInput.anniversary:
        create_log(request, memberInput.uid, "T_MEMBER_INFO", "anniversary", "기념일",
                    res2.anniversary, memberInput.anniversary, user.user_id)
        request.state.inspect = frame()
        res2.anniversary = memberInput.anniversary

    if memberInput.emp_no is not None and res2.emp_no != memberInput.emp_no:
        create_log(request, memberInput.uid, "T_MEMBER_INFO", "emp_no", "사번",
                    res2.emp_no, memberInput.emp_no, user.user_id)
        request.state.inspect = frame()
        res2.emp_no = memberInput.emp_no

    if memberInput.depart is not None and res2.depart != memberInput.depart:
        create_log(request, memberInput.uid, "T_MEMBER_INFO", "depart", "부서",
                    res2.depart, memberInput.depart, user.user_id)
        request.state.inspect = frame()
        res2.depart = memberInput.depart

    if memberInput.position is not None and res2.position != memberInput.position:
        create_log(request, memberInput.uid, "T_MEMBER_INFO", "position", "직급",
                    res2.position, memberInput.position, user.user_id)
        request.state.inspect = frame()
        res2.position = memberInput.position

    if memberInput.position2 is not None and res2.position2 != memberInput.position2:
        create_log(request, memberInput.uid, "T_MEMBER_INFO", "position2", "직책",
                    res2.position2, memberInput.position2, user.user_id)
        request.state.inspect = frame()
        res2.position2 = memberInput.position2

    if memberInput.join_com is not None and res2.join_com != memberInput.join_com:
        create_log(request, memberInput.uid, "T_MEMBER_INFO", "join_com", "입사일",
                    res2.join_com, memberInput.join_com, user.user_id)
        request.state.inspect = frame()
        res2.join_com = memberInput.join_com

    if memberInput.post is not None and res2.post != memberInput.post:
        create_log(request, memberInput.uid, "T_MEMBER_INFO", "post", "우편번호",
                    res2.post, memberInput.post, user.user_id)
        request.state.inspect = frame()
        res2.post = memberInput.post

    if memberInput.addr is not None and res2.addr != memberInput.addr:
        create_log(request, memberInput.uid, "T_MEMBER_INFO", "addr", "주소",
                    res2.addr, memberInput.addr, user.user_id)
        request.state.inspect = frame()
        res2.addr = memberInput.addr

    if memberInput.addr_detail is not None and res2.addr_detail != memberInput.addr_detail:
        create_log(request, memberInput.uid, "T_MEMBER_INFO", "addr_detail", "주소상세",
                    res2.addr_detail, memberInput.addr_detail, user.user_id)
        request.state.inspect = frame()
        res2.addr_detail = memberInput.addr_detail

    if memberInput.tel is not None and res2.tel != memberInput.tel:
        create_log(request, memberInput.uid, "T_MEMBER_INFO", "tel", "전화번호",
                    res2.tel, memberInput.tel, user.user_id)
        request.state.inspect = frame()
        res2.tel = memberInput.tel

    if memberInput.affiliate is not None and res2.affiliate != memberInput.affiliate:
        create_log(request, memberInput.uid, "T_MEMBER_INFO", "affiliate", "법인사",
                    res2.affiliate, memberInput.affiliate, user.user_id)
        request.state.inspect = frame()
        res2.affiliate = memberInput.affiliate

    if memberInput.state is not None and res2.state != memberInput.state:
        create_log(request, memberInput.uid, "T_MEMBER_INFO", "state", "상태",
                    res2.state, memberInput.state, user.user_id)
        request.state.inspect = frame()
        res2.state = memberInput.state

    if memberInput.is_login is not None and res2.is_login != memberInput.is_login:
        create_log(request, memberInput.uid, "T_MEMBER_INFO", "is_login", "복지몰 로그인가능여부",
                    res2.is_login, memberInput.is_login, user.user_id)
        request.state.inspect = frame()
        res2.is_login = memberInput.is_login

    if memberInput.is_point is not None and res2.is_point != memberInput.is_point:
        create_log(request, memberInput.uid, "T_MEMBER_INFO", "is_point", "포인트 사용가능여부",
                    res2.is_point, memberInput.is_point, user.user_id)
        request.state.inspect = frame()
        res2.is_point = memberInput.is_point

    if memberInput.is_pw_reset is not None and res2.is_pw_reset != memberInput.is_pw_reset:
        create_log(request, memberInput.uid, "T_MEMBER_INFO", "is_pw_reset", "비밀번호 초기화 여부",
                    "", "", user.user_id)
        request.state.inspect = frame()
        res2.is_pw_reset = memberInput.is_pw_reset

    res.update_at = util.getNow()
    res2.update_at = util.getNow()
    return res

def member_delete(request: Request, uid: int):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user
    
    db_item = db.query(T_MEMBER).filter(T_MEMBER.uid == uid).first()
    db_item1 = db.query(T_MEMBER_INFO).filter(T_MEMBER_INFO.uid == uid).first()

    create_log(request, uid, "T_MEMBER", "DELETE", "임직원 삭제",
                db_item.delete_at, util.getNow(), user.user_id)
    request.state.inspect = frame()
    db_item.delete_at = util.getNow()

    create_log(request, uid, "T_MEMBER_INFO", "DELETE", "임직원 삭제",
                db_item1.delete_at, util.getNow(), user.user_id)
    request.state.inspect = frame()
    db_item1.delete_at = util.getNow()

    return 

def check_member_id(request: Request, chkMemberIdSchema: ChkMemberIdSchema):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    sql = (
        db.query(T_MEMBER)
        .filter(
             T_MEMBER.partner_id == user.partner_id
            ,T_MEMBER.login_id == chkMemberIdSchema.memberid_input_value
            ,T_MEMBER.prefix == user.prefix
        )
    )
    
    return sql.count()

# 대량등록 전 멤버 유무 확인
def excel_create_before_member_read(request: Request, login_id: str):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    sql = ( 
        db.query(
             T_MEMBER.uid
            ,T_MEMBER.login_id
            ,T_MEMBER.user_name
            ,T_MEMBER.mobile
            ,T_MEMBER.email
            ,T_MEMBER_INFO.prefix
        )
        .join(
             T_MEMBER_INFO
            ,T_MEMBER_INFO.login_id == login_id
        )
        .filter(
            T_MEMBER.login_id == login_id
            ,T_MEMBER.partner_uid == user.partner_uid
            ,T_MEMBER.delete_at == None
        )
    )
    # format_sql(sql)
    return sql.first()


# 임직원 엑셀 대량등록
def bulk_member_create(request: Request, posts: object):
    request.state.inspect = frame()
    db = request.state.db 
    user = request.state.user


    if posts["복지몰로그인"] == '가능' :
        posts["복지몰로그인"] = 'T'
    elif posts["복지몰로그인"] == '불가능' :
        posts["복지몰로그인"] = 'F'

    if posts["포인트사용"] == '가능' :
        posts["포인트사용"] = 'T'
    elif posts["포인트사용"] == '불가능' :
        posts["포인트사용"] = 'F'
    
    user_id = str(user.prefix) + str(posts["아이디"])

    db_item = T_MEMBER (
         login_id = posts["아이디"]
        ,user_id = user_id
        ,partner_uid = user.partner_uid
        ,partner_id = user.partner_id
        ,prefix = user.prefix
        ,user_name = posts["이름"]
        ,mobile = posts["휴대전화"]
        ,email = posts["이메일"]
    )
    db.add(db_item)
    db.flush()

    create_log(request, db_item.uid, "T_MEMBER", "INSERT", "임직원 등록", 0, db_item.uid, user.user_id)
    request.state.inspect = frame()

    db_item2 = T_MEMBER_INFO (
         uid = db_item.uid
        ,user_id = user_id
        ,login_id = posts["아이디"]
        ,user_name=posts["이름"]
        ,prefix = user.prefix
        ,partner_uid = user.partner_uid
        ,partner_id = user.partner_id
        ,serve = posts["재직여부"]
        ,birth = posts["생년월일"]
        ,gender = posts["성별"]
        ,anniversary = posts["기념일"]
        ,emp_no = posts["사번"]
        ,depart = posts["부서"]
        ,position = posts["직급"]
        ,position2 = posts["직책"]
        ,join_com = posts["입사일"]
        ,post = posts["우편번호"]
        ,addr = posts["주소"]
        ,addr_detail = posts["주소상세"]
        ,tel = posts["휴대전화"]
        ,is_login = posts["복지몰로그인"]
        ,is_point = posts["포인트사용"]
    )
    db.add(db_item2)
    db.flush()

    create_log(request, db_item2.uid, "T_MEMBER_INFO", "INSERT", "임직원 정보 등록", 0, db_item2.uid, user.user_id)
    request.state.inspect = frame()

    return db_item



# 임직원 이름, 아이디
def member_list_info(request: Request):
    request.state.inspect = frame()
    db = request.state.db 
    user = request.state.user

    filters = []
    filters.append(getattr(T_MEMBER, "delete_at") == None)
    filters.append(getattr(T_MEMBER, "partner_uid") == user.partner_uid)
    
    sql = (
        db.query(
             T_MEMBER.uid
            ,T_MEMBER.login_id
            ,T_MEMBER.user_id
            ,T_MEMBER.user_name
        )
        .join(
            T_MEMBER_INFO, 
            T_MEMBER_INFO.uid == T_MEMBER.uid,
        )
        .filter(*filters)
        .order_by(T_MEMBER.uid.desc())
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    return rows