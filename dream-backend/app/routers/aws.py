from fastapi import APIRouter, Request
from fastapi.responses import FileResponse

from inspect import currentframe as frame

from app.core import exceptions as ex
from app.core import util
from app.core.config import PROXY_PREFIX, api_same_origin

from fastapi.datastructures import UploadFile
from fastapi.exceptions import HTTPException
from fastapi.param_functions import File, Body, Form
from app.core.aws.s3_utils import S3_SERVICE
import datetime
import os

from app.schemas.aws import *
# from app.core import log

AWS_ACCESS_KEY_ID = "AAAAAAAAAAAAAAAAAAAA"
AWS_SECRET_ACCESS_KEY = "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"
AWS_REGION = "ap-northeast-1"

S3_Key = ""
s3_client = S3_SERVICE(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION)

router = APIRouter (
    prefix = PROXY_PREFIX, # /be 
    tags=["aws"],
)

# file_option: FileOption,
@router.post("/aws/upload", status_code=200, description="***** AWS S3 파일업로드 *****")
async def upload(
    file_object: UploadFile = File(...),
    bucket: str = Form("indend-homepage"),
    upload_path: str = Form(...)
):
    fake_name = file_object.filename
    current_time = datetime.datetime.now()
    split_file_name = os.path.splitext(fake_name)   #split the file name into two different path (string + extention)
    file_name = str(current_time.timestamp()).replace('.','')  #for realtime application you must have genertae unique name for the file
    file_ext = split_file_name[1]  #file extention
    data = file_object.file._file  # Converting tempfile.SpooledTemporaryFile to io.BytesIO
    
    print("bucket", bucket)
    print("upload_path", upload_path)
    print("fake_name", fake_name)
    print("current_time", current_time)
    print("split_file_name", split_file_name)
    print("file_name", file_name)
    print("file_ext", file_ext)
    print("data", data)

    if upload_path != "" and upload_path[0:1] == "/" :
        # 첫 글자에 / 빼기
        upload_path = upload_path[1:len(upload_path)]
    
    if upload_path != "" and upload_path[len(upload_path)-1:len(upload_path)] != "/" :
        # 마지막 글자에 / 없으면 넣기
        upload_path = upload_path + "/"

    uploads3 = await s3_client.upload_fileobj (
        bucket = bucket, 
        key = upload_path + file_name + file_ext, 
        fileobject = data
    )

    if uploads3:
        s3_url = f"https://{bucket}.s3.{AWS_REGION}.amazonaws.com/{upload_path}{file_name+file_ext}"
        return {
            "result_code": 200, 
            "result_msg": "",
            "s3_url": s3_url,
            "fake_name": fake_name,
            "file_name": file_name,
            "file_ext": file_ext
        }
    else:
        return {
            "result_code": 500, 
            "result_msg": "upload fail"
        }
    
# AWS 파일 다운로드
import urllib.request
@router.post("/aws/download")
async def aws_download(
    request: Request
    ,resultInput: ResultInput
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)

    url = resultInput.file_url
    split_imgs = url.split('/')
    file_name = split_imgs[len(split_imgs)-1]
    savelocation = "/usr/src/app/data/temp/" + file_name
    urllib.request.urlretrieve(url, savelocation)

    # temp 폴더의 파일 지우기

    return FileResponse(savelocation, filename=file_name)


# "/aws/temp/delete"
@router.post("/aws/temp/delete")
async def aws_temp_delete(
    request: Request
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)

    dir_path = "/usr/src/app/data/temp"

    file_list = os.listdir(dir_path)
    for file in file_list:
        file_path = os.path.join(dir_path, file)
        os.remove(file_path)

    return ''