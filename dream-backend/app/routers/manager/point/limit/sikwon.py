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
from app.schemas.manager.point.limit.industry import *

from app.service.manager.limit import card_service
from app.service.manager.limit import sikwon_service

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/manager/point/limit"],
)

def 식권카드_허용업종_필터조건 (request: Request):
    request.state.inspect = frame()

    result = {}
    result.update({"skeyword_type": [
        {"key": 'name', "text": '업종명'},
        {"key": 'code', "text": '업종코드'},
    ]})
 
    # 허용여부
    result.update({"yn": [
        {"key": '', "text": '전체'},
        {"key": 'Y', "text": '허용'},
        {"key": 'N', "text": '제한'},
    ]})

    return result

# /be/manager/point/limit/sikwon/init
@router.post("/manager/point/limit/sikwon/init", dependencies=[Depends(api_same_origin)])
async def 식권카드_허용업종_내역_init (
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
            "checked": []
            ,"yn": ""
        }
    }
    result.update({"params": params})
    # [ S ] 초기 파라메터

    result.update({"filter": 식권카드_허용업종_필터조건(request)}) # 초기 필터

    return result

# /be/manager/point/limit/sikwon/list
@router.post("/manager/point/limit/sikwon/list", dependencies=[Depends(api_same_origin)])
async def 식권카드_허용업종_내역 (
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

    res = card_service.industry_list(request, pPage_param, "T_INDUSTRY_SIKWON")
    request.state.inspect = frame()

    return res


# /be/manager/point/limit/sikwon/edit
@router.post("/manager/point/limit/sikwon/edit", dependencies=[Depends(api_same_origin)])
async def 식권카드_허용업종_등록 (
     request: Request
    ,limitIndustryInput: LimitIndustryInput
    ,user: TokenDataManager = Depends(get_current_active_manager)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)

    if limitIndustryInput.mode == 'REG' :
        sikwon_service.industry_create(request, limitIndustryInput)
        request.state.inspect = frame()
        return ex.ReturnOK(200, "식권카드 업종 허용이 완료되었습니다.", request, {})
    
    if limitIndustryInput.mode == 'DEL' :
        sikwon_service.industry_delete(request, limitIndustryInput)
        request.state.inspect = frame()
        
        return ex.ReturnOK(200, "식권카드 업종 제외가 되었습니다.", request, {})