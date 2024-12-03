from typing import List, Dict, Any, Union, Optional
from datetime import date, datetime, time, timedelta

from app.schemas.schema import *

class Manager(Status):
    uid: int = Field(0, title="T_MANAGER 고유번호")
    partner_uid: int = Field(0, title="T_PARTNER의 uid")
    partner_id: Optional[str] = Field("", title="고객사 아이디", max_length=100)
    prefix: Optional[str] = Field("", title="아이디 프리픽스", max_length=50)
    login_id: Optional[str] = Field("", title="prifix 포함 아이디", max_length=150)
    login_pw: Optional[str] = Field("", title="비밀번호", max_length=100)
    user_id: Optional[str] = Field("", title="아이디", max_length=150)
    name: Optional[str] = Field("", title="이름", max_length=50)
    tel: Optional[str] = Field("", title="일반전화번호", max_length=40)
    mobile: Optional[str] = Field("", title="휴대전화번호", max_length=20)
    email: Optional[str] = Field("", title="이메일", max_length=150)
    role: Optional[str] = Field("", title="관리자 권한", max_length=20)
    position1: Optional[str] = Field("", title="직급", max_length=30)
    position2: Optional[str] = Field("", title="직책", max_length=30)
    depart: Optional[str] = Field("", title="부서", max_length=30)
    roles: Optional[List[int]] = Field([], title="권한")
    state: Optional[str] = Field("", title="100 : 승인대기, 200 : 정상, 900 : 탈퇴", max_length=10)
    create_at: Optional[datetime] = Field(None, title="등록일")
    delete_at: Optional[datetime] = Field(None, title="삭제일")
    update_at: Optional[datetime] = Field(None, title="수정일")
    last_at: Optional[datetime] = Field(None, title="마지막 접속일")
    class Config:
        orm_mode = True

class ManagerReadInput(BaseModel):
    uid: Optional[int] = Field(0)
    user_id: Optional[str] = Field(None)

class ManagerInput(BaseModel):
    uid: int = Field(0, title="T_MANAGER 고유번호")
    login_id: Optional[str] = Field(None, title="prifix 포함 아이디", max_length=150)
    login_pw: Optional[str] = Field(None, title="비밀번호", max_length=100)
    user_id: Optional[str] = Field(None, title="아이디", max_length=150)
    name: Optional[str] = Field(None, title="이름", max_length=50)
    tel: Optional[str] = Field(None, title="일반전화번호", max_length=40)
    mobile: Optional[str] = Field(None, title="휴대전화번호", max_length=20)
    email: Optional[str] = Field(None, title="이메일", max_length=150)
    role: Optional[str] = Field(None, title="관리자 권한", max_length=20)
    position1: Optional[str] = Field(None, title="직급", max_length=30)
    position2: Optional[str] = Field(None, title="직책", max_length=30)
    depart: Optional[str] = Field(None, title="부서", max_length=30)
    roles: Optional[List[int]] = Field([], title="권한")
    state: Optional[str] = Field(None, title="100 : 승인대기, 200 : 정상, 900 : 탈퇴", max_length=10)
    class Config:
        orm_mode = True

class AdminRoles(BaseModel):
    uid: Optional[int] = Field(0, title="T_ADMIN_MENU의 고유번호")
    name: Optional[str] = Field("", title="역할명")
    menus: Optional[List[int]] = Field([], title="배정된메뉴 uids")
    class Config:
        orm_mode = True

class AdminRolesInput(BaseModel):
    uid: Optional[int] = Field(0, title="T_ADMIN_ROLES의 고유번호")
    name: Optional[str] = Field(None, title="메뉴명")
    menus: Optional[List[int]] = Field([], title="배정된메뉴 uids")
    mode: Optional[str] = Field(None, title="REG/MOD/DEL")
    class Config:
        orm_mode = True

class MyInfoInput(BaseModel):
    login_pw: Optional[str] = Field(None, title="기존 비밀번호")
    login_pw2: Optional[str] = Field(None, title="새 비밀번호")
    tel: Optional[str] = Field(None, title="내선번호")
    mobile: Optional[str] = Field(None, title="핸드폰번호")
    user_name: Optional[str] = Field(None, title="이름")
    email: Optional[str] = Field(None, title="이메일")
    depart: Optional[str] = Field(None, title="부서")
    login_id: Optional[str] = Field(None, title="아이디", max_length=150)
    mode: Optional[str] = Field(None)