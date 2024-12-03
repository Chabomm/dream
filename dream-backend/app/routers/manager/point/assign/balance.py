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
from fastapi.encoders import jsonable_encoder

from app.schemas.schema import *
from app.schemas.manager.auth import *
from app.schemas.manager.point.assign.balance import *

from app.service.manager.point import balance_service
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
    tags=["/manager/point"],
)

def 예치금_필터조건 (request: Request):
    request.state.inspect = frame()

    result = {}
    result.update({"skeyword_type": [
        {"key": 'input_bank', "text": '입금은행'},
        {"key": 'input_name', "text": '입금자명'},
        {"key": 'reason', "text": '입금메모'},
    ]})

    # 입금상태
    result.update({"input_state": [
        {"key": '', "text": '전체', "checked": True},
        {"key": '입금전', "text": '입금전', "checked": True},
        {"key": '입금중', "text": '입금중', "checked": True},
        {"key": '입금완료', "text": '입금완료', "checked": True},
        {"key": '취소', "text": '취소', "checked": True},
    ]})
    
    return result

# /be/manager/point/balance/init
@router.post("/manager/point/balance/init", dependencies=[Depends(api_same_origin)])
async def 예치금내역_init (
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
            "input_state": '',
            "create_at": {
                "startDate": None,
                "endDate": None,
            },
        }
    }
    result.update({"params": params})
    # [ S ] 초기 파라메터

    result.update({"filter": 예치금_필터조건(request)}) # 초기 필터

    return result

# /be/manager/point/balance/list
@router.post("/manager/point/balance/list", dependencies=[Depends(api_same_origin)])
async def 예치금_내역 (
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

    res = balance_service.balance_list(request, pPage_param)
    request.state.inspect = frame()

    return res

# /be/manager/point/balance/edit
@router.post("/manager/point/balance/edit", dependencies=[Depends(api_same_origin)])
async def 예치금_편집 (
     request: Request
    ,assignBalanceInput: AssignBalanceInput
    ,user: TokenDataManager = Depends(get_current_active_manager)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)

    res = balance_service.balance_create(request, assignBalanceInput)
    request.state.inspect = frame()

    if res is None :
        return ex.ReturnOK(500, "예치금 등록에 실패했습니다.", request)

    return ex.ReturnOK(200, "신청이 완료되었습니다. 입금 계좌정보로 입금 시 1~2분 내 충전 확인이 가능합니다.", request, jsonable_encoder(res))


# be/manager/point/balance/xlsx/download
@router.post("/manager/point/balance/xlsx/download", dependencies=[Depends(api_same_origin)])
async def 예치금내역_엑셀_다운로드(
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
        res = balance_service.balance_list(request, excelLogInput.params, True)
        request.state.inspect = frame()

        output = BytesIO()

        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        
        cell_format1 = workbook.add_format()
        cell_format1.set_border(1)
        cell_format1.set_bold()

        # [ S ] 엑셀헤더
        worksheet.write("A1", "신청일", cell_format1)
        worksheet.write("B1", "신청복지포인트", cell_format1)
        worksheet.write("C1", "입금은행", cell_format1)
        worksheet.write("D1", "입금자명", cell_format1)
        worksheet.write("E1", "입금액", cell_format1)
        worksheet.write("F1", "입금일", cell_format1)
        worksheet.write("G1", "입금메모", cell_format1)
        worksheet.write("H1", "처리상태", cell_format1)
        # [ E ] 엑셀헤더
            
        idx = 2
        for c in res["list"] :
            worksheet.write("A"+str(idx), c["create_at"])
            worksheet.write("B"+str(idx), c["save_point"])
            worksheet.write("C"+str(idx), c["input_bank"])
            worksheet.write("D"+str(idx), c["input_name"])
            worksheet.write("E"+str(idx), c["sum_of_pmoney"])
            worksheet.write("F"+str(idx), c["max_of_at"])
            worksheet.write("G"+str(idx), c["reason"])
            worksheet.write("H"+str(idx), c["input_state"])
            idx = idx + 1

        worksheet.set_column('C:H', width=18, cell_format=None)

        workbook.close()
        output.seek(0)

        headers = {
            'Content-Disposition': 'attachment; filename="filename.xlsx"'
        }

        return StreamingResponse(output, headers=headers)