from fastapi import APIRouter, Depends, Request, Body
from inspect import currentframe as frame
import urllib
import json
import os
import requests
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse, JSONResponse
from app.core import exceptions as ex
from app.core import util
from app.core.config import PROXY_PREFIX, api_same_origin
from app.core.database import get_session
from app.deps.auth import create_access_token, get_current_active_front, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES

from app.schemas.schema import *
from app.models.session import *
from app.schemas.front.auth import *

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/front/partner"],
)

# be/front/partner/notice/list
@router.post("/front/partner/notice/list", dependencies=[Depends(api_same_origin)])
async def 사내공지사항_리스트 (
    request:Request
    ,user: TokenDataDream = Depends(get_current_active_front)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataDream(user), getTokenDataDream(user)


    if os.environ.get('PROFILE') == 'development' :
        URL = "http://192.168.0.81:8888/api/dream/app/notice/list.json.asp"
    else :
        URL = "http://112.221.134.106:8888/api/dream/app/notice/list.json.asp"

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'
    }

    
    result = ""
    params = urllib.parse.urlencode(jsonable_encoder({'partner_id':user.partner_id}))

    result = requests.post(URL, headers=headers, data=params).text
    
    try :
        result = json.loads(result)
        # DreamBuild()
    except Exception as e:
        return ex.ReturnOK(500, "예기치 못한 오류가 발생하였습니다.\n문제 지속시 고객센터(032-719-3366)로 문의 바랍니다.\n평일 10:00~18:00(점심 11:30~12:30)\n주말/공휴일 휴무", request)

    return result

# be/front/partner/notice/detail
@router.post("/front/partner/notice/detail", dependencies=[Depends(api_same_origin)])
async def 사내공지사항_상세 (
    request:Request
    ,user: TokenDataDream = Depends(get_current_active_front)
    ,pRead: PRead = Body(
        ...,
        examples = {
            "example01" : {
                "summary": "사내공지사항",
                "description": "",
                "value": {
                    "uid" : 2
                }
            }
        }
    )
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataDream(user), getTokenDataDream(user)


    if os.environ.get('PROFILE') == 'development' :
        URL = "http://192.168.0.81:8888/api/dream/app/notice/detail.json.asp"
    else :
        URL = "http://112.221.134.106:8888/api/dream/app/notice/detail.json.asp"


    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'
    }

    
    result = ""
    params = urllib.parse.urlencode({
        "uid" : pRead.uid
        ,"partner_id" : user.partner_id
    })
    result = requests.post(URL, headers=headers, data=params).text

    try :
        result = json.loads(result)
        # DreamBuild()
    except Exception as e:
        return ex.ReturnOK(500, "예기치 못한 오류가 발생하였습니다.\n문제 지속시 고객센터(032-719-3366)로 문의 바랍니다.\n평일 10:00~18:00(점심 11:30~12:30)\n주말/공휴일 휴무", request, {"response":result})

    return result


# be/front/partner/welfare/list
@router.post("/front/partner/welfare/list", dependencies=[Depends(api_same_origin)])
async def 사내복지제도_리스트 (
    request:Request
    ,user: TokenDataDream = Depends(get_current_active_front)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataDream(user), getTokenDataDream(user)

    if os.environ.get('PROFILE') == 'development' :
        URL = "http://192.168.0.81:8888/api/dream/app/welfare/list.json.asp"
    else :
        URL = "http://112.221.134.106:8888/api/dream/app/welfare/list.json.asp"


    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'
    }

    
    result = ""
    params = urllib.parse.urlencode(jsonable_encoder({'partner_id':user.partner_id}))

    result = requests.post(URL, headers=headers, data=params).text
    
    try :
        result = json.loads(result)
        # DreamBuild()
    except Exception as e:
        return ex.ReturnOK(500, "예기치 못한 오류가 발생하였습니다.\n문제 지속시 고객센터(032-719-3366)로 문의 바랍니다.\n평일 10:00~18:00(점심 11:30~12:30)\n주말/공휴일 휴무", request)

    return result

# be/front/partner/welfare/detail
@router.post("/front/partner/welfare/detail", dependencies=[Depends(api_same_origin)])
async def 사내복지제도_상세 (
    request:Request
    ,user: TokenDataDream = Depends(get_current_active_front)
    ,pRead: PRead = Body(
        ...,
        examples = {
            "example01" : {
                "summary": "사내복지제도",
                "description": "",
                "value": {
                    "uid" : 2
                }
            }
        }
    )
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataDream(user), getTokenDataDream(user)

    if os.environ.get('PROFILE') == 'development' :
        URL = "http://192.168.0.81:8888/api/dream/app/welfare/detail.json.asp"
    else :
        URL = "http://112.221.134.106:8888/api/dream/app/welfare/detail.json.asp"


    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'
    }

    
    result = ""
    params = urllib.parse.urlencode({
        "uid" : pRead.uid
        ,"partner_id" : user.partner_id
    })
    result = requests.post(URL, headers=headers, data=params).text

    try :
        result = json.loads(result)
        # DreamBuild()
    except Exception as e:
        return ex.ReturnOK(500, "예기치 못한 오류가 발생하였습니다.\n문제 지속시 고객센터(032-719-3366)로 문의 바랍니다.\n평일 10:00~18:00(점심 11:30~12:30)\n주말/공휴일 휴무", request, {"response":result})

    return result
