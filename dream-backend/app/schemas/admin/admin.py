from typing import List, Dict, Any, Union, Optional
from datetime import date, datetime, time, timedelta

from app.schemas.schema import *

class Admin(Status):
    uid: int = Field(0, title="T_MANAGER 고유번호")
    user_id: Optional[str] = Field("", title="아이디", max_length=150)
    user_name: Optional[str] = Field("", title="이름", max_length=50)
    tel: Optional[str] = Field("", title="일반전화번호", max_length=20)
    mobile: Optional[str] = Field("", title="휴대전화번호", max_length=20)
    email: Optional[str] = Field("", title="이메일", max_length=150)
    depart: Optional[str] = Field("", title="부서", max_length=30)
    role: Optional[str] = Field("", title="관리자 권한", max_length=20)
    roles: Optional[List[int]] = Field([], title="권한")
    state: Optional[str] = Field("", title="100 : 승인대기, 200 : 정상, 900 : 탈퇴", max_length=10)
    create_at: Optional[datetime] = Field(None, title="등록일")
    delete_at: Optional[datetime] = Field(None, title="삭제일")
    update_at: Optional[datetime] = Field(None, title="수정일")
    last_at: Optional[datetime] = Field(None, title="마지막 접속일")
    class Config:
        orm_mode = True

class AdminInput(Status):
    uid: int = Field(0, title="T_MANAGER 고유번호")
    user_id: Optional[str] = Field("", title="아이디", max_length=150)
    user_name: Optional[str] = Field("", title="이름", max_length=50)
    tel: Optional[str] = Field("", title="일반전화번호", max_length=20)
    mobile: Optional[str] = Field("", title="휴대전화번호", max_length=20)
    email: Optional[str] = Field("", title="이메일", max_length=150)
    position1: Optional[str] = Field("", title="", max_length=30)
    position2: Optional[str] = Field("", title="", max_length=30)
    depart: Optional[str] = Field("", title="부서", max_length=30)
    role: Optional[str] = Field("", title="관리자 권한", max_length=20)
    roles: Optional[List[int]] = Field([], title="권한")
    state: Optional[str] = Field("", title="100 : 승인대기, 200 : 정상, 900 : 탈퇴", max_length=10)
    create_at: Optional[datetime] = Field(None, title="등록일")
    delete_at: Optional[datetime] = Field(None, title="삭제일")
    update_at: Optional[datetime] = Field(None, title="수정일")
    last_at: Optional[datetime] = Field(None, title="마지막 접속일")
    class Config:
        orm_mode = True

class AdminReadInput(BaseModel):
    uid: Optional[int] = Field(0)
    user_id: Optional[str] = Field(None)

class AdminRolesInitInput(BaseModel):
    uid: Optional[int] = Field(0, title="")
    partner_uid: Optional[int] = Field(0, title="")
    site_id: Optional[str] = Field("", title="")

class AdminRolesListInput(AdminRolesInitInput, PPage_param):
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

class AdminMenuListInput(BaseModel):
    parent: Optional[int] = Field(0, title="부모 uid")

class AdminMenuInput(BaseModel):
    uid: Optional[int] = Field(0, title="T_ADMIN_MENU의 고유번호")
    name: Optional[str] = Field(None, title="메뉴명")
    icon: Optional[str] = Field(None, title="아이콘")
    to: Optional[str] = Field(None, title="링크")
    depth: Optional[int] = Field(None, title="단계")
    parent: Optional[int] = Field(None, title="부모 uid")
    sort_array: Optional[List[int]] = Field([], title="변경할 메뉴 순서")
    mode: Optional[str] = Field(None, title="REG/MOD/DEL")

class AdminMenu(BaseModel):
    uid: Optional[int] = Field(0, title="T_ADMIN_MENU의 고유번호")
    name: Optional[str] = Field("", title="메뉴명")
    icon: Optional[str] = Field("", title="아이콘")
    to: Optional[str] = Field("", title="링크")
    sort: Optional[int] = Field("", title="순서")
    depth: Optional[int] = Field(1, title="단계")
    parent: Optional[int] = Field(0, title="부모uid")
    class Config:
        orm_mode = True

class MyInfoInput(BaseModel):
    user_pw: Optional[str] = Field(None, title="비밀번호")
    tel: Optional[str] = Field(None, title="내선번호")
    mobile: Optional[str] = Field(None, title="핸드폰번호")

class LogListInput(PPage_param):
    table_name: Optional[str] = Field(None, title="테이블명", max_length=100)
    table_uid: Optional[int] = Field(0, title="uid")
    class Config:
        orm_mode = True

class BackendFileListInput(PPage_param):
    folder_name: Optional[str] = Field(None, title="폴더명")
    class Config:
        orm_mode = True

class BackendFileReadInput(BaseModel):
    folder_name: Optional[str] = Field(None, title="폴더명")
    file_name: Optional[str] = Field(None, title="파일명")
    class Config:
        orm_mode = True