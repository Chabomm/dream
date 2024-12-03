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
from app.schemas.admin.entry.partner import *
from app.schemas.admin.auth import *
from app.service.admin.entry import partner_service
from app.service.admin.entry import manager_service
from app.service.admin import filter_service
from app.service.log_service import *

from app.service.admin.entry import build_service

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/admin/entry/partner"],
)

def 고객사_내역_필터조건(request: Request):
    request.state.inspect = frame()

    result = {}
    result.update({"skeyword_type": [
        {"key": 'partner_id', "text": '고객사 아이디'},
        {"key": 'partner_code', "text": '고객사 코드'},
        {"key": 'company_name', "text": '고객사명'},
        {"key": 'mall_name', "text": '복지몰명'},
    ]})

    # 복지몰상태
    result.update({"state": [
        {"key": '100', "text": '대기'},
        {"key": '200', "text": '운영중'},
        {"key": '300', "text": '일시중지'},
        {"key": '400', "text": '폐쇄'},
    ]})

    # 전체 역할 리스트
    roles = filter_service.roles(request, 'manager')
    request.state.inspect = frame()
    result.update({"roles": roles["list"]})

    return result

# be/admin/entry/partner/init
@router.post("/admin/entry/partner/init", dependencies=[Depends(api_same_origin)])
async def 고객사_내역_init(
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
            "state": [],
        }
    }
    result.update({"params": params})
    # [ S ] 초기 파라메터

    result.update({"filter": 고객사_내역_필터조건(request)}) # 초기 필터

    return result

# /be/admin/entry/partner/list
@router.post("/admin/entry/partner/list", dependencies=[Depends(api_same_origin)])
async def 고객사_내역(
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

    res = partner_service.partner_list(request, pPage_param)
    request.state.inspect = frame()

    return res

# /be/admin/entry/partner/read
@router.post("/admin/entry/partner/read", dependencies=[Depends(api_same_origin)])
async def 고객사_상세(
     request: Request
    ,pRead: PRead
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    if pRead.uid == 0 : # 등록할때
        res = {}
        values = jsonable_encoder(PartnerInput())

    else : # 수정할때
        res_partner = partner_service.partner_read(request, pRead.uid)
        request.state.inspect = frame()

        res_partner_info = partner_service.partner_info_read(request, pRead.uid)
        request.state.inspect = frame()

        if res_partner is None or res_partner_info is None :
            return ex.ReturnOK(400, "페이지를 불러오는데 실패하였습니다.", request)
        
        res_partner_words = partner_service.partner_words_read(request, pRead.uid, res_partner["mall_type"])
        request.state.inspect = frame()

        res_dream_config = partner_service.dream_config_read(request, pRead.uid)
        request.state.inspect = frame()

        res_manager_list = manager_service.manager_list_in_partner_read(request, pRead.uid)
        request.state.inspect = frame()
        
        res = {**res_partner, **res_partner_info, **res_partner_words, **res_dream_config, **res_manager_list}
        values = jsonable_encoder(parse_obj_as(PartnerInput, res))

    # 업종코드 리스트
    com_item_list = build_service.com_item_list(request)
    request.state.inspect = frame()

    jsondata = {}
    jsondata.update({"values": values})
    jsondata.update(res)
    jsondata.update({"filter": 고객사_내역_필터조건(request)})
    request.state.inspect = frame()
    jsondata.update({"com_item_list": com_item_list})
        
    return ex.ReturnOK(200, "", request, jsondata)

# /be/admin/entry/partner/edit
@router.post("/admin/entry/partner/edit", dependencies=[Depends(api_same_origin)])
async def 고객사_편집(
     request:Request
    ,partnerInput: PartnerInput
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    # T_PARTNER UPDATE
    res_partner = partner_service.partner_update(request, partnerInput)
    request.state.inspect = frame()
    if res_partner is None :
        return ex.ReturnOK(500, "복지몰 정보 수정에 실패했습니다.", request)
    
    # T_PARTNER_INFO UPDATE
    res_partner_info = partner_service.partner_info_update(request, partnerInput)
    request.state.inspect = frame()
    if res_partner_info is None :
        return ex.ReturnOK(500, "복지몰 계약 정보 수정에 실패했습니다.", request)
    
    # T_DREAM_CONFIG UPDATE
    res_dream_config = partner_service.dream_config_update(request, partnerInput)
    request.state.inspect = frame()
    # if res_dream_config is None :
    #     return ex.ReturnOK(500, "드림포인트 정보 수정에 실패했습니다.", request)
        
    return ex.ReturnOK(200, "고객사 수정 완료", request, {"uid" : res_partner.uid})
