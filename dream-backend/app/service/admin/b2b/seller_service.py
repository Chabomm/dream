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

from app.deps import auth

from app.core.database import format_sql
from app.models.scm.b2b.seller import *
from app.models.admin import *
from app.schemas.admin.b2b.seller import *
from app.service import log_scm_service
from app.service.admin.b2b import seller_service


def seller_list(request: Request, page_param: PPage_param):
    request.state.inspect = frame()
    db_scm = request.state.db_scm

    staff_filters = []
    staff_filters.append(getattr(T_B2B_SELLER_STAFF, "delete_at") == None)
    staff_filters.append(getattr(T_B2B_SELLER_STAFF, "seller_uid") == T_B2B_SELLER.uid)
    staff_filters.append(func.json_contains(T_B2B_SELLER_STAFF.roles, f'[1]'))
    staff_filters.append(getattr(T_B2B_SELLER_STAFF, "sort") == 1)

    staff_stmt = (
        db_scm.query(
             T_B2B_SELLER_STAFF.uid
            ,T_B2B_SELLER_STAFF.seller_uid
            ,T_B2B_SELLER_STAFF.name
            ,T_B2B_SELLER_STAFF.tel
            ,T_B2B_SELLER_STAFF.mobile
            ,T_B2B_SELLER_STAFF.email
        )
        .filter(*staff_filters)
        .subquery()
    ) 

    filters = []

    # [ S ] search filter start
    if page_param.filters :
        if page_param.filters["skeyword"] :
            if page_param.filters["skeyword_type"] != "" :
                filters.append(getattr(T_B2B_SELLER, page_param.filters["skeyword_type"]).like("%"+page_param.filters["skeyword"]   +"%"))
            else : 
                filters.append(
                    T_B2B_SELLER.indend_md.like("%"+page_param.filters["skeyword"]+"%") | 
                    T_B2B_SELLER.indend_md_name.like("%"+page_param.filters["skeyword"]+"%") |
                    T_B2B_SELLER.seller_id.like("%"+page_param.filters["skeyword"]+"%") |
                    T_B2B_SELLER.seller_name.like("%"+page_param.filters["skeyword"]+"%") 
                )

        if page_param.filters["create_at"]["startDate"] and page_param.filters["create_at"]["endDate"] :
            filters.append(
                and_(
                    T_B2B_SELLER.create_at >= page_param.filters["create_at"]["startDate"]
                    ,T_B2B_SELLER.create_at <= page_param.filters["create_at"]["endDate"] + " 23:59:59"
                )
            )

        if page_param.filters["delete_at"]["startDate"] and page_param.filters["delete_at"]["endDate"] :
            filters.append(
                and_(
                    T_B2B_SELLER.delete_at >= page_param.filters["delete_at"]["startDate"]
                    ,T_B2B_SELLER.delete_at <= page_param.filters["delete_at"]["endDate"] + " 23:59:59"
                )
            )

        if page_param.filters["state"] != '' :
            filters.append(T_B2B_SELLER.state == page_param.filters["state"])

        if page_param.filters["seller_uid"] > 0 :
            filters.append(T_B2B_SELLER.uid == page_param.filters["seller_uid"])

    # [ E ] search filter end
    
    sql = (
        db_scm.query(
             T_B2B_SELLER.uid
            ,T_B2B_SELLER.seller_id
            ,T_B2B_SELLER.seller_name
            ,T_B2B_SELLER.account_cycle
            ,T_B2B_SELLER.indend_md
            ,T_B2B_SELLER.state
            ,T_B2B_SELLER.ceo_name
            ,T_B2B_SELLER.tel
            ,T_B2B_SELLER.biz_no
            ,T_B2B_SELLER.biz_kind
            ,T_B2B_SELLER.biz_item
            ,T_B2B_SELLER.bank
            ,T_B2B_SELLER.account
            ,T_B2B_SELLER.depositor
            ,T_B2B_SELLER.homepage
            ,T_B2B_SELLER.post
            ,T_B2B_SELLER.addr
            ,T_B2B_SELLER.addr_detail
            ,T_B2B_SELLER.biz_file
            ,T_B2B_SELLER.biz_hooper
            ,func.date_format(T_B2B_SELLER.create_at, '%Y-%m-%d %T').label('create_at')
            ,func.date_format(T_B2B_SELLER.update_at, '%Y-%m-%d %T').label('update_at')
            ,func.date_format(T_B2B_SELLER.delete_at, '%Y-%m-%d %T').label('delete_at')
            ,staff_stmt.c.name
            ,staff_stmt.c.tel
            ,staff_stmt.c.mobile
            ,staff_stmt.c.email
        )
        .join(
            staff_stmt, 
            staff_stmt.c.seller_uid == T_B2B_SELLER.uid, 
            isouter = True 
        )
        .filter(*filters)
        .order_by(T_B2B_SELLER.uid.desc())
        .offset((page_param.page-1)*page_param.page_view_size)
        .limit(page_param.page_view_size)
    )


    format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    jsondata = {}
    # [ S ] 페이징 처리
    page_param.page_total = (
        db_scm.query(T_B2B_SELLER)
        .join(
            staff_stmt, 
            staff_stmt.c.seller_uid == T_B2B_SELLER.uid, 
            isouter = True 
        )
        .filter(*filters)
        .count()
    )
    page_param.page_last = math.ceil(
        page_param.page_total / page_param.page_view_size)
    page_param.page_size = len(rows)  # 현재 페이지에 검색된 수
    # [ E ] 페이징 처리
    jsondata.update({"params": page_param})
    jsondata.update({"list": rows})

    return jsondata


def seller_search_list(request: Request, sellerSearchInput: SellerSearchInput):
    request.state.inspect = frame()
    db_scm = request.state.db_scm
    
    sql = (
        db_scm.query(
             T_B2B_SELLER.uid
            ,T_B2B_SELLER.seller_id
            ,T_B2B_SELLER.seller_name
            ,T_B2B_SELLER.account_cycle
            ,T_B2B_SELLER.indend_md
        )
        .filter(T_B2B_SELLER.seller_name.like("%"+sellerSearchInput.seller+"%"))
        .filter(T_B2B_SELLER.seller_id.like("%"+sellerSearchInput.seller+"%"))
        .order_by(T_B2B_SELLER.uid.desc())
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    jsondata = {}
    jsondata.update({"list": rows})

    return jsondata


# 업체 상세
def seller_read(request: Request, uid: int):
    request.state.inspect = frame()
    db_scm = request.state.db_scm
    
    filters = []
    filters.append(getattr(T_B2B_SELLER, "uid") == uid)

    sql = ( 
        db_scm.query(
             T_B2B_SELLER.uid
            ,T_B2B_SELLER.seller_id
            ,T_B2B_SELLER.seller_name
            ,T_B2B_SELLER.account_cycle
            ,T_B2B_SELLER.indend_md
            ,T_B2B_SELLER.state
            ,T_B2B_SELLER.ceo_name
            ,T_B2B_SELLER.tel
            ,T_B2B_SELLER.biz_no
            ,T_B2B_SELLER.biz_kind
            ,T_B2B_SELLER.biz_item
            ,T_B2B_SELLER.bank
            ,T_B2B_SELLER.account
            ,T_B2B_SELLER.depositor
            ,T_B2B_SELLER.homepage
            ,T_B2B_SELLER.post
            ,T_B2B_SELLER.addr
            ,T_B2B_SELLER.addr_detail
            ,T_B2B_SELLER.biz_file
            ,T_B2B_SELLER.biz_hooper
            ,T_B2B_SELLER.indend_md_name
            ,T_B2B_SELLER.tax_email
            ,func.date_format(T_B2B_SELLER.create_at, '%Y-%m-%d %T').label('create_at')
            ,func.date_format(T_B2B_SELLER.update_at, '%Y-%m-%d %T').label('update_at')
            ,func.date_format(T_B2B_SELLER.delete_at, '%Y-%m-%d %T').label('delete_at')
        )
        .filter(*filters)
    )
    format_sql(sql)
    
    
    res = sql.first()

    if res == None :
        return ex.ReturnOK(404, "게시물을 찾을 수 없습니다.", request)
    else :
        res = dict(zip(res.keys(), res))
    

    if res["biz_file"] != '' and res["biz_file"] != None :
        res["biz_file_fakename"] = res["biz_file"].split('/')[-1]
    
    if res["biz_hooper"] != '' and res["biz_hooper"] != None :
        res["biz_hooper_fakename"] = res["biz_hooper"].split('/')[-1]
        
    
    staff_list = seller_service.staff_list(request, res["uid"])
    res.update({"staff_list" : staff_list})
    
    memo_list = log_scm_service.memo_list(request, "T_B2B_SELLER", uid)
    res.update({"memo_list" : memo_list["list"]})

    return res


# 담당자 리스트
def staff_list(request: Request, uid: int):
    request.state.inspect = frame()
    db_scm = request.state.db_scm

    sql = """
        SELECT 
            uid
            ,seller_uid
            ,sort
            ,name
            ,roles
            ,tel
            ,mobile
            ,alarm_kakao
            ,email
            ,alarm_email
            ,state
            ,( 
                select GROUP_CONCAT(name SEPARATOR ', ') AS result  
                From T_B2B_SELLER_ROLE 
                where uid MEMBER OF(roles->>'$')
            ) as roles_txt
        FROM T_B2B_SELLER_STAFF
        WHERE delete_at is NULL
        AND seller_uid = {uid}
        ORDER BY sort ASC
    """.format(uid=uid)

    res = db_scm.execute(text(sql)).fetchall()

    rows = []
    for c in res :
        rows.append(dict(zip(c.keys(), c))) 

    return rows

# 업체_편집 - seller_create
def seller_create(request: Request, sellerDetailInput: SellerDetailInput):
    request.state.inspect = frame()
    db_scm = request.state.db_scm
    user = request.state.user

    seller_id = ''
    res = db_scm.query(T_B2B_SELLER).order_by(T_B2B_SELLER.uid.desc()).first()
    seller_id = 'B2B'+str(res.uid+1)

    db_item = T_B2B_SELLER (
         seller_id = seller_id
        ,seller_name = sellerDetailInput.seller_name
        ,account_cycle = sellerDetailInput.account_cycle
        ,indend_md = sellerDetailInput.indend_md
        ,indend_md_name = sellerDetailInput.indend_md_name
        ,indend_md_email = sellerDetailInput.indend_md_email
        ,indend_md_tel = sellerDetailInput.indend_md_tel
        ,indend_md_mobile = sellerDetailInput.indend_md_mobile
        ,state = sellerDetailInput.state
        ,ceo_name = sellerDetailInput.ceo_name
        ,biz_no = sellerDetailInput.biz_no
        ,biz_kind = sellerDetailInput.biz_kind
        ,biz_item = sellerDetailInput.biz_item
        ,bank = sellerDetailInput.bank
        ,account = sellerDetailInput.account
        ,depositor = sellerDetailInput.depositor
        ,homepage = sellerDetailInput.homepage
        ,post = sellerDetailInput.post
        ,addr = sellerDetailInput.addr
        ,addr_detail = sellerDetailInput.addr_detail
        ,biz_file = sellerDetailInput.biz_file
        ,biz_hooper = sellerDetailInput.biz_hooper
        ,tax_email = sellerDetailInput.tax_email
    )
    db_scm.add(db_item)
    db_scm.flush()
    
    if sellerDetailInput.memo != '' and sellerDetailInput.memo != 'undefined':
        log_scm_service.create_memo(request, sellerDetailInput.uid, "T_B2B_SELLER", sellerDetailInput.memo, user.user_id, user.token_name, 'ADMIN', None)
        request.state.inspect = frame()

    log_scm_service.create_log(request, db_item.uid, "T_B2B_SELLER", "INSERT", "업체 등록", 0, db_item.uid, user.user_id)
    request.state.inspect = frame()

    return db_item

# 업체_편집 - seller_update  
def seller_update(request: Request, sellerDetailInput: SellerDetailInput):
    request.state.inspect = frame()
    db_scm = request.state.db_scm
    user = request.state.user

    res = db_scm.query(T_B2B_SELLER).filter(T_B2B_SELLER.uid == sellerDetailInput.uid).first()

    if res is None :
        return ex.ReturnOK(404, "죄송합니다. 오류가 발생 하였습니다. 문제 지속시 개발자에게 접수 바랍니다.", request)
        
    if sellerDetailInput.seller_id is not None and res.seller_id != sellerDetailInput.seller_id : 
        log_scm_service.create_log(request, res.uid, "T_B2B_SELLER", "seller_id", "판매자아이디 수정", res.seller_id, sellerDetailInput.seller_id, user.user_id)
        request.state.inspect = frame()
        res.seller_id = sellerDetailInput.seller_id

    if sellerDetailInput.seller_name is not None and res.seller_name != sellerDetailInput.seller_name : 
        log_scm_service.create_log(request, res.uid, "T_B2B_SELLER", "seller_name", "판매자명 수정", res.seller_name, sellerDetailInput.seller_name, user.user_id)
        request.state.inspect = frame()
        res.seller_name = sellerDetailInput.seller_name

    if sellerDetailInput.account_cycle is not None and res.account_cycle != sellerDetailInput.account_cycle : 
        log_scm_service.create_log(request, res.uid, "T_B2B_SELLER", "account_cycle", "정산일 수정", res.account_cycle, sellerDetailInput.account_cycle, user.user_id)
        request.state.inspect = frame()
        res.account_cycle = sellerDetailInput.account_cycle

    if sellerDetailInput.indend_md is not None and res.indend_md != sellerDetailInput.indend_md : 
        log_scm_service.create_log(request, res.uid, "T_B2B_SELLER", "indend_md", "담당MD아이디 수정", res.indend_md, sellerDetailInput.indend_md, user.user_id)
        request.state.inspect = frame()
        log_scm_service.create_log(request, res.uid, "T_B2B_SELLER", "indend_md_name", "담당MD명 수정", res.indend_md_name, sellerDetailInput.indend_md_name, user.user_id)
        request.state.inspect = frame()
        log_scm_service.create_log(request, res.uid, "T_B2B_SELLER", "indend_md_email", "담당MD 이메일 수정", res.indend_md_email, sellerDetailInput.indend_md_email, user.user_id)
        request.state.inspect = frame()
        log_scm_service.create_log(request, res.uid, "T_B2B_SELLER", "indend_md_tel", "담당MD 일반전화 수정", res.indend_md_tel, sellerDetailInput.indend_md_tel, user.user_id)
        request.state.inspect = frame()
        log_scm_service.create_log(request, res.uid, "T_B2B_SELLER", "indend_md_mobile", "담당MD 휴대전화 수정", res.indend_md_mobile, sellerDetailInput.indend_md_mobile, user.user_id)
        request.state.inspect = frame()

        res.indend_md = sellerDetailInput.indend_md
        res.indend_md_name = sellerDetailInput.indend_md_name
        res.indend_md_email = sellerDetailInput.indend_md_email
        res.indend_md_tel = sellerDetailInput.indend_md_tel
        res.indend_md_mobile = sellerDetailInput.indend_md_mobile

    if sellerDetailInput.ceo_name is not None and res.ceo_name != sellerDetailInput.ceo_name : 
        log_scm_service.create_log(request, res.uid, "T_B2B_SELLER", "ceo_name", "대표자명 수정", res.ceo_name, sellerDetailInput.ceo_name, user.user_id)
        request.state.inspect = frame()
        res.ceo_name = sellerDetailInput.ceo_name

    if sellerDetailInput.biz_no is not None and res.biz_no != sellerDetailInput.biz_no : 
        log_scm_service.create_log(request, res.uid, "T_B2B_SELLER", "biz_no", "사업자등록번호 수정", res.biz_no, sellerDetailInput.biz_no, user.user_id)
        request.state.inspect = frame()
        res.biz_no = sellerDetailInput.biz_no

    if sellerDetailInput.biz_kind is not None and res.biz_kind != sellerDetailInput.biz_kind : 
        log_scm_service.create_log(request, res.uid, "T_B2B_SELLER", "biz_kind", "업태 수정", res.biz_kind, sellerDetailInput.biz_kind, user.user_id)
        request.state.inspect = frame()
        res.biz_kind = sellerDetailInput.biz_kind

    if sellerDetailInput.biz_item is not None and res.biz_item != sellerDetailInput.biz_item : 
        log_scm_service.create_log(request, res.uid, "T_B2B_SELLER", "biz_item", "종목 수정", res.biz_item, sellerDetailInput.biz_item, user.user_id)
        request.state.inspect = frame()
        res.biz_item = sellerDetailInput.biz_item

    if sellerDetailInput.bank is not None and res.bank != sellerDetailInput.bank : 
        log_scm_service.create_log(request, res.uid, "T_B2B_SELLER", "bank", "정산은행 수정", res.bank, sellerDetailInput.bank, user.user_id)
        request.state.inspect = frame()
        res.bank = sellerDetailInput.bank

    if sellerDetailInput.account is not None and res.account != sellerDetailInput.account : 
        log_scm_service.create_log(request, res.uid, "T_B2B_SELLER", "account", "계좌번호 수정", res.account, sellerDetailInput.account, user.user_id)
        request.state.inspect = frame()
        res.account = sellerDetailInput.account

    if sellerDetailInput.depositor is not None and res.depositor != sellerDetailInput.depositor : 
        log_scm_service.create_log(request, res.uid, "T_B2B_SELLER", "depositor", "예금주 수정", res.depositor, sellerDetailInput.depositor, user.user_id)
        request.state.inspect = frame()
        res.depositor = sellerDetailInput.depositor

    if sellerDetailInput.tax_email is not None and res.tax_email != sellerDetailInput.tax_email : 
        log_scm_service.create_log(request, res.uid, "T_B2B_SELLER", "tax_email", "세금계산서 이메일 수정", res.tax_email, sellerDetailInput.tax_email, user.user_id)
        request.state.inspect = frame()
        res.tax_email = sellerDetailInput.tax_email

    if sellerDetailInput.post is not None and res.post != sellerDetailInput.post : 
        log_scm_service.create_log(request, res.uid, "T_B2B_SELLER", "post", "우편번호 수정", res.post, sellerDetailInput.post, user.user_id)
        request.state.inspect = frame()
        res.post = sellerDetailInput.post

    if sellerDetailInput.addr is not None and res.addr != sellerDetailInput.addr : 
        log_scm_service.create_log(request, res.uid, "T_B2B_SELLER", "addr", "주소 수정", res.addr, sellerDetailInput.addr, user.user_id)
        request.state.inspect = frame()
        res.addr = sellerDetailInput.addr

    if sellerDetailInput.addr_detail is not None and res.addr_detail != sellerDetailInput.addr_detail : 
        log_scm_service.create_log(request, res.uid, "T_B2B_SELLER", "addr_detail", "상세주소 수정", res.addr_detail, sellerDetailInput.addr_detail, user.user_id)
        request.state.inspect = frame()
        res.addr_detail = sellerDetailInput.addr_detail

    if sellerDetailInput.biz_file is not None and res.biz_file != sellerDetailInput.biz_file : 
        biz_file_fakename = res.biz_file.split('/')[-1]
        log_scm_service.create_log(request, res.uid, "T_B2B_SELLER", "biz_file", "사업자등록증첨부파일 수정", biz_file_fakename, sellerDetailInput.biz_file_fakename, user.user_id)
        request.state.inspect = frame()
        res.biz_file = sellerDetailInput.biz_file

    if sellerDetailInput.biz_hooper is not None and res.biz_hooper != sellerDetailInput.biz_hooper : 
        biz_hooper_fakename = res.biz_hooper.split('/')[-1]
        log_scm_service.create_log(request, res.uid, "T_B2B_SELLER", "biz_hooper", "통장사본첨부파일 수정", biz_hooper_fakename, sellerDetailInput.biz_hooper_fakename, user.user_id)
        request.state.inspect = frame()
        res.biz_hooper = sellerDetailInput.biz_hooper
    
    res.update_at = util.getNow()

    return res


# 업체_편집 - 순서정렬
def seller_staff_sort(request: Request, sellerDetailInput: SellerDetailInput) :
    request.state.inspect = frame()
    db_scm = request.state.db_scm

    filters = []
    filters.append(getattr(T_B2B_SELLER_STAFF, "seller_uid") == sellerDetailInput.uid)

    res = (
        db_scm.query(
            T_B2B_SELLER_STAFF
        )
        .filter(*filters)
        .all()
    )
    
    for c in res :
        for i in sellerDetailInput.sort_array :
            if c.uid == i :
                c.sort = sellerDetailInput.sort_array.index(i)+1

    return



# 업체 담당자 상세
def staff_read(request: Request, staffInput : StaffInput):
    request.state.inspect = frame()
    db_scm = request.state.db_scm

    filters = []
    filters.append(getattr(T_B2B_SELLER_STAFF, "delete_at") == None)
    filters.append(getattr(T_B2B_SELLER_STAFF, "uid") == staffInput.uid)
    filters.append(getattr(T_B2B_SELLER_STAFF, "seller_uid") == staffInput.seller_uid)

    sql = ( 
        db_scm.query(
             T_B2B_SELLER_STAFF.uid
            ,T_B2B_SELLER_STAFF.seller_uid
            ,T_B2B_SELLER_STAFF.seller_id
            ,T_B2B_SELLER_STAFF.login_id
            ,T_B2B_SELLER_STAFF.name
            ,T_B2B_SELLER_STAFF.roles
            ,T_B2B_SELLER_STAFF.depart
            ,T_B2B_SELLER_STAFF.position
            ,T_B2B_SELLER_STAFF.tel
            ,T_B2B_SELLER_STAFF.mobile
            ,T_B2B_SELLER_STAFF.email
            ,T_B2B_SELLER_STAFF.sort
            ,T_B2B_SELLER_STAFF.alarm_email
            ,T_B2B_SELLER_STAFF.alarm_kakao
            ,T_B2B_SELLER_STAFF.state
            ,func.date_format(T_B2B_SELLER_STAFF.create_at, '%Y-%m-%d %T').label('create_at')
            ,func.date_format(T_B2B_SELLER_STAFF.update_at, '%Y-%m-%d %T').label('update_at')
            ,func.date_format(T_B2B_SELLER_STAFF.delete_at, '%Y-%m-%d %T').label('delete_at')
        )
        .filter(*filters)
    )
    format_sql(sql)
    
    res = sql.first()

    if res == None :
        return ex.ReturnOK(404, "게시물을 찾을 수 없습니다.", request)
    else :
        res = dict(zip(res.keys(), res))

    return res


# 업체 담당자 구분 리스트
def roles_list(request: Request):
    request.state.inspect = frame()
    db_scm = request.state.db_scm
    user = request.state.user

    sql = (
        db_scm.query(
             T_B2B_SELLER_ROLE.uid.label('key')
            ,T_B2B_SELLER_ROLE.name.label('text')
        )
        .order_by(T_B2B_SELLER_ROLE.uid.desc())
    )

    rows = []
    for c in sql.all() :
        rows.append(dict(zip(c.keys(), c)))

    return rows


# 업체_담당자_편집 - seller_staff_create
def seller_staff_create(request: Request, sellerStaffInput: SellerStaffInput):
    request.state.inspect = frame()
    db_scm = request.state.db_scm
    user = request.state.user
   
    res = db_scm.query(T_B2B_SELLER_STAFF).filter(T_B2B_SELLER_STAFF.seller_uid == sellerStaffInput.seller_uid,T_B2B_SELLER_STAFF.delete_at == None).all()

    sort = 1
    for c in res :
        sort = c.sort+1

    db_item = T_B2B_SELLER_STAFF (
         seller_uid = sellerStaffInput.seller_uid
        ,seller_id = sellerStaffInput.seller_id
        ,login_id = sellerStaffInput.login_id
        ,login_pw = auth.get_password_hash(sellerStaffInput.login_id)
        ,user_id = sellerStaffInput.seller_id+'_'+sellerStaffInput.login_id
        ,name = sellerStaffInput.name
        ,roles = sellerStaffInput.roles
        ,depart = sellerStaffInput.depart
        ,position = sellerStaffInput.position
        ,tel = sellerStaffInput.tel
        ,mobile = sellerStaffInput.mobile
        ,email = sellerStaffInput.login_id
        ,sort = sort
        ,alarm_email = sellerStaffInput.alarm_email
        ,alarm_kakao = sellerStaffInput.alarm_kakao
        ,state = sellerStaffInput.state
    )
    db_scm.add(db_item)
    db_scm.flush()

    log_scm_service.create_log(request, db_item.uid, "T_B2B_SELLER_STAFF", "INSERT", "업체 담당자 등록", 0, db_item.uid, user.user_id)
    request.state.inspect = frame()

    return db_item

def duplicate_check(request: Request, sellerStaffInput: SellerStaffInput):
    request.state.inspect = frame()
    db_scm = request.state.db_scm
    user = request.state.user

    res = db_scm.query(T_B2B_SELLER_STAFF).filter(T_B2B_SELLER_STAFF.seller_uid == sellerStaffInput.seller_uid, T_B2B_SELLER_STAFF.login_id == sellerStaffInput.login_id).first()

    return res


# 업체_담당자_편집 - seller_staff_update  
def seller_staff_update(request: Request, sellerStaffInput: SellerStaffInput):
    request.state.inspect = frame()
    db_scm = request.state.db_scm
    user = request.state.user

    res = db_scm.query(T_B2B_SELLER_STAFF).filter(T_B2B_SELLER_STAFF.uid == sellerStaffInput.uid).first()

    if res is None :
        return ex.ReturnOK(404, "죄송합니다. 오류가 발생 하였습니다. 문제 지속시 개발자에게 접수 바랍니다.", request)
    
    if sellerStaffInput.mode == 'DEL' : 
        log_scm_service.create_log(request, res.uid, "T_B2B_SELLER_STAFF", "delete_at", "업체담당자 삭제", res.delete_at, util.getNow(), user.user_id)
        request.state.inspect = frame()
        res.delete_at = util.getNow()
    else :
        if sellerStaffInput.seller_id is not None and res.seller_id != sellerStaffInput.seller_id : 
            log_scm_service.create_log(request, res.uid, "T_B2B_SELLER_STAFF", "seller_id", "서비스구분", res.seller_id, sellerStaffInput.seller_id, user.user_id)
            request.state.inspect = frame()
            res.seller_id = sellerStaffInput.seller_id

        if sellerStaffInput.roles is not None and res.roles != sellerStaffInput.roles:
            log_scm_service.create_log(request, res.uid, "T_B2B_SELLER_STAFF", "roles", "구분 수정", res.roles, sellerStaffInput.roles, user.user_id)
            request.state.inspect = frame()
            res.roles = sellerStaffInput.roles

        if sellerStaffInput.name is not None and res.name != sellerStaffInput.name:
            log_scm_service.create_log(request, res.uid, "T_B2B_SELLER_STAFF", "name", "담당자명 수정", res.name, sellerStaffInput.name, user.user_id)
            request.state.inspect = frame()
            res.name = sellerStaffInput.name

        if sellerStaffInput.depart is not None and res.depart != sellerStaffInput.depart:
            log_scm_service.create_log(request, res.uid, "T_B2B_SELLER_STAFF", "depart", "부서 수정", res.depart, sellerStaffInput.depart, user.user_id)
            request.state.inspect = frame()
            res.depart = sellerStaffInput.depart

        if sellerStaffInput.position is not None and res.position != sellerStaffInput.position:
            log_scm_service.create_log(request, res.uid, "T_B2B_SELLER_STAFF", "position", "직급/직책 수정", res.position, sellerStaffInput.position, user.user_id)
            request.state.inspect = frame()
            res.position = sellerStaffInput.position

        if sellerStaffInput.tel is not None and res.tel != sellerStaffInput.tel:
            log_scm_service.create_log(request, res.uid, "T_B2B_SELLER_STAFF", "tel", "일반전화 수정", res.tel, sellerStaffInput.tel, user.user_id)
            request.state.inspect = frame()
            res.tel = sellerStaffInput.tel

        if sellerStaffInput.mobile is not None and res.mobile != sellerStaffInput.mobile:
            log_scm_service.create_log(request, res.uid, "T_B2B_SELLER_STAFF", "mobile", "휴대전화 수정", res.mobile, sellerStaffInput.mobile, user.user_id)
            request.state.inspect = frame()
            res.mobile = sellerStaffInput.mobile

        if sellerStaffInput.email is not None and res.email != sellerStaffInput.email:
            log_scm_service.create_log(request, res.uid, "T_B2B_SELLER_STAFF", "email", "이메일 수정", res.email, sellerStaffInput.email, user.user_id)
            request.state.inspect = frame()
            res.email = sellerStaffInput.email

        if sellerStaffInput.alarm_kakao is not None and res.alarm_kakao != sellerStaffInput.alarm_kakao:
            log_scm_service.create_log(request, res.uid, "T_B2B_SELLER_STAFF", "alarm_kakao", "알림톡수신 수정", res.alarm_kakao, sellerStaffInput.alarm_kakao, user.user_id)
            request.state.inspect = frame()
            res.alarm_kakao = sellerStaffInput.alarm_kakao

        if sellerStaffInput.alarm_email is not None and res.alarm_email != sellerStaffInput.alarm_email:
            log_scm_service.create_log(request, res.uid, "T_B2B_SELLER_STAFF", "alarm_email", "이메일수신 수정", res.alarm_email, sellerStaffInput.alarm_email, user.user_id)
            request.state.inspect = frame()
            res.alarm_email = sellerStaffInput.alarm_email
            
        res.update_at = util.getNow()

    return res


# 업체_담당자_편집 - seller_staff_update  
def seller_staff_pw_update(request: Request, uid : int):
    request.state.inspect = frame()
    db_scm = request.state.db_scm
    user = request.state.user

    res = db_scm.query(T_B2B_SELLER_STAFF).filter(T_B2B_SELLER_STAFF.uid == uid).first()

    if res is None :
        return ex.ReturnOK(404, "죄송합니다. 오류가 발생 하였습니다. 문제 지속시 개발자에게 접수 바랍니다.", request)
    
    if res.login_pw != res.login_id:
        log_scm_service.create_log(request, res.uid, "T_B2B_SELLER_STAFF", "login_pw", "담당자 비밀번호 초기화", "", "", user.user_id)
        request.state.inspect = frame()
        res.login_pw = auth.get_password_hash(res.login_id)
        res.update_at = util.getNow()

    return res

# 첨부파일 상세
def seller_files_read(request: Request, uid: int):
    request.state.inspect = frame()
    db_scm = request.state.db_scm
    user = request.state.user

    sql = ( 
        db_scm.query(
             T_B2B_SELLER
        )
        .filter(
            T_B2B_SELLER.uid == uid
        )
    ).first()
    
    log_scm_service.create_log(request, sql.uid, "T_B2B_SELLER", "file", "file 상세 다운로드", '', '', user.user_id)
    request.state.inspect = frame()

    return sql


# 고객사 관리자 list 
def admin_list(request: Request, page_param: PPage_param):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user
    
    sql = (
        db.query(
             T_ADMIN.uid
            ,T_ADMIN.user_id
            ,T_ADMIN.user_name
            ,T_ADMIN.tel
            ,T_ADMIN.mobile
            ,T_ADMIN.email
        )
        .filter(T_ADMIN.delete_at == None)
        .order_by(T_ADMIN.uid.desc())
        .offset((page_param.page-1)*page_param.page_view_size)
        .limit(page_param.page_view_size)
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        list = dict(zip(c.keys(), c))
        rows.append(list)

    # [ S ] 페이징 처리
    page_param.page_total = (
        db.query(T_ADMIN)
        .filter(T_ADMIN.delete_at == None)
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