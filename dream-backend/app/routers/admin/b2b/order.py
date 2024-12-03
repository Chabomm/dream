from fastapi import APIRouter, Depends, Request, Body
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from inspect import currentframe as frame
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core import exceptions as ex
from app.core import util
from app.core.config import PROXY_PREFIX, api_same_origin
from app.core.database import get_session
from app.deps.auth import get_current_active_admin
import os
import requests
import json
from fastapi.encoders import jsonable_encoder

from app.core.dbSCM import SessionLocal_scm

from app.schemas.admin.auth import *
from app.schemas.admin.b2b.order import *
from app.service.admin.b2b import order_service


router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/admin/b2b/order"],
)

def B2B_신청내역_필터조건(request: Request, type:str):
    request.state.inspect = frame()

    result = {}
    if type == 'detail' :
        result.update({"state": [
            {"key": '신규상담', "text": '신규상담', "checked": True},
            {"key": '상담중', "text": '상담중', "checked": True},
            {"key": '진행보류', "text": '진행보류', "checked": True},
            {"key": '계약미진행', "text": '계약미진행', "checked": True},
            {"key": '계약진행', "text": '계약진행', "checked": True},
        ]})
    else :
        result.update({"skeyword_type": [
            {"key": 'apply_user_id', "text": '작성자 아이디'},
            {"key": 'apply_name', "text": '작성자명'},
            {"key": 'seller_id', "text": '판매자 아이디'},
            {"key": 'seller_name', "text": '판매자명'},
            {"key": 'indend_md', "text": '담당MD 아이디'},
            {"key": 'indend_md_name', "text": '담당MD명'},
            {"key": 'title', "text": '서비스명'},
        ]})

        # 진행상태
        result.update({"state": [
            {"key": '', "text": '전체', "checked": True},
            {"key": '신규상담', "text": '신규상담', "checked": True},
            {"key": '상담중', "text": '상담중', "checked": True},
            {"key": '진행보류', "text": '진행보류', "checked": True},
            {"key": '계약미진행', "text": '계약미진행', "checked": True},
            {"key": '계약진행', "text": '계약진행', "checked": True},
        ]})
    return result


# /be/admin/b2b/order/init
@router.post("/admin/b2b/order/init", dependencies=[Depends(api_same_origin)])
async def B2B_신청내역_init (
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
            "state": '',
            "create_at": {
                "startDate": None,
                "endDate": None,
            },
        }
    }
    result.update({"params": params})
    # [ S ] 초기 파라메터

    result.update({"filter": B2B_신청내역_필터조건(request,'list')}) # 초기 필터

    return result

# be/admin/b2b/order/list
@router.post("/admin/b2b/order/list", dependencies=[Depends(api_same_origin)])
async def B2B_신청내역_리스트(
     request: Request
    ,page_param: PPage_param
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    request.state.db_scm = SessionLocal_scm() # SCM DB session

    if not page_param.page or int(page_param.page) == 0:
        page_param.page = 1

    if not page_param.page_view_size or int(page_param.page_view_size) == 0:
        page_param.page_view_size = 30

    res = order_service.order_list(request, page_param)
    request.state.inspect = frame()

    return res


# /be/admin/b2b/order/read
@router.post("/admin/b2b/order/read", dependencies=[Depends(api_same_origin)])
async def B2B_신청내역_상세(
    request: Request
    ,pRead : PRead
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    request.state.db_scm = SessionLocal_scm() # SCM DB session

    result = {}
    res = order_service.order_read(request, pRead.uid)

    if res is None :
        return ex.ReturnOK(404, "신청내역을 찾을 수 없습니다.", request)
    # result.update(res)

    result.update({"posts": res})
    result["posts"].update({"filter": B2B_신청내역_필터조건(request, 'detail')})

    return ex.ReturnOK(200, "", request, result, False)



