from decimal import *
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
from fastapi.encoders import jsonable_encoder
from pydantic.tools import parse_obj_as

from app.schemas.schema import *
from app.schemas.manager.point.assign.single import *
from app.schemas.manager.auth import *
from app.service.manager.point.sikwon import single_service
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

def 개별_식권_포인트지급_필터조건 (request: Request):
    request.state.inspect = frame()

    result = {}
    result.update({"skeyword_type": [
        {"key": 'M.user_name', "text": '이름'},
        {"key": 'M.login_id', "text": '아이디'},
        {"key": 'MI.depart', "text": '부서'},
        {"key": 'MI.position', "text": '직급/직책'},
    ]})

    # 포인트 사용상태
    result.update({"is_point": [
        {"key": '', "text": '전체', "checked": True},
        {"key": 'T', "text": '가능', "checked": True},
        {"key": 'F', "text": '불가능', "checked": True},
    ]})

    # 재직여부
    result.update({"serve": [
        {"key": '', "text": '전체', "checked": True},
        {"key": '재직', "text": '재직', "checked": True},
        {"key": '휴직', "text": '휴직', "checked": True},
        {"key": '퇴직', "text": '퇴직', "checked": True},
    ]})

    return result

# /be/manager/point/assign/sikwon/single/init
@router.post("/manager/point/assign/sikwon/single/init", dependencies=[Depends(api_same_origin)])
async def 개별_식권_포인트지급내역_init (
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
            "is_point": '',
            "serve": '',
            "checked": []
        }
    }
    result.update({"params": params})
    # [ S ] 초기 파라메터

    result.update({"filter": 개별_식권_포인트지급_필터조건(request)}) # 초기 필터

    return result

# /be/manager/point/assign/sikwon/single/list
@router.post("/manager/point/assign/sikwon/single/list", dependencies=[Depends(api_same_origin)])
async def 개별_식권_포인트_지급내역 (
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

    res = single_service.sikwon_single_list(request, pPage_param)
    request.state.inspect = frame()

    return res

# /be/manager/point/assign/sikwon/single/read
@router.post("/manager/point/assign/sikwon/single/read", dependencies=[Depends(api_same_origin)])
async def 개별_식권_포인트_지급내역_상세(
     request: Request
    ,assignSingleRead: AssignSingleRead
    ,user: TokenDataManager = Depends(get_current_active_manager)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)

    if assignSingleRead.user_uids == "" :
        return ex.ReturnOK(401, "선택된 회원이 없습니다.", request)

    res = single_service.sikwon_single_select_user_list(request, assignSingleRead)
    request.state.inspect = frame()

    if res is None :
        return ex.ReturnOK(402, "회원정보를 불러오는데 실패하였습니다.", request)
    
    values = jsonable_encoder(parse_obj_as(AssignSingleInput, {
        "user_uids": assignSingleRead.user_uids.split(",")
    }))

    jsondata = {}
    jsondata.update({"values": values})
    jsondata.update(res)
    request.state.inspect = frame()

    return ex.ReturnOK(200, "", request, jsondata)

# /be/manager/point/assign/sikwon/single/edit
@router.post("/manager/point/assign/sikwon/single/edit", dependencies=[Depends(api_same_origin)])
async def 개별_식권_포인트_지급_회수_등록(
     request: Request
    ,assignSingleInput: AssignSingleInput
    ,user: TokenDataManager = Depends(get_current_active_manager)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)


    if assignSingleInput.save_type == "2" or assignSingleInput.save_type == "1" : # 개별지급

        # session의 partner가 가지고 있는 현재 예치금 가져오기
        partner_point = balance_service.balance_read_partner_id(request, user.partner_uid)

        if util.checkNumeric(assignSingleInput.saved_point)*(len(assignSingleInput.user_uids)) > util.checkNumeric(partner_point.spare_point) :
            return ex.ReturnOK(300, "보유 예치금이 부족합니다.", request, {})
        
        res = single_service.single_sikwon_create(request, assignSingleInput)
        request.state.inspect = frame()
        if res is None :
            return ex.ReturnOK(500, "식권포인트 개별 지급에 실패했습니다.", request)
            
        return ex.ReturnOK(200, "식권포인트 개별 지급이 완료되었습니다.", request, {})
    
    elif assignSingleInput.save_type == "3" : # 개별회수

        point_sum = single_service.member_sikwon_point_list(request, assignSingleInput)
        request.state.inspect = frame()

        reject_mem_uids = []
        for res in point_sum["list"] :
            if util.checkNumeric(res["spare_point"]) < util.checkNumeric(assignSingleInput.saved_point) :
                reject_mem_uids.append(res["uid"])
        if len(reject_mem_uids) > 0 :
            return ex.ReturnOK(
                 500
                ,"회수할 포인트가 부족한 회원이 존재합니다. 아래 선택된 회원정보 테이블을 참고하주세요"
                ,request
                ,{"list":reject_mem_uids}
            )
    
        if util.checkNumeric(res["spare_point"]) >= util.checkNumeric(assignSingleInput.saved_point) :
            # 회수할 포인트 금액이 충족되면 회수
            res = single_service.single_sikwon_point_return(request, assignSingleInput)
            request.state.inspect = frame()
            if res is None :
                return ex.ReturnOK(500, "포인트 개별 회수에 실패했습니다.", request)
        
        return ex.ReturnOK(200, "포인트 개별 회수가 완료되었습니다.", request, {})


# be/manager/point/assign/sikwon/single/xlsx/download
@router.post("/manager/point/assign/sikwon/single/xlsx/download", dependencies=[Depends(api_same_origin)])
async def 식권포인트개별지급내역_엑셀_다운로드(
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
        res = single_service.sikwon_single_list(request, excelLogInput.params, True)
        request.state.inspect = frame()

        output = BytesIO()

        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        
        cell_format1 = workbook.add_format()
        cell_format1.set_border(1)
        cell_format1.set_bold()

        # [ S ] 엑셀헤더
        worksheet.write("A1", "이름", cell_format1)
        worksheet.write("B1", "아이디", cell_format1)
        worksheet.write("C1", "부서", cell_format1)
        worksheet.write("D1", "직급/직책", cell_format1)
        worksheet.write("E1", "지급완료포인트", cell_format1)
        worksheet.write("F1", "회수완료포인트", cell_format1)
        worksheet.write("G1", "사용완료포인트", cell_format1)
        worksheet.write("H1", "잔여포인트", cell_format1)
        worksheet.write("I1", "포인트사용상태", cell_format1)
        worksheet.write("J1", "재직여부", cell_format1)
        # [ E ] 엑셀헤더
            
        idx = 2
        for c in res["list"] :
            
            position = c["position"]
            if c["position2"] != None and c["position2"] != '' :
                position = c["position"]+'/'+c["position2"]
            worksheet.write("A"+str(idx), c["user_name"])
            worksheet.write("B"+str(idx), c["login_id"])
            worksheet.write("C"+str(idx), c["depart"])
            worksheet.write("D"+str(idx), position)
            worksheet.write("E"+str(idx), c["saved_point"])
            worksheet.write("F"+str(idx), c["return_point"])
            worksheet.write("G"+str(idx), c["used_point"])
            worksheet.write("H"+str(idx), c["spare_point"])
            worksheet.write("I"+str(idx), c["is_point"])
            worksheet.write("J"+str(idx), c["serve"])
            idx = idx + 1

        worksheet.set_column('B:J', width=18, cell_format=None)

        workbook.close()
        output.seek(0)

        headers = {
            'Content-Disposition': 'attachment; filename="filename.xlsx"'
        }

        return StreamingResponse(output, headers=headers)