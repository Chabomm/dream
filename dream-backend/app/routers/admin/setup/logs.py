from fastapi import APIRouter, Depends, Request, Body
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from inspect import currentframe as frame
from fastapi.responses import RedirectResponse, JSONResponse
from app.core import exceptions as ex
from app.core import util
from app.core.config import PROXY_PREFIX, api_same_origin
from app.core.database import get_session
from app.deps.auth import create_access_token, get_current_active_admin, get_current_user
from app.deps.auth import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES
from fastapi.encoders import jsonable_encoder

from app.core.dbSCM import SessionLocal_scm

from app.schemas.schema import *
from app.service.admin.setup import logs_service
from app.models.session import *
from app.schemas.admin.auth import *
from app.schemas.admin.admin import * 

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/admin/setup/logs"],
)

def 로그_리스트_필터조건(request: Request, type:str):
    request.state.inspect = frame()

    result = {}
    if type == 'detail' :
        result.update({"is_display": [
            {"key": 'T', "text": '진열', "checked": True},
            {"key": 'F', "text": '미진열', "checked": True},
        ]})
    else :
        result.update({"skeyword_type": [
            {"key": 'title', "text": '서비스명'},
        ]})

    return result

# /be/admin/setup/logs/init
@router.post("/admin/setup/logs/init", dependencies=[Depends(api_same_origin)])
async def 로그_리스트_init (
    request: Request
    ,logListInput: LogListInput
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    result = {}

    # [ S ] 초기 파라메터
    params = {
         "page" : 1
        ,"page_view_size": 30
        ,"page_size": 0
        ,"page_total": 0
        ,"page_last": 0
        ,"table_name": logListInput.table_name
        ,"table_uid": logListInput.table_uid
        ,"filters": {
            "skeyword": '',
            "skeyword_type": '',
            "create_at": {
                "startDate": None,
                "endDate": None,
            },
        }
    }
    result.update({"params": params})
    # [ S ] 초기 파라메터

    result.update({"filter": 로그_리스트_필터조건(request,'list')}) # 초기 필터

    return result

# /be/admin/setup/logs/list
@router.post("/admin/setup/logs/list", dependencies=[Depends(api_same_origin)])
async def 로그_리스트(
     request: Request
    ,logListInput: LogListInput
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    request.state.db_scm = SessionLocal_scm() # SCM DB session

    if not logListInput.page or int(logListInput.page) == 0:
        logListInput.page = 1

    if not logListInput.page_view_size or int(logListInput.page_view_size) == 0 :
        logListInput.page_view_size = 30

    table_uid = str(logListInput.table_uid)
        
    _where = ''
    log_title = ""

    if logListInput.table_name == 'T_B2B_SELLER' :
        log_title = "B2B 판매자 정보"
        _where = _where + " AND table_name = 'T_B2B_SELLER' "
        _where = _where + " AND table_uid = " + table_uid + " "

    elif logListInput.table_name == 'T_B2B_SELLER_STAFF' :
        log_title = "B2B 판매자 담당자 정보"
        _where = _where + " AND table_name = 'T_B2B_SELLER_STAFF' "
        _where = _where + " AND table_uid in ( select uid from T_B2B_SELLER_STAFF where seller_uid = " + table_uid + " ) " 

    elif logListInput.table_name == 'B2B_SELLER' :
        log_title = "두개 테이블 봐야할때 예시"
        _where = _where + " AND table_name in ('T_B2B_SELLER', 'T_B2B_SELLER_STAFF') "
        _where = _where + " AND ( "
        _where = _where + "    table_uid = " + table_uid + " "
        _where = _where + "    OR table_uid in ( select uid from T_B2B_SELLER_STAFF where seller_uid = " + table_uid + " ) " 
        _where = _where + ") "
    else :
        _where = _where + " AND 1=0 "


    res = logs_service.log_list(request, logListInput, _where) 
    request.state.inspect = frame()

    res.update({"log_title" : log_title})
    
    return res
