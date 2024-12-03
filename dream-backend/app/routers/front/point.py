from fastapi import APIRouter, Depends, Request, Body, Response, HTTPException, status
from inspect import currentframe as frame
import os, json, urllib, requests
from app.core import exceptions as ex
from app.core import util
from app.core.config import PROXY_PREFIX, api_same_origin

from app.schemas.schema import *
from app.schemas.front.point import *
from app.service.front import point_service

from app.core.cipher import aes256

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/front/point"],
)

dream_key = "00000000000000000000000000000000"
dream_IV  = "9999999999999999"

def check_header(request: Request, response: Response) :
    api_key = request.headers.get('api_key')
    print("┏────────────request.headers.get────────────┓")
    print(api_key)
    print("└───────────────────────────────────────────┘")
    if os.environ.get('PROFILE') != 'development' and util.null2Blank(api_key) == "" :
        raise ex.InvalidApiKeyError

# be/front/point/info
@router.post("/front/point/info", dependencies=[Depends(check_header)])
async def F_복지포인트_잔액 (
    request: Request
    ,pointInfo: PointInfo
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)

    if util.null2Blank(pointInfo.user_id) == "" :
        return ex.ReturnOK(502, "user id empty", request)
    
    try : 
        aes = aes256.AesBase64(dream_key, dream_IV)
        user_id = aes.decrypt(pointInfo.user_id)
    except Exception as e:
        print(pointInfo.user_id, str(e))
        return ex.ReturnOK(503, "user id decrypt fail", request)

    if util.null2Blank(user_id) == "" :
        return ex.ReturnOK(504, "user id empty", request)
    
    res = point_service.get_my_point(request, user_id, False)
    request.state.inspect = frame()
    
    return ex.ReturnOK(200, "OK", request, res)

# be/front/point/use
@router.post("/front/point/use", dependencies=[Depends(check_header)])
async def F_복지포인트_사용 (
    request: Request
    ,pointUse: PointUse
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)

    try : 
        aes = aes256.AesBase64(dream_key, dream_IV)
        pointUse.user_id = aes.decrypt(pointUse.user_id)
        pointUse.order_no = aes.decrypt(pointUse.order_no)
        pointUse.order_uid = aes.decrypt(pointUse.order_uid)
        pointUse.use_point = aes.decrypt(pointUse.use_point)
        pointUse.reason = aes.decrypt(pointUse.reason)
    except Exception as e:
        print(str(e))
        return ex.ReturnOK(503, "decrypt fail", request)

    user = point_service.get_user_info(request, pointUse.user_id)
    request.state.inspect = frame()
    my_spare_point = point_service.use_point(request, pointUse, user)
    request.state.inspect = frame()
    returnData = {"my_spare_point" : my_spare_point}

    if my_spare_point >= 0 : 
        return ex.ReturnOK(200, "OK", request, returnData)
    
    else : # 음수이면 잔액이 부족한거, router가 따로 에러처리
        return ex.ReturnOK(500, "잔액이 부족합니다.", request, returnData)



# be/front/point/cancel
@router.post("/front/point/cancel", dependencies=[Depends(check_header)])
async def F_복지포인트_취소 (
    request: Request
    ,pointCancel: PointCancel
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)

    try : 
        aes = aes256.AesBase64(dream_key, dream_IV)
        pointCancel.user_id = aes.decrypt(pointCancel.user_id)
        pointCancel.order_no = aes.decrypt(pointCancel.order_no)
        pointCancel.order_uid = aes.decrypt(pointCancel.order_uid)
        pointCancel.cancel_point = aes.decrypt(pointCancel.cancel_point)
        pointCancel.reason = aes.decrypt(pointCancel.reason)
    except Exception as e:
        print(str(e))
        return ex.ReturnOK(503, "decrypt fail", request)

    user = point_service.get_user_info(request, pointCancel.user_id)
    request.state.inspect = frame()
    
    poss_remaining_point = point_service.cancel_point(request, pointCancel, user)
    request.state.inspect = frame()

    # 환불요청 후 더 환불 가능한 포인트
    returnData = {"poss_remaining_point" : poss_remaining_point}

    if poss_remaining_point >= 0 : 
        return ex.ReturnOK(200, "OK", request, returnData)
    
    else : # 음수이면 환불가능금액보다 큰 금액을 요청한거
        return ex.ReturnOK(500, "환불가능한 금액보다 많은금액을 요청했습니다.", request, returnData)


