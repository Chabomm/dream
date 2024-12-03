import json
import os
import requests
from sqlalchemy.orm import Session
from datetime import timedelta
from inspect import currentframe as frame
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi import APIRouter, Depends, Request, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
from pydantic.tools import parse_obj_as

from app.core import exceptions as ex
from app.core import util
from app.core.config import PROXY_PREFIX, api_same_origin
from app.core.database import get_session
from app.deps.auth import get_current_active_admin

from app.schemas.schema import *
from app.schemas.admin.entry.build import *
from app.schemas.manager.auth import *
from app.schemas.admin.auth import *
from app.service import log_service
from app.service.admin.entry import partner_service

# [ S ] db_scm을 위한 임시
from app.service import log_scm_service
from app.service.admin.entry import build_service
from app.core.dbSCM import SessionLocal_scm
# [ S ] db_scm을 위한 임시

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/admin/entry/build"],
)


def 복지드림_구축신청_필터조건(request: Request):
    request.state.inspect = frame()

    result = {}
    result.update({"skeyword_type": [
        {"key": 'company_name', "text": '기업명'},
        {"key": 'mall_name', "text": '복지몰명'},
    ]})

    # 진행상태
    result.update({"state": [
        {"key": '100', "text": '도입신청'},
        {"key": '110', "text": '구축신청'},
        {"key": '200', "text": '구축완료'},
    ]})

    return result

# be/admin/entry/build/init
@router.post("/admin/entry/build/init", dependencies=[Depends(api_same_origin)])
async def 복지드림_구축신청_내역_init(
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

    result.update({"filter": 복지드림_구축신청_필터조건(request)}) # 초기 필터

    return result

# be/admin/entry/build/list
@router.post("/admin/entry/build/list", dependencies=[Depends(api_same_origin)])
async def 구축신청_리스트(
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

    res = build_service.build_list(request, page_param)
    request.state.inspect = frame()

    return res

# /be/admin/entry/build/read
@router.post("/admin/entry/build/read", dependencies=[Depends(api_same_origin)])
async def 구축신청_상세(
     request: Request
    ,pRead: PRead
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)
    
    request.state.db_scm = SessionLocal_scm() # SCM DB session

    if pRead.uid == 0 :
        res = {}
        memo_list = {}
        values = jsonable_encoder(DreamBuildInput())

    else :
        res = build_service.build_read(request, pRead.uid)
        request.state.inspect = frame()

        if res is None :
            return ex.ReturnOK(400, "페이지를 불러오는데 실패하였습니다.", request)
        
        if res["state"] == "200" : 
            partner_uid = partner_service.read_partner_uid_for_build_uid(request, pRead.uid)
            if partner_uid == 0 :
                return ex.ReturnOK(400, "고객사 정보가 존재하지 않습니다.", request)
            res.update({"partner_uid": partner_uid})
        
        values = jsonable_encoder(parse_obj_as(DreamBuildInput, res))
        
        memo_list = log_scm_service.memo_list(request, "T_DREAM_BUILD", pRead.uid)
        request.state.inspect = frame()
    
    # 업종코드 리스트
    com_item_list = build_service.com_item_list(request)
    request.state.inspect = frame()

    jsondata = {}
    jsondata.update({"values": values})
    jsondata.update(res)
    jsondata.update({"filter": 복지드림_구축신청_필터조건(request)})
    request.state.inspect = frame()
    jsondata.update({"memo_list": memo_list})
    jsondata.update({"com_item_list": com_item_list})
        
    return ex.ReturnOK(200, "", request, jsondata)


# /be/admin/entry/build/edit
@router.post("/admin/entry/build/edit", dependencies=[Depends(api_same_origin)])
async def 복지드림_구축신청_편집(
     request:Request
    ,dreamBuild: DreamBuild
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)
    
    request.state.db_scm = SessionLocal_scm() # SCM DB session
    
    # 등록
    if dreamBuild.mode == "REG" :
        res = build_service.build_create(request, dreamBuild)
        request.state.inspect = frame()
        if res is None :
            return ex.ReturnOK(500, "구축신청서 등록에 실패했습니다.", request)
        
    # 수정
    if dreamBuild.mode == "MOD" :

        # [ S ] 구축신청 -> 구축완료(200) 상태 변경 시 T_PARTNER insert
        if (dreamBuild.state == "200") : # 기존에 partner 있는지 검사
            res_partner = partner_service.partner_create(request, dreamBuild)
            request.state.inspect = frame()

            partner_service.partner_info_create(request, dreamBuild, res_partner.uid)
            request.state.inspect = frame()

            # 구축완료시 dream config 등록되게 하기
            partner_service.dream_config_create(request, dreamBuild.host, res_partner.uid)
            request.state.inspect = frame()
        # [ E ] 구축신청 -> 구축완료(200) 상태 변경 시 T_PARTNER, T_PARTNER_INFO insert
        
        res = build_service.build_update(request, dreamBuild)
        request.state.inspect = frame()

        if res is None :
            return ex.ReturnOK(500, "구축신청서 수정에 실패했습니다. 다시 시도해 주세요. 문제 지속시 개발자에게 문의하세요", request)
            

    return ex.ReturnOK(200, "구축신청서 등록이 완료되었습니다.", request, {"uid":res.uid})


# /be/admin/entry/build/check 
@router.post("/admin/entry/build/check", dependencies=[Depends(api_same_origin)])
async def 복지드림_구축신청_아이디_중복확인(
    request:Request
    ,chkAdminIdSchema: ChkAdminIdSchema = Body(
        ...,
        examples = {
            "example01" : {
                "summary": "구축신청 아이디 중복체크",
                "description": "",
                "value": {
                     "adminid_input_value" : "aaasssddd"
                    ,"adminid_check_value" : ""
                    ,"is_adminid_checked" : "false"
                }
            }
        }
    )
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)

    result = {}

    if chkAdminIdSchema.adminid_input_value == "" :
        return ex.ReturnOK(400, "중복확인할 아이디를 입력해 주세요", request, result)
    
    res = partner_service.read_partner_id(request, chkAdminIdSchema.adminid_input_value)
    request.state.inspect = frame()

    if res == None : # 중복안됨, 사용가능
        result = {"check_result" : True}
    else : # 중복됨, 사용불가
        result = {"check_result" : False}

    return ex.ReturnOK(200, "", request, result)  
    