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
from app.deps import auth
from app.schemas.admin.admin import *
from app.service.log_scm_service import *

# 로그리스트
def log_list(request: Request, logListInput: LogListInput, _where: str):
    request.state.inspect = frame()
    db_scm = request.state.db_scm

    where = ' WHERE 1=1 ' + _where

    if not util.isEmptyObject(logListInput.filters, "skeyword") :
        if not util.isEmptyObject(logListInput.filters, "skeyword_type") :
            where = where + " AND board_name like '%"+logListInput.filters["skeyword"]+"%'"
        else : 
            where = where + " AND ("
            where = where + " table_uid like '%"+logListInput.filters["skeyword"]+"%'"
            where = where + " or table_name like '%"+logListInput.filters["skeyword"]+"%'"
            where = where + " or column_key like '%"+logListInput.filters["skeyword"]+"%'"
            where = where + " or column_name like '%"+logListInput.filters["skeyword"]+"%'"
            where = where + " or cl_before like '%"+logListInput.filters["skeyword"]+"%'"
            where = where + " or cl_after like '%"+logListInput.filters["skeyword"]+"%'"
            where = where + " or create_user like '%"+logListInput.filters["skeyword"]+"%'"
            where = where + ") "

    if logListInput.filters["create_at"]["startDate"] and logListInput.filters["create_at"]["endDate"] :
        where = where + " AND create_at >= '" +logListInput.filters["create_at"]["startDate"]+ "' " 
        where = where + " AND create_at <= '" +logListInput.filters["create_at"]["endDate"]+ "' " 

    sql = """
        SELECT 
             uid
            ,table_uid
            ,table_name
            ,column_key
            ,column_name
            ,cl_before
            ,cl_after
            ,create_user
            ,DATE_FORMAT(create_at, '%Y-%m-%d %T') as create_at
            ,CONCAT(left(cl_before, 75),'...') as cl_before_left
            ,CONCAT(left(cl_after, 75),'...') as cl_after_left
        FROM T_CHANGE_LOG
        {where}
        ORDER BY uid DESC
        LIMIT {start}, {end}
    """.format(where=where, start=(logListInput.page-1)*logListInput.page_view_size, end=logListInput.page_view_size)

    res = db_scm.execute(text(sql)).fetchall()

    rows = []
    for c in res :
        rows.append(dict(zip(c.keys(), c)))

    # [ S ] 페이징 처리
    logListInput.page_total = db_scm.execute(text("select count(uid) as cnt from T_CHANGE_LOG " + where)).scalar()
    logListInput.page_last = math.ceil(logListInput.page_total / logListInput.page_view_size)
    logListInput.page_size = len(rows) # 현재 페이지에 검색된 수
    # [ E ] 페이징 처리

    jsondata = {}
    jsondata.update({"params" : logListInput})
    jsondata.update({"list": rows})

    return jsondata





