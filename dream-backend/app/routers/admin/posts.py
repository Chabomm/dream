from fastapi import APIRouter, Depends, Request, Body
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from inspect import currentframe as frame
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse
from app.core import exceptions as ex
from app.core import util
from app.core.config import PROXY_PREFIX, api_same_origin
from app.core.database import get_session
from app.deps.auth import get_current_active_admin

from app.models.board import *
from app.schemas.admin.board import *
from app.schemas.admin.auth import *
from app.service.admin import posts_service, board_service

router = APIRouter(
    prefix=PROXY_PREFIX,
    tags=["/admin/posts"],
)

def 관리자_게시물_필터리스트 (request: Request, is_board_master: Boolean) :
    filter = {}
    filter.update({"skeyword_type": [
        {"key": 'title', "value": '제목'},
        {"key": 'contents', "value": '본문내용'},
        {"key": 'create_name', "value": '작성자'}
    ]})
    filter.update({"state": [
        {"key": '100', "value": '미답변'},
        {"key": '200', "value": '답변완료'},
        {"key": '300', "value": '공지'},
    ]})

    # board list (게시판)
    if is_board_master :
        board_list = board_service.board(request)
        request.state.inspect = frame()
        filter.update({"board_uid": board_list["list"]})
    else :
        filter.update({"board_uid": []})
        
    filter.update({"is_board_master": is_board_master})
    return filter

# /be/admin/posts/init
@router.post("/admin/posts/init", dependencies=[Depends(api_same_origin)])
async def 관리자_게시물_init (
     request: Request
    ,postInput: PostInput
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    result = {}

    # [ S ] 초기 파라메터
    params = {
         "page" : 1
        ,"page_view_size": 30
        ,"page_size": 0
        ,"page_total": 0
        ,"page_last": 0
        ,"filters": {
            "board_uid" : postInput.uid
        }
    }
    result.update({"params": params})
    # [ S ] 초기 파라메터

    result.update({"filter": 관리자_게시물_필터리스트(request, postInput.is_board_master)}) # 초기 필터

    return result

# /be/admin/posts/list
@router.post("/admin/posts/list", dependencies=[Depends(api_same_origin)])
async def 관리자_게시물_리스트(
    request : Request
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
    
    if util.checkNumeric(page_param.filters["board_uid"]) >= 0 :
        board = posts_service.board_read(request, page_param.filters["board_uid"]) 
        request.state.inspect = frame()

    res = posts_service.posts_list(request, page_param, board) 
    request.state.inspect = frame()

    return res

# /be/admin/posts/read
@router.post("/admin/posts/read", dependencies=[Depends(api_same_origin)])
async def 관리자_게시물_상세(
     request: Request
    ,postInput : PostInput
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    board = Board()
    person = {}
    files = []
    replys = {}
    replys["list"] = []
    prev_next = {}
    prev_next["prev_posts"] = {}
    prev_next["next_posts"] = {}

    if postInput.uid == 0 :
        posts = Posts()
        values = posts.dict()
        values["files"] = files
        if str(values["files"]) == "[]" :
            values["files"].append({"uid":-1})
    else :
        posts = posts_service.posts_read(request, postInput.uid)
        request.state.inspect = frame()

        if posts is None :
            return ex.ReturnOK(404, "게시물을 찾을 수 없습니다.", request)

        board = posts_service.board_read(request, posts.board_uid) 
        request.state.inspect = frame()

        if postInput.uid != 0 and board is None :
            return ex.ReturnOK(406, "페이지를 불러오는데 실패하였습니다.", request)
        
        if postInput.uid != 0 and board.is_display != "T" :
            return ex.ReturnOK(407, "페이지를 불러오는데 실패하였습니다.", request)
        
        board = dict(zip(board.keys(), board))

        board["poss_insert"] = False
        if user.role == "admin" :
            board["poss_insert"] = True 
        else :
            for p in board["permission_read"] :
                if p in user.roles :
                    board["poss_insert"] = True 
        # posts wirte permission check

        if board["poss_insert"] == False :
            return ex.ReturnOK(301, "권한이 불충분 합니다.", request)

    
        prev_next = posts_service.read_prev_next_posts(request, postInput.uid, posts.board_uid)
        request.state.inspect = frame()
    
        person = posts_service.posts_person_read(request, postInput.uid)
        request.state.inspect = frame()
        
        files = posts_service.posts_files_list(request, postInput.uid) 
        request.state.inspect = frame()

        if board["is_comment"] == "T" :
            replys = posts_service.posts_reply_list(request, postInput.uid) 
            request.state.inspect = frame()
        else :
            replys = {"list":[]}

        values = dict(zip(posts.keys(), posts))
        values["files"] = files

        if str(values["files"]) == "[]" :
            values["files"].append({"uid":-1})
    
    jsondata = {}
    jsondata.update(posts)
    jsondata.update({"values": values})
    jsondata.update({"board": board})
    jsondata.update({"person": person})
    jsondata.update({"files": files})
    jsondata.update({"replys": replys["list"]})
    jsondata.update({"prev_posts": prev_next["prev_posts"]})
    jsondata.update({"next_posts": prev_next["next_posts"]})
    jsondata.update({"filter": 관리자_게시물_필터리스트(request, postInput.is_board_master)})
    
    return ex.ReturnOK(200, "", request, jsondata, False)

# /be/admin/posts/edit
@router.post("/admin/posts/edit", dependencies=[Depends(api_same_origin)])
async def 관리자_게시물_편집(
     request:Request
    ,posts: Posts
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    if posts.mode == "REG" : # 등록
        res = posts_service.posts_create(request, posts)
        request.state.inspect = frame()
        return ex.ReturnOK(200, "게시물 등록 완료", request, {"uid" : res.uid})

    if posts.mode == "MOD" : # 수정
        res = posts_service.posts_update(request, posts)
        request.state.inspect = frame()
        return ex.ReturnOK(200, "게시물 수정 완료", request, {"uid" : res.uid})
   
    if posts.mode == "DEL" : # 삭제
        res = posts_service.posts_delete(request, posts.uid)
        request.state.inspect = frame()
        return ex.ReturnOK(200, "게시물 삭제 완료", request, {"uid" : res.uid})

# /be/admin/posts/reply/edit
@router.post("/admin/posts/reply/edit", dependencies=[Depends(api_same_origin)])
async def 관리자_게시물_댓글_편집(
    request: Request
    ,postsReplyInput: PostsReplyInput
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)
    
    if postsReplyInput.mode == "REG" : # 등록
        res = posts_service.posts_reply_create(request, postsReplyInput)
        request.state.inspect = frame()
        return ex.ReturnOK(200, "등록이 완료되었습니다.", request, {"uid" : res.posts_uid})

    if postsReplyInput.mode == "DEL" : # 삭제
        res = posts_service.posts_reply_delete(request, postsReplyInput.uid)
        request.state.inspect = frame()
        return ex.ReturnOK(200, "삭제가 완료되었습니다.", request, {"uid" : res.posts_uid})
    
@router.post("/admin/posts/file/download/{file_uid}")
async def 게시물_첨부파일_다운로드 (
    request: Request
    ,file_uid: int
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    if request.headers.get('sec-fetch-site') == "same-origin" :
        res = posts_service.posts_files_read(request, file_uid)
        request.state.inspect = frame()

        posts_service.insert_posts_files_log(request, res)
        request.state.inspect = frame()
    
        file_path = res.file_url
        # pinrt(file_path)
        # file_path = file_path.replace("/be/static/", "/usr/src/app/data/static/")
        file_path = "/usr/src/app/resource/" + file_path
        return FileResponse(file_path, filename=res.fake_name)

    elif request.headers.get('host') == "backend:5000" :
        print ("api_same_origin OK")

    else :
        print ("api_same_origin 비정상적인 호출")
    

# /be/admin/posts/intranet
@router.post("/admin/posts/intranet", dependencies=[Depends(api_same_origin)])
async def 관리자_인트라넷_게시물 (
     request : Request
    ,pRead: PRead
    ,user: TokenDataAdmin = Depends(get_current_active_admin)
):  
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataAdmin(user), getTokenDataAdmin(user)

    result = {}

    # [ S ] 게시판 정보
    board = posts_service.board_read(request, pRead.uid) 
    request.state.inspect = frame()

    board = dict(zip(board.keys(), board))

    board["poss_insert"] = False
    
    if user.role == "admin" :
        board["poss_insert"] = True 
    else : 
        if board["permission_write"] != [] :
            for p in board["permission_write"] :
                if p in user.roles :
                    board["poss_insert"] = True 


    result.update({"board": board})
    
    # [ S ] 초기 파라메터
    params = {
         "page" : 1
        ,"page_view_size": 30
        ,"page_size": 0
        ,"page_total": 0
        ,"page_last": 0
        ,"filters": {
            "board_uid" : pRead.uid
        }
    }
    result.update({"params": params})
    # [ S ] 초기 파라메터

    filter = {}
    filter.update({"skeyword_type": [
        {"key": 'title', "value": '제목'},
        {"key": 'contents', "value": '본문내용'},
        {"key": 'create_name', "value": '작성자'}
    ]})
    filter.update({"state": [
        {"key": '100', "value": '미답변'},
        {"key": '200', "value": '답변완료'},
        {"key": '300', "value": '공지'},
    ]})
    result.update({"filter": filter})

    return result