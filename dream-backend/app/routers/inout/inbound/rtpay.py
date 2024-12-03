from fastapi import APIRouter, Depends, Request, Body
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from inspect import currentframe as frame
from fastapi.responses import RedirectResponse, JSONResponse
from app.core import exceptions as ex
from app.core import util
from app.core.config import PROXY_PREFIX, api_same_origin
from app.core.database import get_session
from app.deps.auth import create_access_token, get_current_active_manager, get_current_user
from app.deps.auth import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES
from fastapi.param_functions import File, Body, Form
import requests
import json

from app.schemas.schema import *
from app.service.manager.point import balance_service

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/inbound"],
)

# be/inbound/repay/checkpay
@router.post("/inbound/repay/checkpay")
async def RTPAY_WEBHOOK (
    request: Request
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)

    # res = {'RCODE': '200', 'RPAY': '1000', 'RNAME': '홍길동', 'RTEXT': '입출금내역 알림 [입금] 1,000원 홍길동 114-******-04-050 10/10 17:21', 'RBANK': '신한은행', 'RNUMBER': '114-******-04-050'}
    # balance_service.rpay_checkpay(request, res)
    # request.state.inspect = frame()
    # return

    RTP_KEY = '9d576455-09f7-44b1-bb9b-e16d2597f925' #인증키값 설정
    RTP_URL = ''
    LOG_PATH = '/usr/src/app/data/dream-backend/rtpay/'

    result = await request.body()
    a = result.decode('utf-8')
    b = str(a).split('&')   
    
    print("request.body", b)   
    logm = "[" + util.getNow() + "] " + str(b) + "\n"
    util.file_open (LOG_PATH, util.getNow("%Y-%m-%d") + ".log", logm) 

    for i in b:
        if str(i[0:4]) == "ugrd":
            ugrd = i[5:]
        if str(i[0:7]) == "regPkey":
            regPkey = i[8:]
        if str(i[0:9]) == "rtpayData":
            rtd = i[10:]                  
        
    if int(ugrd) < 20:
        RTP_URL='rtpay.net'          
        s = '/CheckPay/test_checkpay.php'  
    else:
        RTP_URL='rtpay.net'
        s = '/CheckPay/checkpay.php'

    if regPkey == RTP_KEY:   
        headers = { 'Content-type':'application/x-www-form-urlencoded' }
        data = { 'form': a }
        params = json.dumps(data)
        try : 
            res = requests.post("https://" + RTP_URL + s, headers=headers, data=params, timeout=1).text
            
            logm = "[" + util.getNow() + "] " + str(res) + "\n"
            util.file_open (LOG_PATH, util.getNow("%Y-%m-%d") + ".log", logm) 
            
            res = json.loads(res)


            # balance_service.rpay_checkpay(request, res)
            # request.state.inspect = frame()
            
            if (int(res['RCODE']) == 200):
                return {
                    "status": 200,
                    "RCODE": '200',
                    'PCHK': 'OK',
                }
            else:
                return {
                    "status": 200,
                    "RCODE": result['RCODE'],
                    'PCHK': 'NO',
                }

        except Exception as e:
            print(str(e))
            return {
                "status": 200,
                "RCODE": '500',
                'PCHK': 'NO',
            }




