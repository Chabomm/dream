import json
import os
import requests
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
from fastapi.encoders import jsonable_encoder

from app.schemas.schema import *
from app.schemas.manager.partner import *
from app.schemas.manager.auth import *
# from app.service import partner_service
from app.service.inout.inbound import partner_service


router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/inbound"],
)

# /be/inbound/partner/edit
@router.post("/inbound/partner/edit", dependencies=[Depends(api_same_origin)])
async def 인바운드_고객사_편집(
    request: Request
    ,partnerInput: PartnerInput = Body(
        ...,
        examples={
            "example01": {
                "summary": "고객사 등록하기 예시1",
                "description": "",
                "value": {
                    "partner_type" : "300"
                    ,"partner_id" : "testmall"
                    ,"mall_name" : "테스트몰"
                    ,"company_name" : "ㅇㅇㅇ"
                    ,"sponsor" : "welfaredream"
                    ,"partner_code" : "M001JB11W"
                    ,"prefix" : "M001JB11W_"
                    ,"logo" : ""
                    ,"is_welfare" : "F"
                    ,"is_dream" : "F"
                    ,"state" : "100"
                    ,"mem_type" : "임직원"
                    ,"in_user_id" : "aaa@indend.co.kr"
                    ,"mode": "REG"
                },
            },
            "example02": {
                "summary": "고객사 수정하기 예시1",
                "description": "",
                "value": {
                     "partner_type" : "201"
                    ,"partner_id" : "asdfaaaj1"
                    ,"mall_name" : "복지test수정"
                    ,"company_name" : "ㅁㄴㅇㄻㄴㅇㄹ"
                    ,"sponsor" : "welfaredream"
                    ,"logo" : "https://indend-resource.s3.ap-northeast-1.amazonaws.com/logos/asdfff/pick-W_File_ComLogo_16567514394242.svg"
                    ,"is_welfare" : "T"
                    ,"is_dream" : "T"
                    ,"state" : "300"
                    ,"mem_type" : "회원"
                    ,"in_user_id" : "aaa@indend.co.kr"
                    ,"mode": "MOD"
                },
            },
            "example03": {
                "summary": "임직원 삭제하기 예시1",
                "description": "",
                "value": {
                     "uid" : 5
                    ,"mode": "DEL"
                },
            }
        }
    )
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)

    # 등록
    if partnerInput.mode == "REG" :
        res = partner_service.partner_create(request, partnerInput)
        request.state.inspect = frame()
        return ex.ReturnOK(200, "등록이 완료되었습니다. 새로고침 해주세요", request, {"uid" : res.uid})

    # 수정
    if partnerInput.mode == "MOD" :
        res = partner_service.partner_update(request, partnerInput)
        request.state.inspect = frame()
        return ex.ReturnOK(200, "수정이 완료되었습니다. 새로고침 해주세요", request, {"uid" : res.uid})
    
    # # 삭제
    # if memberInput.mode == "DEL" :
    #     member_service.member_delete(request, memberInput.uid)
    #     request.state.inspect = frame()
    #     return ex.ReturnOK(200, "삭제 완료", request)


# be/dream/partner/edit
@router.post("/dream/partner/edit", dependencies=[Depends(api_same_origin)])
async def 복지드림_고객사_편집 (
    request: Request, 
    request_body: Dict = Body(
        ...,
        examples = {
            "example01" : {
                "summary": "고객사 등록 샘플",
                "description": "",
                "value": {
                     "partner_type" : "300"
                    ,"partner_id" : "test"
                    ,"mall_name" : "복지몰명"
                    ,"company_name" : "고객사회사명"
                    ,"sponsor" : "welfaredream"
                    ,"partner_code" : "GX12345"
                    ,"prefix" : "GX12345_"
                    ,"logo" : "https://"
                    ,"state" : "100"
                    ,"mem_type" : "임직원"
                    ,"mall_type" : "임직원몰"
                    ,"is_welfare" : "T"
                    ,"is_dream" : "T"
                }
            },
        }
    )
) :
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
  
    timestr = util.getNow("%Y-%m-%d")
    file_name = timestr + ".log"
    logm = util.getNow() + " |:| " + request.state.user_ip + "\n"
    logm = logm + "┏────────────request.state.body─────────────┓" + "\n"
    logm = logm + json.dumps(request_body, ensure_ascii=False, indent=4) + "\n"
    logm = logm + "└───────────────────────────────────────────┘" 
    util.file_open (
        "/usr/src/app/data/dream-backend/partner/"
        ,file_name
        ,logm
    )
    if "partner_id" in request_body and request_body["partner_id"] != "" :
        res = partner_service.partner_edit(request, request_body)
        # [ S ] UMS 서버에 고객사 업데이트
        URL = "http://0.0.0.0:5000/ums/push/partner/add"
        headers = {
            'Content-Type': 'application/json; charset=utf-8'
            ,'x-user-ip': request.state.user_ip
        }
        result = ""
        params = json.dumps(jsonable_encoder(request_body))
        try : 
            result = requests.post(URL, headers=headers, data=params, timeout=1).text
        except Exception as e:
            result = "fail"
        # [ S ] UMS 서버에 고객사 업데이트
      
        return ex.ReturnOK(200, "", request, {"result" : res})
    else :
        return ex.ReturnOK(404, "필수파라메터 오류", request)
