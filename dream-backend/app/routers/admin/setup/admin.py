from fastapi import APIRouter, Depends, Request, Body
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from inspect import currentframe as frame
from fastapi.responses import RedirectResponse, JSONResponse
from app.core import exceptions as ex
from app.core import util
from app.core.config import PROXY_PREFIX, api_same_origin
from app.core.database import get_session
from app.deps.auth import create_access_token, get_current_active_admin, get_current_user
from app.deps.auth import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES
from fastapi.encoders import jsonable_encoder
from pydantic.tools import parse_obj_as

from app.models.session import *
from app.schemas.admin.auth import *
from app.schemas.schema import *
from app.service.admin import filter_service
from app.schemas.admin.admin import * 

from app.service.admin.setup import admin_service

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/admin/setup/admin"],
)

def 관리자_필터조건 (request: Request):
    request.state.inspect = frame()

    result = {}
    
    # 전체 역할 리스트
    roles = filter_service.roles(request, "admin")
    request.state.inspect = frame()
    result.update({"roles": roles["list"]})

    result.update({"skeyword_type": [
        {"key": 'user_id', "text": '관리자ID'},
        {"key": 'user_name', "text": '이름'},
        {"key": 'depart', "text": '부서'}
    ]})

    result.update({"state": [
        {"key": '', "text": '전체'},
        {"key": '100', "text": '승인대기'},
        {"key": '200', "text": '정상'},
        {"key": '300', "text": '탈퇴'},
    ]})

    return result

# /be/admin/setup/admin/init
@router.post("/admin/setup/admin/init", dependencies=[Depends(api_same_origin)])
async def 관리자내역_init(
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
            "roles": [],
            "state": '',
        }
    }
    result.update({"params": params})
    # [ S ] 초기 파라메터

    result.update({"filter": 관리자_필터조건(request)}) # 초기 필터

    return result

# /be/admin/setup/admin/list
@router.post("/admin/setup/admin/list", dependencies=[Depends(api_same_origin)])
async def 관리자_리스트(
     request: Request
    ,page_param: PPage_param
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    if not page_param.page or int(page_param.page) == 0:
        page_param.page = 1

    if not page_param.page_view_size or int(page_param.page_view_size) == 0:
        page_param.page_view_size = 30

    res = admin_service.admin_user_list(request, page_param)
    request.state.inspect = frame()

    return res

# /be/admin/setup/admin/read
@router.post("/admin/setup/admin/read", dependencies=[Depends(api_same_origin)])
async def 관리자_상세(
      request: Request
     ,adminReadInput: AdminReadInput
     ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    if adminReadInput.uid == 0 :
        res_user_info = {"uid": 0}
        values = jsonable_encoder(AdminInput())

    else :
        res_user_info = admin_service.admin_user_read(request, adminReadInput.uid, adminReadInput.user_id)
        request.state.inspect = frame()

        if res_user_info is None:
            return ex.ReturnOK(404, "정보를 찾을 수 없습니다. 다시 확인 후 시도해주세요", request)

        res_user_info.update({"login_pw": ""})

        values = jsonable_encoder(AdminInput(
            uid = res_user_info["uid"]
            ,user_id = res_user_info["user_id"]
            ,user_name = res_user_info["user_name"]
            ,tel = res_user_info["tel"]
            ,mobile = res_user_info["mobile"]
            ,email = res_user_info["email"]
            ,role = res_user_info["role"]
            ,position1 = res_user_info["position1"]
            ,position2 = res_user_info["position2"]
            ,depart = res_user_info["depart"]
            ,roles = res_user_info["roles"]
            ,state = res_user_info["state"]
        ))

    jsondata = {}
    jsondata.update(res_user_info)
    jsondata.update({"values": values})
    jsondata.update({"filter": 관리자_필터조건(request)})
    request.state.inspect = frame()

    return ex.ReturnOK(200, "", request, jsondata)

# be/admin/setup/admin/edit
@router.post("/admin/setup/admin/edit", dependencies=[Depends(api_same_origin)])
async def 관리자_등록수정(
    request: Request, adminInput: AdminInput
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    if adminInput.uid > 0:  # 관리자 수정
        res = admin_service.admin_user_edit(request, adminInput)
        message = "수정이 완료되었습니다."

    elif adminInput.uid is None or adminInput.uid == 0:
        res = admin_service.admin_user_create(request, adminInput)
        message = "등록이 완료되었습니다."

    request.state.inspect = frame()

    if 'dict' in str(type(res)) and "code" in res:
        if res["code"] == 300:
            return res

    return ex.ReturnOK(200, message, request, {"uid": res.uid})


