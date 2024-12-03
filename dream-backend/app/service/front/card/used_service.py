from fastapi import Request
from inspect import currentframe as frame
from app.core.database import format_sql
from sqlalchemy import func, select, update, delete, Table, MetaData, and_, literal_column
from app.core import util
import math
import random

from app.schemas.schema import *
from app.schemas.manager.point.offcard.used import *
from app.models.offcard.used import *
from app.models.limit.industry import *
from app.models.member import *
from app.service.log_service import *
from app.models.point.point import *
from app.models.point.sikwon import *
from app.core import exceptions as ex


# 복지카드 사용 내역
def offcard_used_list(request: Request, cardUsedListInput: CardUsedListInput, user: T_MEMBER):
    request.state.inspect = frame()
    db = request.state.db

    filters = []
    filters.append(getattr(T_CARD_USED, "delete_at") == None)
    filters.append(getattr(T_CARD_USED, "user_id") == cardUsedListInput.user_id)
    filters.append(getattr(T_CARD_USED, "state") == None)

    if cardUsedListInput.filters :
        if cardUsedListInput.filters["create_at"]["startDate"] and cardUsedListInput.filters["create_at"]["endDate"] :
            filters.append(
                and_(
                    func.date_format(T_CARD_USED.APV_D, '%Y-%m-%d').label('APV_D') >= cardUsedListInput.filters["create_at"]["startDate"]
                    ,func.date_format(T_CARD_USED.APV_D, '%Y-%m-%d').label('APV_D') <= cardUsedListInput.filters["create_at"]["endDate"] + " 23:59:59"
                )
            )
    industry_stmt = (
        db.query(
             T_INDUSTRY_OFFCARD.uid
            ,T_INDUSTRY_OFFCARD.code
        )
        .filter(T_INDUSTRY_OFFCARD.partner_uid == user.partner_uid)
        .subquery()
    )

    sql = (
        db.query(
             T_CARD_USED.uid
            ,func.date_format(T_CARD_USED.APV_D, '%Y-%m-%d').label('APV_D')
            ,T_CARD_USED.RY_CCD
            ,T_CARD_USED.MCT_NM
            ,T_CARD_USED.SEA
            ,literal_column("'신한카드'").label('card_name')
        )
        .join (
            industry_stmt, 
            T_CARD_USED.RY_CCD == industry_stmt.c.code
        )
        .filter(*filters)
        .order_by(T_CARD_USED.uid.desc())
        .offset((cardUsedListInput.page-1)*cardUsedListInput.page_view_size)
        .limit(cardUsedListInput.page_view_size)
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    # [ S ] 페이징 처리
    cardUsedListInput.page_total = (db.query(T_CARD_USED).join (industry_stmt, T_CARD_USED.RY_CCD == industry_stmt.c.code).filter(*filters).count())
    cardUsedListInput.page_last = math.ceil(cardUsedListInput.page_total / cardUsedListInput.page_view_size)
    cardUsedListInput.page_size = len(rows) # 현재 페이지에 검색된 수
    # [ E ] 페이징 처리

    jsondata = {}
    jsondata.update({"params" : cardUsedListInput})
    jsondata.update({"list": rows})

    return jsondata

# 카드 사용 복지포인트 차감신청 내역
def request_offcard_point_deduct(request: Request, cardUsedInput: CardUsedInput, user: T_MEMBER):
    request.state.inspect = frame()
    db = request.state.db

    for deduct_info in cardUsedInput.deduct_list :

        res_card = db.query(T_CARD_USED).filter(T_CARD_USED.uid == deduct_info.card_used_uid, T_CARD_USED.state == None).first()
        
        db_item = T_POINT_DEDUCT (
            card_used_uid = deduct_info.card_used_uid
            ,use_type = 'bokji'
            ,partner_uid = user.partner_uid
            ,partner_id = user.partner_id
            ,user_uid = user.uid
            ,user_id = user.user_id
            ,confirm_at = util.getNow()
            ,detail = res_card.MCT_NM
            ,request_point = deduct_info.request_point
            ,confirm_point = deduct_info.request_point
            ,card = "신한카드"
            ,state = "차감완료"
        )
        db.add(db_item)
        db.flush()

        create_log(request, db_item.uid, "T_POINT_DEDUCT", "INSERT", "카드사용 포인트 차감신청", 0, db_item.uid, user.user_id)
        request.state.inspect = frame()

        res_point = (
            db.query(T_POINT)
            .filter(
                T_POINT.user_id == user.user_id,
                T_POINT.point > 0
            )
        )
        format_sql(res_point)
        
        for c in res_point.all() :
            if deduct_info.request_point > 0 :
                # 회수할 포인트보다 잔여포인트가 같거나 크면
                if c.point >= deduct_info.request_point :
                    befor_point = c.point 
                    c.point = c.point-deduct_info.request_point

                    db_item = T_POINT_USED (
                            point_id = c.uid
                        ,used_type = "3"
                        ,used_point = deduct_info.request_point
                        ,order_no = "C" + str(random.randrange(1111111,9999999))
                        ,reason = "카드차감"
                        ,user_id = user.user_id
                        ,partner_uid = user.partner_uid
                        ,partner_id = user.partner_id
                    )
                    db.add(db_item)
                    db.flush()

                    deduct_info.request_point = 0
                
                    create_log(request, c.uid, "T_POINT", "UPDATE", "복지카드 포인트 차감신청", str(befor_point), str(c.point), user.user_id)
                    request.state.inspect = frame()
                else :
                    befor_point = c.point
                    deduct_info.request_point = deduct_info.request_point - c.point
                    db_item = T_POINT_USED (
                            point_id = c.uid
                        ,used_type = "3"
                        ,used_point = c.point
                        ,order_no = "C" + str(random.randrange(1111111,9999999))
                        ,reason = "카드차감"
                        ,user_id = user.user_id
                        ,partner_uid = user.partner_uid
                        ,partner_id = user.partner_id
                    )
                    db.add(db_item)
                    db.flush()
                    
                    c.point = 0
                
                    create_log(request, c.uid, "T_POINT", "UPDATE", "복지카드 포인트 차감신청", str(befor_point), str(c.point), user.user_id)
                    request.state.inspect = frame()

        res_card.state = "차감신청완료"

    return 1
    

# 식권카드 사용 내역
def sikwon_used_list(request: Request, cardUsedListInput: CardUsedListInput, user: T_MEMBER):
    request.state.inspect = frame()
    db = request.state.db

    filters = []
    filters.append(getattr(T_CARD_USED, "delete_at") == None)
    filters.append(getattr(T_CARD_USED, "user_id") == cardUsedListInput.user_id)
    filters.append(getattr(T_CARD_USED, "state") == None)

    if cardUsedListInput.filters :
        if cardUsedListInput.filters["create_at"]["startDate"] and cardUsedListInput.filters["create_at"]["endDate"] :
            filters.append(
                and_(
                    T_CARD_USED.create_at >= cardUsedListInput.filters["create_at"]["startDate"]
                    ,T_CARD_USED.create_at <= cardUsedListInput.filters["create_at"]["endDate"] + " 23:59:59"
                )
            )
    industry_stmt = (
        db.query(
             T_INDUSTRY_SIKWON.uid
            ,T_INDUSTRY_SIKWON.code
            ,T_INDUSTRY_CODE.name
        )
        .join (
            T_INDUSTRY_CODE, 
            T_INDUSTRY_CODE.code == T_INDUSTRY_SIKWON.code
        )
        .filter(T_INDUSTRY_SIKWON.partner_uid == user.partner_uid)
        .subquery()
    )

    sql = (
        db.query(
             T_CARD_USED.uid
            ,func.date_format(T_CARD_USED.APV_D, '%Y-%m-%d').label('APV_D')
            ,T_CARD_USED.RY_CCD
            ,T_CARD_USED.MCT_NM
            ,T_CARD_USED.SEA
            ,literal_column("'신한카드'").label('card_name')
            ,industry_stmt.c.name
        )
        .join (
            industry_stmt, 
            T_CARD_USED.RY_CCD == industry_stmt.c.code
        )
        .filter(*filters)
        .order_by(T_CARD_USED.uid.desc())
        .offset((cardUsedListInput.page-1)*cardUsedListInput.page_view_size)
        .limit(cardUsedListInput.page_view_size)
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    # [ S ] 페이징 처리
    cardUsedListInput.page_total = (db.query(T_CARD_USED).filter(*filters).count())
    cardUsedListInput.page_last = math.ceil(cardUsedListInput.page_total / cardUsedListInput.page_view_size)
    cardUsedListInput.page_size = len(rows) # 현재 페이지에 검색된 수
    # [ E ] 페이징 처리

    jsondata = {}
    jsondata.update({"params" : cardUsedListInput})
    jsondata.update({"list": rows})

    return jsondata


# 카드 사용 식권포인트 차감신청 내역
def request_sikwon_point_deduct(request: Request, cardUsedInput: CardUsedInput, user: T_MEMBER):
    request.state.inspect = frame()
    db = request.state.db

    for deduct_info in cardUsedInput.deduct_list :

        res_card = db.query(T_CARD_USED).filter(T_CARD_USED.uid == deduct_info.card_used_uid, T_CARD_USED.state == None).first()
        
        db_item = T_POINT_DEDUCT (
            card_used_uid = deduct_info.card_used_uid
            ,use_type = 'sikwon'
            ,partner_uid = user.partner_uid
            ,partner_id = user.partner_id
            ,user_uid = user.uid
            ,user_id = user.user_id
            ,confirm_at = util.getNow()
            ,detail = res_card.MCT_NM
            ,request_point = deduct_info.request_point
            ,confirm_point = deduct_info.request_point
            ,card = "신한카드"
            ,state = "차감완료"
        )
        db.add(db_item)
        db.flush()

        create_log(request, db_item.uid, "T_POINT_DEDUCT", "INSERT", "카드사용 포인트 차감신청", 0, db_item.uid, user.user_id)
        request.state.inspect = frame()

        res_point = (
            db.query(T_SIKWON)
            .filter(
                T_SIKWON.user_id == user.user_id,
                T_SIKWON.point > 0
            )
        )
        format_sql(res_point)

        for c in res_point.all() :
            if deduct_info.request_point > 0 :

                # 회수할 포인트보다 잔여포인트가 같거나 크면
                if c.point >= deduct_info.request_point : 
                    befor_point = c.point
                    c.point = c.point-deduct_info.request_point

                    db_item = T_SIKWON_USED (
                            point_id = c.uid
                        ,used_type = "3"
                        ,used_point = deduct_info.request_point
                        ,order_no = "C" + str(random.randrange(1111111,9999999))
                        ,reason = "카드차감"
                        ,user_id = user.user_id
                        ,partner_uid = user.partner_uid
                        ,partner_id = user.partner_id
                    )
                    db.add(db_item)
                    db.flush()

                    deduct_info.request_point = 0
                
                    create_log(request, c.uid, "T_SIKWON", "UPDATE", "식권카드 포인트 차감신청", str(befor_point), str(c.point), user.user_id)
                    request.state.inspect = frame()
                else :
                    befor_point = c.point
                    deduct_info.request_point = deduct_info.request_point - c.point
                    db_item = T_SIKWON_USED (
                            point_id = c.uid
                        ,used_type = "3"
                        ,used_point = c.point
                        ,order_no = "C" + str(random.randrange(1111111,9999999))
                        ,reason = "카드차감"
                        ,user_id = user.user_id
                        ,partner_uid = user.partner_uid
                        ,partner_id = user.partner_id
                    )
                    db.add(db_item)
                    db.flush()
                    
                    c.point = 0
                
                    create_log(request, c.uid, "T_SIKWON", "UPDATE", "식권카드 포인트 차감신청", str(befor_point), str(c.point), user.user_id)
                    request.state.inspect = frame()

        res_card.state = "차감신청완료"

    return 1
    







# 회원 정보
def get_user_info(request: Request, user_id: str):
    request.state.inspect = frame()
    db = request.state.db
    return db.query(T_MEMBER).filter(T_MEMBER.user_id == user_id).first()

# USER_ID로 USER_CI 가져오기
def get_ci_from_id(request: Request, user_id: str):
    request.state.inspect = frame()
    db = request.state.db
    return (
        db.query(
            T_MEMBER_INFO.user_ci
            ,T_MEMBER_INFO.user_id
            ,T_MEMBER_INFO.partner_uid
            ,T_MEMBER_INFO.partner_id
        )
        .filter(T_MEMBER_INFO.user_id == user_id)
        .first()
    ) 

# # 카드 사용 포인트 차감신청 내역
# def request_point_deduct(request: Request, cardUsedInput: CardUsedInput, user: T_MEMBER):
#     request.state.inspect = frame()
#     db = request.state.db

#     for deduct_info in cardUsedInput.deduct_list :

#         res_card = db.query(T_CARD_USED).filter(T_CARD_USED.uid == deduct_info.card_used_uid, T_CARD_USED.state == None).first()
        
#         db_item = T_POINT_DEDUCT (
#             card_used_uid = deduct_info.card_used_uid
#             ,use_type = cardUsedInput.use_type
#             ,partner_uid = user.partner_uid
#             ,partner_id = user.partner_id
#             ,user_uid = user.uid
#             ,user_id = user.user_id
#             ,confirm_at = util.getNow()
#             ,detail = res_card.MCT_NM
#             ,request_point = deduct_info.request_point
#             ,confirm_point = deduct_info.request_point
#             ,card = "신한카드"
#             ,state = "차감완료"
#         )
#         db.add(db_item)
#         db.flush()

#         create_log(request, db_item.uid, "T_POINT_DEDUCT", "INSERT", "카드사용 포인트 차감신청", 0, db_item.uid, user.user_id)
#         request.state.inspect = frame()

#         if cardUsedInput.use_type == "bokji" :
#             res_point = (
#                 db.query(T_POINT)
#                 .filter(
#                     T_POINT.user_id == user.user_id,
#                     T_POINT.point > 0
#                 )
#             )
#             format_sql(res_point)
            
#             for c in res_point.all() :
#                 if deduct_info.request_point > 0 :

#                     # 회수할 포인트보다 잔여포인트가 같거나 크면
#                     if c.point >= deduct_info.request_point :
#                         befor_point = c.point 
#                         c.point = c.point-deduct_info.request_point

#                         db_item = T_POINT_USED (
#                              point_id = c.uid
#                             ,used_type = "3"
#                             ,used_point = deduct_info.request_point
#                             ,order_no = "C" + str(random.randrange(1111111,9999999))
#                             ,reason = "카드차감"
#                             ,user_id = user.user_id
#                             ,partner_uid = user.partner_uid
#                             ,partner_id = user.partner_id
#                         )
#                         db.add(db_item)
#                         db.flush()

#                         deduct_info.request_point = 0
                    
#                         create_log(request, c.uid, "T_POINT", "UPDATE", "복지카드 포인트 차감신청", str(befor_point), str(c.point), user.user_id)
#                         request.state.inspect = frame()
#                     else :
#                         befor_point = c.point
#                         deduct_info.request_point = deduct_info.request_point - c.point
#                         db_item = T_POINT_USED (
#                              point_id = c.uid
#                             ,used_type = "3"
#                             ,used_point = c.point
#                             ,order_no = "C" + str(random.randrange(1111111,9999999))
#                             ,reason = "카드차감"
#                             ,user_id = user.user_id
#                             ,partner_uid = user.partner_uid
#                             ,partner_id = user.partner_id
#                         )
#                         db.add(db_item)
#                         db.flush()
                        
#                         c.point = 0
                    
#                         create_log(request, c.uid, "T_POINT", "UPDATE", "복지카드 포인트 차감신청", str(befor_point), str(c.point), user.user_id)
#                         request.state.inspect = frame()

#             res_card.state = "차감신청완료"

#         elif cardUsedInput.use_type == "sikwon" :
#             res_point = (
#                 db.query(T_SIKWON)
#                 .filter(
#                     T_SIKWON.user_id == user.user_id,
#                     T_SIKWON.point > 0
#                 )
#             )
#             format_sql(res_point)

#             for c in res_point.all() :
#                 if deduct_info.request_point > 0 :

#                     # 회수할 포인트보다 잔여포인트가 같거나 크면
#                     if c.point >= deduct_info.request_point : 
#                         befor_point = c.point
#                         c.point = c.point-deduct_info.request_point

#                         db_item = T_SIKWON_USED (
#                              point_id = c.uid
#                             ,used_type = "3"
#                             ,used_point = deduct_info.request_point
#                             ,order_no = "C" + str(random.randrange(1111111,9999999))
#                             ,reason = "카드차감"
#                             ,user_id = user.user_id
#                             ,partner_uid = user.partner_uid
#                             ,partner_id = user.partner_id
#                         )
#                         db.add(db_item)
#                         db.flush()

#                         deduct_info.request_point = 0
                    
#                         create_log(request, c.uid, "T_SIKWON", "UPDATE", "식권카드 포인트 차감신청", str(befor_point), str(c.point), user.user_id)
#                         request.state.inspect = frame()
#                     else :
#                         befor_point = c.point
#                         deduct_info.request_point = deduct_info.request_point - c.point
#                         db_item = T_SIKWON_USED (
#                              point_id = c.uid
#                             ,used_type = "3"
#                             ,used_point = c.point
#                             ,order_no = "C" + str(random.randrange(1111111,9999999))
#                             ,reason = "카드차감"
#                             ,user_id = user.user_id
#                             ,partner_uid = user.partner_uid
#                             ,partner_id = user.partner_id
#                         )
#                         db.add(db_item)
#                         db.flush()
                        
#                         c.point = 0
                    
#                         create_log(request, c.uid, "T_SIKWON", "UPDATE", "식권카드 포인트 차감신청", str(befor_point), str(c.point), user.user_id)
#                         request.state.inspect = frame()

#         res_card.state = "차감신청완료"

#     return 1
    
# 카드사용 포인트 차감내역
def deduct_list(request: Request, cardDeductListInput: CardDeductListInput):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    filters = []
    filters.append(getattr(T_POINT_DEDUCT, "delete_at") == None)
    filters.append(getattr(T_POINT_DEDUCT, "user_id") == cardDeductListInput.user_id)

    if cardDeductListInput.filters :
        if cardDeductListInput.filters["create_at"]["startDate"] and cardDeductListInput.filters["create_at"]["endDate"] :
            filters.append(
                and_(
                    T_POINT_DEDUCT.create_at >= cardDeductListInput.filters["create_at"]["startDate"]
                    ,T_POINT_DEDUCT.create_at <= cardDeductListInput.filters["create_at"]["endDate"] + " 23:59:59"
                )
            )
        if cardDeductListInput.filters["confirm_at"]["startDate"] and cardDeductListInput.filters["confirm_at"]["endDate"] :
            filters.append(
                and_(
                    T_POINT_DEDUCT.confirm_at >= cardDeductListInput.filters["confirm_at"]["startDate"]
                    ,T_POINT_DEDUCT.confirm_at <= cardDeductListInput.filters["confirm_at"]["endDate"] + " 23:59:59"
                )
            )
        if cardDeductListInput.filters["point_state"] :
            filters.append(T_POINT_DEDUCT.state == cardDeductListInput.filters["point_state"])

    sql = (
        db.query(
             func.date_format(T_POINT_DEDUCT.create_at, '%Y-%m-%d').label('create_at')
            ,func.date_format(T_POINT_DEDUCT.confirm_at, '%Y-%m-%d').label('confirm_at')
            ,T_POINT_DEDUCT.uid
            ,T_POINT_DEDUCT.use_type
            ,T_POINT_DEDUCT.detail
            ,T_POINT_DEDUCT.request_point
            ,T_POINT_DEDUCT.confirm_point
            ,T_POINT_DEDUCT.card
            ,T_POINT_DEDUCT.state
            ,T_POINT_DEDUCT.note
        )
        .filter(*filters)
        .order_by(T_POINT_DEDUCT.uid.desc())
        .offset((cardDeductListInput.page-1)*cardDeductListInput.page_view_size)
        .limit(cardDeductListInput.page_view_size)
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    # [ S ] 페이징 처리
    cardDeductListInput.page_total = (db.query(T_POINT_DEDUCT).filter(*filters).count())
    cardDeductListInput.page_last = math.ceil(cardDeductListInput.page_total / cardDeductListInput.page_view_size)
    cardDeductListInput.page_size = len(rows) # 현재 페이지에 검색된 수
    # [ E ] 페이징 처리

    jsondata = {}
    jsondata.update({"params" : cardDeductListInput})
    jsondata.update({"list": rows})

    return jsondata 
    
