import json
import os
import requests
from sqlalchemy.orm import Session
from datetime import timedelta
from inspect import currentframe as frame
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic.tools import parse_obj_as
from fastapi import APIRouter, Depends, Request, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.core import exceptions as ex
from app.core import util
from app.core.config import PROXY_PREFIX, api_same_origin
from app.core.database import get_session
from app.deps.auth import get_current_active_admin

from app.schemas.schema import *
from app.schemas.admin.entry.manager import *
from app.schemas.admin.auth import *
from app.service.admin.entry import manager_service
from app.service.admin import filter_service
from app.service.log_service import *

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/admin/entry/manager"],
)

def 고객사관리자_필터조건 (request: Request):
    request.state.inspect = frame()
    result = {}

    # 관리자유형
    result.update({"role": [
        {"key": 'master', "text": '마스터관리자'},
        {"key": 'common', "text": '일반관리자'},
    ]})

    result.update({"skeyword_type": [
        {"key": 'M.partner_id', "text": '고객사아이디'},
        {"key": 'P.company_name', "text": '고객사명'},
        {"key": 'P.mall_name', "text": '복지몰명'},
        {"key": 'M.user_id', "text": '관리자아이디'},
        {"key": 'M.name', "text": '관리자이름'},
        {"key": 'M.mobile', "text": '관리자휴대폰'},
        {"key": 'M.email', "text": '관리자이메일'},
        
    ]})

    # 전체 역할 리스트
    # roles = filter_service.roles(request)
    # request.state.inspect = frame()
    # result.update({"roles": roles["list"]})
    return result


# be/admin/entry/manager/init
@router.post("/admin/entry/manager/init", dependencies=[Depends(api_same_origin)])
async def 고객사관리자_내역_init(
     request: Request
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    result = {}
    
    # [ S ] 초기 파라메터
    params = {
         "page" : 1
        ,"page_view_size": 30
        ,"page_size": 0
        ,"page_total": 0
        ,"page_last": 0
        ,"filters": {
            "skeyword": '',
            "skeyword_type": '',
            "create_at": {
                "startDate": None,
                "endDate": None,
            },
            "role": ''
        }
    }
    result.update({"params": params})
    # [ S ] 초기 파라메터

    result.update({"filter": 고객사관리자_필터조건(request)}) # 초기 필터

    return result

# /be/admin/entry/manager/list
@router.post("/admin/entry/manager/list", dependencies=[Depends(api_same_origin)])
async def 고객사관리자_내역(
     request: Request
    ,pPage_param: PPage_param
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    if not pPage_param.page or int(pPage_param.page) == 0:
        pPage_param.page = 1

    if not pPage_param.page_view_size or int(pPage_param.page_view_size) == 0:
        pPage_param.page_view_size = 30

    res = manager_service.manager_list(request, pPage_param)
    request.state.inspect = frame()

    return res






def 담당자_필터조건 (request: Request):
    request.state.inspect = frame()
    result = {}
    # 전체 역할 리스트
    roles = filter_service.roles(request)
    request.state.inspect = frame()
    result.update({"roles": roles["list"]})
    return result

# /be/admin/entry/manager/read
@router.post("/admin/entry/manager/read", dependencies=[Depends(api_same_origin)])
async def 담당자_상세(
     request: Request
    ,managerReadInput: ManagerReadInput
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    if managerReadInput.uid == 0 : # 등록할때
        res_manager = {}
        values = jsonable_encoder(ManagerInput())

    else : # 수정할때
        res_manager = manager_service.manager_read(request, managerReadInput.uid, "")
        request.state.inspect = frame()

        if res_manager is None :
            return ex.ReturnOK(400, "페이지를 불러오는데 실패하였습니다.", request)
        
        values = jsonable_encoder(parse_obj_as(ManagerInput, res_manager))

    jsondata = {}
    jsondata.update({"values": values})
    jsondata.update({"filter": 담당자_필터조건(request)})
    jsondata.update(res_manager)
        
    return ex.ReturnOK(200, "", request, jsondata)

# /be/admin/entry/manager/edit
@router.post("/admin/entry/manager/edit", dependencies=[Depends(api_same_origin)])
async def 담당자_편집(
     request:Request
    ,managerInput: ManagerInput
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    # 등록
    if managerInput.mode == "REG" or managerInput.mode == "COPY" :
        res = manager_service.manager_create(request, managerInput)
        message = "등록이 완료되었습니다."

    # 수정
    if managerInput.mode == "MOD" or managerInput.mode == "DEL" : 
        res = manager_service.manager_update(request, managerInput)
        message = "수정이 완료되었습니다."
    
    request.state.inspect = frame()

    if 'dict' in str(type(res)) and "code" in res:
        if res["code"] == 300:
            return res

    return ex.ReturnOK(200, message, request, {"uid": res.uid})

# /be/admin/entry/manager/pw/reset
@router.post("/admin/entry/manager/pw/reset", dependencies=[Depends(api_same_origin)])
async def 고객사_담당자_비밀번호초기화(
     request:Request
    ,pRead : PRead
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    res = manager_service.partner_manager_pw_update(request, pRead.uid)
    request.state.inspect = frame()
    return ex.ReturnOK(200, "고객사 담당자 비밀번호 초기화 완료", request, {"uid" : res.uid})
    