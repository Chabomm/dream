import json
from typing import Optional
from fastapi import Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from inspect import currentframe as frame

from app.core import exceptions as ex
from app.core import util
from app.core.database import engine
from app.models.session import *
from app.service import session_service

from app.models.manager import *

from app.schemas.auth import *
from app.schemas.admin.auth import *
from app.schemas.manager.auth import *
from app.schemas.front.auth import *


# to get a string like this run:
# openssl rand -hex 32
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # ACCESS_TOKEN 만료 (분)
REFRESH_TOKEN_EXPIRE_MINUTES = 43200 # REFRESH_TOKEN 만료 (분)
SECRET_KEY = "0000000000000000000000000000000000000000000000000000000000000000"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/be/auth/token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# [ S ] 현재 유저 정보 가져오기
def get_current_user(
     request: Request
    ,response: Response
    ,access_token: str = Depends(oauth2_scheme)
):
    request.state.inspect = frame()
    credentials_exception = HTTPException (
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if access_token == "undefined" :
        raise credentials_exception

    is_expried_error = False

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("user_uid") is None :
            raise credentials_exception

    except jwt.ExpiredSignatureError:  # access_token의 만료가 지나면
        is_expried_error = True

    if is_expried_error :
        # T_SESSION 테이블에서 access와 매칭되는 refresh token 가져오기
        res = session_service.read_session(request, None, access_token)
        request.state.inspect = frame()
        
        print("-=-=-=-=-= read T_SESSION ", util.toJson(res))
        print("")
        
        if res is None or res.refresh_token is None :
            raise credentials_exception

        payload = jwt.decode(res.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        print("-=-=-=-=-= payload by refresh_token", payload)
        print("")

        if payload["token_name"] == "DREAM" :
            token_data = TokenDataDream (
                 token_name = "DREAM"
                ,partner_uid = payload["partner_uid"]
                ,partner_id = payload["partner_id"]
                ,user_uid = payload["user_uid"]
                ,user_id = payload["user_id"]
                ,user_name = payload["user_name"]
                ,user_depart = payload["user_depart"]
                ,user_type = payload["user_type"]
            )

        elif payload["token_name"] == "DREAM-MANAGER" :
            token_data = TokenDataManager (
                 token_name = "DREAM-MANAGER"
                ,partner_uid = payload["partner_uid"]
                ,partner_id = payload["partner_id"]
                ,prefix = payload["prefix"]
                ,user_uid = payload["user_uid"]
                ,user_id = payload["user_id"]
                ,user_name = payload["user_name"]
                ,user_depart = payload["user_depart"]
                ,role = payload["role"]
                ,roles = payload["roles"]
            )

        elif payload["token_name"] == "DREAM-ADMIN" :
            token_data = TokenDataAdmin (
                 token_name = "DREAM-ADMIN"
                ,user_uid = payload["user_uid"]
                ,user_id = payload["user_id"]
                ,user_name = payload["user_name"]
                ,user_depart = payload["user_depart"]
                ,role = payload["role"]
                ,roles = payload["roles"]
            )

        access_token = create_access_token(data=util.toJson(token_data), expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        refresh_token = create_access_token(data=util.toJson(token_data), expires_delta=timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES))
        session_param = T_SESSION (
             site_id = payload["token_name"]
            ,user_uid = token_data.user_uid
            ,user_id = token_data.user_id
            ,access_token = access_token
            ,refresh_token = refresh_token
            ,ip = request.state.user_ip
        )

        res = session_service.create_session(request, session_param)
        request.state.inspect = frame()

        print("-=-=-=-=-= recreate access_token", access_token)
        print("")

    if payload is None :
        raise credentials_exception

    payload["access_token"] = access_token

    response.set_cookie (
         key=payload["token_name"]
        ,value=access_token
    )

    return payload
# [ E ] 현재 유저 정보 가져오기


# [ S ] 일반고객 유저 정보 가져오기
def get_current_active_front(current_member: TokenDataDream = Depends(get_current_user)):
    return current_member
# [ E ] 일반고객 유저 정보 가져오기

# [ S ] 최고관리자 유저 정보 가져오기
def get_current_active_admin(current_admin: TokenDataAdmin = Depends(get_current_user)):
    return current_admin
# [ E ] 최고관리자 유저 정보 가져오기

# [ S ] 고객사 관리자 유저 정보 가져오기
def get_current_active_manager(request: Request, current_manager: TokenDataManager = Depends(get_current_user)):

    # print(request.__dict__)
    # print("http_referer = request.headers.get('referer')", request.headers.get('referer'))
    # print(current_manager)

    return current_manager
# [ E ] 고객사 관리자 유저 정보 가져오기



















def get_current_user_outbound (
     request: Request
    ,response: Response
    ,access_token: str = Depends(oauth2_scheme)
):
    request.state.inspect = frame()

    payload = {}
    token_data = TokenDataOutbound(
        token_name = "INBOUND"
        ,user_uid = 0
        ,user_id = ""
        ,user_name = ""
        ,sosok_id = ""
        ,sosok_uid = 0
    )

    print('access_token inbound', access_token)

    if access_token is not None and access_token != "" :
        try:
            payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])

            print('payloadpayload',payload)
        
            sosok_uid = 0
            sosok_id = ""

            if "sosok_uid" in payload : # INBOUND
                sosok_uid = payload["sosok_uid"]
                sosok_id = payload["sosok_id"]

            elif payload["token_name"] == "DREAM-MANAGER" :
                sosok_uid = payload["partner_uid"]
                sosok_id = payload["partner_id"]
            
            elif payload["token_name"] == "SCM-SELLER" :
                sosok_uid = payload["seller_uid"]
                sosok_id = payload["seller_id"]

            elif payload["token_name"] == "SCM-B2B" :
                payload["user_uid"] = payload["seller_uid"]
                payload["user_id"] = payload["seller_id"]
                payload["user_name"] = payload["staff_name"]
                sosok_uid = payload["seller_uid"]
                sosok_id = payload["seller_id"]

            token_data = TokenDataOutbound (
                token_name = payload["token_name"]
                ,user_uid = payload["user_uid"]
                ,user_id = payload["user_id"]
                ,user_name = payload["user_name"]
                ,sosok_uid = sosok_uid
                ,sosok_id = sosok_id
            )

        except Exception as e :
            print("token decode error", str(e))
            credentials_exception = HTTPException (
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            raise credentials_exception

    # access_token = create_access_token(data=util.toJson(token_data), expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    # response.set_cookie(key="INBOUND", value=access_token)

    print('token_data',token_data)

    return token_data

# Outbound 유저 정보 가져오기
def get_current_active_outbound(request: Request, current_user: TokenDataOutbound = Depends(get_current_user_outbound)):
    return current_user






















