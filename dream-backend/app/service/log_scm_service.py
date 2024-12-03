from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, select, column, table, case
from fastapi import Request
from pydantic import BaseModel, Field
from inspect import currentframe as frame
from typing import Optional

from app.core import util
from app.core.database import format_sql
from app.models.scm.log import *

# SCM log insert
def create_log( 
     request: Request
    ,table_uid: int
    ,table_name: str
    ,column_key: str
    ,column_name: str
    ,cl_before: str
    ,cl_after: str
    ,create_user: str
):  
    request.state.inspect = frame()
    db_scm = request.state.db_scm
    db_item = T_CHANGE_LOG (
         table_uid = table_uid
        ,table_name = table_name      
        ,column_key = column_key      
        ,column_name = column_name   
        ,cl_before = str(cl_before)
        ,cl_after = str(cl_after)
        ,create_user = create_user
        ,create_at = util.getNow()
    )
    db_scm.add(db_item)
    db_scm.flush()
    return db_item

# SCM memo insert
def create_memo( 
     request: Request
    ,table_uid: int
    ,table_name: str
    ,memo: str
    ,create_user: str
    ,token_name: str
    ,sosok_id: str
    ,sosok_uid: int
    ,file_url : Optional[str] = None
    ,file_name : Optional[str] = None
):  
    request.state.inspect = frame()
    db_scm = request.state.db_scm
    db_item = T_MEMO (
         table_uid = table_uid
        ,table_name = table_name
        ,memo = memo
        ,create_user = create_user
        ,token_name = token_name
        ,sosok_id = sosok_id
        ,sosok_uid = sosok_uid
        ,file_url = file_url
        ,file_name = file_name
    )
    db_scm.add(db_item)
    db_scm.flush()
    return db_item

# Dream memo list
def memo_list(request: Request, table_name: str, uid: int):
    request.state.inspect = frame()
    db_scm = request.state.db_scm
    
    sql = (
        db_scm.query(
         T_MEMO.uid
        ,T_MEMO.memo
        ,T_MEMO.file_url
        ,T_MEMO.file_name
        ,T_MEMO.create_user
        ,T_MEMO.token_name
        ,T_MEMO.sosok_id
        ,T_MEMO.sosok_uid
        ,func.date_format(T_MEMO.create_at, '%Y-%m-%d %T').label('create_at')
        )
        .filter(T_MEMO.table_uid == uid, T_MEMO.table_name == table_name)
        .order_by(T_MEMO.create_at.desc())
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    jsondata = {}
    jsondata.update({"list": rows})

    return jsondata