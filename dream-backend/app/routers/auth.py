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

from app.models.session import *
from app.schemas.manager.auth import *
from app.schemas.front.auth import *
from app.schemas.admin.auth import *
from app.service import session_service

from app.service.admin import auth_service as admin_service
from app.service.manager import auth_service as manager_service
from app.service.front import auth_service as front_service

# from app.service.admin import auth_service
# from app.service.manager import auth_service
# from app.service.front import auth_service

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["auth"],
)

# /be/auth/token
@router.post("/auth/token")
def login_for_access_token_user (
     request: Request
    ,form_data: OAuth2PasswordRequestForm = Depends()
):
    request.state.inspect = frame()

    """ 
    # docs에서 authorizations로 토큰 발급하는 경우
    # oauth2_scheme 스키마로 로그인 return access_token
    """ 

    print( util.toJson(form_data.__dict__) )

    if(form_data.client_id == "front") : # 프론트 회원 로그인
        res = front_service.read_by_userid(request, form_data.username)
        request.state.inspect = frame()
        
        if res is None :
            raise ex.NotFoundUser
    
        token_data = TokenDataDream (
             partner_uid = res.partner_uid
            ,partner_id = res.partner_id
            ,user_uid = res.uid
            ,user_id = res.user_id
            ,user_name = res.user_name
            ,user_depart = ""
            ,user_type = ""
        )

        # 관리자 꺼는 만료일 : REFRESH_TOKEN_EXPIRE_MINUTES
        access_token = create_access_token (data=util.toJson(token_data), expires_delta=timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES))
        return {"access_token": access_token, "token_type": "bearer"}

    
    elif(form_data.client_id == "manager") : # 고객사 관리자 회원 로그인
        print("read_by_user_id 함수생성 TokenDataManager로 access_token 생성")
        res = manager_service.read_by_userid(request, form_data.username)
        
        request.state.inspect = frame()

        if res is None :
            raise ex.NotFoundUser
    
        token_data = TokenDataManager (
             partner_uid = res.partner_uid
            ,partner_id = res.partner_id
            ,user_uid = res.uid
            ,user_id = res.user_id
            ,user_name = res.name
            ,depart = res.depart
            ,role = res.role
        )

        # 관리자 꺼는 만료일 : REFRESH_TOKEN_EXPIRE_MINUTES
        access_token = create_access_token (data=util.toJson(token_data), expires_delta=timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES))
        return {"access_token": access_token, "token_type": "bearer"}
    
    elif(form_data.client_id == "admin") : # 어드민 회원 로그인
        print("read_by_user_id 함수생성 TokenDataAdmin로 access_token 생성")
        res = admin_service.read_by_userid(request, form_data.username)
        
        request.state.inspect = frame()

        if res is None :
            raise ex.NotFoundUser
    
        token_data = TokenDataAdmin (
             user_uid = res.uid
            ,user_id = res.user_id
            ,user_name = res.user_name
            ,user_depart = res.depart
            ,role = res.role
        )

        # 관리자 꺼는 만료일 : REFRESH_TOKEN_EXPIRE_MINUTES
        access_token = create_access_token (data=util.toJson(token_data), expires_delta=timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES))
        return {"access_token": access_token, "token_type": "bearer"}
        
    else :
        return {"error":"유효하지 않은 client_id 입니다.", "access_token": "", "token_type": ""}
    