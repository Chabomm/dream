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
from app.schemas.manager.point.assign.single import *
from app.schemas.manager.auth import *

from app.service.manager.member import member_service
from app.routers.manager.point.assign import single as group_single
from app.service import log_service
from app.routers.manager.point.assign.sikwon import single as sikwon_single

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/manager/point"],
)


import pandas as pd
from io import BytesIO # Add to Top of File
import xlsxwriter
import os
from fastapi.datastructures import UploadFile
from fastapi.param_functions import File, Form
import json
# 엑셀 스타일 => https://xlsxwriter.readthedocs.io/format.html#creating-and-using-a-format-object
# be/manager/point/assign/group/excel/sample/download
@router.post("/manager/point/assign/group/excel/sample/download", dependencies=[Depends(api_same_origin)])
async def 샘플_엑셀_다운로드(
     request: Request
    ,user: TokenDataManager = Depends(get_current_active_manager)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)

    output = BytesIO()

    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    member_list = member_service.member_list_info(request)
    request.state.inspect = frame()

    # [ S ] 헤더 색상변경
    cell_format1 = workbook.add_format()
    cell_format1.set_border(1)
    cell_format1.set_bold()
    cell_format2 = workbook.add_format() # 테두리
    cell_format2.set_font_color('#aaaaaa')
    cell_format2.set_border(1)
    cell_format2.set_italic()
    cell_format3 = workbook.add_format() # 테두리
    cell_format3.set_border(1)
    cell_format3.set_align('left')
    # [ E ] 헤더 색상변경 

    # [ S ] 엑셀헤더
    worksheet.write("A1", "고유번호", cell_format1)
    worksheet.write("B1", "아이디", cell_format1)
    worksheet.write("C1", "이름", cell_format1)
    worksheet.write("D1", "적립금액", cell_format1)
    worksheet.write("E1", "포인트소멸일", cell_format1)
    worksheet.write("F1", "지급사유", cell_format1)
    worksheet.write("G1", "관리자기록용", cell_format1)

    worksheet.write("A2", "예시)*수정금지", cell_format2)
    worksheet.write("B2", "예시)*수정금지", cell_format2)
    worksheet.write("C2", "예시)*수정금지", cell_format2)
    worksheet.write("D2", "예시)숫자만 입력", cell_format2)
    worksheet.write("E2", "예시)yyyy-mm-dd, 없을 경우 공란", cell_format2)
    worksheet.write("F2", "예시)임직원에게 노출되는 지급 사유(최대 50자)", cell_format2)
    worksheet.write("G2", "예시)관리자에게만 노출(임직원에게는 노출되지 않습니다.)(최대 50자)", cell_format2)
    # [ E ] 엑셀헤더

    for idx, val in enumerate(member_list) :
        worksheet.write('A'+str(idx+3), val["uid"])
        worksheet.write('B'+str(idx+3), val["login_id"])
        worksheet.write('C'+str(idx+3), val["user_name"])
        
    worksheet.set_column('A2:G2', width=18, cell_format=cell_format3)

    workbook.close()
    output.seek(0)

    headers = {
        'Content-Disposition': 'attachment; filename="filename.xlsx"'
    }

    return StreamingResponse(output, headers=headers)
    

# /be/manager/point/assign/group/excel/files/upload
@router.post("/manager/point/assign/group/excel/files/upload")
async def 포인트지급_대량등록_엑셀_파일업로드 (
    request : Request
    ,file_object: UploadFile = File(...)
    ,upload_path: str = Form(...)
    ,user: TokenDataManager = Depends(get_current_active_manager)
):
    request.state.inspect = frame()
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)
    fake_name = file_object.filename
    split_file_name = os.path.splitext(fake_name)
    file_ext = split_file_name[1]

    data = file_object.file._file  # Converting tempfile.SpooledTemporaryFile to io.BytesIO

    if upload_path != "" and upload_path[0:1] == "/" :
        upload_path = upload_path[1:len(upload_path)] # 첫 글자에 / 빼기
    
    if upload_path != "" and upload_path[len(upload_path)-1:len(upload_path)] != "/" :
        upload_path = upload_path + "/" # 마지막 글자에 / 없으면 넣기

    rows = []
    try :
        df = pd.read_excel(data, engine='openpyxl', dtype={'포인트소멸일':str}) #dtype == type 정해주기
        
        excel_json = df.to_json(force_ascii=False, orient = 'records', indent=4)

        # [ S ] 예시 행 제외
        excel_json = json.loads(excel_json)
        upload_excel = []

        if len(excel_json) <= 0 :
            return ex.ReturnOK(401, "지급대상이 없습니다. 업로드 엑셀파일을 확인해주세요.", request)

        for c in excel_json :
            if '예시)' not in str(c) :
                upload_excel.append(c)
        
        # -----S
        member_list = member_service.member_list_info(request)
        request.state.inspect = frame()

        # print(set(member_list) == set(upload_excel))

        mem_uid = []
        for mem in member_list: 
            mem_uid.append(mem["uid"])
        # -----E
                

        result_msg = ""
        for row in upload_excel :
            if row["고유번호"] not in mem_uid :
                row["검증"] = "고유번호 확인"
                result_msg = "고유번호 올바르지 않습니다.\n샘플엑셀파일을 다시 다운로드 해주세요."
            if row["이름"] == None or row["이름"] == "" :
                row["검증"] = "필수값 누락"
                result_msg = "필수값 누락. (이름)"
            if row["아이디"] == None or row["아이디"] == "" :
                row["검증"] = "필수값 누락"
                result_msg = "필수값 누락. (아이디)"
            
            if util.checkNumeric(row["적립금액"]) == 0 :
                continue

            if row["지급사유"] == None or row["지급사유"] == "" :
                row["검증"] = "필수값 누락"
                result_msg = "필수값 누락. (지급사유)"
            
            # 날짜 검증 현재 nextjs에서 하고 하고 있는데 
            # 여기서 하게끔 변경해야함. 
            # 일단, yyyy-mm-dd 체크

            rows.append(row)
        # [ E ] 예시 행 제외
   
    except Exception as e:
        print(str(e))
        result_msg = "엑셀파일이 올바르지 않습니다. 샘플엑셀파일로 다시 업로드 해주세요. 문제 지속시 관라자에게 문의바랍니다."
    
    if len(rows) <= 0 :
        result_msg = "엑셀파일의 정보가 없습니다. 확인 후 다시 업로드 해주세요. 문제 지속시 관리자에게 문의바랍니다."
        
    return ex.ReturnOK(200 if result_msg == "" else 301, result_msg, request, {
        "upload_excel" : rows
        ,"fail": 0
        ,"success": 0
        ,"fail_list": []
    })

@router.post("/manager/point/assign/group/excel/upload/create", dependencies=[Depends(api_same_origin)])
async def 엑셀파일_포인트지급_대량등록(
     request: Request
    ,excelJson:ExcelJson
    ,user: TokenDataManager = Depends(get_current_active_manager)
):
    copy_deps_user = user # router Depends 때문에 따로 복사해둠

    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)

    success = excelJson.success
    fail = excelJson.fail

    if excelJson.post["포인트소멸일"] == "" :
        excelJson.post["포인트소멸일"] = None

    assignInput = AssignSingleInput(
        user_uids = [excelJson.post["고유번호"]],
        reason = excelJson.post["지급사유"],
        saved_point = excelJson.post["적립금액"],
        admin_memo = excelJson.post["관리자기록용"],
        expiration_date = excelJson.post["포인트소멸일"],
        is_exp_date = None,
        save_type = "1"
    )

    if excelJson.gubun == 'group':
        create_result = await group_single.개별_포인트_지급_회수_등록(
            request
            ,assignInput
            ,copy_deps_user
        )
    elif excelJson.gubun == 'sikwon':
        create_result = await sikwon_single.개별_식권_포인트_지급_회수_등록(
            request
            ,assignInput
            ,copy_deps_user
        )

    # [ S ] 중복검사
    if create_result == None:
        fail = fail + 1
        return ex.ReturnOK(500, "등록 실패", request, {
             "fail": fail
            ,"success": success
            ,"fail_list": excelJson.post
            ,"post": excelJson.post
        })
    else :
        if create_result["code"] != 200 :
            fail = fail + 1
            return ex.ReturnOK(create_result["code"], create_result["msg"], request, {
                "fail": fail
                ,"success": success
                ,"fail_list": excelJson.post
                ,"post": excelJson.post
            })
        else :
            success = success+1
            return ex.ReturnOK(200, "성공", request, {
                "fail": fail
                ,"success": success
                ,"fail_list": []
                ,"post": excelJson.post
            })
    # [ E ]
        
        
# be/manager/point/assign/group/excel/bulk/fail
@router.post("/manager/point/assign/group/excel/bulk/fail", dependencies=[Depends(api_same_origin)])
async def 임직원_대량등록_실패항목_엑셀_다운로드(
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
        output = BytesIO()

        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        # [ S ] 헤더 색상변경
        cell_format1 = workbook.add_format()
        cell_format1.set_border(1)
        cell_format1.set_bold()
        cell_format2 = workbook.add_format() # 테두리
        cell_format2.set_font_color('#aaaaaa')
        cell_format2.set_border(1)
        cell_format2.set_italic()
        cell_format3 = workbook.add_format() # 테두리
        cell_format3.set_border(1)
        cell_format3.set_align('left')
        # [ E ] 헤더 색상변경 
        
        # [ S ] 엑셀헤더
        worksheet.write("A1", "고유번호", cell_format1)
        worksheet.write("B1", "아이디", cell_format1)
        worksheet.write("C1", "이름", cell_format1)
        worksheet.write("D1", "적립금액", cell_format1)
        worksheet.write("E1", "포인트소멸일", cell_format1)
        worksheet.write("F1", "지급사유", cell_format1)
        worksheet.write("G1", "관리자기록용", cell_format1)

        worksheet.write("A2", "예시)*수정금지", cell_format2)
        worksheet.write("B2", "예시)*수정금지", cell_format2)
        worksheet.write("C2", "예시)*수정금지", cell_format2)
        worksheet.write("D2", "예시)숫자만 입력", cell_format2)
        worksheet.write("E2", "예시)yyyy-mm-dd, 없을 경우 공란", cell_format2)
        worksheet.write("F2", "예시)임직원에게 노출되는 지급 사유(최대 50자)", cell_format2)
        worksheet.write("G2", "예시)관리자에게만 노출(임직원에게는 노출되지 않습니다.)(최대 50자)", cell_format2)
        # [ E ] 엑셀헤더
            
        idx = 3
        for c in excelLogInput.fail_list :
            worksheet.write("A"+str(idx), c["고유번호"])
            worksheet.write("B"+str(idx), c["아이디"])
            worksheet.write("C"+str(idx), c["이름"])
            worksheet.write("D"+str(idx), c["적립금액"])
            worksheet.write("E"+str(idx), c["포인트소멸일"])
            worksheet.write("F"+str(idx), c["지급사유"])
            worksheet.write("G"+str(idx), c["관리자기록용"])
            idx = idx + 1

        worksheet.set_column('A:H', width=18, cell_format=cell_format3)

        workbook.close()
        output.seek(0)

        headers = {
            'Content-Disposition': 'attachment; filename="filename.xlsx"'
        }

        return StreamingResponse(output, headers=headers)
    