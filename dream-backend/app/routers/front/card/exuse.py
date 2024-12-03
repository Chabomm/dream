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
from app.schemas.manager.point.offcard.exuse import *
from app.service.front.card import exuse_service

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/front/card/exuse"],
)

def 소명신청_필터조건 (request: Request):
    request.state.inspect = frame()

    result = {}
    result.update({"skeyword_type": [
        {"key": 'a', "text": '이름'},
        {"key": 'a', "text": '생년월일'},
        {"key": 'a', "text": '부서'},
    ]})

    return result

# /be/front/card/exuse/init
@router.post("/front/card/exuse/init", dependencies=[Depends(api_same_origin)])
async def 소명신청_내역_init (
     request: Request
    ,cardExuseInitInput: CardExuseInitInput
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)

    result = {}

    # [ S ] 초기 파라메터
    params = {
         "page" : 1
        ,"page_view_size": 30
        ,"page_size": 0
        ,"page_total": 0
        ,"page_last": 0
        ,"user_id": cardExuseInitInput.user_id
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

    result.update({"filter": 소명신청_필터조건(request)}) # 초기 필터

    return result

# /be/front/card/exuse/list
@router.post("/front/card/exuse/list", dependencies=[Depends(api_same_origin)])
async def 소명신청_내역 (
     request: Request
    ,cardExuseListInput: CardExuseListInput
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)

    user = exuse_service.get_user_join_member(request, cardExuseListInput.user_id)
    request.state.inspect = frame()

    if user == None :
        return ex.ReturnOK(400, "user empty", request)

    if not cardExuseListInput.page or int(cardExuseListInput.page) == 0:
        cardExuseListInput.page = 1

    if not cardExuseListInput.page_view_size or int(cardExuseListInput.page_view_size) == 0:
        cardExuseListInput.page_view_size = 30

    exuse_price = exuse_service.get_my_exuse(request, cardExuseListInput, user)

    res = exuse_service.list(request, cardExuseListInput, user)
    request.state.inspect = frame()

    res.update({"sum_exuse_price": exuse_price})
        
    return res


# /be/front/card/exuse/read
@router.post("/front/card/exuse/read", dependencies=[Depends(api_same_origin)])
async def 소명신청내용_상세(
     request: Request
    ,cardExuseReadInput: CardExuseReadInput
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)

    res = exuse_service.read(request, cardExuseReadInput)
    request.state.inspect = frame()
    
    return res






















# /be/front/card/exuse/edit
@router.post("/front/card/exuse/edit", dependencies=[Depends(api_same_origin)])
async def F_카드사용_소명신청(
     request:Request
    ,cardExuseInput: CardExuseInput
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)

    user = exuse_service.get_user_join_member(request, cardExuseInput.user_id)
    request.state.inspect = frame()

    if user == None :
        return ex.ReturnOK(400, "user empty", request)
    
    res = exuse_service.exuse_card_edit(request, cardExuseInput, user)
    request.state.inspect = frame()

    if res == None or res == 0 :
        return ex.ReturnOK(300, "이미 신청되었거나, 존재하지 않은 사용건 입니다.", request)
    else :
        return ex.ReturnOK(200, "처리가 완료되었습니다.", request)
