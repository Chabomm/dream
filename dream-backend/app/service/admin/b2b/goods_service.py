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
from app.models.scm.b2b.goods import *
from app.models.scm.b2b.seller import *
from app.service import log_scm_service
from app.schemas.admin.b2b.goods import *

def list(request: Request, page_param: PPage_param):
    request.state.inspect = frame()
    db_scm = request.state.db_scm

    seller_stmt = (
        db_scm.query(
             T_B2B_SELLER.uid.label('seller_uid')
            ,T_B2B_SELLER.seller_id
            ,T_B2B_SELLER.seller_name
            ,T_B2B_SELLER.indend_md
            ,T_B2B_SELLER.indend_md_name
        )
        .subquery()
    )

    filters = []
    filters.append(getattr(T_B2B_GOODS, "delete_at") == None)

    # [ S ] search filter start
    if page_param.filters :
        if page_param.filters["skeyword"] :
            if page_param.filters["skeyword_type"] != "" :
                if page_param.filters["skeyword_type"] == "seller_uid" :
                    filters.append(seller_stmt.c.seller_uid.like("%"+page_param.filters["skeyword"]+"%"))
                else :
                    filters.append(getattr(T_B2B_GOODS, page_param.filters["skeyword_type"]).like("%"+page_param.filters["skeyword"]   +"%"))
            else : 
                filters.append(
                    T_B2B_GOODS.title.like("%"+page_param.filters["skeyword"]+"%") 
                )

        if page_param.filters["create_at"]["startDate"] and page_param.filters["create_at"]["endDate"] :
            filters.append(
                and_(
                    T_B2B_GOODS.create_at >= page_param.filters["create_at"]["startDate"]
                    ,T_B2B_GOODS.create_at <= page_param.filters["create_at"]["endDate"] + " 23:59:59"
                )
            )

        if page_param.filters["category"] != '' :
            filters.append(T_B2B_GOODS.category == page_param.filters["category"])

        if page_param.filters["seller_uid"] > 0 :
            filters.append(seller_stmt.c.seller_uid == page_param.filters["seller_uid"])

        if page_param.filters["is_display"] != '' :
            filters.append(T_B2B_GOODS.is_display == page_param.filters["is_display"])

    # [ E ] search filter end


    sql = (
        db_scm.query(
             T_B2B_GOODS.uid
            ,T_B2B_GOODS.sort
            ,T_B2B_GOODS.seller_name
            ,T_B2B_GOODS.category
            ,T_B2B_GOODS.service_type
            ,T_B2B_GOODS.title
            ,func.date_format(T_B2B_GOODS.create_at, '%Y-%m-%d').label('create_at')
            ,func.date_format(T_B2B_GOODS.update_at, '%Y-%m-%d %T').label('update_at')
            ,T_B2B_GOODS.is_display
            ,seller_stmt.c.seller_uid
            ,seller_stmt.c.seller_id
        )
        .join(
            seller_stmt, 
            T_B2B_GOODS.seller_id == seller_stmt.c.seller_id,
            isouter = True 
        )
        .filter(*filters)
        .order_by(T_B2B_GOODS.sort.asc(), T_B2B_GOODS.uid.desc())
        .offset((page_param.page-1)*page_param.page_view_size)
        .limit(page_param.page_view_size)
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    # [ S ] 페이징 처리
    page_param.page_total = (
        db_scm.query(T_B2B_GOODS)
        .join(
            seller_stmt, 
            T_B2B_GOODS.seller_id == seller_stmt.c.seller_id,
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
    jsondata.update({"params":page_param})
    jsondata.update({"list": rows})

    return jsondata


# 관리자 게시판 상세
def read(request: Request, uid: int):
    request.state.inspect = frame()
    db_scm = request.state.db_scm

    filters = []
    filters.append(getattr(T_B2B_GOODS, "delete_at") == None)
    filters.append(getattr(T_B2B_GOODS, "uid") == uid)

    sql = ( 
        db_scm.query(
             T_B2B_GOODS.uid
            ,T_B2B_GOODS.seller_id
            ,T_B2B_GOODS.seller_name
            ,T_B2B_GOODS.service_type
            ,T_B2B_GOODS.sort
            ,T_B2B_GOODS.is_display
            ,func.date_format(T_B2B_GOODS.start_date, '%Y-%m-%d').label('start_date')
            ,func.date_format(T_B2B_GOODS.end_date, '%Y-%m-%d').label('end_date')
            ,T_B2B_GOODS.category
            ,T_B2B_GOODS.title
            ,T_B2B_GOODS.sub_title
            ,T_B2B_GOODS.keyword
            ,T_B2B_GOODS.str_market_price
            ,T_B2B_GOODS.str_price
            ,T_B2B_GOODS.commission_type
            ,T_B2B_GOODS.commission
            ,T_B2B_GOODS.str_sale_percent
            ,T_B2B_GOODS.option_value
            ,T_B2B_GOODS.contents
            ,T_B2B_GOODS.benefit
            ,T_B2B_GOODS.attention
            ,T_B2B_GOODS.thumb
            ,T_B2B_GOODS.option_yn
            ,T_B2B_GOODS.other_service
            ,T_B2B_GOODS.state
            ,func.date_format(T_B2B_GOODS.create_at, '%Y-%m-%d %T').label('create_at')
            ,func.date_format(T_B2B_GOODS.update_at, '%Y-%m-%d %T').label('update_at')
            ,func.date_format(T_B2B_GOODS.delete_at, '%Y-%m-%d %T').label('delete_at')
        )
        .filter(*filters)
    )
    format_sql(sql)
    
    
    res = sql.first()

    if res == None :
        return ex.ReturnOK(404, "서비스를 찾을 수 없습니다.", request)
    else :
        res = dict(zip(res.keys(), res))
    
    memo_list = log_scm_service.memo_list(request, "T_B2B_GOODS", uid)
    request.state.inspect = frame()
    res.update({"memo_list" : memo_list["list"]})

    etc_images = image_list(request, uid)
    res.update({"etc_images" : etc_images})

    options = option_list(request, uid)
    res.update({"option_list" : options})

    return res


def image_list(request: Request, uid: int):
    request.state.inspect = frame()
    db_scm = request.state.db_scm
    
    sql = (
        db_scm.query(
             T_B2B_GOODS_IMAGE.guid
            ,T_B2B_GOODS_IMAGE.img_url
            ,T_B2B_GOODS_IMAGE.sort
        )
        .filter(T_B2B_GOODS_IMAGE.guid == uid)
        .order_by(T_B2B_GOODS_IMAGE.sort.asc())
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    return rows

def option_list(request: Request, uid: int):
    request.state.inspect = frame()
    db_scm = request.state.db_scm
    
    sql = (
        db_scm.query(
             T_B2B_GOODS_INFO.uid
            ,T_B2B_GOODS_INFO.guid
            ,T_B2B_GOODS_INFO.option_title
            ,T_B2B_GOODS_INFO.option_num
            ,T_B2B_GOODS_INFO.option_type
            ,T_B2B_GOODS_INFO.placeholder
            ,T_B2B_GOODS_INFO.option_yn
        )
        .filter(T_B2B_GOODS_INFO.guid == uid)
        .order_by(T_B2B_GOODS_INFO.option_num.asc())
    )

    # format_sql(sql)
    
    rows = []
    for c in sql.all():
        list = dict(zip(c.keys(), c))
        # if list["option_type"] == 'C' or list["option_type"] == 'D' :
        #     placeholder = list["placeholder"].split(',')
        #     placeholder.pop()
        #     list["placeholder"] = placeholder

        rows.append(list)

    return rows


# b2b상품_편집 - goods_create
def goods_create(request: Request, b2bGoodsInput: B2BGoodsInput):
    request.state.inspect = frame()
    db_scm = request.state.db_scm
    user = request.state.user

    option_val = b2bGoodsInput.option_value.split(',')
    cnt = 0
    for ov in option_val :
       cnt = cnt+1 

    db_item = T_B2B_GOODS (
         seller_id = b2bGoodsInput.seller_id
        ,seller_name = b2bGoodsInput.seller_name
        ,service_type = b2bGoodsInput.service_type
        ,sort = b2bGoodsInput.sort
        ,is_display = b2bGoodsInput.is_display
        ,start_date = b2bGoodsInput.start_date if b2bGoodsInput.start_date != "" else None
        ,end_date = b2bGoodsInput.end_date if b2bGoodsInput.end_date != "" else None
        ,category = b2bGoodsInput.category
        ,title = b2bGoodsInput.title
        ,sub_title = b2bGoodsInput.sub_title if b2bGoodsInput.sub_title != "" else None
        ,contents = b2bGoodsInput.contents
        ,benefit = b2bGoodsInput.benefit
        ,attention = b2bGoodsInput.attention
        ,keyword = b2bGoodsInput.keyword if b2bGoodsInput.keyword != "" else None
        ,str_market_price = b2bGoodsInput.str_market_price
        ,str_price = b2bGoodsInput.str_price
        ,market_price = b2bGoodsInput.str_market_price
        ,price = b2bGoodsInput.str_price
        ,commission_type = b2bGoodsInput.commission_type
        ,commission = b2bGoodsInput.commission
        ,str_sale_percent = b2bGoodsInput.str_sale_percent
        ,option_value = b2bGoodsInput.option_value
        ,thumb = b2bGoodsInput.thumb
        ,option_yn = b2bGoodsInput.goods_option_yn # option_value 에 값이 있을 때 T
        ,other_service = b2bGoodsInput.other_service if b2bGoodsInput.other_service != "" else None #추가상품
        ,option_cnt = cnt 
    )
    db_scm.add(db_item)
    db_scm.flush()

    if b2bGoodsInput.memo != '' and b2bGoodsInput.memo != 'undefined':
        log_scm_service.create_memo(request, db_item.uid, "T_B2B_GOODS", b2bGoodsInput.memo, user.user_id, user.token_name, 'ADMIN', None)
        request.state.inspect = frame()
    
    log_scm_service.create_log(request, db_item.uid, "T_B2B_GOODS", "INSERT", "b2b 등록", 0, db_item.uid, user.user_id)
    request.state.inspect = frame()

    return db_item

# b2b상품_편집 - etc_image_create
def etc_image_create(request: Request, etc_images:object, guid:int):
    request.state.inspect = frame()
    db_scm = request.state.db_scm
    user = request.state.user
    
    etc_images_i = 0 
    for image in etc_images:
        image["sort"] = etc_images_i+1
        db_item = T_B2B_GOODS_IMAGE (
            guid = guid
            ,img_url = image["img_url"]
            ,sort = etc_images_i + 1
        )
        db_scm.add(db_item)
        db_scm.flush()

        log_scm_service.create_log(request, db_item.guid, "T_B2B_GOODS_IMAGE", "INSERT", "등록", 0, db_item.guid, user.user_id)
        request.state.inspect = frame()

    return

# b2b상품_편집 - option_list_create
def option_list_create(request: Request, option_list:object, guid:int):
    request.state.inspect = frame()
    db_scm = request.state.db_scm
    user = request.state.user

    for option in option_list :
        if str(type(option["placeholder"])) == "<class 'list'>" :
            result = ""
            for word in option["placeholder"] :
                result += word + ","
            option["placeholder"] = result

        db_item = T_B2B_GOODS_INFO (
            guid = guid
            ,option_num = option["option_num"]
            ,option_type = option["option_type"]
            ,option_title = option["option_title"]
            ,option_yn = option["option_yn"]
            ,placeholder = option["placeholder"]
        )
        db_scm.add(db_item)
        db_scm.flush()
        
        log_scm_service.create_log(request, db_item.guid, "T_B2B_GOODS_INFO", "INSERT", "등록", 0, db_item.uid, user.user_id)
        request.state.inspect = frame()

    return


# b2b상품_편집 - goods_update  
def goods_update(request: Request, b2bGoodsInput: B2BGoodsInput):
    request.state.inspect = frame()
    db_scm = request.state.db_scm
    user = request.state.user
    
    res = db_scm.query(T_B2B_GOODS).filter(T_B2B_GOODS.uid == b2bGoodsInput.uid).first()
    if res is None :
        return ex.ReturnOK(404, "죄송합니다. 오류가 발생 하였습니다. 문제 지속시 개발자에게 접수 바랍니다.", request)
    
    if b2bGoodsInput.memo != '' and b2bGoodsInput.memo != 'undefined':
        log_scm_service.create_memo(request, b2bGoodsInput.uid, "T_B2B_GOODS", b2bGoodsInput.memo, user.user_id, user.token_name, 'ADMIN', None)
        request.state.inspect = frame()
        
    if b2bGoodsInput.seller_id is not None and res.seller_id != b2bGoodsInput.seller_id : 
        log_scm_service.create_log(request, res.uid, "T_B2B_GOODS", "seller_id", "판매자아이디", res.seller_id, b2bGoodsInput.seller_id, user.user_id)
        request.state.inspect = frame()
        res.seller_id = b2bGoodsInput.seller_id
        
    if b2bGoodsInput.seller_name is not None and res.seller_name != b2bGoodsInput.seller_name : 
        log_scm_service.create_log(request, res.uid, "T_B2B_GOODS", "seller_name", "판매자명", res.seller_name, b2bGoodsInput.seller_name, user.user_id)
        request.state.inspect = frame()
        res.seller_name = b2bGoodsInput.seller_name
    
    if b2bGoodsInput.service_type is not None and res.service_type != b2bGoodsInput.service_type : 
        log_scm_service.create_log(request, res.uid, "T_B2B_GOODS", "service_type", "서비스구분", res.service_type, b2bGoodsInput.service_type, user.user_id)
        request.state.inspect = frame()
        res.service_type = b2bGoodsInput.service_type
    
    if b2bGoodsInput.sort is not None and res.sort != b2bGoodsInput.sort : 
        log_scm_service.create_log(request, res.uid, "T_B2B_GOODS", "sort", "진열순서", res.sort, b2bGoodsInput.sort, user.user_id)
        request.state.inspect = frame()
        res.sort = b2bGoodsInput.sort
    
    if b2bGoodsInput.is_display is not None and res.is_display != b2bGoodsInput.is_display : 
        log_scm_service.create_log(request, res.uid, "T_B2B_GOODS", "is_display", "진열여부", res.is_display, b2bGoodsInput.is_display, user.user_id)
        request.state.inspect = frame()
        res.is_display = b2bGoodsInput.is_display
    
    if res.start_date != b2bGoodsInput.start_date : 
        log_scm_service.create_log(request, res.uid, "T_B2B_GOODS", "start_date", "판매기간_시작일", res.start_date, b2bGoodsInput.start_date, user.user_id)
        request.state.inspect = frame()
        res.start_date = b2bGoodsInput.start_date if b2bGoodsInput.start_date != "" else None
    
    if res.end_date != b2bGoodsInput.end_date : 
        log_scm_service.create_log(request, res.uid, "T_B2B_GOODS", "end_date", "판매기간_종료일", res.end_date, b2bGoodsInput.end_date, user.user_id)
        request.state.inspect = frame()
        res.end_date = b2bGoodsInput.end_date if b2bGoodsInput.end_date != "" else None
    
    if b2bGoodsInput.category is not None and res.category != b2bGoodsInput.category : 
        log_scm_service.create_log(request, res.uid, "T_B2B_GOODS", "category", "카테고리", res.category, b2bGoodsInput.category, user.user_id)
        request.state.inspect = frame()
        res.category = b2bGoodsInput.category
    
    if b2bGoodsInput.title is not None and res.title != b2bGoodsInput.title : 
        log_scm_service.create_log(request, res.uid, "T_B2B_GOODS", "title", "상품명", res.title, b2bGoodsInput.title, user.user_id)
        request.state.inspect = frame()
        res.title = b2bGoodsInput.title
    
    if b2bGoodsInput.sub_title is not None and res.sub_title != b2bGoodsInput.sub_title : 
        log_scm_service.create_log(request, res.uid, "T_B2B_GOODS", "sub_title", "서브타이틀", res.sub_title, b2bGoodsInput.sub_title, user.user_id)
        request.state.inspect = frame()
        res.sub_title = b2bGoodsInput.sub_title if b2bGoodsInput.sub_title != "" else None
        
    if b2bGoodsInput.contents is not None and res.contents != b2bGoodsInput.contents : 
        log_scm_service.create_log(request, res.uid, "T_B2B_GOODS", "contents", "상세설명", res.contents, b2bGoodsInput.contents, user.user_id)
        request.state.inspect = frame()
        res.contents = b2bGoodsInput.contents
        
    if b2bGoodsInput.benefit is not None and res.benefit != b2bGoodsInput.benefit : 
        log_scm_service.create_log(request, res.uid, "T_B2B_GOODS", "benefit", "복지드림멤버십혜택", res.benefit, b2bGoodsInput.benefit, user.user_id)
        request.state.inspect = frame()
        res.benefit = b2bGoodsInput.benefit
        
    if b2bGoodsInput.attention is not None and res.attention != b2bGoodsInput.attention : 
        log_scm_service.create_log(request, res.uid, "T_B2B_GOODS", "attention", "유의사항", res.attention, b2bGoodsInput.attention, user.user_id)
        request.state.inspect = frame()
        res.attention = b2bGoodsInput.attention
    
    if b2bGoodsInput.keyword is not None and res.keyword != b2bGoodsInput.keyword : 
        log_scm_service.create_log(request, res.uid, "T_B2B_GOODS", "keyword", "키워드", res.keyword, b2bGoodsInput.keyword, user.user_id)
        request.state.inspect = frame()
        res.keyword = b2bGoodsInput.keyword if b2bGoodsInput.keyword != "" else None
    
    if b2bGoodsInput.str_market_price is not None and res.str_market_price != b2bGoodsInput.str_market_price : 
        log_scm_service.create_log(request, res.uid, "T_B2B_GOODS", "str_market_price", "정가(문자열)", res.str_market_price, b2bGoodsInput.str_market_price, user.user_id)
        request.state.inspect = frame()
        log_scm_service.create_log(request, res.uid, "T_B2B_GOODS", "market_price", "정가", res.market_price, b2bGoodsInput.str_market_price, user.user_id)
        request.state.inspect = frame()

        res.market_price = int(b2bGoodsInput.str_market_price)
        res.str_market_price = b2bGoodsInput.str_market_price
    
    if b2bGoodsInput.str_price is not None and res.str_price != b2bGoodsInput.str_price : 
        log_scm_service.create_log(request, res.uid, "T_B2B_GOODS", "str_price", "판매가(문자열)", res.str_price, b2bGoodsInput.str_price, user.user_id)
        request.state.inspect = frame()
        log_scm_service.create_log(request, res.uid, "T_B2B_GOODS", "price", "판매가", res.price, b2bGoodsInput.str_price, user.user_id)
        request.state.inspect = frame()

        res.price = int(b2bGoodsInput.str_price)
        res.str_price = b2bGoodsInput.str_price


    if b2bGoodsInput.commission_type is not None and res.commission_type != b2bGoodsInput.commission_type : 
        log_scm_service.create_log(request, res.uid, "T_B2B_GOODS", "commission_type", "복지드림_수수료_타입", res.commission_type, b2bGoodsInput.commission_type, user.user_id)
        request.state.inspect = frame()
        res.commission_type = b2bGoodsInput.commission_type
    
    if b2bGoodsInput.commission is not None and res.commission != b2bGoodsInput.commission : 
        log_scm_service.create_log(request, res.uid, "T_B2B_GOODS", "commission", "복지드림_수수료", res.commission, b2bGoodsInput.commission, user.user_id)
        request.state.inspect = frame()
        res.commission = b2bGoodsInput.commission
    
    if b2bGoodsInput.str_sale_percent is not None and res.str_sale_percent != b2bGoodsInput.str_sale_percent : 
        log_scm_service.create_log(request, res.uid, "T_B2B_GOODS", "str_sale_percent", "할인율(문자열)", res.str_sale_percent, b2bGoodsInput.str_sale_percent, user.user_id)
        request.state.inspect = frame()
        res.str_sale_percent = b2bGoodsInput.str_sale_percent
    
    if b2bGoodsInput.option_value is not None and res.option_value != b2bGoodsInput.option_value : 
        option_val = b2bGoodsInput.option_value.split(',')
        cnt = 0
        for ov in option_val :
            cnt = cnt+1 

        log_scm_service.create_log(request, res.uid, "T_B2B_GOODS", "option_value", "옵션", res.option_value, b2bGoodsInput.option_value, user.user_id)
        request.state.inspect = frame()

        res.option_value = b2bGoodsInput.option_value
        res.option_cnt = cnt
    
    if b2bGoodsInput.thumb is not None and res.thumb != b2bGoodsInput.thumb : 
        log_scm_service.create_log(request, res.uid, "T_B2B_GOODS", "thumb", "메인이미지", res.thumb, b2bGoodsInput.thumb, user.user_id)
        request.state.inspect = frame()
        res.thumb = b2bGoodsInput.thumb
    
    if b2bGoodsInput.goods_option_yn is not None and res.option_yn != b2bGoodsInput.goods_option_yn : 
        log_scm_service.create_log(request, res.uid, "T_B2B_GOODS", "goods_option_yn", "옵션사용여부", res.option_yn, b2bGoodsInput.goods_option_yn, user.user_id)
        request.state.inspect = frame()
        res.option_yn = b2bGoodsInput.goods_option_yn
    
    if res.other_service != b2bGoodsInput.other_service : 
        log_scm_service.create_log(request, res.uid, "T_B2B_GOODS", "other_service", "추가상품", res.other_service, b2bGoodsInput.other_service, user.user_id)
        request.state.inspect = frame()
        res.other_service = b2bGoodsInput.other_service if b2bGoodsInput.other_service != "" else None
    
    res.update_at = util.getNow()
    return res

# b2b상품_편집 - option_list_update  
def option_list_update(request: Request, b2bGoodsInput: B2BGoodsInput):
    request.state.inspect = frame()
    db_scm = request.state.db_scm
    user = request.state.user

    res = db_scm.query(T_B2B_GOODS_INFO).filter(T_B2B_GOODS_INFO.guid == b2bGoodsInput.uid).all()

    if res is None :
        return ex.ReturnOK(404, "죄송합니다. 오류가 발생 하였습니다. 문제 지속시 개발자에게 접수 바랍니다.", request)
    
    a1 = []
    for row in res :
        a1.append(row.uid)
    a2 = []
    for row in b2bGoodsInput.option_list :
        a2.append(row["uid"])

    diffrent_uid = set(a1) - set(a2)
    for diffuid in diffrent_uid :
        for row in res :
            if row.uid == diffuid :
                db_item = db_scm.query(T_B2B_GOODS_INFO).filter(T_B2B_GOODS_INFO.uid == row.uid).first()
                db_scm.delete(db_item)
                db_scm.commit()
                log_scm_service.create_log(request, row.guid, "T_B2B_GOODS_INFO", "DELETE", "삭제", row.uid, 0, user.user_id)
                request.state.inspect = frame()

    # 등록 할거 등록(업뎃할때 등록)    
    for inp in b2bGoodsInput.option_list :
        if inp["uid"] == 0 :
            if type(inp["placeholder"]) == list :
                result = ""
                for word in inp["placeholder"] :
                    result += word + ","
                inp["placeholder"] = result

            db_item = T_B2B_GOODS_INFO (
                 guid = b2bGoodsInput.uid
                ,option_num = inp["option_num"]
                ,option_type = inp["option_type"]
                ,option_title = inp["option_title"]
                ,option_yn = inp["option_yn"]
                ,placeholder = inp["placeholder"]
            )
            db_scm.add(db_item)
            db_scm.flush()

            log_scm_service.create_log(request, db_item.guid, "T_B2B_GOODS_INFO", "INSERT", "등록", 0, db_item.uid, user.user_id)
            request.state.inspect = frame()

    return res

# b2b상품_편집 - etc_image_update  
def etc_image_update(request: Request, b2bGoodsInput: B2BGoodsInput):
    request.state.inspect = frame()
    db_scm = request.state.db_scm
    user = request.state.user

    res = db_scm.query(T_B2B_GOODS_IMAGE.sort, T_B2B_GOODS_IMAGE.img_url).filter(T_B2B_GOODS_IMAGE.guid == b2bGoodsInput.uid).all()

    if res is None :
        return ex.ReturnOK(404, "죄송합니다. 오류가 발생 하였습니다. 문제 지속시 개발자에게 접수 바랍니다.", request)
    
    cnt = (
        db_scm.query(T_B2B_GOODS_IMAGE)
        .filter(T_B2B_GOODS_IMAGE.guid == b2bGoodsInput.uid)
        .count()
    )
        
    a1 = []
    for row in res :
        a1.append(row.img_url)

    a2 = []
    for row in b2bGoodsInput.etc_images :
        a2.append(row["img_url"])

    if len(b2bGoodsInput.etc_images) != cnt or a1 != a2 :
        db_item = db_scm.query(T_B2B_GOODS_IMAGE).filter(T_B2B_GOODS_IMAGE.guid == b2bGoodsInput.uid).all()
        for item in db_item :
            db_scm.delete(item)
            db_scm.commit()
        log_scm_service.create_log(request, b2bGoodsInput.uid, "T_B2B_GOODS_IMAGE", "DELETE", "삭제", b2bGoodsInput.uid, 0, user.user_id)
        request.state.inspect = frame()

        etc_image_create(request, b2bGoodsInput.etc_images, b2bGoodsInput.uid)
        request.state.inspect = frame()

    return res