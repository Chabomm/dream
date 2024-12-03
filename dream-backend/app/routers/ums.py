from typing import Dict
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Body, Header
from inspect import currentframe as frame
import requests
import json
import re
from fastapi.encoders import jsonable_encoder
import urllib

from app.core import exceptions as ex
from app.core import util
from app.core.config import *
from app.core.config import PROXY_PREFIX, api_same_origin
from app.models.ums import *
from app.service import ums_service

router = APIRouter (
    prefix = PROXY_PREFIX, # /be 
    tags=["usm"],
)

@router.post("/ums/send", dependencies=[Depends(api_same_origin)])
async def UMS보내기 (
    request: Request, 
    request_body:Dict = Body(
        ...,
        examples = {
            "example01" : {
                "summary": "이메일 sample",
                "description": "",
                "value": {
                    "ums_uid": 6,
                    "send_list": [
                        {
                            "ums_type": "email",
                            "msgId": "sample_0001",
                            "toEmail": "dev@indend.co.kr",
                            "#{받는사람}": "받는이",
                            "#{보내는사람}": "인디앤드코리아",
                        }
                    ]
                }
            },
            "example02" : {
                "summary": "이메일 여러명",
                "description": "",
                "value": {
                    "ums_uid": 1,
                    "send_list": [
                        {
                            "ums_type": "email",
                            "msgId": "sample_0001",
                            "toEmail": "dev@indend.co.kr",
                            "#{받는사람}": "권남구",
                            "#{보내는사람}": "인디앤드코리아",
                        },{
                            "ums_type": "email",
                            "msgId": "sample_0002",
                            "toEmail": "uhjung@indend.co.kr",
                            "#{받는사람}": "정유하",
                            "#{보내는사람}": "인디앤드코리아",
                        },{
                            "ums_type": "email",
                            "msgId": "sample_0003",
                            "toEmail": "bcha@indend.co.kr",
                            "#{받는사람}": "차봄",
                            "#{보내는사람}": "인디앤드코리아",
                        }

                    ]
                }
            },
            "example03" : {
                "summary": "문자 sample",
                "description": "",
                "value": {
                    "ums_uid": 4,
                    "send_list": [
                        {
                            "ums_type": "sms",
                            "msgId": "sample_0001",
                            "toMobile": "01028962650",
                            "#{플랫폼}": "테스트",
                            "#{인증번호}": "123456",
                        }
                    ]
                }
            },
            "example04" : {
                "summary": "알림톡 sample",
                "description": "",
                "value": {
                    "ums_uid": 3,
                    "send_list": [
                        {
                            "ums_type": "at",
                            "msgId": "sample_0002",
                            "toMobile": "01028962650",
                            "#{발송인}": "테스트",
                            "#{상품명}": "테스트상품",
                            "#{고객센터번호}": "123-456",
                        }
                    ]
                }
            },
        }
    )
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)

    timestr = util.getNow("%Y-%m-%d")
    file_name = timestr + ".ums.log"

    logm = util.getNow() + " |:| " + request.state.user_ip + "\n"
    logm = logm + "┏────────────request.state.body─────────────┓" + "\n"
    logm = logm + json.dumps(request_body, ensure_ascii=False, indent=4) + "\n"

    # ums 템플릿 가져오기
    tmpl = ums_service.read_ums_tmpl(request, request_body["ums_uid"])
    request.state.inspect = frame()

    if tmpl is None :
        return ex.ReturnOK(401, "UMS템플릿을 찾을 수 없습니다.", request)

    arr_title_val = re.compile('#{[^{}]*}').findall(tmpl["subject"])
    arr_content_val = re.compile('#{[^{}]*}').findall(tmpl["content"])

    alimtalk_list = []
    send_result = ""
    result_list = []

    for send_obj in request_body["send_list"]:
        send_obj["PROFILE_KEY"] = getATprofileKey(tmpl["profile"])
        send_obj["title"] = tmpl["subject"]
        for k in arr_title_val :
            if k in send_obj["title"]:
                v = send_obj[k]
                send_obj["title"] = send_obj["title"].replace(k, v)
            else:
                send_obj["title"] = send_obj["title"].replace(k, "")

        send_obj["content"] = tmpl["content"]
        for k in arr_content_val :
            if k in send_obj:
                v = send_obj[k]
                send_obj["content"] = send_obj["content"].replace(k,v)
            else:
                send_obj["content"] = send_obj["content"].replace(k,"")

        if send_obj["ums_type"] == "email" and util.checkNumeric(tmpl["layout_uid"]) > 0 :
            read_file = open("/usr/src/app/static/email/tmpl/"+str(tmpl["layout_uid"])+".html", 'r')
            email_layout = read_file.read()
            send_obj["content"] = email_layout.replace("#{contents}", send_obj["content"])
        
        # 이메일 보내기
        if send_obj["ums_type"] == "email" or ("toEmail" in send_obj and send_obj["toEmail"] != "") :
            send_obj = ums_service.send_mail(send_obj)
            result_obj = {}
            result_obj["msgId"] = send_obj["msgId"]
            result_obj["result"] = send_obj["result"]
            result_list.append(result_obj)
            
        # sms 보내기
        elif send_obj["ums_type"] == "sms" :
            send_obj = ums_service.getSmsSendData(send_obj)
            alimtalk_list.append(send_obj)
            result_obj = {}
            result_obj["msgId"] = send_obj["msgid"]
            result_obj["result"] = ""
            result_list.append(result_obj)

        # 알림톡 발송
        elif send_obj["ums_type"] == "at" :
            send_obj["template_code"] = tmpl["template_code"]
            send_obj = ums_service.getAtSendData(send_obj)
            alimtalk_list.append(send_obj)
            result_obj = {}
            result_obj["msgId"] = send_obj["msgid"]
            result_obj["result"] = ""
            result_list.append(result_obj)
        # end if
    # end for

    if len(alimtalk_list) > 0 :
        profile_key = alimtalk_list[0]['profile_key']
        URL = "https://alimtalk-api.sweettracker.net/v2/"+profile_key+"/sendMessage"
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'userid': AT_USER_ID,
            'profile_key': profile_key
        }
        send_result = requests.post(URL, headers=headers, data=json.dumps(alimtalk_list)).text
        try : 
            send_result = json.loads(send_result)
            
            for i in range(len(send_result)): 
                if send_result[i]["result"] == "Y" :
                    result_list[i]["result"] = "OK"
                else :
                    result_list[i]["result"] = send_result[i]["error"]
                # end if
            # end for
        except Exception as e :
            logm = logm + "┏───────────────────Exception────────────────┓" + "\n"
            logm = logm + send_result + "\n"
            logm = logm + json.dumps(alimtalk_list) + "\n"
            logm = logm + "└───────────────────────────────────────────┘" + "\n"
        # end except
    # end if

    logm = logm + "┏───────────────────response────────────────┓" + "\n"
    logm = logm + json.dumps(result_list, ensure_ascii=False, indent=4) + "\n"

    util.file_open (
        "/usr/src/app/data/dream-backend/ums/"
        ,file_name
        ,logm
    )
    
    # ums log db에 들어갈 데이터들 만들어줌
    log_param = T_UMS_LOG (
        ums_uid = tmpl["uid"]
        ,ums_type = tmpl["ums_type"]
        ,platform = tmpl["platform"]
        ,template_code = tmpl["template_code"]
        ,profile = tmpl["profile"]
        ,req = json.dumps(request_body, ensure_ascii=False, indent=4)
        ,res = json.dumps(result_list, ensure_ascii=False, indent=4)
    )
    ums_service.create_umslog(request, log_param)
    request.state.inspect = frame()
    
    return result_list

@router.post("/ums/token", dependencies=[Depends(api_same_origin)])
async def 토큰생성 (
    request: Request, 
    request_body:Dict
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    access_token = create_access_token(data={"a":"a"}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    payload = jwt.decode("eyJ0eXAiOiJKV1QiLCAiYWxnIjoiSFMyNTYifQ.eyJpc3MiOiAiam9lIiwgImV4cCI6IDE2ODg0NjMwNzQsICJodHRwOi8vZXhhbXBsZS5jb20vaXNfcm9vdCI6IHRydWV9.Pm0BGaBAKxJZAagLTS8f1SPwWt8f1BzZV1WGpRTZcjw", SECRET_KEY, algorithms=[ALGORITHM])
    print("payload")
    print(payload)

    return access_token



from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # ACCESS_TOKEN 만료 (분)
SECRET_KEY = "b3e204fda0703c6d33f386ad54627b4783c67440399b353716c6fbc860c4193d"
ALGORITHM = "HS256"
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    print(to_encode, SECRET_KEY, ALGORITHM)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt