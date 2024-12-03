from fastapi import Request
from inspect import currentframe as frame
from app.core.database import format_sql
from sqlalchemy import func, select, update, delete, Table, MetaData, and_, literal_column, tuple_
from app.core import util
import math
import random

from app.schemas.schema import *
from app.schemas.manager.point.offcard.exuse import *
from app.models.point.confirm import *
from app.models.offcard.used import *
from app.models.member import *
from app.models.limit.industry import *
from app.service.log_service import *

# T_MEMBER M_MEMBER_INFO JOIN
def get_user_join_member(request: Request, user_id: str):
    request.state.inspect = frame()
    db = request.state.db
    return db.query(T_MEMBER_INFO).filter(T_MEMBER_INFO.user_id == user_id).first()

def get_my_exuse(request: Request, cardExuseListInput: CardExuseListInput, user: T_MEMBER) :
    request.state.inspect = frame()
    db = request.state.db

    where = ""
    where = where + "WHERE RY_CCD not in ( select code from T_INDUSTRY_SIKWON where partner_uid = "+str(user.partner_uid)+" union select code from T_INDUSTRY_OFFCARD where partner_uid = "+str(user.partner_uid)+") "

    where = where + "AND delete_at is NULL "
    where = where + "AND user_id = '" + str(cardExuseListInput.user_id) + "' "
    where = where + "AND state is Null"

    if cardExuseListInput.filters["create_at"]["startDate"] and cardExuseListInput.filters["create_at"]["endDate"] :
        where = where + " AND DATE_FORMAT(APV_D, '%Y-%m-%d') >= '" +cardExuseListInput.filters["create_at"]["startDate"]+ "' " 
        where = where + " AND DATE_FORMAT(APV_D, '%Y-%m-%d') <= '" +cardExuseListInput.filters["create_at"]["endDate"]+ "' " 

    sum_price_data = 0
    sql = """
        select 
            sum(IFNull(SEA, 0)) as sum_exuse
        from T_CARD_USED
        {where}
        group by user_id
    """.format(where=where)

    posts = db.execute(text(sql)).first()

    if posts != None :
        if int(posts.sum_exuse) > 0 :
            sum_price_data = int(posts.sum_exuse)
            
    return sum_price_data


# 소명신청내역
def list(request: Request, cardExuseListInput: CardExuseListInput, user: T_MEMBER):
    request.state.inspect = frame()
    db = request.state.db

    where = ""
    where = where + "WHERE CU.RY_CCD not in ( select code from T_INDUSTRY_SIKWON where partner_uid = "+str(user.partner_uid)+" union select code from T_INDUSTRY_OFFCARD where partner_uid = "+str(user.partner_uid)+") "

    where = where + "AND CU.delete_at is NULL "
    where = where + "AND CU.user_id = '" + str(cardExuseListInput.user_id) + "' "
    # where = where + "AND CU.state is Null"

    if cardExuseListInput.filters["create_at"]["startDate"] and cardExuseListInput.filters["create_at"]["endDate"] :
        where = where + " AND DATE_FORMAT(CU.APV_D, '%Y-%m-%d') >= '" +cardExuseListInput.filters["create_at"]["startDate"]+ "' " 
        where = where + " AND DATE_FORMAT(CU.APV_D, '%Y-%m-%d') <= '" +cardExuseListInput.filters["create_at"]["endDate"]+ "' " 

    
    sql = """
        select 
            CU.uid
            ,DATE_FORMAT(CU.APV_D, '%Y-%m-%d') as APV_D
            ,CU.RY_CCD
            ,(select name From T_INDUSTRY_CODE as IC where IC.code = CU.RY_CCD) as name
            ,CU.MCT_NM
            ,CU.SEA
            ,'신한카드' as card_name
            ,E.state
        from T_CARD_USED as CU
        left join T_EXUSE as E on E.card_used_uid = CU.uid
        {where}
    """.format(where=where)


    print('db.execute(text(sql)).all()',db.execute(text(sql)).all())

    jsondata = {}
    jsondata.update({"params" : cardExuseListInput})
    jsondata.update({"list": db.execute(text(sql)).all()})
    
    return jsondata


# 소명신청_상세
def read(request: Request, cardExuseReadInput: CardExuseReadInput):
    request.state.inspect = frame()
    db = request.state.db

    sql = ( 
        db.query(
             T_CARD_USED.uid
            ,func.date_format(T_CARD_USED.create_at, '%Y-%m-%d %T').label('create_at')
            ,T_CARD_USED.MCT_NM
            ,T_CARD_USED.APV_N
            ,T_CARD_USED.SEA
        )
        .filter(
            T_CARD_USED.uid == cardExuseReadInput.card_uid
            ,T_CARD_USED.user_id == cardExuseReadInput.user_id
            ,T_CARD_USED.delete_at == None
        )
    )
    format_sql(sql)
    res = sql.first()

    if res != None :
        res = dict(zip(res.keys(), res))

    return res


















# 카드사용_소명신청등록
def exuse_card_edit(request: Request, cardExuseInput: CardExuseInput, user: T_MEMBER_INFO) :
    request.state.inspect = frame()
    db = request.state.db

    card_info = (
        db.query(T_CARD_USED.APV_D, T_CARD_USED.MCT_NM, T_CARD_USED.RY_CCD, T_CARD_USED.SEA)
        .filter(
             T_CARD_USED.uid == cardExuseInput.card_used_uid
            ,T_CARD_USED.state == None
        )
    ).first()

    if card_info == None :
        return 0
    
    db_item = T_EXUSE (
         card_used_uid = cardExuseInput.card_used_uid
        ,partner_uid = user.partner_uid
        ,partner_id = user.partner_id
        ,user_uid = user.uid
        ,user_id = user.user_id
        ,user_name = user.user_name
        ,birth = user.birth
        ,depart = user.depart
        ,position = user.position
        ,pay_at = func.date_format(card_info.APV_D, '%Y-%m-%d')
        ,biz_item = card_info.MCT_NM
        ,detail = card_info.RY_CCD
        ,pay_amount = card_info.SEA
        ,exuse_amount = cardExuseInput.exuse_amount
        ,state = "소명신청"
        ,confirm_at = None
        ,point_type = cardExuseInput.point_type
        ,welfare_type = cardExuseInput.welfare_type
        ,exuse_detail = cardExuseInput.exuse_detail
        ,attch_file = cardExuseInput.attch_file
    )
    db.add(db_item)
    db.flush()

    create_log(request, db_item.uid, "T_EXUSE", "INSERT", "카드사용 소명신청", 0, db_item.uid, user.user_id)
    request.state.inspect = frame()

    return 1