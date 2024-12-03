from fastapi import APIRouter, Depends, Request, Body
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse, StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from inspect import currentframe as frame
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core import exceptions as ex
from app.core import util
from app.core.config import PROXY_PREFIX, api_same_origin
from app.deps.auth import get_current_active_manager
import json

from app.schemas.schema import *
from app.schemas.manager.point.limit.industry import *
from app.schemas.manager.auth import *
from app.service.manager.limit import card_service
from app.service import log_service

import pandas as pd
from io import BytesIO # Add to Top of File
import xlsxwriter
import os
from fastapi.datastructures import UploadFile
from fastapi.param_functions import File, Form
import json

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/manager/point/limit"],
)

def 복지카드_허용업종_필터조건 (request: Request):
    request.state.inspect = frame()

    result = {}
    result.update({"skeyword_type": [
        {"key": 'name', "text": '업종명'},
        {"key": 'code', "text": '업종코드'},
    ]})
 
    # 허용여부
    result.update({"yn": [
        {"key": '', "text": '전체'},
        {"key": 'Y', "text": '허용'},
        {"key": 'N', "text": '제한'},
    ]})

    return result

# /be/manager/point/limit/card/init
@router.post("/manager/point/limit/card/init", dependencies=[Depends(api_same_origin)])
async def 복지카드_허용업종_내역_init (
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
            "checked": []
            ,"yn": ""
        }
    }
    result.update({"params": params})
    # [ S ] 초기 파라메터

    result.update({"filter": 복지카드_허용업종_필터조건(request)}) # 초기 필터

    return result

# /be/manager/point/limit/card/list
@router.post("/manager/point/limit/card/list", dependencies=[Depends(api_same_origin)])
async def 복지카드_허용업종_내역 (
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

    res = card_service.industry_list(request, pPage_param, "T_INDUSTRY_OFFCARD")
    request.state.inspect = frame()

    return res

# /be/manager/point/limit/card/edit
@router.post("/manager/point/limit/card/edit", dependencies=[Depends(api_same_origin)])
async def 복지카드_허용업종_등록 (
     request: Request
    ,limitIndustryInput: LimitIndustryInput
    ,user: TokenDataManager = Depends(get_current_active_manager)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)

    if limitIndustryInput.mode == 'REG' :
        card_service.industry_create(request, limitIndustryInput)
        request.state.inspect = frame()
        return ex.ReturnOK(200, "복지카드 업종 허용이 완료되었습니다.", request, {})
    
    if limitIndustryInput.mode == 'DEL' :
        card_service.industry_delete(request, limitIndustryInput)
        request.state.inspect = frame()
        
        return ex.ReturnOK(200, "복지카드 업종 제외가 되었습니다.", request, {})
            
    


# be/manager/point/limit/card/xlsx/download
@router.post("/manager/point/limit/card/xlsx/download", dependencies=[Depends(api_same_origin)])
async def 복지카드허용업종내역_엑셀_다운로드(
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
        if excelLogInput.params.filters["type"] == "sikwon" :
            res = card_service.industry_list(request, excelLogInput.params, "T_INDUSTRY_SIKWON", True)
            request.state.inspect = frame()
        else :
            res = card_service.industry_list(request, excelLogInput.params, "T_INDUSTRY_OFFCARD", True)
            request.state.inspect = frame()

        output = BytesIO()

        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        
        cell_format1 = workbook.add_format()
        cell_format1.set_border(1)
        cell_format1.set_bold()

        # [ S ] 엑셀헤더
        worksheet.write("A1", "업종명", cell_format1)
        worksheet.write("B1", "업종코드", cell_format1)
        worksheet.write("C1", "복지카드허용여부", cell_format1)
        worksheet.write("D1", "최근허용일", cell_format1)
        # [ E ] 엑셀헤더
            
        idx = 2
        for c in res["list"] :
            worksheet.write("A"+str(idx), c["name"])
            worksheet.write("B"+str(idx), c["code"])
            worksheet.write("C"+str(idx), c["limit"])
            worksheet.write("D"+str(idx), c["create_at"])
            idx = idx + 1

        worksheet.set_column('A:D', width=18, cell_format=None)

        workbook.close()
        output.seek(0)

        headers = {
            'Content-Disposition': 'attachment; filename="filename.xlsx"'
        }

        return StreamingResponse(output, headers=headers)