from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Body
from fastapi.responses import FileResponse, HTMLResponse
from inspect import currentframe as frame

from app.core import exceptions as ex
from app.core import util
from app.core.config import PROXY_PREFIX, api_same_origin

from fastapi.datastructures import UploadFile
from fastapi.exceptions import HTTPException
from fastapi.param_functions import File, Body, Form
import os

import uuid
from app.service.admin import board_service
from bs4 import BeautifulSoup
from PIL import Image

from app.schemas.admin.board import *
from app.schemas.admin.auth import *

from app.core import util
from app.core.database import format_sql
from app.core import exceptions as ex
from app.service import log_service
from app.service import files_service
from app.models.board import *
from app.models.files import *
from app.schemas.schema import *
from app.schemas.admin.board import *

from pydantic import BaseModel

from app.deps.auth import get_current_active_outbound
from app.schemas.auth import *

router = APIRouter (
    prefix = PROXY_PREFIX, # /be 
    tags=["upload"],
)

class InputHtmlRequse(BaseModel):
    path: str
    name: str

# /be/files/upload
@router.post("/files/upload")
async def 파일업로드 (
    request: Request,
    file_object: UploadFile = File(...),
    bucket: str = Form("dream"),
    upload_path: str = Form(...)
):
    fake_name = file_object.filename
    # current_time = datetime.datetime.now()
    split_file_name = os.path.splitext(fake_name)   #split the file name into two different path (string + extention)
    # file_name = str(current_time.timestamp()).replace('.','')  #for realtime application you must have genertae unique name for the file
    file_ext = split_file_name[1]  #file extention
    data = file_object.file._file  # Converting tempfile.SpooledTemporaryFile to io.BytesIO

    if upload_path != "" and upload_path[0:1] == "/" :
        # 첫 글자에 / 빼기
        upload_path = upload_path[1:len(upload_path)]
    
    if upload_path != "" and upload_path[len(upload_path)-1:len(upload_path)] != "/" :
        # 마지막 글자에 / 없으면 넣기
        upload_path = upload_path + "/"

    print("final upload_path : ", upload_path)
    
    UPLOAD_DIR = "/usr/src/app/resource/" + upload_path
    util.makedirs(UPLOAD_DIR)
    
    content = await file_object.read()
    filename = f"{str(uuid.uuid4())}" + file_ext  # uuid로 유니크한 파일명으로 변경
    with open(os.path.join(UPLOAD_DIR, filename), "wb") as fp:
        fp.write(content)  # 서버 로컬 스토리지에 이미지 저장 (쓰기)

    resource_prefix = "/resource/"
    if os.environ.get('PROFILE') == "production" :
        resource_prefix = "/resr/"

    return ex.ReturnOK(200, "", request, {
        "file_url": resource_prefix+ upload_path + filename,
        "fake_name": fake_name,
        "file_name": filename,
        "file_ext": file_ext
    })
    
# @router.get("/files/download/{photo_id}")
# async def download_photo(photo_id: int):
#     file_path = os.path.join("static/board/thumb/", "aca9cef4-9372-435d-afae-4a892174d6b9.jpg")
#     return FileResponse(file_path, media_type="image/jpeg", filename="aa.jpg")

# @router.post("/files/html", dependencies=[Depends(api_same_origin)])
# async def html(
#      request : Request
#     ,inputHtmlRequse: InputHtmlRequse
# ):  
#     # file_path = os.path.join("/usr/src/app/data/static/html/"+inputHtmlRequse.path, inputHtmlRequse.name)
#     file_path = os.path.join("/usr/src/app/resource/html/"+inputHtmlRequse.path, inputHtmlRequse.name)
#     print(file_path)
#     return FileResponse(file_path)


@router.get("/files/contents/thumb/{board_uid}")
async def contents_thumb(request: Request, board_uid: int):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    request.state.user = TokenDataAdmin (
         user_id = "system"
        ,user_name = "system"
    )

    db = request.state.db
    sql = ( 
        db.query(T_BOARD_POSTS)
        .filter(T_BOARD_POSTS.board_uid == board_uid, T_BOARD_POSTS.thumb == "", T_BOARD_POSTS.delete_at == None)
    )
    res = sql.first()

    print("게시물 번호 : ", res.uid)

    # [ S ] html tag 속 첫번째 이미지 주소 가져오기
    html = res.contents
    soup = BeautifulSoup(html, 'html.parser')
    anchor = soup.select_one("img")
    if res.uid == 10947 or anchor is None :
        res.thumb = None
        return "이미지 none " + str(res.uid)
    thumb_path = anchor.get("src")
    print("thumb_path : ", thumb_path)
    # [ E ] html tag 속 첫번째 이미지 주소 가져오기

    # [ S ] 이미지 resize
    basewidth = 500
    try :
        img = Image.open(thumb_path.replace("/be/static/", "/usr/src/app/resource/"))
        wpercent = (basewidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        img_resize = img.resize((basewidth,hsize), Image.ANTIALIAS)
        filename = img.filename.split('/')[-1]
        location = img.filename.split('/')[0:-1]
        title, ext = os.path.splitext(filename)
        new_path = '/'.join(location) + '/' + title + '-resize' + ext
        img_resize.save(new_path)
        print("new_path", new_path)
    except Exception as e: # 이미지가 없을때
        print(str(e))
        if 'http' in str(e) :
            return str(e)
        else :
            res.thumb = None
            return str(e)
    res.thumb = new_path.replace("/usr/src/app/resource/", "/be/static/") # 이미지 thumb로 업데이트
    print("res.thumb", res.thumb)
    # [ E ] 이미지 resize

    return "게시물 번호 : " + str(res.uid)


# @router.post ("/files/download/")
# async def download_photo2(request: Request
#     ,pRead: PRead = Body):
#     file_path = os.path.join("/usr/src/app/data/static/images/company/mobile/", "group_5271.png")
#     return FileResponse(file_path, filename="group_5271.png")






# /be/files/attach/upload
@router.post("/files/attach/upload")
async def 첨부파일_업로드 (
    request: Request
    ,file_object: UploadFile = File(...)
    ,upload_path: str = Form(...)
    ,table_uid: int = Form(...)
    ,table_name: str = Form(...)
    ,user: TokenDataOutbound = Depends(get_current_active_outbound)
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    user, request.state.user = getTokenDataOutbound(user), getTokenDataOutbound(user)

    fake_name = file_object.filename
    split_file_name = os.path.splitext(fake_name)
    file_ext = split_file_name[1]
    
    if upload_path != "" and upload_path[0:1] == "/" :
        upload_path = upload_path[1:len(upload_path)] # 첫 글자에 / 빼기
    
    if upload_path != "" and upload_path[len(upload_path)-1:len(upload_path)] != "/" :
        upload_path = upload_path + "/" # 마지막 글자에 / 없으면 넣기

    UPLOAD_DIR = "/usr/src/app/data/attach/" + upload_path
    util.makedirs(UPLOAD_DIR)
    
    content = await file_object.read()
    filename = f"{str(uuid.uuid4())}" + file_ext  # uuid로 유니크한 파일명으로 변경
    with open(os.path.join(UPLOAD_DIR, filename), "wb") as fp:
        fp.write(content)  # 서버 로컬 스토리지에 이미지 저장 (쓰기)

    files = Files (
         table_uid = table_uid
        ,table_name = table_name
        ,fake_name = fake_name
        ,file_name = filename
        ,file_ext = file_ext
        ,upload_path = upload_path + filename
    )
    f_item = files_service.create_files_attach(request, files)

    return ex.ReturnOK(200, "", request, {
        "file_uid": f_item.uid,
        "file_url": upload_path + filename,
        "fake_name": fake_name,
        "file_name": filename,
        "file_ext": file_ext
    })
    
# /be/files/attach/download
@router.get("/files/attach/download/{attach_uid}")
async def 첨부파일_다운로드(
    request: Request,
    attach_uid: int
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)
    
    res_attach = files_service.read_files_attach(request, attach_uid)
    print("res_attachres_attachres_attach",res_attach)
    file_path = os.path.join("/usr/src/app/data/attach/", res_attach.upload_path)
    print("file_path",file_path)
    return FileResponse(file_path)

