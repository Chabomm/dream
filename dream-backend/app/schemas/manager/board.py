from typing import List, Dict, Any, Union, Optional
from datetime import date, datetime, time, timedelta

from app.schemas.schema import *

class BoardListInput(PPage_param):
    board_uid: Optional[int] = Field(None, title="T_BOARD.uid")

class Board(BaseModel): # 게시물
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
    files: List[Files] = Field([], title="첨부파일 리스트")
    password: Optional[str] = Field(None, title="비밀번호", max_length=100)
    name: Optional[str] = Field(None, title="이름", max_length=50)
    email: Optional[str] = Field(None, title="이메일 주소", max_length=255)
    mobile: Optional[str] = Field(None, title="휴대전화번호", max_length=20)
    class Config:
        orm_mode = True


class BoardEdit(BaseModel): # 게시물
    mode: Optional[str] = Field("", title="REG/MOD/DEL")
    uid: int = Field(0, title="게시물 고유번호")
    board_uid: int = Field(None, title="게시판 번호")
    cate_uid: Optional[int] = Field(None, title="카테고리 번호")
    thumb: Optional[str] = Field(None, title="썸네일", max_length=255)
    youtube: Optional[str] = Field(None, title="유튜브 링크", max_length=255)
    title: str = Field(None, title="게시물 제목", max_length=200)
    contents: str = Field(None, title="게시물 본문")
    files: List[Files] = Field([], title="첨부파일 리스트")
    tags: Optional[str] = Field(None, title="태그", max_length=200)
    is_display: str = Field('T', title="노출여부", max_length=1)
    user_ip: Optional[str] = Field(None, title="아이피주소", max_length=30)
    password: Optional[str] = Field(None, title="비밀번호", max_length=100)
    name: Optional[str] = Field(None, title="이름", max_length=50)
    email: Optional[str] = Field(None, title="이메일 주소", max_length=255)
    mobile: Optional[str] = Field(None, title="휴대전화번호", max_length=20)
    class Config:
        orm_mode = True