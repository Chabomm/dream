from typing import List, Dict, Any, Union, Optional
from datetime import date, datetime, time, timedelta
from datetime import date, datetime, time, timedelta

from app.schemas.schema import *

class Board(BaseModel): # 게시판
    uid: int = Field(0, title="T_BOARD 고유번호")
    site_id: str = Field("", title="프로젝트", max_length=50)
    board_type: str = Field('common', title="게시판 유형", max_length=10)
    board_name: str = Field("", title="게시판 이름", max_length=50)
    permission: Optional[List[int]] = Field([], title="쓰기권한")
    permission_read: Optional[List[int]] = Field([], title="읽기권한")
    permission_write: Optional[List[int]] = Field([], title="쓰기권한")
    per_write: Optional[str] = Field('admin', title="쓰기권한", max_length=50)
    per_read: Optional[str] = Field('admin', title="읽기권한", max_length=50)
    is_comment: Optional[str] = Field('F', title="댓글여부", max_length=1)
    is_display: str = Field('T', title="노출여부", max_length=1)
    front_url: str = Field(None, title="프론트 URL")
    create_at: Optional[datetime] = Field(None, title="등록일")
    update_at: Optional[datetime] = Field(None, title="수정일")
    delete_at: Optional[datetime] = Field(None, title="삭제일")
    mode: Optional[str] = Field(None, title="REG/MOD/DEL")
    class Config:
        orm_mode = True

class PostsCate(BaseModel) : 
    uid: Optional[int] = Field(0, title="카테고리 고유번호")
    cate_name: Optional[str] = Field(None, title="카테고리 명")
    cate_icon: Optional[str] = Field(None, title="카티고리 아이콘")
    cate_sort: Optional[int] = Field(0, title="카티고리 순서")

class PostsFiles(BaseModel) : 
    uid: Optional[int] = Field(0, title="파일 고유번호")
    board_uid: Optional[int] = Field(0, title="T_BOARD uid")
    posts_uid: Optional[int] = Field(0, title="T_BOARD_POSTS uid")
    fake_name: Optional[str] = Field(None, title="파일명")
    file_url: Optional[str] = Field(None, title="파일경로")
    sort: Optional[int] = Field(0, title="파일 순서")


class PostsInput(BaseModel): # 게시물
    posts_uid: int = Field(0, title="게시물 고유번호")
    password: Optional[str] = Field(None, title="비밀번호", max_length=100)
    board_uid: int = Field(None, title="게시판 번호")

class Posts(BaseModel): # 게시물
    no: Optional[int] = Field(0, title="게시물넘버링")
    uid: int = Field(0, title="게시물 고유번호")
    board_uid: int = Field(None, title="게시판 번호")
    cate_uid: Optional[int] = Field(None, title="카테고리 번호")
    thumb: Optional[str] = Field(None, title="썸네일", max_length=255)
    youtube: Optional[str] = Field(None, title="유튜브 링크", max_length=255)
    title: str = Field(None, title="게시물 제목", max_length=200)
    contents: str = Field(None, title="게시물 본문")
    tags: Optional[str] = Field(None, title="태그", max_length=200)
    is_display: str = Field('T', title="노출여부", max_length=1)
    create_at: Optional[datetime] = Field(None, title="등록일")
    update_at: Optional[datetime] = Field(None, title="수정일")
    delete_at: Optional[datetime] = Field(None, title="삭제일")
    state: Optional[str] = Field(None, title="100 : 미답변, 200 : 답변완료, 300 : 공지", max_length=5)
    user_ip: Optional[str] = Field(None, title="아이피주소", max_length=30)
    mode: Optional[str] = Field(None, title="REG/MOD/DEL")
    files: List[PostsFiles] = Field([], title="첨부파일 리스트")
    password: Optional[str] = Field(None, title="비밀번호", max_length=100)
    name: Optional[str] = Field(None, title="이름", max_length=50)
    email: Optional[str] = Field(None, title="이메일 주소", max_length=255)
    mobile: Optional[str] = Field(None, title="휴대전화번호", max_length=20)
    
    class Config:
        orm_mode = True

class PostsListInput(PPage_param, Status):
    board_uid: int = Field(0, title="T_BOARD의 uid")
    cate_uid: Optional[int] = Field(0, title="T_CATEGORY uid")
    class Config:
        orm_mode = True

class PostsList(PPage_param, Status):
    list: List[Posts] = Field([], title="게시물 리스트")
    board_uid: int = Field(0, title="T_BOARD의 uid")
    cate_uid: Optional[int] = Field(0, title="T_CATEGORY uid")
    board: Board = Field({}, title="게시판 상세정보")
    category_list: List[PostsCate] = Field([], title="게시물 리스트")
    class Config:
        orm_mode = True

class PostsViewInput(BaseModel):
    board_uid: int = Field(0, title="T_BOARD의 uid")
    posts_uid: int = Field(0, title="T_BOARD_POSTS의 uid")
    class Config:
        orm_mode = True

class PostsReplyInput(BaseModel):
    uid: Optional[int] = Field(0)
    board_uid: Optional[int] = Field(0)
    posts_uid: Optional[int] = Field(0)
    reply: str = Field(None, title="댓글내용")
    mode: Optional[str] = Field(None, title="REG/MOD/DEL")
    class Config:
        orm_mode = True

class PostInput(PPage_param, Status):
    uid: int = Field(0, title="T_BOARD의 uid 또는 T_BOARD_POSTS의 uid")
    is_board_master: Optional[bool] = Field(False, title="게시판 관리자인지 여부")
    class Config:
        orm_mode = True