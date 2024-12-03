import os
from fastapi import APIRouter, Depends, Request, Body, Response
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from inspect import currentframe as frame
from fastapi.responses import RedirectResponse, JSONResponse
from app.core import exceptions as ex
from app.core import util
from app.core.config import PROXY_PREFIX, api_same_origin
from app.core.database import get_session
from app.deps.auth import create_access_token, get_current_active_manager, get_current_user
from app.deps.auth import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES
from pydantic.tools import parse_obj_as
from fastapi.encoders import jsonable_encoder

from app.schemas.schema import *
from app.service.manager.setup import info_service
from app.service import session_service
from app.service.manager import filter_service
from app.models.session import *
from app.schemas.manager.auth import *
from app.schemas.manager.manager import * 

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/manager/setup/info"],
)

# /be/manager/setup/info/read
@router.post("/manager/setup/info/read", dependencies=[Depends(api_same_origin)])
async def 계정관리_상세정보 (
     request: Request
    ,user: TokenDataManager = Depends(get_current_active_manager)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)

    res_info = info_service.info_read(request)
    request.state.inspect = frame()

    if res_info is None :
        return ex.ReturnOK(404, "정보를 찾을 수 없습니다. 다시 확인 후 시도해주세요", request)
        
    values = jsonable_encoder(MyInfoInput(
         login_pw = ""
        ,tel = res_info.tel
        ,mobile = res_info.mobile
    ))

    jsondata = {}
    jsondata.update(res_info)
    jsondata.update({"values": values})
    return ex.ReturnOK(200, "", request, jsondata)

import re
@router.post("/manager/setup/info/edit", dependencies=[Depends(api_same_origin)])
async def 내정보수정 (
    request: Request
    ,response: Response
    ,myInfoInput: MyInfoInput
    ,user: TokenDataManager = Depends(get_current_active_manager)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)

    res = info_service.info_update(request, myInfoInput)
    request.state.inspect = frame()

    if myInfoInput.login_id != None :
        arry_mobile = myInfoInput.mobile.split('-')
        first_pw = myInfoInput.login_id + arry_mobile[2]
        if myInfoInput.login_pw == first_pw :
            return ex.ReturnOK(300, "비밀번호는 초기비밀번호와 동일하게 설정할 수 없습니다", request)

    if myInfoInput.login_pw != '' and myInfoInput.login_pw != None :
        if (len(myInfoInput.login_pw) < 6 or len(myInfoInput.login_pw) > 20) or (not re.findall('[0-9]+', myInfoInput.login_pw)) or (not re.findall('[a-z]', myInfoInput.login_pw)) :
            return ex.ReturnOK(300, "비밀번호는 영문, 숫자 조합 6자 이상, 20자 이하여야 합니다.", request)
        
    # [ S ] 토큰 및 세션 재생성
    token_data = TokenDataManager (
        token_name = "DREAM-MANAGER"
        ,partner_uid = user.partner_uid
        ,partner_id = user.partner_id
        ,user_uid = user.user_uid
        ,user_id = user.user_id
        ,user_name = user.user_name
        ,user_depart = user.user_depart
        ,role = user.role
        ,roles = user.roles
        ,prefix = user.prefix
        ,is_temp = False
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

    response.set_cookie (
         key="DREAM-MANAGER"
        ,value=access_token
    )
    # [ E ] 토큰 및 세션 재생성

    return ex.ReturnOK(200, "수정이 완료되었습니다.", request, {"uid" : res.uid})
    
# /be/manager/welcome/read
@router.post("/manager/welcome/read", dependencies=[Depends(api_same_origin)])
async def 초기비밀번호_내정보보기 (
     request: Request
    ,user: TokenDataManager = Depends(get_current_active_manager)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)

    res = info_service.info_read(request)
    request.state.inspect = frame()

    if res is not None:
        res = dict(zip(res.keys(), res))

    res["name"] = util.fn_masking_user_name(res["name"] if "name" in res else "")
    res["email"] = util.fn_masking_user_email(res["email"] if "email" in res else "")
    res["mobile"] = util.fn_masking_user_mobile(res["mobile"] if "mobile" in res else "")

    if res is None:
        return ex.ReturnOK(404, "데이터를 찾을 수 없습니다.", request)

    res["user_pw"]= ''
    res["user_pw2"]= ''

    values = jsonable_encoder(parse_obj_as(MyInfoInput, res))

    jsondata = {}
    jsondata.update(res)
    jsondata.update({"values": values})
    return ex.ReturnOK(200, "", request, jsondata)


# /be/manager/setup/info/partner/read
@router.post("/manager/setup/info/partner/read", dependencies=[Depends(api_same_origin)])
async def 구축_상세정보 (
     request: Request
    ,user: TokenDataManager = Depends(get_current_active_manager)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)

    res_info = info_service.partner_build_read(request)
    request.state.inspect = frame()
    
    if res_info is None :
        return ex.ReturnOK(404, "정보를 찾을 수 없습니다. 다시 확인 후 시도해주세요", request)

    jsondata = {}
    jsondata.update(res_info)
    return ex.ReturnOK(200, "", request, jsondata)