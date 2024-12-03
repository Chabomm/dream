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
from app.deps.auth import create_access_token, get_current_active_manager, get_current_user
from app.deps.auth import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES

from app.schemas.schema import *
from app.schemas.manager.auth import *
from app.service.manager import home_service
from app.service.manager.point import status_service, point_service

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/manager/home"],
)

# be/manager/home
@router.post("/manager/home", dependencies=[Depends(api_same_origin)])
async def 메인홈화면 (
     request: Request
    ,user: TokenDataManager = Depends(get_current_active_manager)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)

    user_info = home_service.user_info(request)
    request.state.inspect = frame()
    if user_info is None :
        return ex.ReturnOK(402, "정보를 불러오는데 실패하였습니다.", request)

    point_info = status_service.status_point_read(request, user.partner_uid)
    request.state.inspect = frame()
    if point_info is None :
        return ex.ReturnOK(402, "정보를 불러오는데 실패하였습니다.", request)

    member_info = home_service.member_info(request)
    request.state.inspect = frame()
    if member_info is None :
        return ex.ReturnOK(402, "정보를 불러오는데 실패하였습니다.", request)

    balance_info = home_service.balance_info(request)
    request.state.inspect = frame()
    if balance_info is None :
        return ex.ReturnOK(402, "정보를 불러오는데 실패하였습니다.", request)
    
    point_assign_info = home_service.assign_info(request)
    request.state.inspect = frame()
    if balance_info is None :
        return ex.ReturnOK(402, "정보를 불러오는데 실패하였습니다.", request)
    
    day_point_info = home_service.day_point_info(request)
    request.state.inspect = frame()
    if balance_info is None :
        return ex.ReturnOK(402, "정보를 불러오는데 실패하였습니다.", request)
    
    jsondata = {}
    jsondata.update({"user_info": user_info})
    jsondata.update({"point_info": point_info})
    jsondata.update({"member_info": member_info})
    jsondata.update({"balance_info": balance_info})
    jsondata.update({"point_assign_info": point_assign_info})
    jsondata.update({"day_point_info": day_point_info})

    return jsondata