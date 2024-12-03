from fastapi import Request
from inspect import currentframe as frame
from app.core.database import format_sql
from sqlalchemy import func, select, update, delete, Table, MetaData, and_
from app.core import util
import math

from app.schemas.schema import *
from app.schemas.manager.point.offcard.used import *
from app.models.offcard.used import *
from app.models.member import *
from app.service.log_service import *

# 카드 포인트 차감내역
def deduct_list(request: Request, cardDeductListInput: CardDeductListInput, fullsearch:bool=False):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    offsets = 0
    if fullsearch == False :
        offsets = (cardDeductListInput.page-1)*cardDeductListInput.page_view_size

    limits = None
    if fullsearch == False :
        limits = cardDeductListInput.page_view_size
        
    memeber_filters = []
    if cardDeductListInput.user_id != None : # front 에서 넘어온 경우
        memeber_filters.append(getattr(T_MEMBER, "user_id") == cardDeductListInput.user_id)
    else : # 고객사 관리자 인경우
        memeber_filters.append(getattr(T_MEMBER, "partner_uid") == user.partner_uid)
            
    member_stmt = (
        db.query(
             T_MEMBER.uid
            ,T_MEMBER.user_id
            ,T_MEMBER.user_name
            ,T_MEMBER_INFO.birth
            ,T_MEMBER_INFO.depart
            ,T_MEMBER_INFO.position
        )
        .join(
            T_MEMBER_INFO, 
            T_MEMBER_INFO.uid == T_MEMBER.uid,
        )
        .filter(*memeber_filters)
        .subquery()
    )

    filters = []
    filters.append(getattr(T_POINT_DEDUCT, "delete_at") == None)
    filters.append(getattr(T_POINT_DEDUCT, "use_type") == cardDeductListInput.use_type)

    if cardDeductListInput.user_id != None : # front 에서 넘어온 경우
        filters.append(getattr(T_POINT_DEDUCT, "user_id") == cardDeductListInput.user_id)
    else : # 고객사 관리자 인경우
        filters.append(getattr(T_POINT_DEDUCT, "partner_uid") == user.partner_uid)

    # [ S ] search filter start
    if cardDeductListInput.filters :
        if cardDeductListInput.filters["skeyword"] :
            if cardDeductListInput.filters["skeyword_type"] != "" :
                filters.append(getattr(member_stmt.c, cardDeductListInput.filters["skeyword_type"]).like("%"+cardDeductListInput.filters["skeyword"]+"%"))
            else : 
                filters.append(
                      member_stmt.c.user_name.like("%"+cardDeductListInput.filters["skeyword"]+"%")
                    | member_stmt.c.birth.like("%"+cardDeductListInput.filters["skeyword"]+"%")
                    | member_stmt.c.depart.like("%"+cardDeductListInput.filters["skeyword"]+"%")
                )

        if cardDeductListInput.filters["create_at"]["startDate"] and cardDeductListInput.filters["create_at"]["endDate"] :
            filters.append(
                and_(
                    T_POINT_DEDUCT.confirm_at >= cardDeductListInput.filters["create_at"]["startDate"]
                    ,T_POINT_DEDUCT.confirm_at <= cardDeductListInput.filters["create_at"]["endDate"] + " 23:59:59"
                )
            )
        
        if cardDeductListInput.filters["state"] :
            filters.append(T_POINT_DEDUCT.state == cardDeductListInput.filters["state"])
    # [ E ] search filter end

    sql = (
        db.query(
             member_stmt.c.user_name
            ,member_stmt.c.birth
            ,member_stmt.c.depart
            ,member_stmt.c.position
            ,func.date_format(T_POINT_DEDUCT.create_at, '%Y-%m-%d %T').label('create_at')
            ,func.date_format(T_POINT_DEDUCT.confirm_at, '%Y-%m-%d %T').label('confirm_at')
            ,T_POINT_DEDUCT.detail
            ,T_POINT_DEDUCT.request_point
            ,T_POINT_DEDUCT.confirm_point
            ,T_POINT_DEDUCT.card
            ,T_POINT_DEDUCT.state
            ,T_POINT_DEDUCT.note
        )
        .join (
            member_stmt, 
            T_POINT_DEDUCT.user_uid == member_stmt.c.uid,
        )
        .filter(*filters)
        .order_by(T_POINT_DEDUCT.uid.desc())
        # .offset((cardDeductListInput.page-1)*cardDeductListInput.page_view_size)
        # .limit(cardDeductListInput.page_view_size)
        .offset(offsets)
        .limit(limits)
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


def used_list(request: Request, page_param: PPage_param, fullsearch:bool=False):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    where = ""
    where = where + "WHERE M.delete_at is NULL "
    where = where + "AND M.partner_uid = " + str(user.partner_uid) + " " 

    filter_where = ""
    # [ S ] search filter start
    if not util.isEmptyObject(page_param.filters, "skeyword") :
        if not util.isEmptyObject(page_param.filters, "skeyword_type") :
            where = where + "AND "+page_param.filters["skeyword_type"]+" like '%"+page_param.filters["skeyword"]+"%' "
        else : 
            where = where + "AND ("
            where = where + "   M.user_name like '%"+page_param.filters["skeyword"]+"%'"
            where = where + "   or MI.birth like '%"+page_param.filters["skeyword"]+"%'"
            where = where + "   or MI.depart like '%"+page_param.filters["skeyword"]+"%'"
            where = where + ") "

    if page_param.filters["create_at"]["startDate"] and page_param.filters["create_at"]["endDate"] :
        filter_where = filter_where + " AND create_at >= '" +page_param.filters["create_at"]["startDate"]+ "' " 
        filter_where = filter_where + " AND create_at <= '" +page_param.filters["create_at"]["endDate"]+ "' "

    # [ E ] search filter end
    
    sql = """
        SELECT
            login_id
            ,user_name
            ,serve
            ,depart
            ,birth
            ,position
            ,bokji_point
            ,bokji_mall_point
            ,sikwon_point
            ,(bokji_point+bokji_mall_point+sikwon_point) as sum_point
        FROM (
            SELECT 
                M.login_id
                ,M.user_name
                ,MI.serve
                ,MI.depart
                ,MI.birth
                ,MI.position
                ,(
                    SELECT 
                        sum(IFNull(PU.used_point, 0))-sum(IFNull(PU.remaining_point, 0)) 
                    FROM T_POINT_USED as PU 
                    WHERE PU.user_id = M.user_id and group_id = 1 {filter_where}
                ) as bokji_point
                ,(
                    SELECT 
                        sum(IFNull(PU.used_point, 0))-sum(IFNull(PU.remaining_point, 0))
                    FROM T_POINT_USED as PU
                    WHERE PU.user_id = M.user_id and group_id <> 1{filter_where}
                ) as bokji_mall_point
                ,(
                    SELECT 
                        sum(IFNull(SU.used_point, 0))-sum(IFNull(SU.remaining_point, 0)) 
                    FROM T_SIKWON_USED as SU 
                    WHERE SU.user_id = M.user_id {filter_where}
                ) as sikwon_point
            FROM T_MEMBER as M
            JOIN T_MEMBER_INFO as MI on M.login_id = MI.login_id
            {where}
            ORDER BY M.uid DESC
        ) as T
    """.format(where=where, filter_where=filter_where)
    
    if not fullsearch : # fullserch == True, excel download
        sql = sql + """
            LIMIT {start}, {end}
        """.format(start=(page_param.page-1)*page_param.page_view_size, end=page_param.page_view_size)

    
    res = db.execute(text(sql)).fetchall()

    rows = []
    for c in res :
        rows.append(dict(zip(c.keys(), c)))

    page_param.page_total = db.execute(text("select count(M.uid) as cnt from T_MEMBER AS M join T_MEMBER_INFO AS MI on MI.uid = M.uid " + where)).scalar()

    page_param.page_last = math.ceil(page_param.page_total / page_param.page_view_size)
    page_param.page_size = len(rows) 

    jsondata = {}
    jsondata.update({"params" : page_param})
    jsondata.update({"list": rows})

    return jsondata