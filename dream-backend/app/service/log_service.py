from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, select, column, table, case
from fastapi import Request
from inspect import currentframe as frame
from typing import Optional

from app.core import util
from app.core.database import format_sql
from app.models.log import *
from app.schemas.manager.auth import *

# Dream log insert
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
    db = request.state.db 
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
    db.add(db_item)
    db.flush()
    return db_item

# Dream memo insert
def create_memo( 
     request: Request
    ,table_uid: int
    ,table_name: str
    ,memo: str
    ,create_user: str
    ,file_url : Optional[str] = None
    ,file_name : Optional[str] = None
):  
    request.state.inspect = frame()
    db = request.state.db 
    db_item = T_MEMO (
         table_uid = table_uid
        ,table_name = table_name
        ,memo = memo
        ,create_user = create_user
        ,file_url = file_url
        ,file_name = file_name
    )
    db.add(db_item)
    db.flush()
    return db_item

# Dream memo list
def memo_list(request: Request, table_name: str, uid: int):
    request.state.inspect = frame()
    db = request.state.db
    
    sql = (
        db.query(
         T_MEMO.uid
        ,T_MEMO.memo
        ,T_MEMO.file_url
        ,T_MEMO.file_name
        ,T_MEMO.create_user
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



# 비밀번호 틀린 기록
def create_fail_password( 
     request: Request
    ,table_name: str
    ,table_uid: int
    ,input_value: str
):  
    request.state.inspect = frame()
    db = request.state.db 
    db_item = T_FAIL_PASSWORD (
         table_name = table_name
        ,table_uid = table_uid
        ,input_value = input_value
        ,user_ip = request.state.user_ip
    )
    db.add(db_item)
    db.flush()

    return (
        db.query(T_FAIL_PASSWORD)
        .filter(
            T_FAIL_PASSWORD.table_name == table_name
            ,T_FAIL_PASSWORD.table_uid == table_uid
            ,T_FAIL_PASSWORD.user_ip == request.state.user_ip
        ).count()
    )

# 비밀번호 5회 틀려서 블록되었는지 검사
def check_block_fail_password (
     request: Request
    ,table_name: str
    ,table_uid: int
) :
    request.state.inspect = frame()
    db = request.state.db
    
    sql = """
        select 
             count(table_uid) as fail_count
            ,max(create_at) as last_fail_at
            ,TIMESTAMPDIFF(MINUTE, now(), DATE_ADD(max(create_at), INTERVAL 10 MINUTE)) as ten_min
        From T_FAIL_PASSWORD
        where table_name = '{table_name}'
        and table_uid = {table_uid}
        and user_ip = '{user_ip}'
        group by table_name, table_uid
    """.format(table_name=table_name, table_uid=table_uid, user_ip=request.state.user_ip)
    
    return db.execute(text(sql)).first()


# 비밀번호 성공 또는 10분 지나서 초기화 할때
def reset_block_fail_password (
     request: Request
    ,table_name: str
    ,table_uid: int
) :
    request.state.inspect = frame()
    db = request.state.db
    
    db.query(T_FAIL_PASSWORD).filter(
        T_FAIL_PASSWORD.table_name == table_name
        ,T_FAIL_PASSWORD.table_uid == table_uid
        ,T_FAIL_PASSWORD.user_ip == request.state.user_ip
    ).delete()

# 비밀번호 틀린 기록 로그 쌓기
def fail_password_history( 
     request: Request
    ,table_name: str
    ,table_uid: int
    ,input_value: str
):  
    request.state.inspect = frame()
    db = request.state.db 
    db_item = T_FAIL_PASSWORD_HISTORY (
         table_name = table_name
        ,table_uid = table_uid
        ,input_value = input_value
        ,user_ip = request.state.user_ip
    )
    db.add(db_item)
    db.flush()

    return (
        db.query(T_FAIL_PASSWORD_HISTORY)
        .filter(
            T_FAIL_PASSWORD_HISTORY.table_name == table_name
            ,T_FAIL_PASSWORD_HISTORY.table_uid == table_uid
            ,T_FAIL_PASSWORD_HISTORY.user_ip == request.state.user_ip
        ).count()
    )

# excel_download_log insert
def excel_download_log(request: Request, excelLogInput: ExcelLogInput):
    request.state.inspect = frame()
    db = request.state.db 
    user = request.state.user

    if excelLogInput.params == '' :
        excelLogInput.params.filters = {}

    db_item = T_EXCEL_DOWNLOAD (
         token_name = user.token_name
        ,user_id = user.user_id
        ,user_name = user.user_name
        ,user_ip = request.state.user_ip
        ,reason = excelLogInput.download_reason
        ,url = excelLogInput.url
        ,params = excelLogInput.params.filters
    )

    db.add(db_item)
    db.flush()

    return db_item
