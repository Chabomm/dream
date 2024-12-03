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
from app.service.admin.setup import info_service
from app.service.admin import filter_service
from app.models.session import *
from app.schemas.admin.auth import *
from app.schemas.admin.admin import * 

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/admin/setup/info"],
)

# /be/admin/setup/info/read
@router.post("/admin/setup/info/read", dependencies=[Depends(api_same_origin)])
async def 계정관리_상세정보 (
     request: Request
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

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


@router.post("/admin/setup/info/update", dependencies=[Depends(api_same_origin)])
async def 내정보수정 (
    request: Request
    ,myInfoInput: MyInfoInput
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    res = info_service.info_update(request, myInfoInput)
    request.state.inspect = frame()
    return ex.ReturnOK(200, "수정이 완료되었습니다.", request, {"uid" : res.uid})
    

