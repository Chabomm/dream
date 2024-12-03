from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, select, column, table, case
from fastapi import Request
from inspect import currentframe as frame
import math

from app.core import exceptions as ex
from app.core import util
from app.core.database import format_sql
from app.models.nice import *
from app.models.member import *
from app.schemas.nice import *
from app.service.log_service import *

# nice 등록
def create(request: Request, params: object):
    request.state.inspect = frame()
    db = request.state.db 

    db_item = T_NICE_CHECKPLUS (
         req_seq = params["reqseq"]
        ,client_id = params["client_id"]
        ,method = params["method"]
        ,success_url = params["success_url"]
        ,fail_url = params["fail_url"]
        ,client_ip = params["client_ip"]
        ,err_code = ""
        ,err_msg = ""
        ,create_at = util.getNow()
    )
    db.add(db_item)
    db.flush()
    return db_item

# nice 수정
def update(request: Request, params: object):
    request.state.inspect = frame()
    db = request.state.db
    
    # 기존 등록된 고객사 select 
    res = db.query(T_NICE_CHECKPLUS).filter(T_NICE_CHECKPLUS.req_seq == params["req_seq"]).first()

    if res is None:
        raise ex.NotFoundUser
    
    if params["err_code"] is not None and res.err_code != params["err_code"]:
        create_log(request, res.uid, "T_NICE_CHECKPLUS", "err_code", "에러코드", res.err_code, params["err_code"], "")
        request.state.inspect = frame()
        res.err_code = params["err_code"]

    if params["err_msg"] is not None and res.err_msg != params["err_msg"]:
        create_log(request, res.uid, "T_NICE_CHECKPLUS", "err_msg", "에러메세지", res.err_msg, params["err_msg"], "")
        request.state.inspect = frame()
        res.err_msg = params["err_msg"]

    res.update_at = util.getNow()
    return res

# 인증멤버정보 업데이트
def member_update(request: Request, params: object):
    request.state.inspect = frame()
    db = request.state.db
    
    # T_MEMBER select 
    res = db.query(T_MEMBER).filter(T_MEMBER.mobile == params["mobileno"]).first()

    if res is None:
        return ex.ReturnOK(403, "회원정보가 없습니다.", request)
    
    # T_MEMBER_INFO select 
    res2 = db.query(T_MEMBER_INFO).filter(T_MEMBER_INFO.uid == res.uid).first()
    
    if params["mobileno"] is not None and res2.tel != params["mobileno"]:
        create_log(request, res2.uid, "T_MEMBER_INFO", "tel", "핸드폰번호", res2.tel, params["mobileno"], res.user_name)
        request.state.inspect = frame()
        res2.tel = params["mobileno"]
    if params["conninfo"] is not None and res2.user_ci != params["conninfo"]:
        create_log(request, res2.uid, "T_MEMBER_INFO", "user_ci", "연계정보 확인값", res2.user_ci, params["conninfo"], res.user_name)
        request.state.inspect = frame()
        res2.user_ci = params["conninfo"]
    if params["dupinfo"] is not None and res2.user_di != params["dupinfo"]:
        create_log(request, res2.uid, "T_MEMBER_INFO", "user_di", "중복확인값", res2.user_di, params["dupinfo"], res.user_name)
        request.state.inspect = frame()
        res2.user_di = params["dupinfo"]
    if params["birthdate"] is not None and res2.birth != params["birthdate"]:
        create_log(request, res2.uid, "T_MEMBER_INFO", "birth", "생년월일", res2.birth, params["birthdate"], res.user_name)
        request.state.inspect = frame()
        res2.birth = params["birthdate"]
    if params["gender"] is not None and res2.gender != params["gender"]:
        create_log(request, res2.uid, "T_MEMBER_INFO", "gender", "성별", res2.gender, params["gender"], res.user_name)
        request.state.inspect = frame()
        res2.gender = params["gender"]

    res2.update_at = util.getNow()

    return res2
    
def userci_check(request: Request, userciInput: UserciInput):
    request.state.inspect = frame()
    db = request.state.db 

    filters = []
    filters.append(T_MEMBER_INFO.user_id == userciInput.user_id)
    filters.append(T_MEMBER_INFO.partner_id == userciInput.partner_id)
        
    sql = (
        db.query(
             T_MEMBER_INFO.uid
            ,T_MEMBER_INFO.partner_id
            ,T_MEMBER_INFO.user_id
            ,T_MEMBER_INFO.user_ci
        )
        .filter(*filters)
    ).first()
    

    return sql