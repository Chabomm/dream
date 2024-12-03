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
from app.deps.auth import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES


from app.schemas.schema import *
from app.schemas.admin.auth import *
from app.service import session_service
from app.service.admin import auth_service
from app.service import menu_service
from app.models.session import *
from app.deps.auth import get_current_active_admin

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/admin/auth"],
)

from typing import List, Dict, Any, Union, Optional
from datetime import date, datetime, time, timedelta
from app.schemas.schema import *

aesKey = "0000000000000000"
aesIv  = "9999999999999999"
class Sub(AppModel):
    sub: str = Field("", title="암호화값")
    class Config:
        orm_mode = True

@router.post(path="/admin/pullgy")
async def pullgy (
     request: Request
    ,response: Response
    ,sub: Sub
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    plantext = util.decrypt_aes_128(sub.sub, aesKey, aesIv)
    user_info = plantext.split("|:|")

    user_id = user_info[0]

    user = auth_service.read_by_userid(request, user_id)
    request.state.inspect = frame()

    if user is None :
        return ex.ReturnOK(404, "정보를 찾을 수 없습니다.", request)

    token_data = TokenDataAdmin (
        token_name = "DREAM-ADMIN"
        ,user_uid = user.uid
        ,user_id = user.user_id
        ,user_name = user.user_name
        ,user_depart = user.depart
        ,role = user.role
        ,roles = user.roles
        ,access_token = ""
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

    # 관리자 메뉴 가져오기
    res = menu_service.get_admin_menus(request, None)
    request.state.inspect = frame()

    response = JSONResponse(
        ex.ReturnOK(200, "", request, {
            "access_token": access_token
            ,"token_type": "bearer"
            ,"admin_menus": res["admin_menus"]
        })
    )

    user.last_at = util.getNow()

    response.set_cookie( key=token_data.token_name, value=access_token )

    return response

# 로그아웃
@router.post(path="/admin/logout")
async def logout (
     request: Request
    ,response: Response
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)
    
    session_service.delete_session(request, user.user_uid) # 세션 제거
    response.delete_cookie(request.state.user.token_name) # 쿠키 제거

    response = JSONResponse(
        ex.ReturnOK(200, "", request, {})
    )

    return response




