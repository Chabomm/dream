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
from pydantic.tools import parse_obj_as


from app.core.dbSCM import SessionLocal_scm


from app.routers import aws
from app.schemas.admin.auth import *
from app.schemas.admin.b2b.seller import *
from app.service.admin.b2b import seller_service
from app.service import log_scm_service

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/admin/b2b/seller"],
)

def 업체_리스트_필터조건(request: Request, type:str):
    request.state.inspect = frame()

    result = {}
    result.update({"skeyword_type": [
        {"key": 'indend_md', "text": '담당MD아이디'},
        {"key": 'indend_md_name', "text": '담당MD명'},
        {"key": 'seller_id', "text": '판매자아이디'},
        {"key": 'seller_name', "text": '판매자명'},
    ]})

    # 처리상태
    result.update({"state": [
        {"key": '', "text": '전체', "checked": True},
        {"key": '100', "text": '정상', "checked": True},
        {"key": '200', "text": '1차승인', "checked": True},
        {"key": '900', "text": '퇴점', "checked": True},
    ]})

    # 정산주기
    result.update({"account_cycle": [
        {"key": '1', "text": '일정산', "checked": True},
        {"key": '7', "text": '주정산', "checked": True},
        {"key": '15', "text": '15일정산', "checked": True},
        {"key": '30', "text": '월정산', "checked": True},
    ]})

    # 은행리스트
    result.update({"bank_list": [
        {"key": '경남은행', "text": '경남은행'},
        {"key": '기업은행', "text": '기업은행'},
        {"key": '부산은행', "text": '부산은행'},
        {"key": '수협중앙회', "text": '수협중앙회'},
        {"key": '신용협동조합', "text": '신용협동조합'},
        {"key": '우체국', "text": '우체국'},
        {"key": 'SC제일은행', "text": 'SC제일은행'},
        {"key": '주택은행', "text": '주택은행'},
        {"key": '하나은행', "text": '하나은행'},
        {"key": '광주은행', "text": '광주은행'},
        {"key": '농협중앙회', "text": '농협중앙회'},
        {"key": '한국산업은행', "text": '한국산업은행'},
        {"key": '한국씨티은행', "text": '한국씨티은행'},
        {"key": '외환은행', "text": '외환은행'},
        {"key": '장기신용', "text": '장기신용'},
        {"key": '제주은행', "text": '제주은행'},
        {"key": '축협중앙회', "text": '축협중앙회'},
        {"key": '한미은행', "text": '한미은행'},
        {"key": 'KB국민은행', "text": 'KB국민은행'},
        {"key": '대구은행', "text": '대구은행'},
        {"key": '서울은행', "text": '서울은행'},
        {"key": '신한은행', "text": '신한은행'},
        {"key": '우리은행', "text": '우리은행'},
        {"key": '전북은행', "text": '전북은행'},
        {"key": '조흥은행', "text": '조흥은행'},
        {"key": '평화은행', "text": '평화은행'},
        {"key": '새마을금고', "text": '새마을금고'},
        {"key": 'HSBC', "text": 'HSBC'},
        {"key": '스탠다드차타드은행', "text": '스탠다드차타드은행'},
        {"key": '한국수출입은행', "text": '한국수출입은행'},
        {"key": '중소기업은행', "text": '중소기업은행'},
        {"key": '카카오은행', "text": '카카오은행'},
        {"key": '금화저축은행', "text": '금화저축은행'},
    ]})

    return result

# /be/admin/b2b/seller/init
@router.post("/admin/b2b/seller/init", dependencies=[Depends(api_same_origin)])
async def B2B상품리스트_init (
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
            "seller_uid": 0,
            "create_at": {
                "startDate": None,
                "endDate": None,
            },
            "delete_at": {
                "startDate": None,
                "endDate": None,
            },
        }
    }
    result.update({"params": params})
    # [ S ] 초기 파라메터

    result.update({"filter": 업체_리스트_필터조건(request,'list')}) # 초기 필터

    return result

# /be/admin/b2b/seller/list
@router.post("/admin/b2b/seller/list", dependencies=[Depends(api_same_origin)])
async def 업체_리스트(
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

    res = seller_service.seller_list(request, page_param) 
    request.state.inspect = frame()

    return res

# /be/admin/b2b/seller/search/list
@router.post("/admin/b2b/seller/search/list", dependencies=[Depends(api_same_origin)])
async def 업체_리스트_검색창(
     request: Request
    ,sellerSearchInput: SellerSearchInput
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    request.state.db_scm = SessionLocal_scm() # SCM DB session

    res = seller_service.seller_search_list(request, sellerSearchInput) 
    request.state.inspect = frame()

    return res

# /be/admin/b2b/seller/read
@router.post("/admin/b2b/seller/read", dependencies=[Depends(api_same_origin)])
async def 업체_상세(
    request: Request
    ,pRead : PRead
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    request.state.db_scm = SessionLocal_scm() # SCM DB session

    result = {}
    if pRead.uid <= 0 :
        res = jsonable_encoder(SellerDetail())
        values = jsonable_encoder(SellerDetail())
    else :
        res = seller_service.seller_read(request, pRead.uid)
        request.state.inspect = frame()
        values = jsonable_encoder(parse_obj_as(SellerDetailInput, res))

    result.update(res)
    result.update({"values": values})
    result.update({"filter": 업체_리스트_필터조건(request, 'detail')})

    return result

# /be/admin/b2b/seller/edit
@router.post("/admin/b2b/seller/edit", dependencies=[Depends(api_same_origin)])
async def 업체_편집(
     request:Request
    ,sellerDetailInput: SellerDetailInput
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    request.state.db_scm = SessionLocal_scm() # SCM DB session

    # 등록
    if sellerDetailInput.mode == "REG" :
        res = seller_service.seller_create(request, sellerDetailInput)
        request.state.inspect = frame()
        return ex.ReturnOK(200, "업체 등록 완료", request, {"uid" : res.uid})

    # 수정
    if sellerDetailInput.mode == "MOD" : 
        res = seller_service.seller_update(request, sellerDetailInput)
        request.state.inspect = frame()
        return ex.ReturnOK(200, "업체 수정 완료", request, {"uid" : res.uid})

    # 순서
    if sellerDetailInput.mode == "SORT" :
        seller_service.seller_staff_sort(request, sellerDetailInput)
        request.state.inspect = frame()
        return ex.ReturnOK(200, "순서 수정 완료", request)

    # 메모
    if sellerDetailInput.mode == "MEMO" :
        log_scm_service.create_memo(request, sellerDetailInput.uid, "T_B2B_SELLER", sellerDetailInput.memo, user.user_id, user.token_name, 'ADMIN', None)
        request.state.inspect = frame()

        return ex.ReturnOK(200, "메모 등록 완료", request)

def 업체_담당자_필터조건(request: Request, type:str):
    request.state.inspect = frame()

    result = {}
    
    roles = seller_service.roles_list(request)
    result.update({"roles": roles})

    return result

# /be/admin/b2b/seller/staff/read
@router.post("/admin/b2b/seller/staff/read", dependencies=[Depends(api_same_origin)])
async def 업체_담당자_상세(
    request: Request
    ,staffInput : StaffInput
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    request.state.db_scm = SessionLocal_scm() # SCM DB session

    result = {}
    if staffInput.uid <= 0 :
        res = jsonable_encoder(SellerStaff(seller_uid=staffInput.seller_uid, seller_id=staffInput.seller_id, seller_name=staffInput.seller_name))
    else :
        res = seller_service.staff_read(request, staffInput)
        request.state.inspect = frame()
        if staffInput.mode == 'COPY' :
            res["login_id"] = None
            res["login_pw"] = None

    values = jsonable_encoder(parse_obj_as(SellerStaffInput, res))

    result.update(res)
    result.update({"values": values})
    result.update({"filter": 업체_담당자_필터조건(request, 'detail')})

    return result

# /be/admin/b2b/seller/staff/edit
@router.post("/admin/b2b/seller/staff/edit", dependencies=[Depends(api_same_origin)])
async def 업체_담당자_편집(
     request:Request
    ,sellerStaffInput: SellerStaffInput
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    request.state.db_scm = SessionLocal_scm() # SCM DB session

    # 등록
    if sellerStaffInput.mode == "REG" or sellerStaffInput.mode == "COPY" :
        res = seller_service.duplicate_check(request, sellerStaffInput)
        request.state.inspect = frame()
        if res != None :
            return ex.ReturnOK(404, "해당 로그인 아이디는 중복된 아이디로 등록할 수 없습니다.", request)
        else :
            res = seller_service.seller_staff_create(request, sellerStaffInput)
            request.state.inspect = frame()
            return ex.ReturnOK(200, "업체담당자 등록 완료", request, {"uid" : res.uid})

    # 수정
    if sellerStaffInput.mode == "MOD" or sellerStaffInput.mode == "DEL" : 
        res = seller_service.seller_staff_update(request, sellerStaffInput)
        request.state.inspect = frame()
        return ex.ReturnOK(200, "업체담당자 수정 완료", request, {"uid" : res.uid})

# /be/admin/b2b/seller/pw/reset
@router.post("/admin/b2b/seller/pw/reset", dependencies=[Depends(api_same_origin)])
async def 업체_담당자_비밀번호초기화(
     request:Request
    ,pRead : PRead
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    request.state.db_scm = SessionLocal_scm() # SCM DB session
    res = seller_service.seller_staff_pw_update(request, pRead.uid)
    request.state.inspect = frame()
    return ex.ReturnOK(200, "업체담당자 비밀번호 초기화 완료", request, {"uid" : res.uid})
    

    
@router.post("/admin/b2b/seller/file/download/{file_uid}/{file_kind}")
async def 내부_첨부파일_다운로드 (
    request: Request
    ,file_uid: int
    ,file_kind: str
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    request.state.db_scm = SessionLocal_scm() # SCM DB session

    if request.headers.get('sec-fetch-site') == "same-origin" :
        res = seller_service.seller_files_read(request, file_uid)
        request.state.inspect = frame()

        if file_kind == 'biz_file':
            file_path = res.biz_file
            file_name = res.biz_file.split('/')[-1]
        else :
            file_path = res.biz_hooper
            file_name = res.biz_hooper.split('/')[-1]

        file_path = "/usr/src/app" + file_path
        return FileResponse(file_path, filename=file_name)

    elif request.headers.get('host') == "backend:5000" :
        print ("api_same_origin OK")
    else :
        print ("api_same_origin 비정상적인 호출")


# be/admin/b2b/seller/admin/list
@router.post("/admin/b2b/seller/admin/list", dependencies=[Depends(api_same_origin)])
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
        page_param.page_view_size = 100

    res = seller_service.admin_list(request, page_param)
    request.state.inspect = frame()

    return res