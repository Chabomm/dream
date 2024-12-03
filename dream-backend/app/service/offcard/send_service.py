from fastapi import Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Optional
from inspect import currentframe as frame
from sqlalchemy.dialects import mysql as mysql_dialetct
from pymysql.converters import conversions, escape_item, encoders
from sqlalchemy import func, select, update, delete, Table, MetaData, and_, insert
import math
from datetime import datetime, timedelta
from app.core import exceptions as ex
from app.core import util
from app.core.database import format_sql
from app.models.session import *

from app.models.member import *
from app.models.partner import *
from app.models.offcard.files import *
from app.schemas.offcard.send import *
from app.service.log_service import *

# 복지카드 송신할 고객정보 setting
def set_SLS00390(request: Request, is_holiday: bool):
    request.state.inspect = frame()
    db = request.state.db

    today = datetime.today().strftime("%Y%m%d")
    
    if is_holiday : # 공휴일(주말포함) 이면, 검색 범위 update
        # res = db.query(FT_SLS00390).filter(FT_SLS00390.is_ban == "N").all()
        update_stmt = (
            update(FT_SLS00390).where(FT_SLS00390.is_ban == 'N').
            values(QY_EDD=today)
        )
        db.execute(update_stmt)
        db.commit()
    
    else : # 평일이면, 오늘날짜 데이터 생성
        db.query(FT_SLS00390).filter(FT_SLS00390.is_ban == "N").delete()
        partner_stmt = db.query(T_PARTNER.uid).filter(T_PARTNER.state == "200").subquery()
        select_stmt = (
            select (
                T_MEMBER_INFO.user_ci
                ,text(f"'{today}'")
                ,text(f"'{today}'")
            )
            .where(
                T_MEMBER_INFO.delete_at == None
                ,T_MEMBER_INFO.serve == '재직'
                ,T_MEMBER_INFO.state == '100'
                ,T_MEMBER_INFO.partner_uid.in_(partner_stmt)
            )
        )
        insert_stmt = insert(FT_SLS00390).from_select(
            ["IPN_LIK_N", "QY_STD", "QY_EDD"], select_stmt
        )
        db.execute(insert_stmt)
        db.commit()


    # sql = '''
    #     insert into FT_SLS00390 (IPN_LIK_N, QY_STD, QY_EDD)
    #     select 
    #          user_ci 
    #         ,'{st_date}'
    #         ,'{ed_date}'
    #     From T_MEMBER_INFO
    #     where delete_at is NULL
    #     and partner_uid in (select uid from T_PARTNER where state = '200')
    #     and serve = '재직'
    #     and state = '100'
    # '''.format(st_date=today, ed_date=today)
    # res = db.execute(text(sql))
    # print(res)

# 복지카드 송신할 고객정보 getting
def get_SLS00390(request: Request, page_param: PPage_param):
    request.state.inspect = frame()
    db = request.state.db

    filters = []
    filters.append(getattr(FT_SLS00390, "is_send") == "N")

    sql = (
        db.query(
            FT_SLS00390.IPN_LIK_N
            ,FT_SLS00390.QY_STD
            ,FT_SLS00390.QY_EDD
            ,FT_SLS00390.AFL_CRD_C
            ,FT_SLS00390.IE_TI_F
            ,FT_SLS00390.SLT_WF_FIM_CD
        )
        .filter(*filters)
        .order_by(FT_SLS00390.IPN_LIK_N.desc())
        .offset((page_param.page-1)*page_param.page_view_size)
        .limit(page_param.page_view_size)
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    # [ S ] 페이징 처리
    page_param.page_total = (db.query(FT_SLS00390).filter(*filters).count())
    page_param.page_last = math.ceil(page_param.page_total / page_param.page_view_size)
    page_param.page_size = len(rows)  # 현재 페이지에 검색된 수
    # [ E ] 페이징 처리

    jsondata = {}
    jsondata.update({"params": page_param})
    jsondata.update({"list": rows})

    return jsondata

# 복지카드 송신할 고객정보 
def offcard_member_list(request: Request, page_param: PPage_param):
    request.state.inspect = frame()
    db = request.state.db

    filters = []
    filters.append(getattr(T_MEMBER_INFO, "delete_at") == None)
    stmt = db.query(T_PARTNER.uid).filter(T_PARTNER.state == "200").subquery()
    filters.append(getattr(T_MEMBER_INFO, "partner_uid").in_(stmt))
    filters.append(getattr(T_MEMBER_INFO, "serve") == "재직")
    filters.append(getattr(T_MEMBER_INFO, "state") == "100")

    sql = (
        db.query(
             T_MEMBER_INFO.user_ci
        )
        .filter(*filters)
        .order_by(T_MEMBER_INFO.uid.desc())
        .offset((page_param.page-1)*page_param.page_view_size)
        .limit(page_param.page_view_size)
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    # [ S ] 페이징 처리
    page_param.page_total = (db.query(T_MEMBER_INFO).filter(*filters).count())
    page_param.page_last = math.ceil(page_param.page_total / page_param.page_view_size)
    page_param.page_size = len(rows)  # 현재 페이지에 검색된 수
    # [ E ] 페이징 처리

    jsondata = {}
    jsondata.update({"params": page_param})
    jsondata.update({"list": rows})

    return jsondata

def test(request: Request, page_param: PPage_param):
    request.state.inspect = frame()
    db = request.state.db

    filters = []
    # filters.append(getattr(T_MEMBER_INFO, "delete_at") == None)
    # stmt = db.query(T_PARTNER.uid).filter(T_PARTNER.state == "200").subquery()
    # filters.append(getattr(T_MEMBER_INFO, "partner_uid").in_(stmt))
    # filters.append(getattr(T_MEMBER_INFO, "serve") == "재직")
    # filters.append(getattr(T_MEMBER_INFO, "state") == "100")

    sql = (
        db.query(
             T_TEST.user_ci
        )
        .filter(*filters)
        .order_by(T_TEST.uid.desc())
        .offset((page_param.page-1)*page_param.page_view_size)
        .limit(page_param.page_view_size)
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    # [ S ] 페이징 처리
    page_param.page_total = (db.query(T_TEST).filter(*filters).count())
    page_param.page_last = math.ceil(page_param.page_total / page_param.page_view_size)
    page_param.page_size = len(rows)  # 현재 페이지에 검색된 수
    # [ E ] 페이징 처리

    jsondata = {}
    jsondata.update({"params": page_param})
    jsondata.update({"list": rows})

    return jsondata