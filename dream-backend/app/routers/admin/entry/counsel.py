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
from app.schemas.admin.entry.counsel import *
from app.schemas.admin.entry.build import *
from app.schemas.manager.auth import *
from app.schemas.admin.auth import *
from app.service import log_scm_service

# [ S ] db_scm을 위한 임시
from app.service.admin.entry import counsel_service, build_service
from app.core.dbSCM import SessionLocal_scm
# [ S ] db_scm을 위한 임시

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/admin/entry/counsel"],
)

def 복지드림_상담신청_필터조건(request: Request):
    request.state.inspect = frame()

    result = {}
    result.update({"skeyword_type": [
        {"key": 'company_name', "text": '기업명'},
        {"key": 'staff', "text": '담당자명'},
    ]})

    # 진행상태
    result.update({"state": [
        {"key": '100', "text": '상담문의'},
        {"key": '200', "text": '상담중'},
        {"key": '300', "text": '도입보류'},
        {"key": '501', "text": '도입대기'},
        {"key": '502', "text": '도입신청완료'},
    ]})

    return result

# /be/admin/entry/counsel/init
@router.post("/admin/entry/counsel/init", dependencies=[Depends(api_same_origin)])
async def 복지드림_상담신청_내역_init(
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

    result.update({"filter": 복지드림_상담신청_필터조건(request)}) # 초기 필터

    return result

# /be/admin/entry/counsel/list
@router.post("/admin/entry/counsel/list", dependencies=[Depends(api_same_origin)])
async def 복지드림_상담신청_내역(
     request: Request
    ,pPage_param: PPage_param
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    request.state.db_scm = SessionLocal_scm() # SCM DB session

    if not pPage_param.page or int(pPage_param.page) == 0:
        pPage_param.page = 1

    if not pPage_param.page_view_size or int(pPage_param.page_view_size) == 0:
        pPage_param.page_view_size = 30

    res = counsel_service.counsel_list(request, pPage_param)
    request.state.inspect = frame()

    return res

# /be/admin/entry/counsel/read
@router.post("/admin/entry/counsel/read", dependencies=[Depends(api_same_origin)])
async def 복지드림_상담신청_상세(
     request: Request
    ,pRead: PRead
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    request.state.db_scm = SessionLocal_scm() # SCM DB session

    if pRead.uid == 0 : # 등록할때
        res = {}
        memo_list = {}
        values = jsonable_encoder(DreamCounselInput())

    else : # 수정할때
        res = counsel_service.consel_read(request, pRead.uid)
        request.state.inspect = frame()

        if res is None :
            return ex.ReturnOK(400, "페이지를 불러오는데 실패하였습니다.", request)
        
        values = jsonable_encoder(parse_obj_as(DreamCounselInput, res))

        memo_list = log_scm_service.memo_list(request, "T_DREAM_COUNSEL", pRead.uid)
        request.state.inspect = frame()

    jsondata = {}
    jsondata.update({"values": values})
    jsondata.update(res)
    jsondata.update({"filter": 복지드림_상담신청_필터조건(request)})
    request.state.inspect = frame()
    jsondata.update({"memo_list": memo_list})
        
    return ex.ReturnOK(200, "", request, jsondata)

# /be/admin/entry/counsel/edit
@router.post("/admin/entry/counsel/edit", dependencies=[Depends(api_same_origin)])
async def 복지드림_상담신청_편집(
     request:Request
    ,dreamCounsel: DreamCounselInput = Body(
        ...,
        examples = {
            "example01" : {
                "summary": "상담문의 수정 예시 1",
                "description": "",
                "value": {
                     "mode" : "MOD"
                    ,"uid" : 3
                    ,"state" : "200"
                    ,"company_name" : "(주)ABCDE"
                    ,"homepage_url" : "https://adfasdf"
                    ,"staff_count" : 659
                    ,"wish_build_at" : "2023-10-31"
                    ,"staff_name" : "담당자"
                    ,"staff_position" : "직책"
                    ,"staff_mobile" : "010-1234-1234"
                    ,"staff_email" : "asdf@ttt.com"
                    ,"contents" : "테스트 상담 문의"
                }
            },
            "example03" : {
                "summary": "게시물 Board의 uid",
                "description": "",
                "value": {
                    "uid" : 2076
                    ,"mode" : "DEL"
                }
            },
        }
    )
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    request.state.db_scm = SessionLocal_scm() # SCM DB session

    # 등록
    if dreamCounsel.mode == "REG" :
        res = counsel_service.counsel_create(request, dreamCounsel)
        request.state.inspect = frame()
        if res is None :
            return ex.ReturnOK(500, "상담신청서 등록에 실패했습니다.", request)

        return ex.ReturnOK(200, "상담신청서 등록이 완료되었습니다.", request, {"uid":res.uid})
    
    # 수정
    if dreamCounsel.mode == "MOD" :
        res = counsel_service.counsel_update(request, dreamCounsel)
        request.state.inspect = frame()
        if res is None :
            return ex.ReturnOK(500, "상담신청서 수정에 실패했습니다.", request)
        
        # 상담신청서 -> 도입대기(501) 상태 변경 시 구축신청서 셋팅
        if (dreamCounsel.state == "501") :

            # 상담정보 가져오기
            counsel_info = counsel_service.consel_read(request, dreamCounsel.uid)
            request.state.inspect = frame()
            
            if counsel_info is None :
                return ex.ReturnOK(501, "상담정보가 존재하지 않습니다.", request)
            
            # T_DREAM_BUILD counsel_uid 있으면 (0보다 크면) delete
            build_service.build_delete(request, counsel_info.uid)
            request.state.inspect = frame()

            build_info = DreamBuild(
                 company_name = counsel_info.company_name
                ,staff_name = counsel_info.staff_name
                ,staff_dept = counsel_info.staff_dept
                ,staff_position = counsel_info.staff_position
                ,staff_position2 = counsel_info.staff_position2
                ,staff_mobile = counsel_info.staff_mobile
                ,staff_email = counsel_info.staff_email
                ,counsel_uid = counsel_info.uid
            )
            res = build_service.build_create(request, build_info)
            request.state.inspect = frame()

            if res is None :
                return ex.ReturnOK(500, "상담신청서 수정 실패했습니다. 다시 시도해 주세요. 문제 지속시 개발자에게 문의하세요", request)
        
        return ex.ReturnOK(200, "상담신청서 수정 완료", request, {"uid" : res.uid})
    