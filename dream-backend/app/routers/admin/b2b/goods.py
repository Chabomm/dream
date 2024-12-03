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

from app.schemas.admin.auth import *
from app.schemas.admin.b2b.goods import *
from app.service.admin.b2b import goods_service

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/admin/b2b/goods"],
)


def B2B_리스트_필터조건(request: Request, type:str):
    request.state.inspect = frame()

    result = {}
    if type == 'detail' :
        result.update({"category": [
            {"key": '기업지원', "text": '기업지원', "checked": True},
            {"key": '인사총무', "text": '인사총무', "checked": True},
            {"key": '마케팅/광고/홍보', "text": '마케팅/광고/홍보', "checked": True},
            {"key": '기업복지', "text": '기업복지', "checked": True},
            {"key": '영업관리', "text": '영업관리', "checked": True},
            {"key": '기타', "text": '기타', "checked": True},
        ]})
        result.update({"is_display": [
            {"key": 'T', "text": '진열', "checked": True},
            {"key": 'F', "text": '미진열', "checked": True},
        ]})
    else :
        result.update({"skeyword_type": [
            {"key": 'title', "text": '서비스명'},
        ]})

        # 카테고리
        result.update({"category": [
            {"key": '', "text": '전체', "checked": True},
            {"key": '기업지원', "text": '기업지원', "checked": True},
            {"key": '인사총무', "text": '인사총무', "checked": True},
            {"key": '마케팅/광고/홍보', "text": '마케팅/광고/홍보', "checked": True},
            {"key": '기업복지', "text": '기업복지', "checked": True},
            {"key": '영업관리', "text": '영업관리', "checked": True},
            {"key": '기타', "text": '기타', "checked": True},
        ]})

        # 처리상태
        result.update({"is_display": [
            {"key": '', "text": '전체', "checked": True},
            {"key": 'T', "text": '진열', "checked": True},
            {"key": 'F', "text": '미진열', "checked": True},
        ]})

    return result

# /be/admin/b2b/goods/init
@router.post("/admin/b2b/goods/init", dependencies=[Depends(api_same_origin)])
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
            "category": '',
            "is_display": '',
            "seller_uid": 0,
            "create_at": {
                "startDate": None,
                "endDate": None,
            },
        }
    }
    result.update({"params": params})
    # [ S ] 초기 파라메터

    result.update({"filter": B2B_리스트_필터조건(request,'list')}) # 초기 필터

    return result

# be/admin/b2b/goods/list
@router.post("/admin/b2b/goods/list", dependencies=[Depends(api_same_origin)])
async def B2B_리스트(
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
    
    if not page_param.page_view_size or int(page_param.page_view_size) == 0 :
        page_param.page_view_size = 30
        
    res = goods_service.list(request, page_param)
    request.state.inspect = frame()
    
    return res

# /be/admin/b2b/goods/read
@router.post("/admin/b2b/goods/read", dependencies=[Depends(api_same_origin)])
async def B2B상품_상세(
    request: Request
    ,pRead : PRead
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    request.state.db_scm = SessionLocal_scm() # SCM DB session

    result = {}
    if pRead.uid == 0 :
        res = jsonable_encoder(B2BGoods())
        values = jsonable_encoder(B2BGoodsInput())
    else :
        res = goods_service.read(request, pRead.uid)
        request.state.inspect = frame()
        values = jsonable_encoder(parse_obj_as(B2BGoodsInput, res))

    values_memo = {
         "table_uid" : pRead.uid
        ,"memo" : ''
        ,"file_url" : ''
        ,"file_name" : ''
    }

    result.update(res)
    result.update({"values": values})
    result.update({"filter": B2B_리스트_필터조건(request, 'detail')})
    result["values"].update({"values_memo": values_memo})
        
    return result

# be/admin/b2b/goods/edit
@router.post("/admin/b2b/goods/edit", dependencies=[Depends(api_same_origin)])
async def b2b_상품_편집(
     request:Request
    ,b2bGoodsInput: B2BGoodsInput
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    request.state.db_scm = SessionLocal_scm() # SCM DB session

    # 등록
    if b2bGoodsInput.mode == "REG" :
        res = goods_service.goods_create(request, b2bGoodsInput)
        request.state.inspect = frame()
        if res is None :
            return ex.ReturnOK(500, "B2B 상품 등록에 실패했습니다.", request)

        goods_service.option_list_create(request, b2bGoodsInput.option_list, res.uid)
        request.state.inspect = frame()

        goods_service.etc_image_create(request, b2bGoodsInput.etc_images, res.uid)
        request.state.inspect = frame()

        return ex.ReturnOK(200, "B2B 상품 등록이 완료되었습니다.", request, {"uid":res.uid})
    # 수정
    if b2bGoodsInput.mode == "MOD" : 
        res = goods_service.goods_update(request, b2bGoodsInput)
        request.state.inspect = frame()

        goods_service.option_list_update(request, b2bGoodsInput)
        request.state.inspect = frame()

        goods_service.etc_image_update(request, b2bGoodsInput)
        request.state.inspect = frame()

        return ex.ReturnOK(200, "B2B 상품 수정이 완료되었습니다.", request)

