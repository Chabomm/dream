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
from app.schemas.admin.board import *
from app.service.admin import board_service
from app.service.admin.setup import roles_service

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/admin/board"],
)

# /be/admin/board/list
@router.post("/admin/board/list", dependencies=[Depends(api_same_origin)])
async def 관리자_게시판_리스트(
     request: Request
    ,page_param: PPage_param
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    if not page_param.page or int(page_param.page) == 0:
        page_param.page = 1

    if not page_param.page_view_size or int(page_param.page_view_size) == 0 :
        page_param.page_view_size = 30

    res = board_service.list(request, page_param) 
    request.state.inspect = frame()

    return res

# /be/admin/board/filter
@router.post("/admin/board/filter", dependencies=[Depends(api_same_origin)])
async def 관리자_게시판리스트_필터조건 (
    request: Request
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)
    request.state.body = await util.getRequestParams(request)

    result = {}
    result.update({"skeyword_type": [
        {"key": 'board_name', "text": '게시판 제목'},
    ]})
    

    # board type list (게시판 유형)
    result.update({"board_type": [
        {"key": 'notice', "value": 'notice'},
        {"key": 'faq', "value": 'faq'},
        {"key": 'common', "value": 'common'},
        {"key": 'gallery', "value": 'gallery'},
    ]})

    return result

# /be/admin/board/read
@router.post("/admin/board/read", dependencies=[Depends(api_same_origin)])
async def 관리자_게시판_상세(
    request: Request
    ,pRead : PRead
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    result = {}
    if pRead.uid == 0 :
        res = Board()
    else :
        res = board_service.read(request, pRead.uid)

    if res is None :
        return ex.ReturnOK(404, "게시판이 존재하지 않습니다", request)
        
    result.update({"values": res})
    result.update({"filter": {}})

    result["filter"].update({"site_id": [
        {"key": 'admin', "value": '어드민'},
        {"key": 'manager', "value": '고객사어드민'}
    ]})

    result["filter"].update({"board_type": [
        {"key": 'gallery', "value": '갤러리'},
        {"key": 'qna', "value": '질의응답'},
        {"key": 'common', "value": '일반'}
    ]})

    roles = roles_service.admin_rols_list(request)
    request.state.inspect = frame()
    result["filter"].update({"roles": roles["list"]})

    return result


# be/admin/board/edit
@router.post("/admin/board/edit", dependencies=[Depends(api_same_origin)])
async def 관리자_게시판_편집(
     request: Request
    ,board: Board
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    # 등록
    if board.mode == "REG" :
        res = board_service.create(request, board)
        request.state.inspect = frame()
        return ex.ReturnOK(200, "등록이 완료되었습니다.", request, {"uid" : res.uid})

    # 수정
    if board.mode == "MOD" :
        res = board_service.update(request, board)
        request.state.inspect = frame()
        return ex.ReturnOK(200, "수정이 완료되었습니다.", request, {"uid" : res.uid})
    
    # 삭제
    if board.mode == "DEL" :
        board_service.delete(request, board.uid)
        request.state.inspect = frame()
        return ex.ReturnOK(200, "삭제 완료", request)
    