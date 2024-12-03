from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, select, column, table, case
from fastapi import Request
from inspect import currentframe as frame
from typing import Optional

from app.core import util
from app.core.database import format_sql
from app.models.files import *
from app.schemas.schema import *

# 첨부파일 INSERT
def create_files_attach ( 
     request: Request
    ,files: Files
):  
    request.state.inspect = frame()
    db = request.state.db 
    user = request.state.user

    sosok_uid = user.sosok_uid
    sosok_id = user.sosok_id

    db_item = T_FILES_ATTACH (
         table_name = files.table_name
        ,table_uid = files.table_uid
        ,fake_name = files.fake_name
        ,file_name = files.file_name
        ,file_ext = files.file_ext
        ,upload_path = files.upload_path
        ,sort = 0
        ,token_name = user.token_name
        ,sosok_uid = sosok_uid
        ,sosok_id = sosok_id
        ,user_uid = user.user_uid
        ,user_id = user.user_id
        ,user_name = user.user_name
    )
    db.add(db_item)
    db.flush()
    return db_item

# 첨부파일 select
def read_files_attach ( 
     request: Request
    ,attach_uid: int
):  
    request.state.inspect = frame()
    db = request.state.db 
    user = request.state.user
    sql = db.query(T_FILES_ATTACH).filter(T_FILES_ATTACH.uid == attach_uid)
    return sql.first()