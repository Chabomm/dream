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
from app.schemas.manager.member import *
from app.schemas.manager.auth import *
from app.service.manager.member import member_service
from app.service import partner_service

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/inbound"],
)

# 복지몰에서 회원등록 시 inbound인데 지금은 사용안함
# be/manager/member/edit
@router.post("/inbound/member/edit", dependencies=[Depends(api_same_origin)])
async def 일반회원_편집(
    request: Request
    ,memberInput: MemberInput = Body(
        ...,
        examples={
            "example01": {
                "summary": "임직원 등록하기 예시1",
                "description": "",
                "value": {
                     "login_id" : "dream_test_user1"
                    ,"user_id" : "demo_dream_test_user1"
                    ,"prefix" : "demo_"
                    ,"user_name" : "가나다"
                    ,"mobile" : "010-1234-5678"
                    ,"email" : "dream_test_user1@indend.co.kr"
                    ,"aff_uid" : 12345
                    ,"mem_uid" : 558488
                    ,"serve" : "휴직"
                    ,"birth" : "1999-06-19"
                    ,"gender" : "여자"
                    ,"anniversary" : "adf"
                    ,"emp_no" : "1234"
                    ,"depart" : "경영지원팀"
                    ,"position" : "사원"
                    ,"position2" : "사원"
                    ,"join_com" : "2023-06-19"
                    ,"post" : "05237"
                    ,"addr" : "서울 강동구 아리수로 46 (암사동)"
                    ,"addr_detail" : "1층"
                    ,"tel" : "010-1234-5678"
                    ,"affiliate" : ""
                    ,"state" : "100"
                    ,"is_login" : "T"
                    ,"is_point" : "T"
                    ,"is_pw_reset": "F"
                    ,"mode": "REG"
                    ,"in_partner_id": "sample"
                    ,"in_user_id": "demo_test@indend.co.kr"
                },
            },
            "example02": {
                "summary": "임직원 수정하기 예시1",
                "description": "",
                "value": {
                     "uid" : 5
                    ,"user_name" : "가나다수정"
                    ,"birth" : "1999-07-19"
                    ,"mode": "MOD"
                },
            },
            "example03": {
                "summary": "임직원 삭제하기 예시1",
                "description": "",
                "value": {
                     "uid" : 5
                    ,"mode": "DEL"
                },
            }
        }
    )
):
    request.state.inspect = frame()
    request.state.body = await util.getRequestParams(request)

    partner_info = partner_service.read_partner_info(request, memberInput.in_partner_id)
    
    request.state.user = TokenDataManager (
         partner_uid = partner_info.uid
        ,partner_id = memberInput.in_partner_id
        ,user_id = memberInput.in_user_id
    )

    # 등록
    if memberInput.mode == "REG" :
        res = member_service.member_create(request, memberInput)
        request.state.inspect = frame()
        return ex.ReturnOK(200, "등록이 완료되었습니다. 새로고침 해주세요", request, {"uid" : res.uid})

    # # 수정
    # if memberInput.mode == "MOD" :
    #     res = member_service.member_update(request, memberInput)
    #     request.state.inspect = frame()
    #     return ex.ReturnOK(200, "수정이 완료되었습니다. 새로고침 해주세요", request, {"uid" : res.uid})
    
    # # 삭제
    # if memberInput.mode == "DEL" :
    #     member_service.member_delete(request, memberInput.uid)
    #     request.state.inspect = frame()
    #     return ex.ReturnOK(200, "삭제 완료", request)


