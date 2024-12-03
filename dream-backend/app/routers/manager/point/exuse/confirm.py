from fastapi import APIRouter, Depends, Request, Body
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse, StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
from inspect import currentframe as frame
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic.tools import parse_obj_as
from app.core import exceptions as ex
from app.core import util
from app.core.config import PROXY_PREFIX, api_same_origin
from app.deps.auth import get_current_active_manager
import json

from app.schemas.schema import *
from app.schemas.manager.point.exuse.confirm import *
from app.schemas.manager.point.offcard.used import *
from app.schemas.manager.auth import *
from app.models.point.confirm import *
from app.service.manager.point import confirm_service
from app.service import log_service
from app.routers.front.card.used import *

import pandas as pd
from io import BytesIO # Add to Top of File
import xlsxwriter
import os
from fastapi.datastructures import UploadFile
from fastapi.param_functions import File, Form
import json

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/manager/point/exuse"],
)

def 소명승인_필터조건 (request: Request):
    request.state.inspect = frame()

    result = {}
    result.update({"skeyword_type": [
        {"key": 'user_name', "text": '이름'},
        {"key": 'birth', "text": '생년월일'},
        {"key": 'depart', "text": '부서'},
    ]})
 
    # 처리상태
    result.update({"state": [
        {"key": '', "text": '전체'},
        {"key": '소명신청', "text": '소명신청'},
        {"key": '소명승인완료', "text": '소명승인완료'},
        {"key": '미승인(반려)', "text": '미승인(반려)'},
        {"key": '재차감설정', "text": '재차감설정'},
        {"key": '결제취소', "text": '결제취소', "disabled": True},
    ]})

    return result

# /be/manager/point/exuse/confirm/init
@router.post("/manager/point/exuse/confirm/init", dependencies=[Depends(api_same_origin)])
async def 소명승인_내역_init (
     request: Request
    ,user: TokenDataManager = Depends(get_current_active_manager)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)

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
            "pay_at": {
                "startDate": None,
                "endDate": None,
            },
            "pay_cancel_at": {
                "startDate": None,
                "endDate": None,
            },
            "confirm_at": {
                "startDate": None,
                "endDate": None,
            },
            "state": '소명신청',
            "estate": '',
            "checked": [],
        }
    }
    result.update({"params": params})
    # [ S ] 초기 파라메터

    result.update({"filter": 소명승인_필터조건(request)}) # 초기 필터

    return result

# /be/manager/point/exuse/list
@router.post("/manager/point/exuse/confirm/list", dependencies=[Depends(api_same_origin)])
async def 소명승인_내역 (
     request: Request
    ,pPage_param: PPage_param
    ,user: TokenDataManager = Depends(get_current_active_manager)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)

    if not pPage_param.page or int(pPage_param.page) == 0:
        pPage_param.page = 1

    if not pPage_param.page_view_size or int(pPage_param.page_view_size) == 0:
        pPage_param.page_view_size = 30

    res = confirm_service.confirm_list(request, pPage_param)
    request.state.inspect = frame()

    return res

# /be/manager/point/exuse/confirm/read
@router.post("/manager/point/exuse/confirm/read", dependencies=[Depends(api_same_origin)])
async def 소명승인_상세 (
     request: Request
     ,pRead: PRead
    ,user: TokenDataManager = Depends(get_current_active_manager)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)

    res = confirm_service.confirm_read(request, pRead.uid)
    request.state.inspect = frame()

    if res is None :
        return ex.ReturnOK(400, "페이지를 불러오는데 실패하였습니다.", request)
    
    values = jsonable_encoder(parse_obj_as(ConfirmInput, res))

    memo_list = log_service.memo_list(request, "T_EXUSE", pRead.uid)
    request.state.inspect = frame()

    jsondata = {}
    jsondata.update({"values": values})
    jsondata.update(res)
    jsondata.update({"filter": 소명승인_필터조건(request)})
    request.state.inspect = frame()
    jsondata.update({"memo_list": memo_list})
        
    return ex.ReturnOK(200, "", request, jsondata)

# /be/manager/point/exuse/confirm/edit
@router.post("/manager/point/exuse/confirm/edit", dependencies=[Depends(api_same_origin)])
async def 소명승인_수정(
     request:Request
    ,confirmInput: ConfirmInput
    ,user: TokenDataManager = Depends(get_current_active_manager)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)

    if confirmInput.state == "소명승인완료" :

        if confirmInput.point_type == "복지포인트" : 
            use_type = "bokji"
        elif confirmInput.point_type == "식권포인트" : 
            use_type = "sikwon"

        cardUsedInput = CardUsedInput (
            user_id = user.user_id
            ,use_type = use_type
            ,deduct_list = [{"card_used_uid" : confirmInput.card_used_uid, "request_point": confirmInput.exuse_amount}]
        )
        
        if confirmInput.point_type == "복지포인트" : 
            await F_복지카드사용_복지포인트차감신청(request, cardUsedInput)
        elif confirmInput.point_type == "식권포인트" : 
            await F_식권카드사용_식권포인트차감신청(request, cardUsedInput)

        
    
    res = confirm_service.confirm_update(request, confirmInput)
    request.state.inspect = frame()
    return ex.ReturnOK(200, "수정이 완료되었습니다.", request, {"uid" : res.uid})

# be/manager/point/exuse/confirm/xlsx/download
@router.post("/manager/point/exuse/confirm/xlsx/download", dependencies=[Depends(api_same_origin)])
async def 소명승인내역_엑셀_다운로드(
     request: Request
    ,excelLogInput: ExcelLogInput
    ,user: TokenDataManager = Depends(get_current_active_manager)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)
    
    res = log_service.excel_download_log(request, excelLogInput) 
    request.state.inspect = frame()

    if res != None :
        res = confirm_service.confirm_list(request, excelLogInput.params, True)
        request.state.inspect = frame()

        output = BytesIO()

        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        
        cell_format1 = workbook.add_format()
        cell_format1.set_border(1)
        cell_format1.set_bold()

        # [ S ] 엑셀헤더
        worksheet.write("A1", "번호", cell_format1)
        worksheet.write("B1", "이름", cell_format1)
        worksheet.write("C1", "생년월일", cell_format1)
        worksheet.write("D1", "부서", cell_format1)
        worksheet.write("E1", "직급", cell_format1)
        worksheet.write("F1", "카드결제일", cell_format1)
        worksheet.write("G1", "포인트종류", cell_format1)
        worksheet.write("H1", "소명신청일", cell_format1)
        worksheet.write("I1", "업종명", cell_format1)
        worksheet.write("J1", "사용내역", cell_format1)
        worksheet.write("K1", "결제금액", cell_format1)
        worksheet.write("L1", "차감신청금액", cell_format1)
        worksheet.write("M1", "처리상태", cell_format1)
        worksheet.write("N1", "처리완료일", cell_format1)
        worksheet.write("O1", "결제취소일", cell_format1)
        # [ E ] 엑셀헤더
            
        idx = 2
        for c in res["list"] :
            worksheet.write("A"+str(idx), c["uid"])
            worksheet.write("B"+str(idx), c["user_name"])
            worksheet.write("C"+str(idx), c["birth"])
            worksheet.write("D"+str(idx), c["depart"])
            worksheet.write("E"+str(idx), c["position"])
            worksheet.write("F"+str(idx), c["pay_at"])
            worksheet.write("G"+str(idx), c["point_type"])
            worksheet.write("H"+str(idx), c["create_at"])
            worksheet.write("I"+str(idx), c["biz_item"])
            worksheet.write("J"+str(idx), c["detail"])
            worksheet.write("K"+str(idx), c["pay_amount"])
            worksheet.write("L"+str(idx), c["exuse_amount"])
            worksheet.write("M"+str(idx), c["state"])
            worksheet.write("N"+str(idx), c["confirm_at"])
            worksheet.write("O"+str(idx), c["pay_cancel_at"])
            idx = idx + 1

        worksheet.set_column('B:O', width=18, cell_format=None)

        workbook.close()
        output.seek(0)

        headers = {
            'Content-Disposition': 'attachment; filename="filename.xlsx"'
        }

        return StreamingResponse(output, headers=headers)