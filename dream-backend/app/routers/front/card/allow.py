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
from app.schemas.manager.point.offcard.allow import *

from app.service.front.card import allow_service

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/front/card/allow"],
)

def F_카드허용업종_필터조건 (request: Request):
    request.state.inspect = frame()

    result = {}
    result.update({"skeyword_type": [
        {"key": 'a', "text": '이름'},
        {"key": 'a', "text": '생년월일'},
        {"key": 'a', "text": '부서'},
    ]})

    return result

# init 에서 
# bokji or sikwon 인지 받아오고
# use_type
# 스키마 아래랑 비슷
# class CardDeductListInput(PPage_param):
#     use_type: Optional[str] = Field(None, title="사용종류(bokji, sikwon)")
#     user_id: Optional[str] = Field(None, title="사용자아이디")
#     class Config:
#         orm_mode = True

# /be/front/card/allow/init
@router.post("/front/card/allow/init", dependencies=[Depends(api_same_origin)])
async def F_카드허용업종_내역_init (
     request: Request
    ,cardAllowListInput: CardAllowListInput
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)

    result = {}

    # [ S ] 초기 파라메터
    params = {
         "use_type": cardAllowListInput.use_type
        ,"user_id": cardAllowListInput.user_id
    }
    result.update({"params": params})
    # [ S ] 초기 파라메터

    # result.update({"filter": F_카드허용업종_필터조건(request)}) # 초기 필터

    return result


# /be/front/card/allow/list
@router.post("/front/card/allow/list", dependencies=[Depends(api_same_origin)])
async def F_카드허용업종_내역 (
     request: Request
    ,cardAllowListInput: CardAllowListInput
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)

    user = allow_service.get_user_info(request, cardAllowListInput.user_id)
    request.state.inspect = frame()

    if user == None :
        return ex.ReturnOK(400, "user empty", request)
    
    if cardAllowListInput.use_type == 'bokji' :
        allow_list = allow_service.allow_bokji_list(request, user)
        request.state.inspect = frame()
    elif cardAllowListInput.use_type == 'sikwon' :
        allow_list = allow_service.allow_sikwon_list(request, user)
        request.state.inspect = frame()
        
    return ex.ReturnOK(200, "", request, allow_list, False)