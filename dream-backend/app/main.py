import json
import os
from fastapi import FastAPI, Depends, HTTPException, status, Request, Header
from fastapi.responses import PlainTextResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from fastapi.staticfiles import StaticFiles
from inspect import currentframe as frame

from app.core import exceptions as ex
from app.core.logger import api_logger
from app.core.database import SessionLocal
from app.core import util

app = FastAPI(
    title = '인디앤드코리아 복지드림 API Server',
    description = '인디앤드코리아 복지드림 API Server'
)

allow_ip_list = [
    "112.221.134.106"
]

api_key_header = APIKeyHeader(name="Token")

origins = [
    "http://localhost:5000",
    "http://localhost:5001",
]

# origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header (request: Request, call_next):
    request.state.req_time = util.getNow()
    request.state.start = util.getUnixTime()

    if os.environ['PROFILE'] == "development" :
        request.state.user_ip = "127.0.0.1"

    elif request.headers.get('x-user-ip') != None and os.environ['HOST_IP'] != str(request.headers.get('x-user-ip')) :
        request.state.user_ip = str(request.headers.get('x-user-ip')) # nextjs serversideprops에서 보낸 아이피

    elif request.headers.get('x-real-ip') != None and os.environ['HOST_IP'] != str(request.headers.get('x-real-ip')) :
        request.state.user_ip = str(request.headers.get('x-real-ip'))

    elif request.client.host != None and os.environ['HOST_IP'] != str(request.client.host) :
        request.state.user_ip = str(request.client.host)

    if not hasattr(request.state, 'user_ip') :
        request.state.user_ip = "127.0.0.1"

    # static 미들웨어 허용
    if request.url.path.startswith("/be/static/") or request.url.path.startswith("/be/resource/") :
        response = await call_next(request)
        return response
    
    if request.url.path.startswith("/openapi.json") :
        IS_BLOCK = True
        for allow_ip in allow_ip_list:
            if os.environ.get('PROFILE') == 'development' :
                IS_BLOCK = False
            elif allow_ip == str(request.state.user_ip) :
                IS_BLOCK = False
            if IS_BLOCK :
                return PlainTextResponse(status_code=404)
            
        response = await call_next(request)
        return response

    # docs local만 허용
    if request.url.path.startswith("/docs") \
        or request.url.path.startswith("/redoc") :
        
        IS_BLOCK = True
        for allow_ip in allow_ip_list:
            if os.environ.get('PROFILE') == 'development' :
                IS_BLOCK = False
            elif allow_ip == str(request.state.user_ip) :
                IS_BLOCK = False
            if IS_BLOCK :
                return PlainTextResponse(status_code=404)

    request.state.inspect = None
    request.state.body = None
    request.state.user = None
    request.state.db = SessionLocal()

    try :
        print("")
        print("")
        print("\033[95m" + "######################## [",request.state.user_ip,"] [", util.getNow(), "] [",util.get_request_url(request),"] START " + "\033[0m")
        response = await call_next(request)
        request.state.db.commit()
        request.state.db.close()

        # SCM DB conn 있으면 커밋
        if hasattr(request.state, 'db_scm'):
            request.state.db_scm.commit()
            request.state.db_scm.close()

        print("\033[95m" + "######################## [",request.state.user_ip,"] [", util.getNow(), "] [",util.get_request_url(request),"] SUCCESS END " + "\033[0m")
    except Exception as e:
        request.state.db.rollback()
        request.state.db.close()

        # SCM DB conn 있으면 롤백
        if hasattr(request.state, 'db_scm'):
            request.state.db_scm.rollback()
            request.state.db_scm.close()

        # 디테일한 내용을 log 찍어주고 간단한 내용을 클라이언트한테 response
        error = await ex.exception_handler(e)
        error_dict = dict(status=error.status_code, msg=error.msg, code=error.code)
        response = JSONResponse(status_code=error.status_code, content=error_dict)
        await api_logger(request=request, error=error)
        print("\033[95m" + "######################## [",request.state.user_ip,"] [", util.getNow(), "] [",util.get_request_url(request),"] EXCEPTION END " + "\033[0m")

    if request.state.user :
        print("\033[95m" + str(request.state.user) + "\033[0m")
        if '/logout' in str(request._url):
            response.delete_cookie(request.state.user.token_name)
        else :
            response.set_cookie (
                key=request.state.user.token_name
                ,value=request.state.user.access_token
            )

    # print("")
    # print("")
    # print("--- request")
    # print(request.__dict__)
    # print("")
    # print("")
    # print("--- response")
    # print(response.__dict__)
    # print("")
    # print("")

    return response

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    print(f"{repr(exc)}")
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)

@app.get("/")
def read_root(request: Request):
    print(request.state.user_ip)
    return "Hello World"

API_TOKEN = "SECRET_API_TOKEN"

async def api_token(token: str = Depends(APIKeyHeader(name="Token"))):
    if token != API_TOKEN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

@app.get("/protected-route", dependencies=[Depends(api_token)])
async def protected_route():
    return {"hello": "world"}

@app.get("/be/ping", status_code=200, description="***** Liveliness Check *****")
async def ping(
    request:Request
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)

    return "pong"

@app.post("/be/client_error")
async def client_error(
    request:Request
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)

    timestr = util.getNow("%Y-%m-%d")
    file_name = timestr + ".log"
    logm = util.getNow() + " |:| " + request.state.user_ip + "\n"
    logm = logm + "┏────────────request.state.body─────────────┓" + "\n"
    logm = logm + json.dumps(request.state.body, ensure_ascii=False, indent=4) + "\n"
    logm = logm + "└───────────────────────────────────────────┘" 

    util.file_open (
        "/usr/src/app/data/dream-backend/client/"
        ,file_name
        ,logm
    )
    
# ==== start common ==== 
from .routers import nextAuthJWT
app.include_router(nextAuthJWT.router)

from .routers import auth
app.include_router(auth.router)

from .routers import aws
app.include_router(aws.router)

from .routers import ums
app.include_router(ums.router)

from .routers import batch
app.include_router(batch.router)

from .routers import nice
app.include_router(nice.router)

from .routers import files
app.include_router(files.router)
# ==== end common ==== 

# ==== start admin ==== 
from .routers.admin import auth
app.include_router(auth.router)

from .routers.admin.b2b import goods as admin_goods
app.include_router(admin_goods.router)

from .routers.admin.b2b import order as admin_order
app.include_router(admin_order.router)

from .routers.admin.b2b import seller as admin_seller
app.include_router(admin_seller.router)

from .routers.admin import board
app.include_router(board.router)

from .routers.admin.entry import counsel
app.include_router(counsel.router)

from .routers.admin.entry import build
app.include_router(build.router)

from .routers.admin.entry import partner as admin_partner
app.include_router(admin_partner.router)

from .routers.admin.entry import manager as admin_manager
app.include_router(admin_manager.router)

from .routers.admin import member
app.include_router(member.router)

from .routers.admin import posts
app.include_router(posts.router)

from .routers.admin.setup import admin
app.include_router(admin.router)

from .routers.admin.setup import roles
app.include_router(roles.router)

from .routers.admin.setup import info
app.include_router(info.router)

from .routers.admin.setup import logs
app.include_router(logs.router)

from .routers.admin import ums
app.include_router(ums.router)
# ==== end admin ==== 

# ==== start manager ==== 
from .routers.manager import auth
app.include_router(auth.router)

from .routers.manager.b2b import goods as manager_goods
app.include_router(manager_goods.router)

from .routers.manager.b2b import order as manager_order
app.include_router(manager_order.router)

from .routers.manager.setup import manager
app.include_router(manager.router)

from .routers.manager.setup import roles
app.include_router(roles.router)

from .routers.manager.setup import info
app.include_router(info.router)

from .routers.manager import home
app.include_router(home.router)

from .routers.manager.member import member
app.include_router(member.router)

from .routers.manager import bbs
app.include_router(bbs.router)


from .routers.manager.point.assign import merge
app.include_router(merge.router)

from .routers.manager.point.assign import balance
app.include_router(balance.router)

from .routers.manager.point.assign import single
app.include_router(single.router)

from .routers.manager.point.assign import group
app.include_router(group.router)

from .routers.manager.point.assign.sikwon import single as single_sikwon
app.include_router(single_sikwon.router)

from .routers.manager.point import status
app.include_router(status.router)

from .routers.manager.point.used import merge as used_merge
app.include_router(used_merge.router)

from .routers.manager.point.used import mall as used_mall
app.include_router(used_mall.router)

from .routers.manager.point.used import card as used_card
app.include_router(used_card.router)

from .routers.manager.point.used import sikwon as used_sikwon
app.include_router(used_sikwon.router)

from .routers.manager.point.exuse import confirm
app.include_router(confirm.router)

from .routers.manager.point.exuse import remaining
app.include_router(remaining.router)

from .routers.manager.point.limit import mall as mall_limit
app.include_router(mall_limit.router)

from .routers.manager.point.limit import card as card_limit
app.include_router(card_limit.router)

from .routers.manager.point.limit import sikwon as sikwon_limit
app.include_router(sikwon_limit.router)

from .routers.manager.account import merge as merge_account
app.include_router(merge_account.router)
from .routers.manager.account import mall as mall_account
app.include_router(mall_account.router)
from .routers.manager.account import card as card_account
app.include_router(card_account.router)
from .routers.manager.account import person as person_account
app.include_router(person_account.router)
from .routers.manager.account import cate as cate_account
app.include_router(cate_account.router)
from .routers.manager.account import discount as discount_account
app.include_router(discount_account.router)
from .routers.manager.account import receipt as receipt_account
app.include_router(receipt_account.router)
# ==== end manager ==== 

# ==== start front ==== 
from .routers.front import auth
app.include_router(auth.router)

from .routers.front import intro
app.include_router(intro.router)

from .routers.front import point
app.include_router(point.router)

from .routers.front import partner
app.include_router(partner.router)

from .routers.front.card import used
app.include_router(used.router)

from .routers.front.card import remaining
app.include_router(remaining.router)

from .routers.front.card import allow
app.include_router(allow.router)

from .routers.front.card import exuse
app.include_router(exuse.router)
# ==== end front ==== 

# ==== start inout ==== 
from .routers.inout.inbound import member
app.include_router(member.router)

from .routers.inout.inbound import partner
app.include_router(partner.router)

from .routers.inout.inbound import rtpay
app.include_router(rtpay.router)
# ==== end inout ==== 

# ==== start offcard ==== 
from .routers.offcard import send
app.include_router(send.router)

from .routers.offcard import recv
app.include_router(recv.router)
# ==== end offcard ==== 

