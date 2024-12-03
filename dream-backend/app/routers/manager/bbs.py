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

from app.schemas.schema import *
from app.service.manager import bbs_service
from app.schemas.manager.auth import *
from app.schemas.manager.board import *

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/manager/bbs"],
)

def 게시물_필터조건 (request: Request):
    request.state.inspect = frame()

    result = {}
    result.update({"skeyword_type": [
        {"key": 'title', "text": '제목'},
        {"key": 'contents', "text": '본문내용'},
        {"key": 'create_name', "text": '작성자'}
    ]})

    return result

# /be/manager/bbs/init
@router.post("/manager/bbs/init/{board_uid}", dependencies=[Depends(api_same_origin)])
async def 게시물내역_init (
     request: Request
    ,board_uid: int
    ,user: TokenDataManager = Depends(get_current_active_manager)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)

    result = {}

    # 게시판 config 정보
    board = bbs_service.read(request, board_uid)
    request.state.inspect = frame()
    result.update({"board": board})

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
        }
    }
    result.update({"params": params})
    # [ S ] 초기 파라메터

    result.update({"filter": 게시물_필터조건(request)}) # 초기 필터

    return result

# /be/manager/bbs/list
@router.post("/manager/bbs/list/{board_uid}", dependencies=[Depends(api_same_origin)])
async def 게시물내역 (
     request: Request
    ,page_param: PPage_param
    ,board_uid: int
    ,user: TokenDataManager = Depends(get_current_active_manager)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)

    if not page_param.page or int(page_param.page) == 0:
        page_param.page = 1

    if not page_param.page_view_size or int(page_param.page_view_size) == 0:
        page_param.page_view_size = 30

    res = bbs_service.posts_list(request, page_param, board_uid)
    request.state.inspect = frame()

    return res

# /be/manager/bbs/list
@router.post("/manager/bbs/list", dependencies=[Depends(api_same_origin)])
async def 게시물_리스트(
    request : Request
    ,boardListInput: BoardListInput
    ,user: TokenDataManager = Depends(get_current_active_manager)
):  
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)

    if not boardListInput.page or int(boardListInput.page) == 0:
        boardListInput.page = 1
    
    if not boardListInput.page_view_size or int(boardListInput.page_view_size) == 0 :
        boardListInput.page_view_size = 30
    
    res = bbs_service.board_list(request, boardListInput) 
    request.state.inspect = frame()

    return res

# /be/manager/bbs/read
@router.post("/manager/bbs/read", dependencies=[Depends(api_same_origin)])
async def 게시물_상세(
     request: Request
    ,uid : PRead
    ,user: TokenDataManager = Depends(get_current_active_manager)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)

    files = []
    replys = {}
    replys["list"] = []
    prev_next = {}
    prev_next["prev_posts"] = {}
    prev_next["next_posts"] = {}

    if uid.uid == 0 :
        board = Board()
        values = BoardEdit()
        # values = board.dict()
        # values["files"] = files
        # if str(values["files"]) == "[]" :
        #     values["files"].append({"uid":-1})
    else :
        board = bbs_service.read(request, uid.uid)
        request.state.inspect = frame()

        prev_next = bbs_service.read_prev_next(request, uid.uid, board.board_uid)
        request.state.inspect = frame()

        files = bbs_service.files_list(request, uid.uid) 
        request.state.inspect = frame()

        replys = bbs_service.reply_list(request, uid.uid) 
        request.state.inspect = frame()
        if replys is None :
            replys = {"list":[]}

        values = dict(zip(board.keys(), board))
        values["files"] = files

        if str(values["files"]) == "[]" :
            values["files"].append({"uid":-1})

    if board is None :
        return ex.ReturnOK(404, "게시물을 찾을 수 없습니다.", request)
        
    jsondata = {}
    jsondata.update(board)
    jsondata.update({"values":values})
    jsondata.update({"files": files})
    jsondata.update({"replys": replys["list"]})
    jsondata.update({"prev_posts": prev_next["prev_posts"]})
    jsondata.update({"next_posts": prev_next["next_posts"]})
    
    return ex.ReturnOK(200, "", request, jsondata, False)

# /be/manager/bbs/edit
@router.post("/manager/bbs/edit", dependencies=[Depends(api_same_origin)])
async def 게시물_편집(
     request:Request
    ,board: Board
    ,user: TokenDataManager = Depends(get_current_active_manager)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataManager(user), getTokenDataManager(user)

    if board.mode == "REG" : # 등록
        res = bbs_service.create(request, board)
        request.state.inspect = frame()
        return ex.ReturnOK(200, "게시물 등록 완료", request)

    if board.mode == "MOD" : # 수정
        res = bbs_service.update(request, board)
        request.state.inspect = frame()
        return ex.ReturnOK(200, "게시물 수정 완료", request, {"uid" : res.uid})
   
    if board.mode == "DEL" : # 삭제
        res = bbs_service.delete(request, board.uid)
        request.state.inspect = frame()
        return ex.ReturnOK(200, "게시물 삭제 완료", request, {"uid" : res.uid})