from fastapi import APIRouter, Depends, Request, Body
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from inspect import currentframe as frame
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core import exceptions as ex
from app.core import util
from app.core.config import PROXY_PREFIX, api_same_origin
from app.deps.auth import get_current_active_manager
import json

from app.schemas.schema import *
from app.schemas.manager.auth import *

from app.service.manager.point import balance_service

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/manager/point/limit"],
)

def 복지몰_사용제한_필터조건 (request: Request):
    request.state.inspect = frame()

    result = {}
    result.update({"skeyword_type": [
        {"key": 'a', "text": '업종명'},
        {"key": 'a', "text": '업종코드'},
    ]})
 
    # 처리상태
    # result.update({"state": [
    #     {"key": '', "text": '전체'},
    #     {"key": '차감완료', "text": '차감완료'},
    #     {"key": '차감취소', "text": '차감취소'},
    # ]})

    return result

# /be/manager/point/limit/mall/init
@router.post("/manager/point/limit/mall/init", dependencies=[Depends(api_same_origin)])
async def 복지몰_사용제한_내역_init (
     request: Request
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
            "create_at": {
                "startDate": None,
                "endDate": None,
            },
        }
    }
    result.update({"params": params})
    # [ S ] 초기 파라메터

    result.update({"filter": 복지몰_사용제한_필터조건(request)}) # 초기 필터

    return result

# /be/manager/point/limit/mall/list
@router.post("/manager/point/limit/mall/list", dependencies=[Depends(api_same_origin)])
async def 복지몰_사용제한_내역 (
     request: Request
    ,pPage_param: PPage_param
    ,user: TokenDataManager = Depends(get_current_active_manager)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)

    if not pPage_param.page or int(pPage_param.page) == 0:
        pPage_param.page = 1

    if not pPage_param.page_view_size or int(pPage_param.page_view_size) == 0:
        pPage_param.page_view_size = 30

    # res = used_service.used_list(request, pPage_param)
    # request.state.inspect = frame()
        
    res = {}
    res.update({"params": pPage_param})
    res.update({"list": []})

    return res

