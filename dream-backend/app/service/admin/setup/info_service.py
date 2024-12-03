from fastapi import Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Optional
from inspect import currentframe as frame
from sqlalchemy.dialects import mysql as mysql_dialetct
from pymysql.converters import conversions, escape_item, encoders
from sqlalchemy import func, select, update, delete, Table, MetaData
import math

from app.core import exceptions as ex
from app.core import util
from app.core.database import format_sql
from app.deps import auth
from app.models.session import *
from app.models.admin import *
from app.models.menu import *
from app.models.partner import *
from app.schemas.schema import *
from app.schemas.admin.auth import *
from app.schemas.admin.admin import *
from app.service import log_service
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Optional
from inspect import currentframe as frame
from sqlalchemy.dialects import mysql as mysql_dialetct
from pymysql.converters import conversions, escape_item, encoders
from sqlalchemy import func, select, update, delete, Table, MetaData
import math

from app.core import exceptions as ex
from app.core import util
from app.core.database import format_sql
from app.deps import auth
from app.models.session import *
from app.models.admin import *
from app.models.menu import *
from app.models.partner import *
from app.schemas.schema import *
from app.schemas.admin.auth import *
from app.schemas.admin.admin import *
from app.service import log_service

# 계정관리_상세정보
def info_read(request: Request):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    sql = (
        db.query(
             T_ADMIN.uid
            ,T_ADMIN.user_id
            ,T_ADMIN.user_name
            ,T_ADMIN.tel
            ,T_ADMIN.mobile
            ,T_ADMIN.email
            ,T_ADMIN.role
            ,T_ADMIN.position1
            ,T_ADMIN.position2
            ,T_ADMIN.depart
        )
        .filter(T_ADMIN.user_id == user.user_id)
    )
    return sql.first()

# 내 정보 보기 - 수정
def info_update(request: Request, myInfoInput: MyInfoInput) :
    request.state.inspect = frame()
    db = request.state.db 
    user = request.state.user

    res = db.query(T_ADMIN).filter(T_ADMIN.user_id == user.user_id).first()

    if res is None :
        return ex.ReturnOK(404, "정보를 찾을 수 없습니다.", request)

    if myInfoInput.tel is not None and res.tel != myInfoInput.tel : 
        log_service.create_log(request, res.uid, "T_ADMIN", "tel", "일반전화번호", res.tel, myInfoInput.tel, user.user_id)
        request.state.inspect = frame()
        res.tel = myInfoInput.tel

    if myInfoInput.mobile is not None and res.mobile != myInfoInput.mobile : 
        log_service.create_log(request, res.uid, "T_ADMIN", "mobile", "핸드폰번호", res.mobile, myInfoInput.mobile, user.user_id)
        request.state.inspect = frame()
        res.mobile = myInfoInput.mobile

    res.update_at = util.getNow()

    return res





