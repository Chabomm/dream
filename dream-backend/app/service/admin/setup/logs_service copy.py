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
def log_list(request: Request, table_name:str, logListInput: LogListInput):
    request.state.inspect = frame()
    db_scm = request.state.db_scm

    filters = []
    if table_name != '' :
        filters.append(
            and_(
                T_CHANGE_LOG.table_name.in_([logListInput.table_name])
                ,T_CHANGE_LOG.table_uid == logListInput.table_uid
            )
        )

    if logListInput.filters :
        if logListInput.filters["skeyword"] :
            if logListInput.filters["skeyword_type"] != "" :
                filters.append(getattr(T_CHANGE_LOG, logListInput.filters["skeyword_type"]).like("%"+logListInput.filters["skeyword"]+"%"))
            else : 
                filters.append(
                    T_CHANGE_LOG.table_uid.like("%"+logListInput.filters["skeyword"]+"%") 
                    | T_CHANGE_LOG.table_name.like("%"+logListInput.filters["skeyword"]+"%")
                    | T_CHANGE_LOG.column_key.like("%"+logListInput.filters["skeyword"]+"%")
                    | T_CHANGE_LOG.column_name.like("%"+logListInput.filters["skeyword"]+"%")
                    | T_CHANGE_LOG.cl_before.like("%"+logListInput.filters["skeyword"]+"%")
                    | T_CHANGE_LOG.cl_after.like("%"+logListInput.filters["skeyword"]+"%")
                    | T_CHANGE_LOG.create_user.like("%"+logListInput.filters["skeyword"]+"%")
                )

        if logListInput.filters["create_at"]["startDate"] and logListInput.filters["create_at"]["endDate"] :
            filters.append(
                and_(
                    T_CHANGE_LOG.create_at >= logListInput.filters["create_at"]["startDate"]
                    ,T_CHANGE_LOG.create_at <= logListInput.filters["create_at"]["endDate"] + " 23:59:59"
                )
            )
    
    sql = (
        db_scm.query(
             T_CHANGE_LOG.uid
            ,T_CHANGE_LOG.table_uid
            ,T_CHANGE_LOG.table_name
            ,T_CHANGE_LOG.column_key
            ,T_CHANGE_LOG.column_name
            ,T_CHANGE_LOG.cl_before
            ,T_CHANGE_LOG.cl_after
            ,T_CHANGE_LOG.create_user
            ,func.date_format(T_CHANGE_LOG.create_at, '%Y-%m-%d %T').label('create_at')
            ,func.left(T_CHANGE_LOG.cl_before, 75).label('cl_before_left')
            ,func.left(T_CHANGE_LOG.cl_after, 75).label('cl_after_left')
        )
        .filter(*filters)
        .order_by(T_CHANGE_LOG.uid.desc())
        .offset((logListInput.page-1)*logListInput.page_view_size)
        .limit(logListInput.page_view_size)
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        list = dict(zip(c.keys(), c))
        if list["cl_before"] is not None and len(list["cl_before"]) > 75 : 
            list["cl_before"] = list["cl_before_left"]+"..."
        if list["cl_after"] is not None and len(list["cl_after"]) > 75 : 
            list["cl_after"] = list["cl_after_left"]+"..."
        rows.append(list)

    # [ S ] 페이징 처리
    logListInput.page_total = (
        db_scm.query(T_CHANGE_LOG)
        .filter(*filters)
        .count()
    )
    logListInput.page_last = math.ceil(logListInput.page_total / logListInput.page_view_size)
    logListInput.page_size = len(rows) # 현재 페이지에 검색된 수
    # [ E ] 페이징 처리

    jsondata = {}
    jsondata.update(logListInput)
    jsondata.update({"params":logListInput})
    jsondata.update({"list": rows})

    return jsondata





