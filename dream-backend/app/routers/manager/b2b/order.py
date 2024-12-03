from fastapi import APIRouter, Depends, Request, Body
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from inspect import currentframe as frame
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse
from app.core import exceptions as ex
from app.core import util
from app.core.config import PROXY_PREFIX, api_same_origin
from app.core.database import get_session
from app.deps.auth import create_access_token, get_current_active_manager, get_current_user
from app.deps.auth import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES
import os
import requests
import json
from fastapi.encoders import jsonable_encoder

from app.core.dbSCM import SessionLocal_scm

from app.schemas.manager.b2b.goods import *
from app.schemas.schema import *
from app.schemas.manager.auth import *
from app.schemas.manager.b2b.order import *
from app.service.manager.b2b import order_service
from app.service.manager.setup import manager_service
from app.service import partner_service

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/manager/b2b/order"],
)

def 서비스상품_신청_필터조건(request: Request):
    result = {}
    result.update({"skeyword_type": [
        {"key": 'title', "text": '서비스명'},
        {"key": 'apply_name', "text": '작성자'},
        {"key": 'apply_position', "text": '직급/직책'},
    ]})

    result.update({"category": [
        {"key": '', "text": '전체'},
        {"key": '기업지원', "text": '기업지원'},
        {"key": '인사총무', "text": '인사총무'},
        {"key": '마케팅/광고/홍보', "text": '마케팅/광고/홍보'},
        {"key": '기업복지', "text": '기업복지'},
        {"key": '영업관리', "text": '영업관리'},
        {"key": '기타', "text": '기타'},
    ]})
    
    result.update({"state": [
        {"key": '', "text": '전체', "checked": True},
        {"key": '신규상담', "text": '신규상담', "checked": True},
        {"key": '상담중', "text": '상담중', "checked": True},
        {"key": '진행보류', "text": '진행보류', "checked": True},
        {"key": '계약미진행', "text": '계약미진행', "checked": True},
        {"key": '계약진행', "text": '계약진행', "checked": True},
    ]})
    return result

# /be/manager/b2b/order/init
@router.post("/manager/b2b/order/init", dependencies=[Depends(api_same_origin)])
async def 서비스상품_신청_내역_init (
     request : Request
    ,user: TokenDataManager = Depends(get_current_active_manager)
):  
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)
    
    result = {}

    # [ S ] 초기 파라메터
    params = {
         "page" : 1
        ,"page_view_size": 30
        ,"page_size": 0
        ,"page_total": 0
        ,"page_last": 0
        ,"filters": {
            "skeyword": '',
            "skeyword_type": '',
            "category": "",
            "state": '',
            "create_at": {
                "startDate": None,
                "endDate": None,
            },

        }
    }
    result.update({"params": params})
    # [ S ] 초기 파라메터

    result.update({"filter": 서비스상품_신청_필터조건(request)}) # 초기 필터

    return result

# be/manager/b2b/order/list
@router.post("/manager/b2b/order/list", dependencies=[Depends(api_same_origin)])
async def 서비스상품_신청_내역 (
     request: Request
    ,page_param : PPage_param
    ,user: TokenDataManager = Depends(get_current_active_manager)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)

    request.state.db_scm = SessionLocal_scm() # SCM DB session

    if not page_param.page or int(page_param.page) == 0:
        page_param.page = 1

    if not page_param.page_view_size or int(page_param.page_view_size) == 0:
        page_param.page_view_size = 30

    res = order_service.order_list(request, page_param)
    request.state.inspect = frame()

    return res

# /be/manager/b2b/order/detail
@router.post("/manager/b2b/order/detail", dependencies=[Depends(api_same_origin)])
async def 서비스_신청_상세(
     request: Request
    ,orderInput : OrderInput
    ,user: TokenDataManager = Depends(get_current_active_manager)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)

    if orderInput.partner_uid != 0 :
        partner = partner_service.read_partner_by_puid(request, orderInput.partner_uid)
        request.state.inspect = frame()

    manager = manager_service.admin_user_read(request, orderInput.user_uid)
    request.state.inspect = frame()

    if orderInput.partner_uid != 0 :
        orderInput.company_name = partner.company_name
    else :
        orderInput.company_name = ''
    orderInput.manager = manager

    jsondata = {}
    jsondata.update(orderInput)
        
    return ex.ReturnOK(200, "", request, jsondata, False)

# /be/manager/b2b/order/read
@router.post("/manager/b2b/order/read", dependencies=[Depends(api_same_origin)])
async def 신청내역_상세(
     request: Request
    ,uid : PRead
    ,user: TokenDataManager = Depends(get_current_active_manager)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)

    request.state.db_scm = SessionLocal_scm() # SCM DB session

    apply = order_service.order_read(request, uid.uid)
    request.state.inspect = frame()
        
    return ex.ReturnOK(200, "", request, apply, False)
