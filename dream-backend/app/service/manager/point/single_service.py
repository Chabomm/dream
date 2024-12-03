import json
from decimal import *
from fastapi import Request
from inspect import currentframe as frame
from app.core.database import format_sql
from sqlalchemy import func, select, update, delete, Table, MetaData, and_
from app.core import util
import math
from app.core import exceptions as ex

from app.schemas.schema import *
from app.schemas.manager.point.assign.single import *
from app.models.member import *
from app.models.point.balance import *
from app.models.point.point import *
from app.models.point.sikwon import *
from app.service.log_service import *

# 포인트개별지급 - 리스트
def single_list(request: Request, page_param: PPage_param, fullsearch:bool=False):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    where = ""
    where = where + "WHERE M.delete_at is NULL "
    where = where + "AND M.partner_uid = " + str(user.partner_uid) + " " 

    # [ S ] search filter start
    if not util.isEmptyObject(page_param.filters, "is_point") :
        where = where + "AND MI.is_point = '" + page_param.filters["is_point"] + "' "

    if not util.isEmptyObject(page_param.filters, "serve") :
        where = where + "AND MI.serve = '" + page_param.filters["serve"] + "' "

    if not util.isEmptyObject(page_param.filters, "skeyword") :
        if not util.isEmptyObject(page_param.filters, "skeyword_type") :
            where = where + "AND "+page_param.filters["skeyword_type"]+" like '%"+page_param.filters["skeyword"]+"%' "
        else : 
            where = where + "AND ("
            where = where + "   M.user_name like '%"+page_param.filters["skeyword"]+"%'"
            where = where + "   or M.login_id like '%"+page_param.filters["skeyword"]+"%'"
            where = where + "   or MI.depart like '%"+page_param.filters["skeyword"]+"%'"
            where = where + "   or MI.position like '%"+page_param.filters["skeyword"]+"%'"
            where = where + ") "
    # [ E ] search filter end
    
    sql = """
        SELECT 
             MI.uid
            ,date_format(MI.join_com, '%%Y-%%m-%%d') AS join_com
            ,M.login_id
            ,M.user_name
            ,MI.depart
            ,MI.position
            ,MI.position2
            ,MI.serve
            ,(case when MI.is_point = 'T' then '가능' else '불가능' end) as is_point
            ,P.spare_point
            ,P.saved_point
            ,P.return_point
            ,PU.used_point
        FROM T_MEMBER_INFO as MI
        INNER JOIN T_MEMBER as M ON M.uid = MI.uid
        LEFT JOIN (
            SELECT 
                user_id
                ,sum(point) AS spare_point
                ,sum(case when saved_type in ('1','2') then saved_point end ) AS saved_point
                ,sum(case when saved_type = '3' then saved_point end) as return_point
            FROM T_POINT 
            GROUP BY user_id
        ) as P ON M.user_id = P.user_id
        LEFT JOIN (
            SELECT 
                user_id
                ,sum(IFNULL(used_point,0))-sum(IFNULL(remaining_point,0)) AS used_point
            FROM T_POINT_USED
            GROUP BY user_id
        ) as PU ON M.user_id = PU.user_id
        {where}
        ORDER BY MI.uid DESC
    """.format(where=where)
    
    if not fullsearch : # fullserch == True, excel download
        sql = sql + """
            LIMIT {start}, {end}
        """.format(start=(page_param.page-1)*page_param.page_view_size, end=page_param.page_view_size)

    
    res = db.execute(text(sql)).fetchall()

    rows = []
    for c in res :
        rows.append(dict(zip(c.keys(), c)))

    page_param.page_total = db.execute(text("select count(MI.uid) as cnt from T_MEMBER_INFO AS MI join T_MEMBER AS M on M.uid = MI.uid " + where)).scalar()

    page_param.page_last = math.ceil(page_param.page_total / page_param.page_view_size)
    page_param.page_size = len(rows) 

    jsondata = {}
    jsondata.update({"params" : page_param})
    jsondata.update({"list": rows})

    return jsondata


# 포인트개별지급 - 상세 - 포인트지급할 대상들 
def single_select_user_list(request: Request, assignSingleRead: AssignSingleRead):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user
    arr_user_uids = assignSingleRead.user_uids.split(",")

    filters = []
    filters.append(getattr(T_MEMBER, "delete_at") == None)
    filters.append(getattr(T_MEMBER, "partner_uid") == user.partner_uid)
    filters.append(getattr(T_MEMBER, "uid").in_(arr_user_uids))

    point_stmt = (
        db.query(
             T_POINT.user_id
            ,func.sum(T_POINT.point).label('spare_point')
        )
        .group_by(T_POINT.user_id)
        .subquery()
    )
    
    sql = (
        db.query(
             T_MEMBER_INFO.uid
            ,T_MEMBER.login_id
            ,T_MEMBER.user_name
            ,T_MEMBER_INFO.depart
            ,T_MEMBER_INFO.position
            ,T_MEMBER_INFO.position2
            ,T_MEMBER_INFO.serve
            ,T_MEMBER_INFO.is_point
            ,point_stmt.c.spare_point
        )
        .join(
            T_MEMBER,
            T_MEMBER.uid == T_MEMBER_INFO.uid,
        )
        .join (
            point_stmt, 
            T_MEMBER.user_id == point_stmt.c.user_id,
            isouter = True # LEFT JOIN
        )
        .filter(*filters)
    )
    format_sql(sql)

    rows = []
    for c in sql.all():
        row = dict(zip(c.keys(), c))

        if row["spare_point"] != None :
            row["spare_point"] = str(row["spare_point"])

        rows.append(row)

    jsondata = {}
    jsondata.update({"list": rows})
    return jsondata

# 포인트개별지급 - 복지포인트 등록
def single_point_create(request: Request, assignSingleInput: AssignSingleInput):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user
    
    for i in assignSingleInput.user_uids :

        member_info = db.query(T_MEMBER.user_id, T_MEMBER.partner_uid, T_MEMBER.partner_id).filter(T_MEMBER.uid == i, T_MEMBER.delete_at == None).first()
        
        if member_info is None:
            return ex.ReturnOK(403, "회원정보가 없습니다.", request)

        db_item = T_POINT (
            saved_type = assignSingleInput.save_type
            ,point = util.checkNumeric(assignSingleInput.saved_point)
            ,saved_point = util.checkNumeric(assignSingleInput.saved_point)
            ,expiration_date = assignSingleInput.expiration_date
            ,user_id = member_info["user_id"]
            ,manager_id = user.user_id
            ,partner_uid = member_info["partner_uid"]
            ,partner_id = member_info["partner_id"]
            ,reason = assignSingleInput.reason
            ,admin_memo = assignSingleInput.admin_memo
        )
        db.add(db_item)

        sql = (
            db.query( T_BALANCE )
            .filter(
                 T_BALANCE.input_state == "입금완료"
                ,T_BALANCE.point > 0
                ,T_BALANCE.partner_uid == user.partner_uid
            )
            .order_by(T_BALANCE.uid.asc())
        )
        give_spare_point = util.checkNumeric(assignSingleInput.saved_point) # 지급해야될 포인트
        for c in sql.all():
            if give_spare_point > 0 :
                if util.checkNumeric(c.point) >= give_spare_point :
                    c.point = c.point-give_spare_point
                    give_spare_point = 0
                else :
                    give_spare_point = give_spare_point - c.point
                    c.point = 0
        
        create_log(request, db_item.uid, "T_POINT", "INSERT", "개별 복지포인트 지급", 0, db_item.uid, user.user_id)
        request.state.inspect = frame()

    return db_item

# 포인트개별지급 - 복지포인트 회수
def single_point_collect(request: Request, assignSingleInput: AssignSingleInput):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    for i in assignSingleInput.user_uids :

        # member_info = db.query(T_MEMBER.user_id, T_MEMBER.partner_uid, T_MEMBER.partner_id).filter(T_MEMBER.uid == i, T_MEMBER.delete_at == None).first()
        # if member_info is None :
        #     return ex.ReturnOK(403, "회원정보가 없습니다.", request)

        # [ S ] 각 멤버의 잔여 포인트 select 후 차감하기
        stmt = db.query(T_MEMBER.user_id).filter(T_MEMBER.uid == i, T_MEMBER.partner_id == user.partner_id, T_MEMBER.delete_at == None).subquery()
        sql = db.query(T_POINT).filter(
             T_POINT.user_id.in_(stmt)
            ,T_POINT.saved_type != "3"
            ,T_POINT.point > 0
        )
        format_sql(sql)
        
        give_spare_point = util.checkNumeric(assignSingleInput.saved_point) # 회수해야될 포인트
        member_spare_point_res = sql.all()

        # 회수할 금액과 정확히 일치하는거 우선으로 회수
        for c in member_spare_point_res :
            if c.point == give_spare_point :
                db_item = T_POINT (
                    saved_type = "3"
                    ,point = 0
                    ,saved_point = (-give_spare_point)
                    ,user_id = c.user_id
                    ,manager_id = user.user_id
                    ,partner_uid = c.partner_uid
                    ,partner_id = c.partner_id
                    ,reason = assignSingleInput.reason
                    ,admin_memo = assignSingleInput.admin_memo
                )
                db.add(db_item)
                c.point = 0 # T_POINT UPDATE
                give_spare_point = 0
        
        for c in member_spare_point_res :
            if give_spare_point > 0 :
                # 회수할 포인트보다 잔여포인트가 같거나 크면
                if util.checkNumeric(c.point) > give_spare_point : 
                    db_item = T_POINT (
                        saved_type = "3"
                        ,point = 0
                        ,saved_point = (-give_spare_point)
                        ,user_id = c.user_id
                        ,manager_id = user.user_id
                        ,partner_uid = c.partner_uid
                        ,partner_id = c.partner_id
                        ,reason = assignSingleInput.reason
                        ,admin_memo = assignSingleInput.admin_memo
                    )
                    db.add(db_item)
                    c.point = c.point - give_spare_point # T_POINT UPDATE
                    give_spare_point = 0

                else : # 회수할 포인트가 잔여포인트보다 크면
                    db_item = T_POINT (
                        saved_type = "3"
                        ,point = 0
                        ,saved_point = (-c.point)
                        ,user_id = c.user_id
                        ,manager_id = user.user_id
                        ,partner_uid = c.partner_uid
                        ,partner_id = c.partner_id
                        ,reason = assignSingleInput.reason
                        ,admin_memo = assignSingleInput.admin_memo
                    )
                    db.add(db_item)
                    give_spare_point = give_spare_point - c.point
                    c.point = 0 # T_POINT UPDATE
        # [ E ] 각 멤버의 잔여 포인트 select 후 차감하기

        # [ S ] 차감한 금액만큼 예치금 전환
        sql = (
            db.query( T_BALANCE )
            .filter(
                 T_BALANCE.input_state == "입금완료"
                ,T_BALANCE.partner_uid == user.partner_uid
            )
            .order_by(T_BALANCE.uid.asc())
        )
        format_sql(sql)
        give_point = util.checkNumeric(assignSingleInput.saved_point) # 전환 해야될 포인트
        for c in sql.all():
            if give_point > 0 :
                # 이전 예치금 충전포인트가 전환포인트 보다 크거나 같으면
                if (c.save_point - c.point) >= give_point :
                    c.point = c.point+give_point
                    give_point = 0
                else :
                    # 이전 예치금 포인트가 전환포인트 보다 작으면
                    give_point = give_point -(c.save_point-c.point)
                    c.point = c.point + (c.save_point - c.point) 
                    
        
        create_log(request, db_item.uid, "T_POINT", "INSERT", "개별 복지포인트 회수", 0, db_item.uid, user.user_id)
        request.state.inspect = frame()
        # [ E ] 차감한 금액만큼 예치금 전환
    return db_item


# 임직원 잔여 포인트
def member_point_list(request: Request, assignSingleInput: AssignSingleInput):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    filters = []
    filters.append(getattr(T_MEMBER, "delete_at") == None)
    filters.append(getattr(T_MEMBER, "partner_uid") == user.partner_uid)
    filters.append(getattr(T_MEMBER, "uid").in_(assignSingleInput.user_uids))

    point_stmt = (
        db.query(
             T_POINT.user_id
            ,func.sum(T_POINT.point).label('spare_point')
        )
        .group_by(T_POINT.user_id)
        .subquery()
    )

    sql = (
        db.query(
             T_MEMBER.uid
            ,point_stmt.c.spare_point
        )
        .join (
            point_stmt, 
            T_MEMBER.user_id == point_stmt.c.user_id,
            isouter = True # LEFT JOIN
        )
        .filter(*filters)
    )
    format_sql(sql)

    rows = []
    for c in sql.all():
        row = dict(zip(c.keys(), c))

        if row["spare_point"] != None :
            row["spare_point"] = str(row["spare_point"])

        rows.append(row)

    jsondata = {}
    jsondata.update({"list": rows})
    return jsondata