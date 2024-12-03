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
from app.deps.auth import get_current_active_admin

from app.schemas.admin.auth import *
from app.schemas.admin.member import *
from app.service.admin import member_service

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/admin/member"],
)

# be/admin/member/list
@router.post("/admin/member/list", dependencies=[Depends(api_same_origin)])
async def 회원_리스트(
     request: Request
    ,page_param: PPage_param
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    if not page_param.page or int(page_param.page) == 0:
        page_param.page = 1

    if not page_param.page_view_size or int(page_param.page_view_size) == 0:
        page_param.page_view_size = 30

    res = member_service.list(request, page_param)
    request.state.inspect = frame()

    return res

# /be/admin/member/filter
@router.post("/admin/member/filter", dependencies=[Depends(api_same_origin)])
async def 회원_리스트_필터조건 (
    request: Request
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)
    request.state.body = await util.getRequestParams(request)

    result = {}
    result.update({"skeyword_type": [
        {"key": 'company_name', "text": '고객사명'},
        {"key": 'mall_name', "text": '복지몰명'},
        {"key": 'partner_code', "text": '고객사코드'},
        {"key": 'partner_id', "text": '고객사HOST'},
        {"key": 'user_id', "text": '회원아이디'},
        {"key": 'user_name', "text": '회원이름'},
    ]})

    # 진행상태
    result.update({"serve": [
        {"key": '', "text": '전체', "checked": True},
        {"key": '재직', "text": '재직', "checked": True},
        {"key": '휴직', "text": '휴직', "checked": True},
        {"key": '퇴직', "text": '퇴직', "checked": True},
    ]})

    return result

# be/admin/member/read
@router.post("/admin/member/read", dependencies=[Depends(api_same_origin)])
async def 회원_상세(
    request: Request
    ,pRead : PRead
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    if pRead.uid == 0 :
        return MemberInput()
    
    res = member_service.read(request, pRead.uid)
    request.state.inspect = frame()

    if res is None:
        return ex.ReturnOK(404, "회원정보가 존재하지 않습니다.", request)
        
    return res



# be/admin/member/edit
@router.post("/admin/member/edit", dependencies=[Depends(api_same_origin)])
async def 회원_편집(
    request: Request
    ,memberInput: MemberInput
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    # 수정
    if memberInput.mode == "MOD" :
        res = member_service.update(request, memberInput)
        request.state.inspect = frame()
        return ex.ReturnOK(200, "회원 수정 완료", request, {"uid":res["member_res"].uid})
    

# be/admin/member/partner/list
@router.post("/admin/member/partner/list", dependencies=[Depends(api_same_origin)])
async def 파트너_리스트(
     request: Request
    ,partnerSearchInput: PartnerSearchInput
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    res = member_service.partner_list(request, partnerSearchInput)
    request.state.inspect = frame()

    return res


#  ----------------------- [ S ] APP 리스트(device)
# be/admin/member/device/list
@router.post("/admin/member/device/list", dependencies=[Depends(api_same_origin)])
async def APP_리스트(
     request: Request
    ,page_param: PPage_param
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    if not page_param.page or int(page_param.page) == 0:
        page_param.page = 1

    if not page_param.page_view_size or int(page_param.page_view_size) == 0:
        page_param.page_view_size = 30

    res = member_service.app_list(request, page_param)
    request.state.inspect = frame()

    return res


# /be/admin/member/device/filter
@router.post("/admin/member/device/filter", dependencies=[Depends(api_same_origin)])
async def APP_리스트_필터조건 (
    request: Request
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)
    request.state.body = await util.getRequestParams(request)

    result = {}
    result.update({"skeyword_type": [
        {"key": 'company_name', "text": '고객사명'},
        {"key": 'mall_name', "text": '복지몰명'},
        {"key": 'partner_id', "text": '고객사HOST'},
        {"key": 'user_id', "text": '회원아이디'},
    ]})

    # 문자허용
    result.update({"is_sms": [
        {"key": '', "text": '전체', "checked": True},
        {"key": 'T', "text": '허용', "checked": True},
        {"key": 'F', "text": '거부', "checked": True},
    ]})
    # 이메일허용
    result.update({"is_mailing": [
        {"key": '', "text": '전체', "checked": True},
        {"key": 'T', "text": '허용', "checked": True},
        {"key": 'F', "text": '거부', "checked": True},
    ]})
    # 푸쉬허용
    result.update({"is_push": [
        {"key": '', "text": '전체', "checked": True},
        {"key": 'T', "text": '허용', "checked": True},
        {"key": 'F', "text": '거부', "checked": True},
    ]})

    return result