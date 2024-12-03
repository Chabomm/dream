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
from app.schemas.manager.auth import *

from app.service.manager.point import balance_service, used_service
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
    tags=["/manager/point/used"],
)

def 포인트전체사용_필터조건 (request: Request):
    request.state.inspect = frame()

    result = {}
    result.update({"skeyword_type": [
        {"key": 'a', "text": '이름'},
        {"key": 'a', "text": '생년월일'},
        {"key": 'a', "text": '부서'},
    ]})

    return result

# /be/manager/point/used/merge/init
@router.post("/manager/point/used/merge/init", dependencies=[Depends(api_same_origin)])
async def 포인트전체사용_내역_init (
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
        }
    }
    result.update({"params": params})
    # [ S ] 초기 파라메터

    result.update({"filter": 포인트전체사용_필터조건(request)}) # 초기 필터

    return result

# /be/manager/point/used/merge/list
@router.post("/manager/point/used/merge/list", dependencies=[Depends(api_same_origin)])
async def 포인트전체사용_내역 (
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

    res = used_service.used_list(request, pPage_param)
    request.state.inspect = frame()

    return res


# be/manager/point/used/merge/xlsx/download
@router.post("/manager/point/used/merge/xlsx/download", dependencies=[Depends(api_same_origin)])
async def 포인트전체사용내역_엑셀_다운로드(
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
        res = used_service.used_list(request, excelLogInput.params, True)
        request.state.inspect = frame()

        output = BytesIO()

        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        
        cell_format1 = workbook.add_format()
        cell_format1.set_border(1)
        cell_format1.set_bold()

        # [ S ] 엑셀헤더
        worksheet.write("A1", "이름", cell_format1)
        worksheet.write("B1", "생년월일", cell_format1)
        worksheet.write("C1", "부서", cell_format1)
        worksheet.write("D1", "직급", cell_format1)
        worksheet.write("E1", "복지몰사용포인트", cell_format1)
        worksheet.write("F1", "복지카드사용포인트", cell_format1)
        worksheet.write("G1", "식권카드사용포인트", cell_format1)
        worksheet.write("H1", "사용포인트합계", cell_format1)
        # [ E ] 엑셀헤더
            
        idx = 2
        for c in res["list"] :
            worksheet.write("A"+str(idx), c["user_name"])
            worksheet.write("B"+str(idx), c["birth"])
            worksheet.write("C"+str(idx), c["depart"])
            worksheet.write("D"+str(idx), c["position"])
            worksheet.write("E"+str(idx), c["bokji_mall_point"])
            worksheet.write("F"+str(idx), c["bokji_point"])
            worksheet.write("G"+str(idx), c["sikwon_point"])
            worksheet.write("H"+str(idx), c["sum_point"])
            idx = idx + 1

        worksheet.set_column('A:H', width=18, cell_format=None)

        workbook.close()
        output.seek(0)

        headers = {
            'Content-Disposition': 'attachment; filename="filename.xlsx"'
        }

        return StreamingResponse(output, headers=headers)