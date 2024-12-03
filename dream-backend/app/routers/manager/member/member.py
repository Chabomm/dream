from fastapi import APIRouter, Depends, Request, Body
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from inspect import currentframe as frame
from fastapi.responses import RedirectResponse, JSONResponse, StreamingResponse
from app.core import exceptions as ex
from app.core import util
from app.core.config import PROXY_PREFIX, api_same_origin
from app.core.database import get_session
from app.deps.auth import create_access_token, get_current_active_manager, get_current_user
from app.deps.auth import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES
from fastapi.encoders import jsonable_encoder
from pydantic.tools import parse_obj_as

from app.schemas.schema import *
from app.schemas.manager.member import *
from app.schemas.manager.auth import *
from app.service.manager.member import member_service
from app.service import log_service


router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/manager/member"],
)

def 고객사회원_필터조건 (request: Request):
    request.state.inspect = frame()

    result = {}
    result.update({"skeyword_type": [
        {"key": 'user_name', "text": '이름'},
        {"key": 'login_id', "text": '아이디'},
        {"key": 'depart', "text": '부서'},
        {"key": 'position', "text": '직급'},
        {"key": 'position2', "text": '직책'}
    ]})

    result.update({"birth_type": [
        {"key": '01', "text": '1월'},
        {"key": '02', "text": '2월'},
        {"key": '03', "text": '3월'},
        {"key": '04', "text": '4월'},
        {"key": '05', "text": '5월'},
        {"key": '06', "text": '6월'},
        {"key": '07', "text": '7월'},
        {"key": '08', "text": '8월'},
        {"key": '09', "text": '9월'},
        {"key": '10', "text": '10월'},
        {"key": '11', "text": '11월'},
        {"key": '12', "text": '12월'},
    ]})

    # serve type list (재직상태)
    result.update({"serve_type": [
        {"key": '재직', "text": '재직'},
        {"key": '휴직', "text": '휴직'},
        {"key": '퇴직', "text": '퇴직'},
    ]})
    return result

# /be/manager/member/init
@router.post("/manager/member/init", dependencies=[Depends(api_same_origin)])
async def 고객사회원_내역_init (
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
            "birth_type" : "",
            "serve_type" : []
        }
    }
    result.update({"params": params})
    # [ S ] 초기 파라메터

    result.update({"filter": 고객사회원_필터조건(request)}) # 초기 필터

    return result

# be/manager/member/list
@router.post("/manager/member/list", dependencies=[Depends(api_same_origin)])
async def 고객사회원_내역(
     request: Request
    ,page_param: PPage_param
    ,user: TokenDataManager = Depends(get_current_active_manager)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)

    if not page_param.page or int(page_param.page) == 0:
        page_param.page = 1

    if not page_param.page_view_size or int(page_param.page_view_size) == 0:
        page_param.page_view_size = 30

    res = member_service.member_list(request, page_param)
    request.state.inspect = frame()

    return res

# be/manager/member/read
@router.post("/manager/member/read", dependencies=[Depends(api_same_origin)])
async def 고객사회원_상세(
      request: Request
     ,pRead: PRead
     ,user: TokenDataManager = Depends(get_current_active_manager)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)

    if pRead.uid == 0 :
        res = {}
        values = jsonable_encoder(MemberInput()) 
    
    else :
        res = member_service.member_read(request, pRead.uid)
        request.state.inspect = frame()
        if res is None:
            return ex.ReturnOK(404, "정보를 찾을 수 없습니다. 다시 확인 후 시도해주세요", request)
        values = jsonable_encoder(parse_obj_as(MemberInput, res))


    values["roles"] = []

    jsondata = {}
    jsondata.update(res)
    jsondata.update({"values": values})
    # jsondata.update({"filter": 고객사_관리자_역할_필터조건(request)})
    # request.state.inspect = frame()
    return ex.ReturnOK(200, "", request, jsondata)

    return res


# be/manager/member/edit
@router.post("/manager/member/edit", dependencies=[Depends(api_same_origin)])
async def 고객사회원_편집(
    request: Request
    ,memberInput: MemberInput = Body(
        ...,
        examples={
            "example01": {
                "summary": "임직원 등록하기 예시1",
                "description": "",
                "value": {
                     "login_id" : "test_user1"
                    ,"user_id" : "ind_test_user1"
                    ,"prefix" : "ind_"
                    ,"user_name" : "가나다"
                    ,"mobile" : "010-1234-5678"
                    ,"email" : "test_user1@indend.co.kr"
                    ,"serve" : "휴직"
                    ,"birth" : "1999-06-19"
                    ,"gender" : "여자"
                    ,"anniversary" : "adf"
                    ,"emp_no" : "1234"
                    ,"depart" : "경영지원팀"
                    ,"position" : "사원"
                    ,"position2" : "사원"
                    ,"join_com" : "2023-06-19"
                    ,"post" : "05237"
                    ,"addr" : "서울 강동구 아리수로 46 (암사동)"
                    ,"addr_detail" : "1층"
                    ,"tel" : "010-1234-5678"
                    ,"affiliate" : ""
                    ,"state" : "100"
                    ,"is_login" : "T"
                    ,"is_point" : "T"
                    ,"mode": "REG"
                },
            },
            "example02": {
                "summary": "임직원 수정하기 예시1",
                "description": "",
                "value": {
                     "uid" : 5
                    ,"user_name" : "가나다수정"
                    ,"birth" : "1999-07-19"
                    ,"mode": "MOD"
                },
            },
            "example03": {
                "summary": "임직원 삭제하기 예시1",
                "description": "",
                "value": {
                     "uid" : 5
                    ,"mode": "DEL"
                },
            }
        }
    )
     ,user: TokenDataManager = Depends(get_current_active_manager)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)

    # 등록
    if memberInput.mode == "REG" :
        res = member_service.member_create(request, memberInput)
        request.state.inspect = frame()
        return ex.ReturnOK(200, "등록이 완료되었습니다. 새로고침 해주세요", request, {"uid" : res.uid})

    # 수정
    if memberInput.mode == "MOD" :
        res = member_service.member_update(request, memberInput)
        request.state.inspect = frame()
        return ex.ReturnOK(200, "수정이 완료되었습니다. 새로고침 해주세요", request, {"uid" : res.uid})
    
    # 삭제
    if memberInput.mode == "DEL" :
        member_service.member_delete(request, memberInput.uid)
        request.state.inspect = frame()
        return ex.ReturnOK(200, "삭제 완료", request)

# be/manager/member/check
@router.post("/manager/member/check", dependencies=[Depends(api_same_origin)])
async def 고객사회원_아이디_중복체크(
    request:Request
    ,ChkMemberIdSchema: ChkMemberIdSchema = Body(
        ...,
        examples = {
            "example01" : {
                "summary": "임직원 아이디 중복체크",
                "description": "",
                "value": {
                     "memberid_input_value" : "aaasssddd"
                    ,"memberid_check_value" : ""
                    ,"is_memberid_checked" : "false"
                    ,"prefix" : "ind_"
                }
            }
        }
    ), user: TokenDataManager = Depends(get_current_active_manager)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)

    print(ChkMemberIdSchema, user)

    res = member_service.check_member_id(request, ChkMemberIdSchema)
    request.state.inspect = frame()

    if res is None:
        return ex.ReturnOK(404, "정보를 찾을 수 없습니다. 다시 확인 후 시도해주세요", request)
    
    if res == 0:
        return ex.ReturnOK(200, "사용가능한 아이디입니다.", request)
    else:
        return ex.ReturnOK(300, "이미 사용중인 아이디입니다.", request)
    
    

import pandas as pd
from io import BytesIO # Add to Top of File
import xlsxwriter
import os
from fastapi.datastructures import UploadFile
from fastapi.param_functions import File, Form
import json
# 엑셀 스타일 => https://xlsxwriter.readthedocs.io/format.html#creating-and-using-a-format-object
# be/manager/member/excel/sample/download
@router.post("/manager/member/excel/sample/download", dependencies=[Depends(api_same_origin)])
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

    # [ S ] 헤더 색상변경
    cell_format1 = workbook.add_format()
    cell_format1.set_border(1)
    cell_format1.set_font_color('red')
    cell_format2 = workbook.add_format() # 테두리
    cell_format2.set_border(1)
    cell_format3 = workbook.add_format() # 테두리
    cell_format3.set_font_color('#aaaaaa')
    cell_format3.set_italic()
    # [ E ] 헤더 색상변경 

    # wb = openpyxl.load_workbook(output)
    # ws = wb.active
    # header_row = ws[1]

    # print('header_row',header_row)

    # # 머리글의 모든 셀을 반복
    # for cell in header_row:
    #     cell.fill = openpyxl.styles.PatternFill(start_color="00B0F0", end_color="00B0F0", patternType="solid")

    # [ S ] 엑셀헤더
    if user.partner_id == 'indend' :
        worksheet.write("A1", "아이디", cell_format1)
        worksheet.write("B1", "이름", cell_format1)
        worksheet.write("C1", "성별", cell_format1)
        worksheet.write("D1", "재직여부", cell_format1)
        worksheet.write("E1", "복지몰로그인", cell_format1)
        worksheet.write("F1", "포인트사용", cell_format1)
        worksheet.write("G1", "휴대전화", cell_format1)
        worksheet.write("H1", "이메일", cell_format1)
        worksheet.write("I1", "우편번호", cell_format2)
        worksheet.write("J1", "주소", cell_format2)
        worksheet.write("K1", "주소상세", cell_format2)
        worksheet.write("L1", "생년월일", cell_format1)
        worksheet.write("M1", "기념일", cell_format2)
        worksheet.write("N1", "사번", cell_format2)
        worksheet.write("O1", "부서", cell_format2)
        worksheet.write("P1", "직급", cell_format2)
        worksheet.write("Q1", "직책", cell_format2)
        worksheet.write("R1", "입사일", cell_format2)

        worksheet.write("A2", "예시)아이디", cell_format3)
        worksheet.write("B2", "예시)이름", cell_format3)
        worksheet.write("C2", "예시)여자", cell_format3)
        worksheet.write("D2", "예시)재직", cell_format3)
        worksheet.write("E2", "예시)가능", cell_format3)
        worksheet.write("F2", "예시)가능", cell_format3)
        worksheet.write("G2", "예시)010-1234-1234", cell_format3)
        worksheet.write("H2", "예시)email@naver.com", cell_format3)
        worksheet.write("I2", "예시)12345", cell_format3)
        worksheet.write("J2", "예시)인천시연수구인천타워대로323", cell_format3)
        worksheet.write("K2", "예시)B동2105호", cell_format3)
        worksheet.write("L2", "예시)2024-02-20", cell_format3)
        worksheet.write("M2", "예시)2024-02-20", cell_format3)
        worksheet.write("N2", "예시)12345", cell_format3)
        worksheet.write("O2", "예시)개발", cell_format3)
        worksheet.write("P2", "예시)사원", cell_format3)
        worksheet.write("Q2", "예시)직책", cell_format3)
        worksheet.write("R2", "예시)2024-02-20", cell_format3)
    else :
        worksheet.write("A1", "샘플리스트")
    # [ E ] 엑셀헤더
    

    worksheet.set_column('A2:R2', width=18, cell_format=None)

    workbook.close()
    output.seek(0)

    headers = {
        'Content-Disposition': 'attachment; filename="filename.xlsx"'
    }

    return StreamingResponse(output, headers=headers)
    
    
# be/manager/member/xlsx/download
@router.post("/manager/member/xlsx/download", dependencies=[Depends(api_same_origin)])
async def 임직원목록_엑셀_다운로드(
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
        res = member_service.member_list(request, excelLogInput.params, True)
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
        worksheet.write("C1", "부서", cell_format1)
        worksheet.write("D1", "직급", cell_format1)
        worksheet.write("E1", "아이디", cell_format1)
        worksheet.write("F1", "연락처", cell_format1)
        worksheet.write("G1", "생년월일", cell_format1)
        worksheet.write("H1", "회원등록일", cell_format1)
        # [ E ] 엑셀헤더
            
        idx = 2
        for c in res["list"] :
            worksheet.write("A"+str(idx), c["uid"])
            worksheet.write("B"+str(idx), c["user_name"])
            worksheet.write("C"+str(idx), c["depart"])
            worksheet.write("D"+str(idx), c["position"])
            worksheet.write("E"+str(idx), c["login_id"])
            worksheet.write("F"+str(idx), c["mobile"])
            worksheet.write("G"+str(idx), c["birth"])
            worksheet.write("H"+str(idx), c["create_at"])
            idx = idx + 1

        worksheet.set_column('C:H', width=18, cell_format=None)

        workbook.close()
        output.seek(0)

        headers = {
            'Content-Disposition': 'attachment; filename="filename.xlsx"'
        }

        return StreamingResponse(output, headers=headers)
    
# /be/manager/member/excel/files/upload
@router.post("/manager/member/excel/files/upload")
async def 임직원대량등록_엑셀_파일업로드_read (
    request : Request,
    file_object: UploadFile = File(...),
    upload_path: str = Form(...)
):
    request.state.inspect = frame()
    fake_name = file_object.filename
    split_file_name = os.path.splitext(fake_name)
    file_ext = split_file_name[1]

    data = file_object.file._file  # Converting tempfile.SpooledTemporaryFile to io.BytesIO

    if upload_path != "" and upload_path[0:1] == "/" :
        upload_path = upload_path[1:len(upload_path)] # 첫 글자에 / 빼기
    
    if upload_path != "" and upload_path[len(upload_path)-1:len(upload_path)] != "/" :
        upload_path = upload_path + "/" # 마지막 글자에 / 없으면 넣기

    try :
        df = pd.read_excel(data, engine='openpyxl', dtype={'생년월일':str, '입사일': str}) #dtype == type 정해주기
        
        excel_json = df.to_json(force_ascii=False, orient = 'records', indent=4)

        # [ S ] 예시 행 제외
        excel_json = json.loads(excel_json)
        upload_excel = []
        for c in excel_json :
            if '예시)' not in str(c) :
                upload_excel.append(c)
        # [ E ] 예시 행 제외

        result_msg = ""

        rows = []
        for row in upload_excel :
            row["검증"] = "대기"
            if row["아이디"] == None or row["아이디"] == "" :
                row["검증"] = "필수값 누락"
                result_msg = "필수값 누락. (아이디)"
            if row["이름"] == None or row["이름"] == "" :
                row["검증"] = "필수값 누락"
                result_msg = "필수값 누락. (이름)"
            if row["성별"] == None or row["성별"] == "" :
                row["검증"] = "필수값 누락"
                result_msg = "필수값 누락. (성별)"
            if row["재직여부"] == None or row["재직여부"] == "" :
                row["검증"] = "필수값 누락"
                result_msg = "필수값 누락. (재직여부)"
            if row["복지몰로그인"] == None or row["복지몰로그인"] == "" :
                row["검증"] = "필수값 누락"
                result_msg = "필수값 누락. (복지몰로그인)"
            if row["포인트사용"] == None or row["포인트사용"] == "" :
                row["검증"] = "필수값 누락"
                result_msg = "필수값 누락. (포인트사용)"
            if row["휴대전화"] == None or row["휴대전화"] == "" :
                row["검증"] = "필수값 누락"
                result_msg = "필수값 누락. (휴대전화)"
            if row["이메일"] == None or row["이메일"] == "" :
                row["검증"] = "필수값 누락"
                result_msg = "필수값 누락. (이메일)"
            if row["생년월일"] == None or row["생년월일"] == "" :
                row["검증"] = "필수값 누락"
                result_msg = "필수값 누락. (생년월일)"
                
            rows.append(row)
    except Exception as e:
        result_msg = "엑셀파일이 올바르지 않습니다. 샘플엑셀파일로 다시 업로드 해주세요. 문제 지속시 관라자에게 문의바랍니다."

    if len(rows) <= 0 :
        result_msg = "엑셀파일의 정보가 없습니다. 확인 후 다시 업로드 해주세요. 문제 지속시 관리자에게 문의바랍니다."



    return ex.ReturnOK(200 if result_msg == "" else 301, result_msg, request, {
        "upload_excel" : rows
        ,"fail": 0
        ,"success": 0
        ,"fail_list": []
    })


# be/manager/member/excel/upload/create
@router.post("/manager/member/excel/upload/create", dependencies=[Depends(api_same_origin)])
async def 엑셀파일_임직원_대량등록(
     request: Request
    ,excelJson:ExcelJson
    ,user: TokenDataManager = Depends(get_current_active_manager)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)

    success = excelJson.success
    fail = excelJson.fail

    # [ S ] 중복검사
    res = member_service.excel_create_before_member_read(request, excelJson.post['아이디']) 
    request.state.inspect = frame()

    if res != None:
        fail = fail + 1
        return ex.ReturnOK(500, "중복된 회원", request, {
             "fail": fail
            ,"success": success
            ,"fail_list": excelJson.post
            ,"post": excelJson.post
        })

    member = member_service.bulk_member_create(request, excelJson.post)
    request.state.inspect = frame()

    if member != None :
        success = success+1
        return ex.ReturnOK(200, "성공", request, {
            "fail": fail
            ,"success": success
            ,"fail_list": []
            ,"post": excelJson.post
        })
    # [ E ]


# be/manager/member/excel/bulk/fail
@router.post("/manager/member/excel/bulk/fail", dependencies=[Depends(api_same_origin)])
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
        cell_format_dict1 = {
            'font_color':'red',
        }
        cell_format1 = workbook.add_format(cell_format_dict1)
        cell_format1.set_border(1)
        cell_format2 = workbook.add_format() # 테두리
        cell_format2.set_border(1)
        # [ E ] 헤더 색상변경 
        
        # [ S ] 엑셀헤더
        worksheet.write("A1", "아이디", cell_format1)
        worksheet.write("B1", "이름", cell_format1)
        worksheet.write("C1", "성별", cell_format1)
        worksheet.write("D1", "재직여부", cell_format1)
        worksheet.write("E1", "복지몰로그인", cell_format1)
        worksheet.write("F1", "포인트사용", cell_format1)
        worksheet.write("G1", "휴대전화", cell_format1)
        worksheet.write("H1", "이메일", cell_format1)
        worksheet.write("I1", "우편번호", cell_format2)
        worksheet.write("J1", "주소", cell_format2)
        worksheet.write("K1", "주소상세", cell_format2)
        worksheet.write("L1", "생년월일", cell_format1)
        worksheet.write("M1", "기념일", cell_format2)
        worksheet.write("N1", "사번", cell_format2)
        worksheet.write("O1", "부서", cell_format2)
        worksheet.write("P1", "직급", cell_format2)
        worksheet.write("Q1", "직책", cell_format2)
        worksheet.write("R1", "입사일", cell_format2)
        # [ E ] 엑셀헤더
            
        idx = 2
        for c in excelLogInput.fail_list :
            worksheet.write("A"+str(idx), c["아이디"])
            worksheet.write("B"+str(idx), c["이름"])
            worksheet.write("C"+str(idx), c["성별"])
            worksheet.write("D"+str(idx), c["재직여부"])
            worksheet.write("E"+str(idx), c["복지몰로그인"])
            worksheet.write("F"+str(idx), c["포인트사용"])
            worksheet.write("G"+str(idx), c["휴대전화"])
            worksheet.write("H"+str(idx), c["이메일"])
            worksheet.write("I"+str(idx), c["우편번호"])
            worksheet.write("J"+str(idx), c["주소"])
            worksheet.write("K"+str(idx), c["주소상세"])
            worksheet.write("L"+str(idx), c["생년월일"])
            worksheet.write("M"+str(idx), c["기념일"])
            worksheet.write("N"+str(idx), c["사번"])
            worksheet.write("O"+str(idx), c["부서"])
            worksheet.write("P"+str(idx), c["직급"])
            worksheet.write("Q"+str(idx), c["직책"])
            worksheet.write("R"+str(idx), c["입사일"])
            idx = idx + 1

        worksheet.set_column('C:H', width=18, cell_format=None)

        workbook.close()
        output.seek(0)

        headers = {
            'Content-Disposition': 'attachment; filename="filename.xlsx"'
        }

        return StreamingResponse(output, headers=headers)
    