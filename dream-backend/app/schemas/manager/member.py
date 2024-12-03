from typing import List, Dict, Any, Union, Optional
from datetime import date, datetime, time, timedelta

from app.schemas.schema import *

class Member(Status):
    uid: int = Field(0, title="T_MEMBER 고유번호")
    site_id: Optional[str] = Field(None, title="사이트 아이디", max_length=100)
    login_id: Optional[str] = Field(None, title="로그인 아이디", max_length=100)
    user_id: Optional[str] = Field(None, title="실제 아이디", max_length=100)
    partner_uid: Optional[int] = Field(0, title="고객사 uid")
    partner_id: Optional[str] = Field(None, title="고객사 아이디", max_length=100)
    prefix: Optional[str] = Field(None, title="고객사 prefix", max_length=100)
    user_name: Optional[str] = Field(None, title="이름", max_length=100)
    mobile: Optional[str] = Field(None, title="전화번호", max_length=100)
    email: Optional[str] = Field(None, title="이메일", max_length=100)
    aff_uid: Optional[int] = Field(None, title="소속구분")
    user_ci: Optional[str] = Field(None, title="CI", max_length=100)
    create_at: Optional[datetime] = Field(None, title="등록일")
    delete_at: Optional[datetime] = Field(None, title="삭제일")
    update_at: Optional[datetime] = Field(None, title="수정일")
    class Config:
        orm_mode = True

class MemberInfo(Status):
    uid: int = Field(0, title="T_MEMBER 고유번호")
    user_id: str = Field(None, title="실제 아이디", max_length=150)
    login_id: str = Field(None, title="로그인 아이디", max_length=150)
    prefix: str = Field(None, title="고객사 prefix", max_length=50)
    partner_uid: int = Field(None, title="고객사 uid")
    partner_id: str = Field("", title="고객사 id", max_length=100)
    mem_uid: Optional[int] = Field(None, title="복지몰 T_MEMBER uid")
    serve: Optional[str] = Field("재직", title="재직여부", max_length=10)
    birth: Optional[str] = Field(None, title="생년월일", max_length=20)
    gender: Optional[str] = Field(None, title="성별", max_length=10)
    anniversary: Optional[str] = Field(None, title="기념일", max_length=10)
    emp_no: Optional[str] = Field(None, title="사번", max_length=30)
    depart: Optional[str] = Field(None, title="부서", max_length=100)
    position: Optional[str] = Field(None, title="직급", max_length=30)
    position2: Optional[str] = Field(None, title="직책", max_length=30)
    join_com: Optional[str] = Field(None, title="입사일", max_length=10)
    post: Optional[str] = Field(None, title="우편번호", max_length=10)
    addr: Optional[str] = Field(None, title="주소", max_length=255)
    addr_detail: Optional[str] = Field(None, title="주소상세", max_length=100)
    tel: Optional[str] = Field(None, title="일반전화번호", max_length=15)
    affiliate: Optional[str] = Field(None, title="법인사", max_length=100)
    state: Optional[str] = Field("100", title="회원상태 (100:정상, 200:대기, 900:탈퇴)", max_length=10)
    is_login: Optional[str] = Field("T", title="복지몰로그인 가능여부", max_length=1)
    is_point: Optional[str] = Field("T", title="포인트사용 가능여부", max_length=1)
    is_pw_reset: Optional[str] = Field("T", title="비밀번호 초기화 여부", max_length=1)
    create_at: Optional[datetime] = Field(None, title="등록일")
    delete_at: Optional[datetime] = Field(None, title="삭제일")
    update_at: Optional[datetime] = Field(None, title="수정일")
    class Config:
        orm_mode = True

class MemberInput(BaseModel):
    uid: int = Field(0, title="T_MEMBER 고유번호")
    login_id: str = Field('', title="로그인 아이디", max_length=150)
    user_id: str = Field('', title="실제 아이디", max_length=150)
    user_name: Optional[str] = Field('', title="이름", max_length=100)
    prefix: str = Field('', title="고객사 prefix", max_length=50)
    mobile: Optional[str] = Field('', title="전화번호", max_length=100)
    email: Optional[str] = Field('', title="이메일", max_length=100)
    aff_uid: Optional[int] = Field(0, title="소속구분")
    mem_uid: Optional[int] = Field(0, title="복지몰 T_MEMBER uid")
    serve: Optional[str] = Field("재직", title="재직여부", max_length=10)
    birth: Optional[str] = Field('', title="생년월일", max_length=20)
    gender: Optional[str] = Field("", title="성별", max_length=10)
    anniversary: Optional[str] = Field('', title="기념일", max_length=10)
    emp_no: Optional[str] = Field('', title="사번", max_length=30)
    depart: Optional[str] = Field('', title="부서", max_length=100)
    position: Optional[str] = Field('', title="직급", max_length=30)
    position2: Optional[str] = Field('', title="직책", max_length=30)
    join_com: Optional[str] = Field('', title="입사일", max_length=20)
    post: Optional[str] = Field('', title="우편번호", max_length=10)
    addr: Optional[str] = Field('', titlse="주소", max_length=255)
    addr_detail: Optional[str] = Field('', title="주소상세", max_length=100)
    tel: Optional[str] = Field('', title="일반전화번호", max_length=15)
    affiliate: Optional[str] = Field('', title="법인사", max_length=100)
    state: Optional[str] = Field('', title="회원상태 (100:정상, 200:대기, 900:탈퇴)", max_length=10)
    is_login: Optional[str] = Field('', title="복지몰로그인 가능여부", max_length=1)
    is_point: Optional[str] = Field('', title="포인트사용 가능여부", max_length=1)
    is_pw_reset: Optional[str] = Field('', title="비밀번호 초기화 여부", max_length=1)
    mode: Optional[str] = Field('', title="REG/MOD/DEL")
    in_partner_id: Optional[str] = Field('', title="inbound용")
    in_user_id: Optional[str] = Field('', title="inbound용")

    class Config:
        orm_mode = True

class ChkMemberIdSchema(BaseModel):
    memberid_input_value : Optional[str] = Field(None, title="체크할 값")
    memberid_check_value : Optional[str] = Field(None, title="이전에 체크한 값")
    is_memberid_checked : Optional[str] = Field(None, title="이전에 체크 했는지")
    prefix: Optional[str] = Field(None, title="고객사 prefix", max_length=50)
