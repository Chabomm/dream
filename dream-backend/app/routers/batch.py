from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Body, Header, BackgroundTasks
from inspect import currentframe as frame
import json
import re
from fastapi.encoders import jsonable_encoder
import urllib

from datetime import datetime
from fastapi.responses import HTMLResponse
from starlette.status import HTTP_200_OK
import threading, requests, time
from multiprocessing import Process, Queue

from app.core import exceptions as ex
from app.core import util
from app.core.config import *
from app.core.config import PROXY_PREFIX, api_same_origin
from app.service import batch_service
from app.models.ums import *
from app.schemas.admin.ums import *
from app.routers.ums import *

router = APIRouter (
    prefix = PROXY_PREFIX, # /be 
    tags=["batch"],
)

# PUSH_TOKEN = "m3zzaZ6Nf7fzngj1XKhCU88DW0JNNtU4"
# PUSH_URL = "https://openapi2.byapps.co.kr/v2/"

# headers = {
#     'Authorization': PUSH_TOKEN,
#     'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'
# }

# def push_send_task (v: dict, que: Any, request: Request):

#     print(" ")
#     print(" ### sub thread start ", threading.currentThread().getName())

#     send_param = {}
#     send_param.update({"uid": v["bars_uuid"]})
#     send_param.update({"os": v["device_os"]})
#     send_param.update({"title": v["push_title"]})
#     send_param.update({"msg": v["push_msg"]})

#     if v["push_img"] != "" :
#         send_param.update({"img": v["push_img"]})

#     if v["push_link"] != "" :
#         send_param.update({"url": v["push_link"]})

#     timestr = util.getNow("%Y-%m-%d")
#     file_name = "push_send." + timestr + ".log"
#     logm = ""

#     response = {}
#     push_result = ""
#     try : 
#         prams = {}
#         prams["data"] = json.dumps(send_param)
#         response = requests.post(PUSH_URL, headers=headers, data=prams).text
#         if str(response) != "" :
#             response = json.loads(response)
#             push_result = response["result"]
#             # print(push_result)
#     except Exception as e:
#         print(e)
#         push_result = {
#             "code": "99",
#             "msg": str(e),
#             "result": "99",
#         }

#     push_response_json = {}
#     push_response_json["bars_uuid"] = v["bars_uuid"]
#     push_response_json["msg_uid"] = v["uid"]
#     push_response_json["user_id"] = v["user_id"]
#     push_response_json["send_at"] = util.getNow()
#     push_response_json["result"] = push_result
#     logm = logm + json.dumps(push_response_json, ensure_ascii=False, indent=4) + "\n"
#     util.file_open (
#         "/usr/src/app/data/dream-backend/batch/"
#         ,file_name
#         ,logm
#     )

#     # print(json.dumps(push_result, ensure_ascii=False, indent=4))
#     que.put({
#          "msg_uid": push_response_json["msg_uid"]
#         ,"send_at": push_response_json["send_at"]
#         ,"push_result": json.dumps(push_result, ensure_ascii=False, indent=4)
#     })

#     print(" ### sub thread end ", threading.currentThread().getName())
#     print(" ")

# @router.get("/batch/push/send", dependencies=[Depends(api_same_origin)])
# async def 배치_푸시_보내기 (
#      request: Request
#     ,x_token: Union[str, None] = Header(default=None) 
# ) :
#     request.state.inspect = frame()
#     request.state.body = await util.getRequestParams(request)

#     if x_token != "f2210dacd9c6ccb8133606d94ff8e61d99b477fd" :
#         return "not vaild token"

#     print("### main thread start")
    
#     push_list = batch_service.push_send_list(request)
#     request.state.inspect = frame()

#     if len(push_list) == 0 :
#         return

#     datas = [] # bind data for bulk update  
#     que = Queue()
#     for v in push_list:
#         t1 = threading.Thread(target=push_send_task, args=(util.object_as_dict(v), que, request))
#         t1.daemon = True 
#         t1.start()
#         que_data = que.get()
#         # print(" ")
#         # print(str(que_data))
#         # print(" ")
#         datas.append(que_data)

#     # print(" ")
#     # print("msg bulk update ", datas)
#     # print(" ")
#     batch_service.bulk_update_push_message(request, datas)
#     request.state.inspect = frame()

#     # print("msg post process ")
#     batch_service.push_booking_jungry(request)
#     request.state.inspect = frame()
    
#     print("### main thread end")

#     return



# @router.get("/batch/test", dependencies=[Depends(api_same_origin)])
# async def 배치_테스트 (
#      request: Request
#     ,x_token: Union[str, None] = Header(default=None) 
# ) :
#     request.state.inspect = frame()
#     request.state.body = await util.getRequestParams(request)

#     timestr = util.getNow("%Y-%m-%d")
#     file_name = "test." + timestr + ".log"
#     logm = ""
#     logm = str(util.getNow()) + x_token + "\n"
#     util.file_open (
#         "/usr/src/app/data/dream-backend/batch/"
#         ,file_name
#         ,logm
#     )


#     return




