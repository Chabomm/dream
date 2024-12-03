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

# 식권카드 허용 업종 - 등록(허용)
def industry_create(request: Request, limitIndustryInput: LimitIndustryInput) :
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user
    
    delim = ','
    arr_code_uids = delim.join(map(str, limitIndustryInput.uids))

    sql = """
        DELETE FROM T_INDUSTRY_SIKWON 
        WHERE 
            partner_uid = {partner_uid}
        AND partner_id = '{partner_id}'
        AND indus_uid in ({uids})
    """.format(partner_uid = user.partner_uid, partner_id = user.partner_id, uids = arr_code_uids)

    db.execute(text(sql))

    sql2 = """
        INSERT INTO T_INDUSTRY_SIKWON (indus_uid, code, partner_uid, partner_id)
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

# 식권카드 허용 업종 - 삭제(제외)
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
        
        db_item = db.query(T_INDUSTRY_SIKWON).filter(T_INDUSTRY_SIKWON.code == industry_info["code"], T_INDUSTRY_SIKWON.partner_uid == user.partner_uid).delete()

        create_log(request, uid, "T_INDUSTRY_SIKWON", "DELETE", "식권카드 허용 업종 제외", uid, None, user.user_id)
        request.state.inspect = frame()

    return db_item
