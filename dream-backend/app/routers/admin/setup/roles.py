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

from app.schemas.schema import *
from app.service.admin.setup import roles_service
from app.service.admin import filter_service
from app.models.session import *
from app.schemas.admin.auth import *
from app.schemas.admin.admin import * 

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/admin/setup/roles"],
)

def 역할_필터조건 (request: Request, partner_uid: any, site_id: any):
    request.state.inspect = frame()

    result = {}

    # 전체 메뉴 리스트
    menus = filter_service.menu_list_for_roles(request, site_id)
    request.state.inspect = frame()
    result.update({"menus": menus})
    result.update({"skeyword_type": [
        {"key": 'name', "text": '역할명'},
    ]})

    return result

# /be/admin/setup/roles/init
@router.post("/admin/setup/roles/init", dependencies=[Depends(api_same_origin)])
async def 역할_내역_init(
    request: Request
    ,adminRolesInitInput: AdminRolesInitInput
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
        ,"partner_uid": adminRolesInitInput.partner_uid
        ,"site_id": adminRolesInitInput.site_id
        ,"filters": {
            "skeyword": '',
            "skeyword_type": '',
        }
    }
    result.update({"params": params})
    # [ S ] 초기 파라메터

    result.update({"filter": 역할_필터조건(request, adminRolesInitInput.partner_uid, adminRolesInitInput.site_id)}) # 초기 필터

    return result

# /be/admin/setup/roles/list
@router.post("/admin/setup/roles/list", dependencies=[Depends(api_same_origin)])
async def 역할_내역(
     request: Request
    ,page_param: AdminRolesListInput
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    # 페이징이 없는 내역
    res = roles_service.admin_rols_list(request, page_param)
    request.state.inspect = frame()

    return res

# /be/admin/setup/roles/read
@router.post("/admin/setup/roles/read", dependencies=[Depends(api_same_origin)])
async def 고객사_관리자역할_상세(
     request: Request
    ,adminRolesInitInput: AdminRolesInitInput
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    if adminRolesInitInput.uid == 0 :
        res_roles = {"uid": 0}
        values = jsonable_encoder(AdminRolesInput())
    else :
        res_roles = roles_service.admin_roles_read(request, adminRolesInitInput.uid)
        request.state.inspect = frame()

        if res_roles is None :
            return ex.ReturnOK(404, "정보를 찾을 수 없습니다. 다시 확인 후 시도해주세요", request)
        
        values = jsonable_encoder(AdminRolesInput(
            uid = res_roles["uid"]
            ,name = res_roles["name"]
            ,menus = res_roles["menus"]
        ))

    jsondata = {}
    jsondata.update(res_roles)
    jsondata.update({"values": values})
    jsondata.update({"filter": 역할_필터조건(request, adminRolesInitInput.partner_uid, adminRolesInitInput.site_id)}) # 초기 필터
    request.state.inspect = frame()
    return ex.ReturnOK(200, "", request, jsondata)

# be/admin/setup/roles/edit
@router.post("/admin/setup/roles/edit", dependencies=[Depends(api_same_origin)])
async def 고객사_관리자역할_편집(
    request: Request, adminRolesInput: AdminRolesInput
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    if adminRolesInput.mode == "REG" : # 등록
        res = roles_service.admin_roles_create(request, adminRolesInput)
        request.state.inspect = frame()
        return ex.ReturnOK(200, "등록이 완료되었습니다.", request, {"uid" : res.uid})

    if adminRolesInput.mode == "MOD" : # 수정
        res = roles_service.admin_roles_update(request, adminRolesInput)
        request.state.inspect = frame()
        return ex.ReturnOK(200, "수정이 완료되었습니다.", request, {"uid" : res.uid})
    
    if adminRolesInput.mode == "DEL" : # 삭제
        roles_service.admin_roles_delete(request, adminRolesInput.uid)
        request.state.inspect = frame()
        return ex.ReturnOK(200, "삭제 완료", request)



