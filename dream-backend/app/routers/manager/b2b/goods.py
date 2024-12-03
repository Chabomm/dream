
from fastapi import APIRouter, Depends, Request, Body, Response
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
from urllib import parse

from app.core.dbSCM import SessionLocal_scm

from app.schemas.manager.b2b.goods import *
from app.schemas.manager.auth import *
from app.schemas.manager.b2b import *
from app.service.manager.b2b import goods_service
from app.service import partner_service

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/manager/b2b/goods"],
)

def 서비스상품_필터조건(request: Request):
    result = {}
    result.update({"category": [
        {"key": '', "text": '전체'},
        {"key": '기업지원', "text": '기업지원'},
        {"key": '인사총무', "text": '인사총무'},
        {"key": '마케팅/광고/홍보', "text": '마케팅/광고/홍보'},
        {"key": '기업복지', "text": '기업복지'},
        {"key": '영업관리', "text": '영업관리'},
        {"key": '기타', "text": '기타'},
    ]})

    return result

# /be/manager/b2b/goods/init
@router.post("/manager/b2b/goods/init", dependencies=[Depends(api_same_origin)])
async def 서비스상품_내역_inti (
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
            "category" : ''
        }
    }
    result.update({"params": params})
    # [ S ] 초기 파라메터

    result.update({"filter": 서비스상품_필터조건(request)}) # 초기 필터

    return result

# be/manager/b2b/goods/list
@router.post("/manager/b2b/goods/list", dependencies=[Depends(api_same_origin)])
async def 서비스상품_내역 (
     request: Request
    ,page_param: PPage_param
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

    res = goods_service.goods_list(request, page_param)
    request.state.inspect = frame()

    return res











