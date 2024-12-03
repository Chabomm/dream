import os
import json
import requests
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Body
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from inspect import currentframe as frame
from fastapi.responses import RedirectResponse, JSONResponse
import string
import random
from app.core import exceptions as ex
from app.core import util
from app.core.config import PROXY_PREFIX, api_same_origin
from app.core.database import get_session
from app.deps.auth import create_access_token
from app.deps.auth import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES, get_current_active_front

from app.service import session_service
from app.service.front import auth_service, member_service, partner_service
from app.models.session import *
from app.schemas.front.auth import *

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/front/auth"],
)

# be/front/auth/send
@router.post("/front/auth/send")
def 앱사용자_인증번호_발송 (
    request: Request,
    response: Response,
    authNum: AuthNum = Body(
        ...,
        examples = {
            "example01" : {
                "summary": "문자인증",
                "description": "",
                "value": {
                    "send_type" : "mobile",
                    "value" : "010-3231-7638",
                    "login_id" : "uhjung"
                }
            },
            "example02" : {
                "summary": "이메일인증",
                "description": "",
                "value": {
                    "send_type" : "email",
                    "value" : "uhjung@indend.co.kr",
                    "login_id" : "uhjung"
                }
            },
        }
    )
):
    request.state.inspect = frame()

    # 회원 select
    member = member_service.member_read(request, authNum)
    request.state.inspect = frame()

    # None => 없으니깐 다시 확인하라고 메시지 리턴
    if member == None :
        return ex.ReturnOK(404, "일치하는 정보가 없습니다", request, {})
    # 그리고나서 밑에 소스는 실행안됨 

    # 6가지 랜덤숫자
    _LENGTH = 6
    string_pool = string.digits
    random_num = "" #결과값
    for i in range(_LENGTH) :
        random_num += random.choice(string_pool)     

    # 4가지 랜덤숫자
    LENGTH_SMS = 4
    string_SMS = string.digits
    sms_num = "" #결과값
    for i in range(LENGTH_SMS) :
        sms_num += random.choice(string_SMS)

    if authNum.send_type == 'email' :
        params = {
            "ums_uid": 1,
            "send_list": [
                {
                    "ums_type": "email",
                    "msgId": "sample_0001",
                    "toEmail": authNum.value,
                    "#{받는사람}": "복지몰명이라고치고",
                    "#{보내는사람}": random_num
                }
            ]
        }
    else :
        params = {
            "ums_uid": 2,
            "send_list": [
                {
                    "ums_type": "sms",
                    "msgId": "sample_"+sms_num,
                    "toMobile": authNum.value,
                    "#{플랫폼}": "복지몰명이라고치고",
                    "#{인증번호}": random_num,
                }
            ]
        }


    URL = "https://api.bokjidream.com/api/ums/send"

    headers = {
        'Content-Type': 'application/json; charset=utf-8'
    }
    send_result = requests.post(URL, headers=headers, data=json.dumps(params)).text
    send_result = json.loads(send_result)
    
    
    if send_result[0]["result"] == "OK" :
        auth_confirm = auth_service.auth_num_create(request, random_num, authNum)
        request.state.inspect = frame()


    return ex.ReturnOK(200, "", request, {"uid":auth_confirm.uid})

# be/front/auth/send/vaild
@router.post("/front/auth/send/vaild")
async def 앱사용자_인증번호_확인 (
    request: Request,
    response: Response,
    authNumInput: AuthNumInput = Body(
        ...,
        examples = {
            "example01" : {
                "summary": "로그인",
                "description": "",
                "value": {
                    "uid" : "2",
                    "auth_num" : "688844",
                    "login_id" : "uhjung",
                    "email" : "uhjung@indend.co.kr",
                    "mobile" : "010-3231-7638"
                }
            },
        }
    )
):
    request.state.inspect = frame()

    # result = auth_service.auth_num_vaild(request, authNumInput)
    # request.state.inspect = frame()

    # if result["code"] != 200 :
    #     return ex.ReturnOK(result["code"], result["msg"], request, {})
    # result["partner_list"] = []
    
    
    # 회원정보 select  
    member = member_service.read(request, authNumInput.login_id)
    # member = member_service.read(request, authNumInput.login_id, authNumInput.email, authNumInput.mobile)
    request.state.inspect = frame()

    # 이부분 삭제
    result = {}
    result["partner_list"] = []
    # 이부분 삭제
    
    # if member가 두줄이상인경우 고객사정보(로고, 회사명, 복지몰명, uid, id) 리스트로 리턴
    # 회원정보가 2개 이상인 경우 고객사정보 리스트로 리턴
    if len(member) >= 2 :
        uids = []
        for item in member:
            uids.append(item["partner_uid"])
        partner = partner_service.list(request, uids)
        request.state.inspect = frame()

        result["partner_list"] = partner
        return result
    else :
        result = await 앱사용자_로그인(request, {
            "uid": authNumInput.uid
            ,"login_id": authNumInput.login_id
            ,"mobile": authNumInput.mobile
            ,"partner_uid": member[0]["partner_uid"]
        })

        return result
 
# be/front/auth/signin
@router.post("/front/auth/signin")
async def 앱사용자_로그인 (
    request: Request,
    authNumInput: dict = Body(
        ...,
        examples = {
            "example01" : {
                "summary": "로그인",
                "description": "",
                "value": {
                    "uid" : "1",
                    "login_id" : "uhjung",
                    "mobile" : "010-3231-7638",
                    "partner_uid" : 126
                }
            },
        }
    )
):
    request.state.inspect = frame()

    user = member_service.login_read(request, authNumInput)
    request.state.inspect = frame()

    token_data = TokenDataDream (
        token_name = "DREAM"
        ,partner_uid = user.partner_uid
        ,partner_id = user.partner_id
        ,user_uid = user.uid
        ,user_id = user.user_id
        ,user_name = user.user_name
        ,user_depart = ""
        ,user_type = ""
    )

    access_token = create_access_token(data=util.toJson(token_data), expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_access_token(data=util.toJson(token_data), expires_delta=timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES))

    session_param = T_SESSION (
         site_id = token_data.token_name
        ,user_uid = token_data.user_uid
        ,user_id = token_data.user_id
        ,access_token = access_token
        ,refresh_token = refresh_token
        ,ip = request.state.user_ip
        ,profile = os.environ.get('PROFILE')
    )

    token_data.access_token = access_token
    request.state.user = token_data

    session_service.create_session(request, session_param)
    request.state.inspect = frame()

    # 파트너 정보(로고)
    partner_info = partner_service.get_partner_read(request)
    request.state.inspect = frame()

    response = JSONResponse(
        ex.ReturnOK(200, "", request, {
            "access_token": access_token
            ,"token_type": "bearer"
            ,"partner_info": partner_info
            ,"partner_list": []
        })
    )

    response.set_cookie( key=token_data.token_name, value=access_token )

    return response

# 로그아웃
@router.post(path="/front/logout")
async def logout (
     request: Request
    ,response: Response
    ,user: TokenDataDream = Depends(get_current_active_front)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataDream(user), getTokenDataDream(user)
    
    session_service.delete_session(request, user.user_uid) # 세션 제거
    response.delete_cookie(request.state.user.token_name) # 쿠키 제거

    response = JSONResponse(
        ex.ReturnOK(200, "", request, {})
    )

    return response













# be/front/test
@router.get("/front/test")
async def 테스트 (
    request: Request,
    response: Response,
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    print("--- request")
    print(request.__dict__)

    print(".")
    print(".")
    print(str(request.headers.get('x-real-ip')))
    print(str(request.headers.get('x-user-ip')))
    print(".")
    print(".")

    return {}

# [ S ] ---- 레거시 

# be/front/auth/device
@router.post("/front/auth/device")
async def 레거시_앱_디바이스_등록 (
    request: Request,
    request_body: dict
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)

    timestr = util.getNow("%Y-%m-%d")
    file_name = timestr + ".log"

    logm = util.getNow() + " |:| " + request.state.user_ip + "\n"
    logm = logm + "┏────────────request.state.body─────────────┓" + "\n"
    logm = logm + json.dumps(request_body, ensure_ascii=False, indent=4) + "\n"
    logm = logm + "└───────────────────────────────────────────┘" 
    util.file_open (
        "/usr/src/app/data/dream-backend/device/"
        ,file_name
        ,logm
    )

    if "bars_uuid" in request_body and request_body["bars_uuid"] != "" :
        res = auth_service.device_update(request, request_body)
        request.state.inspect = frame()
        return ex.ReturnOK(200, "", request, {"result" : res})
    else :
        return ex.ReturnOK(404, "필수파라메터 오류", request)

    return {}
# [ E ] ---- 레거시 