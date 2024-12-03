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
from app.service.manager.point.sikwon import used_service
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

# ------------------------- [ S ] 식권카드 사용내역 -------------------------
# @@@@@@@사용안함########################################################################################################
def 식권카드사용_필터조건 (request: Request):
    request.state.inspect = frame()

    result = {}
    result.update({"skeyword_type": [
        {"key": 'a', "text": '이름'},
        {"key": 'a', "text": '생년월일'},
        {"key": 'a', "text": '부서'},
    ]})
 
    # 처리상태
    result.update({"state": [
        {"key": '', "text": '전체'},
        {"key": '차감완료', "text": '차감완료'},
        {"key": '차감취소', "text": '차감취소'},
    ]})

    return result

# @@@@@@@사용안함########################################################################################################
# /be/manager/point/used/sikwon/init
@router.post("/manager/point/used/sikwon/init", dependencies=[Depends(api_same_origin)])
async def 식권카드사용_내역_init (
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
            "state": '',
        }
    }
    result.update({"params": params})
    # [ S ] 초기 파라메터

    result.update({"filter": 식권카드사용_필터조건(request)}) # 초기 필터

    return result

# @@@@@@@사용안함########################################################################################################
# /be/manager/point/used/sikwon/list
@router.post("/manager/point/used/sikwon/list", dependencies=[Depends(api_same_origin)])
async def 식권카드사용_내역 (
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

    # res = used_service.used_list(request, pPage_param)
    # request.state.inspect = frame()
        
    res = {}
    res.update({"params": pPage_param})
    res.update({"list": [
        {
             "이름": "홍길동"
            ,"생년월일": "1998-01-01"
            ,"부서": "개발팀"
            ,"직급": "사원"
            ,"소명신청일": "2024-01-11"
            ,"포인트차감승인일": "2024-01-13"
            ,"사용내역": "후라토식당"
            ,"포인트차감금액": 16000
            ,"카드": "신한카드"
            ,"처리상태": "차감완료"
            ,"비고": "소명승인완료"
        },
        {
             "이름": "김철수"
            ,"생년월일": "1994-01-14"
            ,"부서": "개발팀"
            ,"직급": "사원"
            ,"소명신청일": "2024-01-11"
            ,"포인트차감승인일": "2024-01-13"
            ,"사용내역": "후라토식당"
            ,"포인트차감금액": 16000
            ,"카드": "신한카드"
            ,"처리상태": "차감완료"
            ,"비고": "소명승인완료"
        }
    ]})

    return res
# ------------------------- [ E ] 식권카드 사용내역 -------------------------










# ------------------------- [ S ] 식권포인트 사용내역 -------------------------
def 식권포인트사용_필터조건 (request: Request):
    request.state.inspect = frame()

    result = {}
    result.update({"skeyword_type": [
        {"key": 'user_name', "text": '이름'},
        {"key": 'user_id', "text": '아이디'},
        {"key": 'order_no', "text": '주문번호'},
    ]})
 
    result.update({"used_type": [
        {"key": '', "text": '전체'},
        {"key": '1', "text": '결제완료'},
        {"key": '2', "text": '환불/취소'},
        {"key": '3', "text": '차감'},
    ]})

    return result

# /be/manager/point/used/sikwon_point/init
@router.post("/manager/point/used/sikwon_point/init", dependencies=[Depends(api_same_origin)])
async def 식권포인트사용_내역_init (
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
            "used_type": '',
        }
    }
    result.update({"params": params})
    # [ S ] 초기 파라메터

    result.update({"filter": 식권포인트사용_필터조건(request)}) # 초기 필터

    return result

# /be/manager/point/used/sikwon_point/list
@router.post("/manager/point/used/sikwon_point/list", dependencies=[Depends(api_same_origin)])
async def 식권포인트사용_내역 (
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

    res = used_service.sikwon_point_list(request, pPage_param)
    request.state.inspect = frame()
    
    return res


# ------------------------- [ E ] 식권포인트 사용내역 -------------------------

# be/manager/point/used/sikwon_point/xlsx/download
@router.post("/manager/point/used/sikwon_point/xlsx/download", dependencies=[Depends(api_same_origin)])
async def 식권포인트사용내역_엑셀_다운로드(
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
        res = used_service.sikwon_point_list(request, excelLogInput.params, True)
        request.state.inspect = frame()

        output = BytesIO()

        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        
        cell_format1 = workbook.add_format()
        cell_format1.set_border(1)
        cell_format1.set_bold()

        # [ S ] 엑셀헤더
        worksheet.write("A1", "고유번호", cell_format1)
        worksheet.write("B1", "주문일자", cell_format1)
        worksheet.write("C1", "결제상태", cell_format1)
        worksheet.write("D1", "사유", cell_format1)
        worksheet.write("E1", "이름", cell_format1)
        worksheet.write("F1", "아이디", cell_format1)
        worksheet.write("G1", "주문번호", cell_format1)
        worksheet.write("H1", "사용포인트", cell_format1)
        worksheet.write("I1", "환불포인트", cell_format1)
        # [ E ] 엑셀헤더
            
        idx = 2
        for c in res["list"] :
            worksheet.write("A"+str(idx), c["uid"])
            worksheet.write("B"+str(idx), c["create_at"])
            worksheet.write("C"+str(idx), c["used_type"])
            worksheet.write("D"+str(idx), c["reason"])
            worksheet.write("E"+str(idx), c["user_name"])
            worksheet.write("F"+str(idx), c["user_id"])
            worksheet.write("G"+str(idx), c["order_no"])
            worksheet.write("H"+str(idx), c["used_point"])
            worksheet.write("I"+str(idx), c["remaining_point"])
            idx = idx + 1

        worksheet.set_column('B:I', width=18, cell_format=None)

        workbook.close()
        output.seek(0)

        headers = {
            'Content-Disposition': 'attachment; filename="filename.xlsx"'
        }

        return StreamingResponse(output, headers=headers)