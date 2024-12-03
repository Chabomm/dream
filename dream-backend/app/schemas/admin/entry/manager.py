from typing import List, Dict, Any, Union, Optional
from datetime import date, datetime, time, timedelta

from app.schemas.schema import *

class DreamManager(BaseModel):
    uid: Optional[int] = Field(0, title="uid")
    partner_uid: Optional[int] = Field(0, title="T_PARTNER 의 uid")
    partner_id: Optional[str] = Field(None, title="고객사 아이디", max_length=100)
    prefix: Optional[str] = Field(None, title="아이디 프리픽스", max_length=50)
    login_id: Optional[str] = Field(None, title="실제 로그인 아이디", max_length=150)
    login_pw: Optional[str] = Field(None, title="비밀번호", max_length=100)
    user_id: Optional[str] = Field(None, title="", max_length=150)
    name: Optional[str] = Field(None, title="이름", max_length=50)
    tel: Optional[str] = Field(None, title="일반전화번호", max_length=40)
    mobile: Optional[str] = Field(None, title="휴대전화번호", max_length=20)
    email: Optional[str] = Field(None, title="이메일", max_length=150)
    role: Optional[str] = Field(None, title="", max_length=20)
    position1: Optional[str] = Field(None, title="직급", max_length=30)
    position2: Optional[str] = Field(None, title="직책", max_length=30)
    depart: Optional[str] = Field(None, title="부서", max_length=30)
    roles: Optional[List[int]] = Field([], title="권한")
    state: Optional[str] = Field(None, title="100 : 승인대기, 200 : 정상, 900 : 탈퇴", max_length=10)
    create_at: Optional[datetime] = Field(None, title="등록일")
    delete_at: Optional[datetime] = Field(None, title="삭제일")
    update_at: Optional[datetime] = Field(None, title="수정일")
    last_at: Optional[datetime] = Field(None, title="마지막 접속일")
    class Config:
        orm_mode = True

class ManagerInput(BaseModel):
    mode: Optional[str] = Field("", title="REG/MOD/DEL")
    uid: Optional[int] = Field(0, title="uid")
    partner_uid: Optional[int] = Field(0, title="T_PARTNER 의 uid")
    partner_id: Optional[str] = Field(None, title="고객사 아이디", max_length=100)
    prefix: Optional[str] = Field(None, title="아이디 프리픽스", max_length=50)
    login_id: Optional[str] = Field(None, title="실제 로그인 아이디", max_length=150)
    name: Optional[str] = Field(None, title="이름", max_length=50)
    tel: Optional[str] = Field(None, title="일반전화번호", max_length=40)
    mobile: Optional[str] = Field(None, title="휴대전화번호", max_length=20)
    email: Optional[str] = Field(None, title="이메일", max_length=150)
    role: Optional[str] = Field(None, title="", max_length=20)
    position1: Optional[str] = Field(None, title="직급", max_length=30)
    position2: Optional[str] = Field(None, title="직책", max_length=30)
    depart: Optional[str] = Field(None, title="부서", max_length=30)
    roles: Optional[List[int]] = Field([], title="권한")
    class Config:
        orm_mode = True


class ManagerReadInput(BaseModel):
    mode: Optional[str] = Field("", title="REG/MOD/DEL")
    uid: Optional[int] = Field(0, title="uid")
    partner_uid: Optional[int] = Field(0, title="T_PARTNER 의 uid")
    login_id: Optional[str] = Field(None, title="실제 로그인 아이디", max_length=150)
    class Config:
        orm_mode = True