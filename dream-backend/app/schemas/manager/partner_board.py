from typing import List, Dict, Any, Union, Optional
from datetime import date, datetime, time, timedelta

from app.schemas.schema import *

class PartnerBoard(AppModel): # 게시판
    uid: int = Field(0, title="게시판 고유번호")
    board_type: str = Field('common', title="게시판 유형", max_length=10)
    board_name: str = Field("", title="게시판 이름", max_length=50)
    per_write: Optional[str] = Field('admin', title="쓰기권한", max_length=50)
    per_read: Optional[str] = Field('admin', title="읽기권한", max_length=50)
    is_comment: Optional[str] = Field('F', title="댓글여부", max_length=1)
    is_display: str = Field('T', title="노출여부", max_length=1)
    create_at: Optional[datetime] = Field(None, title="등록일")
    update_at: Optional[datetime] = Field(None, title="수정일")
    delete_at: Optional[datetime] = Field(None, title="삭제일")
    front_url: str = Field('', title="프론트 URL")
    mode: Optional[str] = Field(None, title="REG/MOD/DEL")
    class Config:
        orm_mode = True

class PartnerPosts(BaseModel): # 게시물
    uid: int = Field(0, title="게시물 고유번호")
    partner_uid: int = Field(None, title="T_PARTNER 의 uid")
    partner_id: Optional[str] = Field(None, title="고객사 아이디", max_length=100)
    board_uid: int = Field(None, title="게시판 번호")
    cate_uid: Optional[int] = Field(None, title="카테고리 번호")
    thumb: Optional[str] = Field(None, title="썸네일", max_length=255)
    title: str = Field(None, title="게시물 제목", max_length=200)
    contents: str = Field(None, title="게시물 본문")
    tags: Optional[str] = Field(None, title="태그", max_length=200)
    is_display: str = Field('T', title="노출여부", max_length=1)
    create_at: Optional[datetime] = Field(None, title="등록일")
    update_at: Optional[datetime] = Field(None, title="수정일")
    delete_at: Optional[datetime] = Field(None, title="삭제일")
    create_user: Optional[str] = Field(None, title="작성자 아이디", max_length=100)
    mode: Optional[str] = Field(None, title="REG/MOD/DEL")
    class Config:
        orm_mode = True

class PostsListInput(PPage_param, Status):
    board_uid: int = Field(0, title="T_PARTNER_BOARD의 uid")
    cate_uid: Optional[int] = Field(0, title="T_MAIN_CATE uid")
    class Config:
        orm_mode = True