import os
import json
import requests
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Body
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from inspect import currentframe as frame
from fastapi.responses import RedirectResponse, JSONResponse, StreamingResponse
import string
import random
from app.core import exceptions as ex
from app.core import util
from app.core.config import PROXY_PREFIX, api_same_origin
from app.core.database import get_session
from app.deps.auth import create_access_token, get_current_active_manager
from app.deps.auth import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES

from app.schemas.schema import *
from app.service import session_service
from app.service.manager import auth_service
from app.service import menu_service
from app.models.session import *
from app.schemas.manager.auth import *

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/manager/auth"],
)

# /be/manager/signin
@router.post("/manager/signin")
async def 고객사관리자_로그인(
    request: Request,
    response: Response,
    signin_request: SignInRequest
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)

    # [ S ] 고객사 정보 select
    res_partner = auth_service.read_by_partnerid(request, signin_request.partner_id)
    request.state.inspect = frame()

    if res_partner is None :
        return ex.ReturnOK(404, "정보를 찾을 수 없습니다. 다시 확인해 주세요", request)
    # [ E ] 고객사 정보 select

    user = auth_service.signin_manager(request, signin_request)
    request.state.inspect = frame()

    if user is None :
        return ex.ReturnOK(404, "정보를 찾을 수 없습니다. 아이디와 비밀번호를 다시 확인해 주세요", request)
    
    elif 'dict' in str(type(user)) :
        return user
    
    is_temp = False
    try :
        arry_mobile = user.mobile.split('-')
        first_pw = user.login_id + arry_mobile[2]

        if signin_request.user_pw == first_pw :
            is_temp = True
    except Exception as e:
        print(str(e))
    
    token_data = TokenDataManager (
        token_name = "DREAM-MANAGER"
        ,partner_uid = user.partner_uid
        ,partner_id = user.partner_id
        ,user_uid = user.uid
        ,user_id = user.user_id
        ,user_name = user.name
        ,user_depart = user.depart
        ,role = user.role
        ,roles = user.roles
        ,prefix = user.prefix
        ,is_temp = is_temp
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

    session_service.create_session(request, session_param, util.toJson(token_data))
    request.state.inspect = frame()

    # 파트너 정보(로고)
    partner_info = auth_service.get_partner_read(request)
    request.state.inspect = frame()

    # 관리자 메뉴 가져오기
    res = menu_service.get_admin_menus(request, partner_info)
    request.state.inspect = frame()

    response = JSONResponse(
        ex.ReturnOK(200, "", request, {
            "access_token": access_token
            ,"token_type": "bearer"
            ,"admin_menus": res["admin_menus"]
            ,"partner_info": partner_info
        })
    )

    response.set_cookie( key=token_data.token_name, value=access_token )

    return response

# 로그아웃
@router.post(path="/manager/logout")
async def logout (
     request: Request
    ,response: Response
    ,user: TokenDataManager = Depends(get_current_active_manager)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)
    
    session_service.delete_session(request, user.user_uid) # 세션 제거
    response.delete_cookie(request.state.user.token_name) # 쿠키 제거

    response = JSONResponse(
        ex.ReturnOK(200, "", request, {})
    )

    return response




# from app.deps.auth import get_password_hash
# @router.post("/manager/password/create")
# def 패스워드_생성_임시 (
#     request: Request,
#     response: Response,
#     signin_request: SignInRequest
# ):
#     request.state.inspect = frame()
#     return get_password_hash(signin_request.user_pw)

