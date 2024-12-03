from fastapi import Request
from inspect import currentframe as frame
from app.core.database import format_sql
from app.core import exceptions as ex
from sqlalchemy import func, select, update, delete, Table, MetaData, and_
from app.core import util
import math

from app.schemas.schema import *
from app.schemas.manager.point.limit.industry import *
from app.models.limit.industry import *
from app.service.log_service import *

# 복지카드 허용 업종 - 리스트
def industry_list(request: Request, page_param: PPage_param, table_name: str, fullsearch:bool=False):
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
    filters.append(getattr(T_INDUSTRY_CODE, "delete_at") == None)

    # [ S ] search filter start
    if page_param.filters :
        if page_param.filters["skeyword"] :
            if page_param.filters["skeyword_type"] != "" :
                if page_param.filters["skeyword_type"] == "name" :
                    filters.append(
                         getattr(T_INDUSTRY_CODE, "name").like("%"+page_param.filters["skeyword"]+"%")
                    )
                else :
                    filters.append(getattr(T_INDUSTRY_CODE, page_param.filters["skeyword_type"]).like("%"+page_param.filters["skeyword"]+"%"))
            else : 
                filters.append(
                      T_INDUSTRY_CODE.name.like("%"+page_param.filters["skeyword"]+"%")
                    | T_INDUSTRY_CODE.code.like("%"+page_param.filters["skeyword"]+"%")
                )

        # if page_param.filters["create_at"]["startDate"] and page_param.filters["create_at"]["endDate"] :
        #     filters.append(
        #         and_(
        #             T_INDUSTRY_CODE.create_at >= page_param.filters["create_at"]["startDate"]
        #             ,T_INDUSTRY_CODE.create_at <= page_param.filters["create_at"]["endDate"] + " 23:59:59"
        #         )
        #     )
    # [ E ] search filter end
    
    partner_stmt = None

    if table_name == "T_INDUSTRY_OFFCARD" :
        partner_stmt = (
            db.query(
                 T_INDUSTRY_OFFCARD.uid
                ,T_INDUSTRY_OFFCARD.indus_uid
                ,T_INDUSTRY_OFFCARD.code
                ,T_INDUSTRY_OFFCARD.std_class
                ,T_INDUSTRY_OFFCARD.create_at
            )
            .filter(T_INDUSTRY_OFFCARD.delete_at == None)
            .filter(T_INDUSTRY_OFFCARD.partner_uid == user.partner_uid)
            .filter(T_INDUSTRY_OFFCARD.partner_id == user.partner_id)
            .subquery()
        )
    
    if table_name == "T_INDUSTRY_OFFCARD" and page_param.filters["yn"] == 'Y' :
            filters.append(partner_stmt.c.create_at != None)
        
    if table_name == "T_INDUSTRY_OFFCARD" and page_param.filters["yn"] == 'N' :
        filters.append(partner_stmt.c.create_at == None)

    elif table_name == "T_INDUSTRY_SIKWON" :
        partner_stmt = (
            db.query(
                 T_INDUSTRY_SIKWON.uid
                ,T_INDUSTRY_SIKWON.indus_uid
                ,T_INDUSTRY_SIKWON.code
                ,T_INDUSTRY_SIKWON.std_class
                ,T_INDUSTRY_SIKWON.create_at
            )
            .filter(T_INDUSTRY_SIKWON.delete_at == None)
            .filter(T_INDUSTRY_SIKWON.partner_uid == user.partner_uid)
            .filter(T_INDUSTRY_SIKWON.partner_id == user.partner_id)
            .subquery()
        )

    if table_name == "T_INDUSTRY_SIKWON" and page_param.filters["yn"] == 'Y' :
            filters.append(partner_stmt.c.create_at != None)
        
    if table_name == "T_INDUSTRY_SIKWON" and page_param.filters["yn"] == 'N' :
        filters.append(partner_stmt.c.create_at == None)

    sql = (
        db.query(
             T_INDUSTRY_CODE.uid
            ,T_INDUSTRY_CODE.code
            ,T_INDUSTRY_CODE.name
            ,func.date_format(partner_stmt.c.create_at, '%Y-%m-%d').label('create_at')
            ,case(
                (partner_stmt.c.create_at == None, "제한"),
                else_= "허용"
            ).label("limit")
            ,partner_stmt.c.indus_uid
        )
        .join (
            partner_stmt, 
            and_(partner_stmt.c.code == T_INDUSTRY_CODE.code),
            isouter = True # LEFT JOIN
        )
        .filter(*filters)
        .offset(offsets)
        .limit(limits)
    )


    format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    # [ S ] 페이징 처리
    page_param.page_total = (
         db.query(T_INDUSTRY_CODE)
        .join (
            partner_stmt, 
            and_(partner_stmt.c.code == T_INDUSTRY_CODE.code),
            isouter = True # LEFT JOIN
        )
        .filter(*filters)
        .count()
    )
    page_param.page_last = math.ceil(page_param.page_total / page_param.page_view_size)
    page_param.page_size = len(rows) # 현재 페이지에 검색된 수
    # [ E ] 페이징 처리

    jsondata = {}
    jsondata.update({"params" : page_param})
    jsondata.update({"list": rows})

    return jsondata

# 복지카드 허용 업종 - 등록(허용)
def industry_create(request: Request, limitIndustryInput: LimitIndustryInput) :
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user
    
    delim = ','
    arr_code_uids = delim.join(map(str, limitIndustryInput.uids))

    sql = """
        DELETE FROM T_INDUSTRY_OFFCARD 
        WHERE 
            partner_uid = {partner_uid}
        AND partner_id = '{partner_id}'
        AND indus_uid in ({uids})
    """.format(partner_uid = user.partner_uid, partner_id = user.partner_id, uids = arr_code_uids)

    db.execute(text(sql))

    sql2 = """
        INSERT INTO T_INDUSTRY_OFFCARD (indus_uid, code, partner_uid, partner_id)
        SELECT 
             uid
            ,code
            ,{partner_uid}
            ,'{partner_id}'
        FROM T_INDUSTRY_CODE as IC
        WHERE uid in ({uids})
    """.format(partner_uid = user.partner_uid, partner_id = user.partner_id, uids = arr_code_uids)
    
    db.execute(text(sql2))
    db.flush()

    # db.add(text(sql))
    # res = db.execute(text(sql)).fetchall()

    # db.add(db_item)

    return

# 복지카드 허용 업종 - 삭제(제외)
def industry_delete(request: Request, limitIndustryInput: LimitIndustryInput) :
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user
    
    if len(limitIndustryInput.uids) == 0:
            return ex.ReturnOK(404, "죄송합니다. 오류가 발생 하였습니다. 문제 지속시 개발자에게 접수 바랍니다.", request)

    for uid in limitIndustryInput.uids :
        industry_info = db.query(T_INDUSTRY_CODE.code).filter(T_INDUSTRY_CODE.uid == uid, T_INDUSTRY_CODE.delete_at == None).first()
        
        if industry_info is None:
            return ex.ReturnOK(403, "업종코드 정보가 없습니다.", request)
        
        db_item = db.query(T_INDUSTRY_OFFCARD).filter(T_INDUSTRY_OFFCARD.code == industry_info["code"], T_INDUSTRY_OFFCARD.partner_uid == user.partner_uid).delete()

        create_log(request, uid, "T_INDUSTRY_OFFCARD", "DELETE", "복지카드 허용 업종 제외", uid, None, user.user_id)
        request.state.inspect = frame()

    return db_item
