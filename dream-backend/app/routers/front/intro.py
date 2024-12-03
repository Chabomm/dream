from fastapi import APIRouter, Depends, Request, Body
from inspect import currentframe as frame
import urllib
import json
import requests
import os
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse, JSONResponse
from app.core import exceptions as ex
from app.core import util
from app.core.config import PROXY_PREFIX, api_same_origin
from app.core.database import get_session
from app.deps.auth import create_access_token, get_current_active_front, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES

from app.schemas.schema import *
from app.models.session import *
from app.schemas.front.auth import *
from app.schemas.front.intro import *

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/front/intro"],
)

# be/front/intro
@router.post("/front/intro", dependencies=[Depends(api_same_origin)])
async def 앱_인트로(
     request: Request
    ,user: TokenDataDream = Depends(get_current_active_front)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataDream(user), getTokenDataDream(user)

    return {}

# be/front/intro/dream
@router.post("/front/intro/dream", dependencies=[Depends(api_same_origin)])
async def 복지드림_인트로_화면(
    request:Request
    ,user: TokenDataDream = Depends(get_current_active_front)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataDream(user), getTokenDataDream(user)

    if os.environ.get('PROFILE') == 'development' :
        URL = "http://192.168.0.81:8888/api/dream/app/intro.json.asp"
    else :
        URL = "https://devindend.co.kr/api/dream/app/intro.json.asp"
    

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'
        ,'X-TOKEN': user.access_token
    }


    result = ""
    params = urllib.parse.urlencode({ 
        "user_id":user.user_id,
        "partner_id":user.partner_id
    })
    result = requests.post(URL, headers=headers, data=params).text

    try :
        result = json.loads(result)
        # DreamBuild()
    except Exception as e:
        return ex.ReturnOK(500, "예기치 못한 오류가 발생하였습니다.\n문제 지속시 고객센터(032-719-3366)로 문의 바랍니다.\n평일 10:00~18:00(점심 11:30~12:30)\n주말/공휴일 휴무", request)

    return result

# be/front/intro/agreement
@router.post("/front/intro/agreement", dependencies=[Depends(api_same_origin)])
async def 복지드림_약관_정보 (
    request:Request
    ,user: TokenDataDream = Depends(get_current_active_front)
    ,agreementInput: AgreementInput = Body(
        ...,
        examples = {
            "example01" : {
                "summary": "복지드림_약관_정보",
                "description": "",
                "value": {
                    "mode" : 'licensing',
                    "partner_name" : '데모컴퍼니'
                }
            }
        }
    )
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataDream(user), getTokenDataDream(user)

    if os.environ.get('PROFILE') == 'development' :
        URL = "http://192.168.0.81:8888/api/dream/app/terms.json.asp"
    else :
        URL = "http://112.221.134.106:8888/api/dream/app/terms.json.asp"


    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'
    }

    result = ""
    params = urllib.parse.urlencode({
        "mode" : agreementInput.mode
        ,"partner_name" : agreementInput.partner_name
    })
    result = requests.post(URL, headers=headers, data=params).text

    try :
        result = json.loads(result)
        # DreamBuild()
    except Exception as e:
        return ex.ReturnOK(500, "예기치 못한 오류가 발생하였습니다.\n문제 지속시 고객센터(032-719-3366)로 문의 바랍니다.\n평일 10:00~18:00(점심 11:30~12:30)\n주말/공휴일 휴무", request, {"response":result})

    return result


# # be/front/intro/welfare/signin
# @router.post("/front/intro/welfare/signin")
# async def 복지몰_로그인 (
#     request: Request
#     ,authNumInput: dict = Body(
#         ...,
#         examples = {
#             "example01" : {
#                 "summary": "복지몰 로그인",
#                 "description": "",
#                 "value": {
#                     "uid" : "1",
#                     "auth_num" : "123465",
#                     "login_id" : "uhjung",
#                     "email" : "uhjung@indend.co.kr",
#                     "mobile" : "010-3231-7638",
#                     "partner_uid" : 126
#                 }
#             },
#         }
#     )
#     ,user: TokenDataDream = Depends(get_current_active_front)
# ):
#     request.state.inspect = frame()

#     token_data = TokenDataDream (
#         token_name = "DREAM"
#         ,partner_uid = user.partner_uid
#         ,partner_id = user.partner_id
#         ,user_uid = user.user_uid
#         ,user_id = user.user_id
#         ,user_name = user.user_name
#         ,user_depart = ""
#         ,user_type = ""
#     )

#     access_token = create_access_token(data=util.toJson(token_data), expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#     refresh_token = create_access_token(data=util.toJson(token_data), expires_delta=timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES))

#     session_param = T_SESSION (
#          site_id = token_data.token_name
#         ,user_uid = token_data.user_uid
#         ,user_id = token_data.user_id
#         ,access_token = access_token
#         ,refresh_token = refresh_token
#         ,ip = util.getClientIP(request)
#     )

#     token_data.access_token = access_token
#     request.state.user = token_data

#     session_service.create_session(request, session_param)
#     request.state.inspect = frame()

#     # 파트너 정보(로고)
#     partner_info = partner_service.get_partner_read(request)
#     request.state.inspect = frame()

#     response = JSONResponse(
#         ex.ReturnOK(200, "", request, {
#             "access_token": access_token
#             ,"token_type": "bearer"
#             ,"partner_info": partner_info
#             ,"partner_list": []
#         })
#     )

#     response.set_cookie( key=token_data.token_name, value=access_token )

#     return response
