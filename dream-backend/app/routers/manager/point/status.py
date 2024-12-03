from decimal import *
from unittest import result
from fastapi import APIRouter, Depends, Request, Body
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from inspect import currentframe as frame
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core import exceptions as ex
from app.core import util
from app.core.config import PROXY_PREFIX, api_same_origin
from app.deps.auth import get_current_active_manager
import json
from fastapi.encoders import jsonable_encoder
from pydantic.tools import parse_obj_as

from app.schemas.schema import *
# from app.schemas.manager.point.assign.single import *
from app.schemas.manager.point.status import *
from app.schemas.manager.auth import *
from app.service.manager.point import status_service

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/manager/point"],
)

# /be/manager/point/status/read
@router.post("/manager/point/status/read", dependencies=[Depends(api_same_origin)])
async def 포인트_충전현황(
     request: Request
    ,pointStatusInput: PointStatusInput
    ,user: TokenDataManager = Depends(get_current_active_manager)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)

    if pointStatusInput.point_type == "bokji" :
        res = status_service.status_point_read(request, user.partner_uid)
        request.state.inspect = frame()
        if res is None :
            return ex.ReturnOK(402, "정보를 불러오는데 실패하였습니다.", request)
        
    if pointStatusInput.point_type == "sikwon" :
        res = status_service.status_sikwon_read(request, user.partner_uid)
        request.state.inspect = frame()
        if res is None :
            return ex.ReturnOK(402, "정보를 불러오는데 실패하였습니다.", request)
    
    return res
