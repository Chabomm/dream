from fastapi import APIRouter, Depends, Request, Body
from inspect import currentframe as frame
import urllib
import json
import requests
import os, subprocess, re, base64, sys
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse, JSONResponse
from app.core import exceptions as ex
from app.core import util
from app.core.logger import api_logger
from app.core.config import PROXY_PREFIX, api_same_origin
from app.core.database import get_session
from app.deps.auth import create_access_token, get_current_active_front, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES
from urllib import parse

from app.schemas.schema import *
from app.schemas.nice import *
from app.service import nice_service
from app.service.front import member_service, partner_service
from app.routers.front import auth


router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["nice"],
)

log_path = "/usr/src/app/data/dream-backend/nice/"

# be/nice/checkplus
@router.post("/nice/checkplus", dependencies=[Depends(api_same_origin)])
async def checkplus(
     request: Request
    ,checkplusInput: CheckplusInput
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)

    logm = "[" + util.getNow() + "] " + str(checkplusInput)+ "\n"
    util.file_open (log_path, util.getNow("%Y-%m-%d") + ".log", logm)

    router.secret_key = os.urandom(24)

    # NICE평가정보에서 발급한 안심본인인증 서비스 개발정보 (사이트코드, 사이트패스워드)
    sitecode = '00000'   
    sitepasswd = '000000000000'

    # 안심본인인증 모듈의 절대경로 (권한:755, FTP업로드방식: 바이너리)
    # ex) cb_encode_path = 'C:\\module\\CPClient.exe'
    #     cb_encode_path = '/root/module/CPClient'
    # cb_encode_path = 'C://module//CPClient' 
    # print(os.getcwd())

    cb_encode_path = "./module/CPClient_linux_x64"

        
    if checkplusInput.client_id == "front" : # 복지몰이 보낼때
        if request.state.user_ip == "112.216.134.171" : # dev 서버
            returnurl = 'http://'+checkplusInput.partner_id+'.devindend.co.kr/front/mypage/offlinecard/nice/success.asp'
            errorurl = 'http://'+checkplusInput.partner_id+'.devindend.co.kr/front/mypage/offlinecard/nice/fail.asp'

        elif request.state.user_ip == "48." : # prod 서버
            returnurl = 'https://'+checkplusInput.partner_id+'.welfaredream.com/front/mypage/offlinecard/nice/success.asp'
            errorurl = 'https://'+checkplusInput.partner_id+'.welfaredream.com/front/mypage/offlinecard/nice/fail.asp'

        else : 
            return ex.ReturnOK(500, "허용되지 않는 요청입니다", request)

    else : 
        if os.environ['PROFILE'] == "development" :
            returnurl = 'http://localhost:10000/nice/success'  
            errorurl = 'http://localhost:10000/nice/fail'  
        else : 
            returnurl = 'https://app.dreamy.kr/nice/success'
            errorurl = 'https://app.dreamy.kr/nice/fail'

    # 팝업화면 설정
    authtype = '' # 인증타입 (공백(기본 선택화면) ,M(휴대폰), X(인증서공통), U(공동인증서), F(금융인증서), S(PASS인증서), C(신용카드))
    customize = '' # 화면타입 (공백:PC페이지, Mobile:모바일페이지)

    # 요청번호 초기화 
    # :세션에 저장해 사용자 특정 및 데이타 위변조 검사에 이용하는 변수 (인증결과와 함께 전달됨)
    reqseq = ''

    # 인증요청 암호화 데이터 초기화
    enc_data = ''

    # 처리결과 메세지 초기화
    returnMsg = ''

    # 요청번호 생성
    try: # 파이썬 버전이 3.5 미만인 경우 check_output 함수 이용
        #  reqseq = subprocess.check_output([cb_encode_path, 'SEQ', sitecode])  
        reqseq = subprocess.run([cb_encode_path, 'SEQ', sitecode], capture_output=True, encoding='euc-kr').stdout
    except subprocess.CalledProcessError as e: # check_output 함수 이용하는 경우 1 이외의 결과는 에러로 처리됨
        reqseq = e.output.decode('euc-kr')
        logm = "[" + util.getNow() + "] " + f"Exception {reqseq} {e}" + "\n"
        util.file_open (log_path, util.getNow("%Y-%m-%d") + ".log", logm)

    # 요청번호 세션에 저장 (세션 이용하지 않는 경우 생략)
    # session['REQ_SEQ'] = reqseq

    # print("reqseqreqseqreqseq", reqseq)

    # plain 데이터 생성 (형식 수정불가)
    plaindata = '7:REQ_SEQ' + str(len(reqseq)) + ':' + reqseq + '8:SITECODE' + str(len(sitecode)) + ':' + sitecode + '9:AUTH_TYPE' + str(len(authtype)) + ':' + authtype + '7:RTN_URL' + str(len(returnurl)) + ':' + returnurl + '7:ERR_URL' + str(len(errorurl)) + ':' + errorurl + '9:CUSTOMIZE' + str(len(customize)) + ':' + customize

    # 인증요청 암호화 데이터 생성
    try: # 파이썬 버전이 3.5 미만인 경우 check_output 함수 이용
        #  enc_data = subprocess.check_output([cb_encode_path, 'ENC', sitecode, sitepasswd, plaindata])
        enc_data = subprocess.run([cb_encode_path, 'ENC', sitecode, sitepasswd, plaindata],  capture_output=True, encoding='euc-kr').stdout
    except subprocess.CalledProcessError as e: # check_output 함수 이용하는 경우 1 이외의 결과는 에러로 처리됨
        enc_data = e.output.decode('euc-kr')
        logm = "[" + util.getNow() + "] " + f"Exception {enc_data} {e}" + "\n"
        util.file_open (log_path, util.getNow("%Y-%m-%d") + ".log", logm)
        
    # ################### insert ###################
    params = {
        "enc_data" : enc_data
        ,"client_id" : checkplusInput.client_id
        ,"method" : checkplusInput.method
        ,"reqseq": reqseq
        ,"success_url" : returnurl
        ,"fail_url" : errorurl
        ,"client_ip" : request.state.user_ip 
    }
    nice_service.create(request, params)
    request.state.inspect = frame()

    # ################### insert ###################

    result = {
        "enc_data" : enc_data
        ,"client_id" : checkplusInput.client_id
        ,"method" : checkplusInput.method
    }

    # return result
    # 화면 렌더링 변수 설정 
    # render_params = {}  
    # render_params['enc_data'] = enc_data
    # render_params['returnMsg'] = returnMsg 

    return ex.ReturnOK(200, "", request, result)

# be/nice/checkplus/success
@router.post("/nice/checkplus/success", dependencies=[Depends(api_same_origin)])
async def 인증성공 (request: Request, resultInput:resultInput):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)

    sitecode = 'CB620'   
    sitepasswd = 'zHnBtw6iuNzP'
    cb_encode_path = "./module/CPClient_linux_x64"
   
    reqseq = '' # CP요청번호 초기화 
    enc_data = '' # 인증결과 암호화 데이터 초기화
    plaindata = '' # 인증결과 복호화 데이터 초기화
    returnMsg = '' # 처리결과 메세지 초기화
    ciphertime = '' # 인증결과 복호화 시간 초기화 

    # 인증결과 데이터 초기화 (success)
    requestnumber = '' # 요청번호
    responsenumber = '' # 본인인증 응답코드 (응답코드 문서 참조)
    authtype = '' # 인증수단 (M:휴대폰, c:카드, X:인증서, P:삼성패스)
    name = '' # 이름 (EUC-KR)
    utfname = '' # 이름 (UTF-8, URL인코딩)
    birthdate = '' # 생년월일 (YYYYMMDD)
    gender = '' # 성별 코드 (0:여성, 1:남성)
    nationalinfo = '' # 내/외국인 정보 (0:내국인, 1:외국인)
    dupinfo = '' # 중복가입확인값 (64Byte, 개인식별값, DI:Duplicate Info)
    conninfo = '' # 연계정보확인값 (88Byte, 개인식별값, CI:Connecting Info)
    mobileno = '' # 휴대폰번호
    mobileco = '' # 통신사 (가이드 참조)
   
    try : # NICE에서 전달받은 인증결과 암호화 데이터 취득
        # GET 요청 처리 
        # if request.method == 'GET':
        #     print('checkplus_success:GET') 
        #     enc_data = request.args.get('EncodeData', default = '', type = str)
        # POST 요청 처리 
        # else:
        enc_data = resultInput.encode_data
        enc_data = parse.unquote(enc_data) 
    except:
        logm = "[" + util.getNow() + "] " + f"Exception {sys.exc_info()[0]} {e}" + "\n"
        util.file_open (log_path, util.getNow("%Y-%m-%d") + ".log", logm)

    ################################### 문자열 점검 ######################################
    errChars = re.findall('[^0-9a-zA-Z+/=]', enc_data)
    if len(re.findall('[^0-9a-zA-Z+/=]', enc_data)) > 0:
        print("errChars=", errChars)
        return('문자열오류: 입력값 확인이 필요합니다')
    
    if (base64.b64encode(base64.b64decode(enc_data))).decode() != enc_data:
        return('변환오류: 입력값 확인이 필요합니다')
    #####################################################################################  

    print('reqseq:', reqseq) 

    if enc_data != '':
        # 인증결과 암호화 데이터 복호화 처리
        try: # 파이썬 버전이 3.5 미만인 경우 check_output 함수 이용
            #  plaindata = subprocess.check_output([cb_encode_path, 'DEC', sitecode, sitepasswd, enc_data])
            plaindata = subprocess.run([cb_encode_path, 'DEC', sitecode, sitepasswd, enc_data], capture_output=True, encoding='euc-kr').stdout
        except subprocess.CalledProcessError as e: # check_output 함수 이용하는 경우 1 이외의 결과는 에러로 처리됨
            plaindata = e.output.decode('euc-kr')
            logm = "[" + util.getNow() + "] " + f"Exception {plaindata} {e}" + "\n"
            util.file_open (log_path, util.getNow("%Y-%m-%d") + ".log", logm)
    else:
        returnMsg = '처리할 암호화 데이타가 없습니다.'

    # 복호화 처리결과 코드 확인
    if plaindata == -1:
        returnMsg = '암/복호화 시스템 오류'
    elif plaindata == -4:
        returnMsg = '복호화 처리 오류'
    elif plaindata == -5:
        returnMsg = 'HASH값 불일치 - 복호화 데이터는 리턴됨'
    elif plaindata == -6:
        returnMsg = '복호화 데이터 오류'
    elif plaindata == -9:
        returnMsg = '입력값 오류'
    elif plaindata == -12:
        returnMsg = '사이트 비밀번호 오류'
    else: # 요청번호 추출
        requestnumber   = GetValue(plaindata, 'REQ_SEQ')

        # 데이터 위변조 검사 (세션 이용하지 않는 경우 분기처리 생략)
        # : checkplus_main에서 세션에 저장한 요청번호와 결과 데이터의 추출값 비교하는 추가적인 보안처리
        # if reqseq == requestnumber:
        # 인증결과 복호화 시간 생성 (생략불가)
        try: # 파이썬 버전이 3.5 미만인 경우 check_output 함수 이용
        #  ciphertime = subprocess.check_output([cb_encode_path, 'CTS', sitecode, sitepasswd, enc_data])
            ciphertime = subprocess.run([cb_encode_path, 'CTS', sitecode, sitepasswd, enc_data],  capture_output=True, encoding='euc-kr').stdout
        except subprocess.CalledProcessError as e: # check_output 함수 이용하는 경우 1 이외의 결과는 에러로 처리됨
            ciphertime = e.output.decode('euc-kr')
            logm = "[" + util.getNow() + "] " + f"Exception {ciphertime} {e}" + "\n"
            util.file_open (log_path, util.getNow("%Y-%m-%d") + ".log", logm)
        # else:
        #   returnMsg = '세션 불일치 오류'

    # 인증결과 복호화 시간 확인
    if ciphertime != '':

        #####################################################################################
        # 인증결과 데이터 추출
        # : 결과 데이터의 통신이 필요한 경우 암호화 데이터(EncodeData)로 통신 후 복호화 해주십시오
        #   복호화된 데이터를 통신하는 경우 데이터 유출에 주의해주십시오 (세션처리 권장)     
        #####################################################################################

        responsenumber  = GetValue(plaindata, 'RES_SEQ')
        authtype        = GetValue(plaindata, 'AUTH_TYPE')
        name            = GetValue(plaindata, 'NAME')
        utfname         = GetValue(plaindata, 'UTF8_NAME')
        birthdate       = GetValue(plaindata, 'BIRTHDATE')
        gender          = GetValue(plaindata, 'GENDER')
        nationalinfo    = GetValue(plaindata, 'NATIONALINFO')
        dupinfo         = GetValue(plaindata, 'DI')
        conninfo        = GetValue(plaindata, 'CI')
        mobileno        = GetValue(plaindata, 'MOBILE_NO')
        mobileco        = GetValue(plaindata, 'MOBILE_CO')

        print('responsenumber:' + responsenumber)
        print('authtype:' + authtype)
        print('name:' + name)
        print('utfname:' + utfname)
        print('birthdate:' + birthdate)
        print('gender:' + gender)
        print('nationalinfo:' + nationalinfo)
        print('dupinfo:' + dupinfo)
        print('conninfo:' + conninfo)
        print('mobileno:' + mobileno)

        returnMsg = "사용자 인증 성공"						

    # 화면 렌더링 변수 설정      
    render_params = {}  
    render_params['plaindata'] = plaindata
    render_params['returnMsg'] = returnMsg
    render_params['ciphertime'] = ciphertime
    render_params['requestnumber'] = requestnumber
    render_params['responsenumber'] = responsenumber
    render_params['authtype'] = authtype
    render_params['name'] = name
    render_params['utfname'] = utfname
    render_params['birthdate'] = birthdate
    render_params['gender'] = gender
    render_params['nationalinfo'] = nationalinfo
    render_params['dupinfo'] = dupinfo
    render_params['conninfo'] = conninfo
    render_params['mobileno'] = mobileno
    render_params['mobileco'] = mobileco
    
    result = {
         "req_seq": requestnumber
        ,"method" : resultInput.method
        ,"client_id" : resultInput.client_id
        ,"err_code" : "200"
        ,"err_msg" : returnMsg
    }

    nice_service.update(request, result)
    request.state.inspect = frame()

    phone = ''
    for i in render_params['mobileno'] : 
        phone += i
        if len(phone) == 3 or len(phone) == 8 : 
            phone += "-"
    if mobileVaild(phone) == True :
        render_params['mobileno'] = phone
    else :
        return ex.ReturnOK(501, "핸드폰 번호를 확인해주세요", request, render_params['mobileno'])


    birthdate = ''        
    for i in render_params['birthdate'] : 
        birthdate += i
        if len(birthdate) == 4 or len(birthdate) == 7 : 
            birthdate += "-"
    if birthVaild(birthdate) == True :
        render_params['birthdate'] = birthdate
    else :
        return ex.ReturnOK(502, "생년월일을 확인해주세요", request, render_params['birthdate'] )
    
    if render_params['gender'] == '0' :
        render_params['gender'] = '여자'
    elif render_params['gender'] == '1' :
        render_params['gender'] = '남자'
    
    res = nice_service.member_update(request, render_params)
    request.state.inspect = frame()

    if 'dict' in str(type(res)) and "code" in res:
        if res["code"] != 200:
            return res
    
    # 회원정보 select  
    member = member_service.read(request, res.login_id, res.tel)
    request.state.inspect = frame()

    nice_result = {
        "uid" : res.uid
        ,"mobile" : res.tel
        ,"login_id" : res.login_id
    }
    nice_result["partner_list"] = []
    if len(member) >= 2 :
        uids = []
        for item in member:
            uids.append(item["partner_uid"])
        partner = partner_service.list(request, uids)
        request.state.inspect = frame()
        nice_result["partner_list"] = partner
        nice_result["code"] = '200'

        return ex.ReturnOK(200, "", request, nice_result)

    else :
        nice_result = await auth.앱사용자_로그인(request, {
            "uid": res.uid
            ,"login_id": res.login_id
            ,"mobile": res.tel
            ,"partner_uid": member[0]["partner_uid"]
        })
        request.state.inspect = frame()

        return nice_result

import re
def mobileVaild(mobile):
    regex = r'\d{2,3}-\d{3,4}-\d{4}'
    if(re.fullmatch(regex, mobile)):
        return True
    else:
        return False
def birthVaild(birthday):
    regex = r'\d{4}-\d{2}-\d{2}'
    if(re.fullmatch(regex, birthday)):
        return True
    else:
        return False

# be/nice/checkplus/fail
@router.post("/nice/checkplus/fail", dependencies=[Depends(api_same_origin)])
async def 인증실패 (request: Request, resultInput:resultInput):
    
    sitecode = 'CB620'   
    sitepasswd = 'zHnBtw6iuNzP'
    cb_encode_path = "./module/CPClient_linux_x64"

    # 인증결과 암호화 데이터 초기화
    enc_data = ''

    # 인증결과 복호화 데이터 초기화
    plaindata = ''   

    # 처리결과 메세지 초기화
    returnMsg = ''

    # 인증결과 복호화 시간 초기화 
    ciphertime = ''   

    # 인증결과 데이터 초기화
    requestnumber   = '' # 요청번호
    errcode         = '' # 본인인증 응답코드 (응답코드 문서 참조)
    authtype        = '' # 인증수단 (M:휴대폰, c:카드, X:인증서, P:삼성패스)

    # NICE에서 전달받은 인증결과 암호화 데이터 취득
    result = request.form
    try:
        enc_data = result['EncodeData']
    except KeyError as e:
        logm = "[" + util.getNow() + "] " + f"Exception {e}" + "\n"
        util.file_open (log_path, util.getNow("%Y-%m-%d") + ".log", logm)

    ################################### 문자열 점검 ######################################
    errChars = re.findall('[^0-9a-zA-Z+/=]', enc_data)
    if len(re.findall('[^0-9a-zA-Z+/=]', enc_data)) > 0:
        print("errChars=", errChars)
        return('문자열오류: 입력값 확인이 필요합니다')
    if (base64.b64encode(base64.b64decode(enc_data))).decode() != enc_data:
        return('변환오류: 입력값 확인이 필요합니다')
    #####################################################################################

    if enc_data != '':
        try: # 인증결과 암호화 데이터 복호화 처리
        #  plaindata = subprocess.check_output([cb_encode_path, 'DEC', sitecode, sitepasswd, enc_data])
            plaindata = subprocess.run([cb_encode_path, 'DEC', sitecode, sitepasswd, enc_data], capture_output=True, encoding='euc-kr').stdout
        except subprocess.CalledProcessError as e: # check_output 함수 이용하는 경우 1 이외의 결과는 에러로 처리됨
            plaindata = e.output.decode('euc-kr')
            logm = "[" + util.getNow() + "] " + f"Exception {plaindata} {e}" + "\n"
            util.file_open (log_path, util.getNow("%Y-%m-%d") + ".log", logm)
    else:
        returnMsg = '처리할 암호화 데이타가 없습니다.'

    # 복호화 처리결과 코드 확인
    if plaindata == -1:
        returnMsg = '암/복호화 시스템 오류'
    elif plaindata == -4:
        returnMsg = '복호화 처리 오류'
    elif plaindata == -5:
        returnMsg = 'HASH값 불일치 - 복호화 데이터는 리턴됨'
    elif plaindata == -6:
        returnMsg = '복호화 데이터 오류'
    elif plaindata == -9:
        returnMsg = '입력값 오류'
    elif plaindata == -12:
        returnMsg = '사이트 비밀번호 오류'
    else:
        # 인증결과 복호화 시간 생성
        try: # 파이썬 버전이 3.5 미만인 경우 check_output 함수 이용
        #  ciphertime = subprocess.check_output([cb_encode_path, 'CTS', sitecode, sitepasswd, enc_data])
            ciphertime = subprocess.run([cb_encode_path, 'CTS', sitecode, sitepasswd, enc_data],  capture_output=True, encoding='euc-kr').stdout
        except subprocess.CalledProcessError as e: # check_output 함수 이용하는 경우 1 이외의 결과는 에러로 처리됨
            ciphertime = e.output.decode('euc-kr')
            logm = "[" + util.getNow() + "] " + f"Exception {ciphertime} {e}" + "\n"
            util.file_open (log_path, util.getNow("%Y-%m-%d") + ".log", logm)

        # 인증결과 데이터 추출
        requestnumber  = GetValue(plaindata, 'REQ_SEQ')
        errcode  = GetValue(plaindata, 'ERR_CODE')
        authtype  = GetValue(plaindata, 'AUTH_TYPE')

        print('requestnumber:' + requestnumber)
        print('errcode:' + errcode)
        print('authtype:' + authtype)

    # 화면 렌더링 변수 설정      
    render_params = {}  
    render_params['plaindata'] = plaindata
    render_params['returnMsg'] = returnMsg
    render_params['ciphertime'] = ciphertime
    render_params['requestnumber'] = requestnumber
    render_params['errcode'] = errcode
    render_params['authtype'] = authtype
    
    result = {
         "req_seq": requestnumber
        ,"method" : resultInput.method
        ,"client_id" : resultInput.client_id
        ,"err_code" : errcode
        ,"err_msg" : returnMsg
    }

    nice_service.update(request, result)
    request.state.inspect = frame()

    return ex.ReturnOK(400, returnMsg, request, render_params)




# 인증결과 데이터 추출 함수
def GetValue(plaindata, key):
   value = ''
   keyIndex = -1
   valLen = 0

   # 복호화 데이터 분할
   arrData = plaindata.split(':')
   cnt = len(arrData)
   for i in range(cnt):
      item = arrData[i]
      itemKey = re.sub('[\d]+$', '', item)

      # 키값 검색
      if itemKey == key:
         keyIndex = i

         # 데이터 길이값 추출
         valLen = int(item.replace(key, '', 1))

         if key != 'NAME':
            # 실제 데이터 추출
            value = arrData[keyIndex + 1][:valLen]
         else:
            # 이름 데이터 추출 (한글 깨짐 대응)
            value = re.sub('[\d]+$', '', arrData[keyIndex + 1])
            
         break

   return value

# be/nice/checkplus/userci
@router.post("/nice/checkplus/userci", dependencies=[Depends(api_same_origin)])
async def userci (request: Request, userciInput: UserciInput):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)

    res = nice_service.userci_check(request, userciInput)
    request.state.inspect = frame()

    if res is None :
        return ex.ReturnOK(404, "죄송합니다. 오류가 발생했습니다. 문제 지속시 1:1문의로 접수 바랍니다.", request)
    
    if res.user_ci is None :
        return ex.ReturnOK(405, "인증필요", request)

    return ex.ReturnOK(200, "", request, res)