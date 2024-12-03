from fastapi import APIRouter, Depends, Request, Body
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse,StreamingResponse
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
from app.service.manager.point import point_service
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

def 포인트지급_필터조건 (request: Request):
    request.state.inspect = frame()

    result = {}
    result.update({"skeyword_type": [
        {"key": 'user_name', "text": '이름'},
        {"key": 'user_id', "text": '아이디'},
        {"key": 'depart', "text": '부서'},
        {"key": 'position', "text": '직급/직책'},
        {"key": 'reason', "text": '지급/회수 사유'},
        {"key": 'admin_memo', "text": '관리자 메모'},
        {"key": 'admin_name', "text": '처리자'},
    ]})

    # 지급구분
    result.update({"saved_type": [
        {"key": '', "text": '전체', "checked": True},
        {"key": '1', "text": '대량지급', "checked": True},
        {"key": '2', "text": '개별지급', "checked": True},
        {"key": '3', "text": '개별회수', "checked": True},
    ]})

    return result

# /be/manager/point/assign/init
@router.post("/manager/point/assign/init", dependencies=[Depends(api_same_origin)])
async def 포인트지급내역_init (
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
            "saved_type": '',
            "create_at": {
                "startDate": None,
                "endDate": None,
            },
            "expiry_at": {
                "startDate": None,
                "endDate": None,
            },
        }
    }
    result.update({"params": params})
    # [ S ] 초기 파라메터

    result.update({"filter": 포인트지급_필터조건(request)}) # 초기 필터

    return result

# /be/manager/point/assign/list
@router.post("/manager/point/assign/list", dependencies=[Depends(api_same_origin)])
async def 복지포인트지급내역 (
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

    res = point_service.assign_list(request, pPage_param)
    request.state.inspect = frame()
        
    return res

# /be/manager/point/assign/sikwon
@router.post("/manager/point/assign/sikwon", dependencies=[Depends(api_same_origin)])
async def 식권포인트지급내역 (
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

    res = point_service.assign_sikwon_list(request, pPage_param)
    request.state.inspect = frame()
        
    return res

# be/manager/point/assign/bokji/xlsx/download
@router.post("/manager/point/assign/bokji/xlsx/download", dependencies=[Depends(api_same_origin)])
async def 복지포인트지급내역_엑셀_다운로드(
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
        res = point_service.assign_list(request, excelLogInput.params, True)
        request.state.inspect = frame()

        output = BytesIO()

        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        
        cell_format1 = workbook.add_format()
        cell_format1.set_border(1)
        cell_format1.set_bold()

        # [ S ] 엑셀헤더
        worksheet.write("A1", "고유번호", cell_format1)
        worksheet.write("B1", "구분", cell_format1)
        worksheet.write("C1", "일자", cell_format1)
        worksheet.write("D1", "이름", cell_format1)
        worksheet.write("E1", "아이디", cell_format1)
        worksheet.write("F1", "부서", cell_format1)
        worksheet.write("G1", "직급/직책", cell_format1)
        worksheet.write("H1", "처리액", cell_format1)
        worksheet.write("I1", "지급/회수사유", cell_format1)
        worksheet.write("J1", "관리자메모", cell_format1)
        worksheet.write("K1", "소멸예정일", cell_format1)
        worksheet.write("L1", "처리자", cell_format1)
        # [ E ] 엑셀헤더
            
        idx = 2
        for c in res["list"] :
            position = c["position"]
            if c["position2"] != None and c["position2"] != '' :
                position = c["position"]+'/'+c["position2"]
            

            worksheet.write("A"+str(idx), c["uid"])
            worksheet.write("B"+str(idx), c["saved_type"])
            worksheet.write("C"+str(idx), c["create_at"])
            worksheet.write("D"+str(idx), c["user_name"])
            worksheet.write("E"+str(idx), c["user_id"])
            worksheet.write("F"+str(idx), c["depart"])
            worksheet.write("G"+str(idx), position)
            worksheet.write("H"+str(idx), c["saved_point"])
            worksheet.write("I"+str(idx), c["reason"])
            worksheet.write("J"+str(idx), c["admin_memo"])
            worksheet.write("K"+str(idx), c["expiration_date"])
            worksheet.write("L"+str(idx), c["admin_name"])
            idx = idx + 1

        worksheet.set_column('C:L', width=18, cell_format=None)

        workbook.close()
        output.seek(0)

        headers = {
            'Content-Disposition': 'attachment; filename="filename.xlsx"'
        }

        return StreamingResponse(output, headers=headers)
    
    
# be/manager/point/assign/sikwon/xlsx/download
@router.post("/manager/point/assign/sikwon/xlsx/download", dependencies=[Depends(api_same_origin)])
async def 식권포인트지급내역_엑셀_다운로드(
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
        res = point_service.assign_sikwon_list(request, excelLogInput.params, True)
        request.state.inspect = frame()

        output = BytesIO()

        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        
        cell_format1 = workbook.add_format()
        cell_format1.set_border(1)
        cell_format1.set_bold()

        # [ S ] 엑셀헤더
        worksheet.write("A1", "고유번호", cell_format1)
        worksheet.write("B1", "구분", cell_format1)
        worksheet.write("C1", "일자", cell_format1)
        worksheet.write("D1", "이름", cell_format1)
        worksheet.write("E1", "아이디", cell_format1)
        worksheet.write("F1", "부서", cell_format1)
        worksheet.write("G1", "직급/직책", cell_format1)
        worksheet.write("H1", "처리액", cell_format1)
        worksheet.write("I1", "지급/회수사유", cell_format1)
        worksheet.write("J1", "관리자메모", cell_format1)
        worksheet.write("K1", "소멸예정일", cell_format1)
        worksheet.write("L1", "처리자", cell_format1)
        # [ E ] 엑셀헤더
            
        idx = 2
        for c in res["list"] :
            position = c["position"]
            if c["position2"] != None and c["position2"] != '' :
                position = c["position"]+'/'+c["position2"]
            

            worksheet.write("A"+str(idx), c["uid"])
            worksheet.write("B"+str(idx), c["saved_type"])
            worksheet.write("C"+str(idx), c["create_at"])
            worksheet.write("D"+str(idx), c["user_name"])
            worksheet.write("E"+str(idx), c["user_id"])
            worksheet.write("F"+str(idx), c["depart"])
            worksheet.write("G"+str(idx), position)
            worksheet.write("H"+str(idx), c["saved_point"])
            worksheet.write("I"+str(idx), c["reason"])
            worksheet.write("J"+str(idx), c["admin_memo"])
            worksheet.write("K"+str(idx), c["expiration_date"])
            worksheet.write("L"+str(idx), c["admin_name"])
            idx = idx + 1

        worksheet.set_column('C:L', width=18, cell_format=None)

        workbook.close()
        output.seek(0)

        headers = {
            'Content-Disposition': 'attachment; filename="filename.xlsx"'
        }

        return StreamingResponse(output, headers=headers)