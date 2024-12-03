import os
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Body
from fastapi.responses import RedirectResponse, JSONResponse
from inspect import currentframe as frame
import jwt
import requests
import json
import re
from fastapi.encoders import jsonable_encoder
import urllib

from app.deps.auth import get_current_active_admin
from app.schemas.admin.auth import *
from app.core import exceptions as ex
from app.core import util
from app.core.config import *
from app.core.config import PROXY_PREFIX, api_same_origin
from app.models.session import *
from app.models.ums import *
from app.schemas.admin.ums import *
from app.service.admin import ums_service

router = APIRouter (
    prefix = PROXY_PREFIX,
    tags=["admin/ums"],
)

# /be/admin/ums/tmpl/list 
# 세션복원을 위해 ServerSide에서 호출은 자체 백엔드 호출로함
@router.post("/admin/ums/tmpl/list", dependencies=[Depends(api_same_origin)])
async def UMS템플릿_리스트 (
     request: Request
    ,page_param: PPage_param
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)
    request.state.body = await util.getRequestParams(request)

    if not page_param.page or int(page_param.page) == 0:
        page_param.page = 1
    
    if not page_param.page_view_size or int(page_param.page_view_size) == 0 :
        page_param.page_view_size = 30

    URL = os.environ.get('UMS_URL') + "/ums/tmpl/list"

    headers = {
        'Content-Type': 'application/json; charset=utf-8'
        ,'x-user-ip': request.state.user_ip
        ,'Authorization': "Bearer " + user.access_token
    }
    
    result = ""
    params = json.dumps(jsonable_encoder(page_param))
    try : 
        result = requests.post(URL, headers=headers, data=params, timeout=1).text
        result = json.loads(result)
    except Exception as e:
        return ex.ReturnOK(500, str(e), request, {"params":params, "list": []})
    
    return result

# /be/admin/ums/push/booking/list
# 세션복원을 위해 ServerSide에서 호출은 자체 백엔드 호출로함
@router.post("/admin/ums/push/booking/list", dependencies=[Depends(api_same_origin)])
async def 푸시발송예약_리스트(
    request: Request
    ,page_param: PPage_param
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)
    request.state.body = await util.getRequestParams(request)

    if not page_param.page or int(page_param.page) == 0:
        page_param.page = 1
    
    if not page_param.page_view_size or int(page_param.page_view_size) == 0 :
        page_param.page_view_size = 30

    URL = os.environ.get('UMS_URL') + "/ums/push/booking/list"

    headers = {
        'Content-Type': 'application/json; charset=utf-8'
        ,'x-user-ip': request.state.user_ip
        ,'Authorization': "Bearer " + user.access_token
    }
    
    result = ""
    params = json.dumps(jsonable_encoder(page_param))
    try : 
        result = requests.post(URL, headers=headers, data=params, timeout=1).text
        result = json.loads(result)
    except Exception as e:
        return ex.ReturnOK(500, str(e), request, {"params":params, "list": []})
    
    return result






















# /be/admin/ums/tmpl/list
# @router.post("/admin/ums/tmpl/list", dependencies=[Depends(api_same_origin)])
# async def UMS템플릿_리스트 (
#      request: Request
#     ,page_param: PPage_param
#     ,user: TokenDataAdmin = Depends(get_current_active_admin)
# ):
#     request.state.inspect = frame()
#     user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)
#     request.state.body = await util.getRequestParams(request)

#     if not page_param.page or int(page_param.page) == 0:
#         page_param.page = 1
    
#     if not page_param.page_view_size or int(page_param.page_view_size) == 0 :
#         page_param.page_view_size = 30

#     res = ums_service.ums_list(request, page_param) 
#     request.state.inspect = frame()
#     return res

# /be/admin/ums/tmpl/filter
# @router.post("/admin/ums/tmpl/filter", dependencies=[Depends(api_same_origin)])
# async def UMS템플릿_리스트_필터조건(
#     request: Request
#     ,user: TokenDataAdmin = Depends(get_current_active_admin)
# ):
#     request.state.inspect = frame()
#     user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)
#     request.state.body = await util.getRequestParams(request)

#     result = {}
#     result.update({"skeyword_type": [
#         {"key": 'subject', "text": '제목'},
#         {"key": 'tmpl_code', "text": '템플릿 코드'}, 
#     ]})

#     # 분류
#     result.update({"ums_type": [
#         {"key": 'email', "text": '이메일', "checked": True},
#         {"key": 'at', "text": '알림톡', "checked": True},
#         {"key": 'sms', "text": '문자', "checked": True},
#     ]})

#     # 프로필
#     result.update({"profile": [
#         {"key": 'indend', "text": '인디앤드코리아', "checked": True},
#         {"key": 'eum', "text": '인천e몰', "checked": True},
#         {"key": 'goolbi', "text": '굴비몰', "checked": True},
#         {"key": 'dream', "text": '복지드림', "checked": True},
#     ]})

#     # 플랫폼
#     result.update({"platform": [
#         {"key": 'manager', "text": '매니저', "checked": True},
#         {"key": 'admin', "text": '관리자', "checked": True},
#     ]})

#     # 레이아웃
#     layouts = ums_service.layout_list(request)
#     result.update({"layout_uid": layouts})

#     return result
    
# /be/admin/ums/tmpl/read
# @router.post("/admin/ums/tmpl/read", dependencies=[Depends(api_same_origin)])
# async def UMS템플릿_상세(
#     request: Request
#     ,pRead : PRead
#     ,user: TokenDataAdmin = Depends(get_current_active_admin)
# ):
#     copy_deps_user = user # router Depends 때문에 따로 복사해둠
#     request.state.inspect = frame()
#     user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)
#     request.state.body = await util.getRequestParams(request)

#     if pRead.uid == 0 :
#         return UmsTmpl()
    
#     res = ums_service.ums_read(request, pRead.uid)
#     request.state.inspect = frame()

#     if res is None :
#         return ex.ReturnOK(404, "페이지를 불러오는데 실패하였습니다.", request)
    
#     jsondata = {}
#     jsondata.update({"values": res})
#     jsondata.update({"filter": await UMS템플릿_리스트_필터조건(request, copy_deps_user)})
        
#     return jsondata

# /be/admin/ums/tmpl/edit
# @router.post("/admin/ums/tmpl/edit", dependencies=[Depends(api_same_origin)])
# async def ums템플릿_편집(
#     request: Request
#     ,umsTmpl: UmsTmpl
#     ,user: TokenDataAdmin = Depends(get_current_active_admin)
# ):
#     request.state.inspect = frame()
#     user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)
#     request.state.body = await util.getRequestParams(request)

#     if umsTmpl.mode == "REG" : # 등록
#         res = ums_service.ums_create(request, umsTmpl)
#         request.state.inspect = frame()
#         return ex.ReturnOK(200, "ums 등록 완료", request, {"uid" : res.uid})

#     if umsTmpl.mode == "MOD" : # 수정
#         res = ums_service.ums_update(request, umsTmpl)
#         request.state.inspect = frame()
#         return ex.ReturnOK(200, "ums 수정 완료", request, {"uid" : res.uid})

#     if umsTmpl.mode == "DEL" : # 삭제
#         res = ums_service.ums_delete(request, umsTmpl.uid)
#         request.state.inspect = frame()
#         return ex.ReturnOK(200, "ums 삭제 완료", request, {"uid" : res.uid})
    
# # /be/admin/ums/tmpl/preview
# @router.post("/admin/ums/tmpl/preview", dependencies=[Depends(api_same_origin)])
# async def UMS템플릿_프리뷰(
#     request: Request
#     ,umsPreviewInput : UmsPreviewInput
#     ,user: TokenDataAdmin = Depends(get_current_active_admin)
# ):
#     request.state.inspect = frame()
#     user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)
#     request.state.body = await util.getRequestParams(request)

#     if umsPreviewInput.uid == 0 :
#         return ex.NotFoundData
    
#     res = ums_service.ums_read(request, umsPreviewInput.uid)
#     request.state.inspect = frame()

#     if res is None :
#         return ex.ReturnOK(404, "페이지를 불러오는데 실패하였습니다.", request)
    
#     layout = ums_service.ums_layout_read(request, umsPreviewInput.layout_uid)
#     request.state.inspect = frame()

#     preview = layout.content.replace("#{contents}", res.content)
    
#     jsondata = {}
#     jsondata.update({"values": res})
#     jsondata.update({"preview": preview})
        
#     return jsondata

























# ===== [ S ] PUSH 예약 리스트 ====== #

# /be/admin/ums/push/booking
# @router.post("/admin/ums/push/booking/list", dependencies=[Depends(api_same_origin)])
# async def 푸시발송예약_리스트(
#     request: Request
#     ,page_param: PPage_param
#     ,user: TokenDataAdmin = Depends(get_current_active_admin)
# ):
#     request.state.inspect = frame()
#     user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)
#     request.state.body = await util.getRequestParams(request)

#     if not page_param.page or int(page_param.page) == 0:
#         page_param.page = 1
    
#     if not page_param.page_view_size or int(page_param.page_view_size) == 0 :
#         page_param.page_view_size = 30

#     res = ums_service.push_booking_list(request, page_param) 
#     request.state.inspect = frame()
#     return res
  
# /be/admin/ums/push/booking/filter
# @router.post("/admin/ums/push/booking/filter", dependencies=[Depends(api_same_origin)])
# async def 푸시발송예약_리스트_필터조건 (
#      request: Request
#     ,user: TokenDataAdmin = Depends(get_current_active_admin)
# ):
#     request.state.inspect = frame()
#     user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)
#     request.state.body = await util.getRequestParams(request)

#     result = {}
#     result.update({"skeyword_type": [
#         {"key": 'push_title', "text": '푸시 제목'},
#         {"key": 'push_msg', "text": '푸시 내용'},
#         {"key": 'create_user', "text": '등록자'},
#     ]})

#     # 수신대상
#     result.update({"rec_type": [
#         {"key": 'A', "text": '앱사용자전체', "checked": True},
#         {"key": 'P', "text": '고객사', "checked": True},
#         {"key": 'S', "text": '개별', "checked": True},
#     ]})

#     # 발송상태
#     result.update({"state": [
#         {"key": '100', "text": '대기', "checked": True},
#         {"key": '200', "text": '발송완료', "checked": True},
#         {"key": '300', "text": '발송취소', "checked": True},
#     ]})

#     return result

# # /be/admin/ums/push/booking/read
# @router.post("/admin/ums/push/booking/read", dependencies=[Depends(api_same_origin)])
# async def 푸시발송예약_상세(
#     request: Request
#     ,pRead : PRead
#     ,user: TokenDataAdmin = Depends(get_current_active_admin)
# ):
#     copy_deps_user = user # router Depends 때문에 따로 복사해둠
#     request.state.inspect = frame()
#     user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)
#     request.state.body = await util.getRequestParams(request)

#     if pRead.uid == 0 :
#         res = PushBooking()
#     else :
#         res = ums_service.push_booking_read(request, pRead.uid)
#         request.state.inspect = frame()

#     if res is None :
#         return ex.ReturnOK(404, "페이지를 불러오는데 실패하였습니다.", request)
    
#     jsondata = {}

#     if res.uid > 0 :
#         values = dict(zip(res.keys(), res))
#         values.update({"booking_at_date": {
#             "startDate" : str(res.booking_at)[0:10]
#             ,"endDate" : str(res.booking_at)[0:10]
#         }})
#         values.update({"booking_at_time": str(res.booking_at)[11:19]})
#     else :
#         values = res

#     jsondata.update({"values": values})
#     jsondata.update({"filter": await 푸시발송예약_리스트_필터조건(request, copy_deps_user)})
#     return jsondata


# /be/admin/ums/push/booking/edit
# @router.post("/admin/ums/push/booking/edit", dependencies=[Depends(api_same_origin)])
# async def 푸시발송예약_편집(
#     request: Request
#     ,pushBooking: PushBooking = Body(
#         ...,
#         examples = {
#             "example01" : {
#                 "summary": "푸시발송예약 등록예시 01",
#                 "description": "",
#                 "value": {
#                      "mode" : "REG"
#                     ,"push_title" : "예약발송 #{복지몰명} 테스트"
#                     ,"push_msg" : "예약발송 #{고객사명} 테스트"
#                     ,"push_img" : ""
#                     ,"rec_type" : "P"
#                     ,"send_type" : "20230519130000"
#                     ,"partners" : ["143", "129", "140", "136"]
#                 }
#             },
#         }
#     )
#     ,user: TokenDataAdmin = Depends(get_current_active_admin)
# ):
#     copy_deps_user = user # router Depends 때문에 따로 복사해둠
#     request.state.inspect = frame()
#     user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)
#     request.state.body = await util.getRequestParams(request)
    
#     # 등록
#     if pushBooking.mode == "REG" :
#         res = ums_service.push_booking_create(request, pushBooking)
#         request.state.inspect = frame()
#         return ex.ReturnOK(200, "ums 등록 완료", request, {"uid" : res.uid})

#     # 수정
#     if pushBooking.mode == "MOD" :
#         res = ums_service.push_booking_update(request, pushBooking)
#         request.state.inspect = frame()
#         return ex.ReturnOK(200, "ums 수정 완료", request, {"uid" : res.uid})

#     # # 삭제
#     # if pushBooking.mode == "DEL" :
#     #     res = ums_service.push_booking_delete(request, pushBooking.uid)
#     #     request.state.inspect = frame()
#     #     return ex.ReturnOK(200, "ums 삭제 완료", request, {"uid" : res.uid})
    

# # /be/admin/ums/push/rec_type/partners
# @router.post("/admin/ums/push/rec_type/partners", dependencies=[Depends(api_same_origin)])
# async def 푸시발송예약_수신대상_고객사(
#     request: Request
#     ,user: TokenDataAdmin = Depends(get_current_active_admin)
# ):
#     request.state.inspect = frame()
#     user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)
#     request.state.body = await util.getRequestParams(request)

#     res = ums_service.rec_type_partners(request) 
#     request.state.inspect = frame()
#     return res


# # /be/admin/ums/push/booking/send/list
# @router.post("/admin/ums/push/booking/send/list", dependencies=[Depends(api_same_origin)])
# async def 발송_예정_내역 (
#     request: Request
#     ,page_param : PushBookingMsgListInput
#     ,user: TokenDataAdmin = Depends(get_current_active_admin)
# ):
#     request.state.inspect = frame()
#     user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)
#     request.state.body = await util.getRequestParams(request)

#     if not page_param.page or int(page_param.page) == 0:
#         page_param.page = 1
    
#     if not page_param.page_view_size or int(page_param.page_view_size) == 0 :
#         page_param.page_view_size = 30

#     res = ums_service.push_send_list(request, page_param) 
#     request.state.inspect = frame()

#     res_tester = ums_service.push_booking_tester_list(request)
#     request.state.inspect = frame()

#     jsondata = {}
#     jsondata.update({"list": res["list"] })
#     jsondata.update({"list_tester": res_tester["list"] })
#     return jsondata


#     return res

# # ===== [ E ] PUSH 예약 리스트 ====== #


# PUSH_TOKEN = "m3zzaZ6Nf7fzngj1XKhCU88DW0JNNtU4"
# PUSH_URL = "https://openapi2.byapps.co.kr/v2/"
# PUSH_HEADERS = {
#     'Authorization': PUSH_TOKEN,
#     'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'
# }

# # /be/admin/ums/push/send/tester
# @router.post("/admin/ums/push/send/tester", dependencies=[Depends(api_same_origin)])
# async def 푸시발송_테스트(
#      request: Request
#     ,pushTesterInput : PushTesterInput
#     ,user: TokenDataAdmin = Depends(get_current_active_admin)
# ):
#     request.state.inspect = frame()
#     user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)
#     request.state.body = await util.getRequestParams(request)

#     res = ums_service.read_tester(request, pushTesterInput) 
#     request.state.inspect = frame()

#     send_param = {}
#     send_param.update({"uid": res.bars_uuid})
#     send_param.update({"os": res.device_os})
#     send_param.update({"title": res.push_title})
#     send_param.update({"msg": res.push_msg})
    
#     if res.push_img != "" :
#         send_param.update({"img": res.push_img})

#     if res.push_link != "" :
#         send_param.update({"url": res.push_link})

#     timestr = util.getNow("%Y-%m-%d")
#     file_name = "push_send_tester." + timestr + ".log"
#     logm = ""

#     response = {}
#     push_result = ""
#     try : 
#         prams = {}
#         prams["data"] = json.dumps(send_param)
#         response = requests.post(PUSH_URL, headers=PUSH_HEADERS, data=prams).text
#         if str(response) != "" :
#             response = json.loads(response)
#             if str(response["result"]["result"]) == "1" :
#                 push_result = "1"
#             else :
#                 push_result = str(response)
#     except Exception as e:
#         print(e)
#         push_result = str(e)

#     push_response_json = response
#     push_response_json["tester"] = dict(zip(res.keys(), res))
#     push_response_json["bars_uuid"] = res.bars_uuid
#     push_response_json["msg_uid"] = res.uid
#     push_response_json["user_id"] = res.user_id
#     push_response_json["push_result"] = push_result
#     push_response_json["send_at"] = util.getNow()
    
#     logm = logm + json.dumps(push_response_json, ensure_ascii=False, indent=4) + "\n"
#     util.file_open (
#         "/usr/src/app/data/dream-backend/batch/"
#         ,file_name
#         ,logm
#     )

    

#     return ex.ReturnOK(200, "", request, push_response_json)

















