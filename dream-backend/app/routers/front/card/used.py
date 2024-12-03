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
from app.schemas.manager.point.offcard.used import *

from app.service.front.card import used_service
from app.service.offcard import recv_service
from app.service.front import point_service

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/front/card/used"],
)

def F_카드사용_필터조건 (request: Request):
    request.state.inspect = frame()

    result = {}
    result.update({"skeyword_type": [
        {"key": 'a', "text": '이름'},
        {"key": 'a', "text": '생년월일'},
        {"key": 'a', "text": '부서'},
    ]})
 
    # 처리상태
    result.update({"point_state": [
        {"key": '', "text": '전체조회'},
        {"key": '차감완료', "text": '차감완료'},
        {"key": '차감취소', "text": '차감취소'},
    ]})

    return result

# /be/front/card/used/offcard/init
@router.post("/front/card/used/offcard/init", dependencies=[Depends(api_same_origin)])
async def F_복지카드사용_내역_init (
     request: Request
    ,cardUsedInitInput: CardUsedInitInput
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
        ,"user_id": cardUsedInitInput.user_id
        ,"filters": {
            "skeyword": '',
            "skeyword_type": '',
            "create_at": {
                "startDate": None,
                "endDate": None,
            },
            "state": '',
        }
    }
    result.update({"params": params})
    # [ S ] 초기 파라메터

    my_point_res = point_service.get_my_point(request, cardUsedInitInput.user_id, True)
    request.state.inspect = frame()
    result.update(my_point_res)
    result.update({"filter": F_카드사용_필터조건(request)}) # 초기 필터

    return result

# /be/front/card/used/offcard/list
@router.post("/front/card/used/offcard/list", dependencies=[Depends(api_same_origin)])
async def F_복지카드사용_내역 (
     request: Request
    ,cardUsedListInput: CardUsedListInput
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)

    # user = used_service.get_user_info(request, cardUsedListInput.user_id)
    user = used_service.get_ci_from_id(request, cardUsedListInput.user_id)
    request.state.inspect = frame()

    if user == None :
        return ex.ReturnOK(400, "user empty", request)

    if not cardUsedListInput.page or int(cardUsedListInput.page) == 0:
        cardUsedListInput.page = 1

    if not cardUsedListInput.page_view_size or int(cardUsedListInput.page_view_size) == 0:
        cardUsedListInput.page_view_size = 30

    # res = used_service.offcard_used_list(request, cardUsedListInput, res.user_ci)
    res = recv_service.get_EDI06983(request, cardUsedListInput, user)
    request.state.inspect = frame()
        
    return res

# /be/front/card/used/offcard/deduct
@router.post("/front/card/used/offcard/deduct", dependencies=[Depends(api_same_origin)])
async def F_복지카드사용_복지포인트차감신청(
     request:Request
    ,cardUsedInput: CardUsedInput
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)

    user = used_service.get_user_info(request, cardUsedInput.user_id)
    request.state.inspect = frame()

    if user == None :
        return ex.ReturnOK(400, "user empty", request)

    res = used_service.request_offcard_point_deduct(request, cardUsedInput, user)
    request.state.inspect = frame()

    if res == None or res == 0 :
        return ex.ReturnOK(200, "오류가 발생하였습니다.", request)
    else :
        return ex.ReturnOK(200, "처리가 완료되었습니다.", request)



# /be/front/card/used/sikwon/init
@router.post("/front/card/used/sikwon/init", dependencies=[Depends(api_same_origin)])
async def F_식권카드사용_내역_init (
     request: Request
    ,cardUsedInitInput: CardUsedInitInput
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
        ,"user_id": cardUsedInitInput.user_id
        ,"filters": {
            "skeyword": '',
            "skeyword_type": '',
            "create_at": {
                "startDate": None,
                "endDate": None,
            },
            "point_state": '',
        }
    }
    result.update({"params": params})
    # [ S ] 초기 파라메터

    my_point_res = point_service.get_my_point(request, cardUsedInitInput.user_id, True)
    request.state.inspect = frame()
    result.update(my_point_res)
    result.update({"filter": F_카드사용_필터조건(request)}) # 초기 필터

    return result

# /be/front/card/used/sikwon/list
@router.post("/front/card/used/sikwon/list", dependencies=[Depends(api_same_origin)])
async def F_식권카드사용_내역 (
     request: Request
    ,cardUsedListInput: CardUsedListInput
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)

    user = used_service.get_user_info(request, cardUsedListInput.user_id)
    request.state.inspect = frame()

    if user == None :
        return ex.ReturnOK(400, "user empty", request)

    if not cardUsedListInput.page or int(cardUsedListInput.page) == 0:
        cardUsedListInput.page = 1

    if not cardUsedListInput.page_view_size or int(cardUsedListInput.page_view_size) == 0:
        cardUsedListInput.page_view_size = 30

    res = used_service.sikwon_used_list(request, cardUsedListInput, user)
    request.state.inspect = frame()
        
    return res


# /be/front/card/used/sikwon/deduct
@router.post("/front/card/used/sikwon/deduct", dependencies=[Depends(api_same_origin)])
async def F_식권카드사용_식권포인트차감신청(
     request:Request
    ,cardUsedInput: CardUsedInput
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)

    user = used_service.get_user_info(request, cardUsedInput.user_id)
    request.state.inspect = frame()

    if user == None :
        return ex.ReturnOK(400, "user empty", request)

    res = used_service.request_sikwon_point_deduct(request, cardUsedInput, user)
    request.state.inspect = frame()

    if res == None or res == 0 :
        return ex.ReturnOK(200, "오류가 발생하였습니다.", request)
    else :
        return ex.ReturnOK(200, "처리가 완료되었습니다.", request)









# /be/front/card/deduct/init
@router.post("/front/card/deduct/init", dependencies=[Depends(api_same_origin)])
async def F_카드_포인트차감_내역_init (
     request: Request
    ,cardUsedInitInput: CardUsedInitInput
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
        ,"user_id": cardUsedInitInput.user_id
        ,"filters": {
            "skeyword": '',
            "skeyword_type": '',
            "create_at": {
                "startDate": None,
                "endDate": None,
            },
            "confirm_at": {
                "startDate": None,
                "endDate": None,
            },
            "point_state": '',
        }
    }
    result.update({"params": params})
    # [ S ] 초기 파라메터

    my_point_res = point_service.get_my_point(request, cardUsedInitInput.user_id, True)
    request.state.inspect = frame()
    result.update(my_point_res)
    result.update({"filter": F_카드사용_필터조건(request)}) # 초기 필터

    return result

# /be/front/card/deduct/list
@router.post("/front/card/deduct/list", dependencies=[Depends(api_same_origin)])
async def F_카드_포인트차감_내역 (
     request: Request
    ,cardDeductListInput: CardDeductListInput
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)

    if not cardDeductListInput.page or int(cardDeductListInput.page) == 0:
        cardDeductListInput.page = 1

    if not cardDeductListInput.page_view_size or int(cardDeductListInput.page_view_size) == 0:
        cardDeductListInput.page_view_size = 30

    res = used_service.deduct_list(request, cardDeductListInput)
    request.state.inspect = frame()
        
    return res
