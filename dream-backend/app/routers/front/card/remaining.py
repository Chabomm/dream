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
from app.schemas.manager.point.offcard.remaining import *

from app.service.front.card import remaining_service
from app.service.front.card import used_service

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/front/card/remaining"],
)

def 환급내역_필터조건 (request: Request):
    request.state.inspect = frame()

    result = {}
    result.update({"skeyword_type": [
        {"key": 'a', "text": '사용내역'},
        {"key": 'a', "text": '카드'},
        {"key": 'a', "text": '입금은행'},
    ]})

    return result

# /be/front/card/remaining/init
@router.post("/front/card/remaining/init", dependencies=[Depends(api_same_origin)])
async def 환급내역_init (
     request: Request
    ,cardRemainingInitInput: CardRemainingInitInput
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
        ,"user_id": cardRemainingInitInput.user_id
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
    result.update({"filter": 환급내역_필터조건(request)}) # 초기 필터

    return result

# /be/front/card/remaining/list
@router.post("/front/card/remaining/list", dependencies=[Depends(api_same_origin)])
async def 환급내역 (
     request: Request
    ,cardRemainingListInput: CardRemainingListInput
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)

    user = used_service.get_user_info(request, cardRemainingListInput.user_id)
    request.state.inspect = frame()

    if not cardRemainingListInput.page or int(cardRemainingListInput.page) == 0:
        cardRemainingListInput.page = 1

    if not cardRemainingListInput.page_view_size or int(cardRemainingListInput.page_view_size) == 0:
        cardRemainingListInput.page_view_size = 30

    remaining_price = remaining_service.get_my_remaining(request, cardRemainingListInput, user)

    res = remaining_service.offcard_remaining_list(request, cardRemainingListInput, user)
    request.state.inspect = frame()

    res.update({"remaining_price": remaining_price})
        
    return res

