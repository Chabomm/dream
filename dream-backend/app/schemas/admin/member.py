from typing import List, Dict, Any, Union, Optional
from datetime import date, datetime, time, timedelta

from app.schemas.schema import *

class MemberInput(BaseModel):
    uid: Optional[int] = Field(0, title="T_MEMBER 고유번호")
    site_id: Optional[str] = Field(None, title="사이트아이디", max_length=100)
    login_id: Optional[str] = Field(None, title="로그인아이디", max_length=150)
    user_id: Optional[str] = Field(None, title="실제아아디", max_length=150)
    partner_uid: Optional[int] = Field(None, title="T_PARTNER 고유번호")
    partner_id: Optional[str] = Field(None, title="고객사명", max_length=100)
    prefix: Optional[str] = Field(None, title="고객사 prefix", max_length=50)
    user_name: Optional[str] = Field(None, title="이름", max_length=50)
    mobile: Optional[str] = Field(None, title="전화번호", max_length=20)
    email: Optional[str] = Field(None, title="이메일", max_length=100)
    aff_uid: Optional[int] = Field(None, title="소속구분")
    user_ci: Optional[str] = Field(None, title="CI", max_length=100)
    create_at: Optional[datetime] = Field(None, title="등록일")
    update_at: Optional[datetime] = Field(None, title="수정일")
    delete_at: Optional[datetime] = Field(None, title="삭제일")
    serve: Optional[str] = Field('재직', title="재직여부", max_length=10)
    is_pw_reset: Optional[str] = Field(None, title="비밀번호 초기화 여부", max_length=1)
    is_login: Optional[str] = Field('T', title="복지몰로그인 가능여부", max_length=1)
    is_point: Optional[str] = Field('T', title="포인트사용 가능여부", max_length=1)
    state: Optional[str] = Field('100', title="회원상태 (100:정상, 200:대기, 900:탈퇴)", max_length=10)
    birth: Optional[str] = Field(None, title="생년월일", max_length=20)
    gender: Optional[str] = Field('남자', title="성별", max_length=10)
    anniversary: Optional[str] = Field(None, title="기념일", max_length=10)
    emp_no: Optional[str] = Field(None, title="사번", max_length=30)
    position: Optional[str] = Field(None, title="직급", max_length=30)
    position2: Optional[str] = Field(None, title="직책", max_length=30)
    join_com: Optional[str] = Field(None, title="입사일", max_length=10)
    post: Optional[str] = Field(None, title="우편번호")
    addr: Optional[str] = Field(None, title="주소")
    addr_detail: Optional[str] = Field(None, title="주소상세")
    depart: Optional[str] = Field(None, title="부서")
    mall_name: Optional[str] = Field(None, title="고객사 복지몰명", max_length=100)
    partner_code: Optional[str] = Field(None, title="고객사 코드", max_length=50)
    mode: Optional[str] = Field("", title="REG/MOD/DEL")
    class Config:
        orm_mode = True
        
class PartnerSearchInput(BaseModel):
    partner_name: Optional[str] = Field(None, title="고객사명", max_length=100)
    class Config:
        orm_mode = True