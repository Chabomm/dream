from typing import List, Dict, Any, Union, Optional
from datetime import date, datetime, time, timedelta

from app.schemas.schema import *

class DreamCounsel(BaseModel):
    mode: Optional[str] = Field("", title="REG/MOD/DEL")
    uid: Optional[int] = Field(0, title="uid")
    company_name: Optional[str] = Field(None, title="기업명", max_length=100)
    homepage_url: Optional[str] = Field(None, title="홈페이지url", max_length=255)
    staff_count: Optional[int] = Field(None, title="직원수")
    wish_build_at: Optional[str] = Field(None, title="구축희망일")
    staff_name: Optional[str] = Field(None, title="담당자명", max_length=30)
    staff_dept: Optional[str] = Field(None, title="담당자 부서", max_length=30)
    staff_position: Optional[str] = Field(None, title="담당자 직급", max_length=30)
    staff_position2: Optional[str] = Field(None, title="담당자 직책", max_length=30)
    staff_mobile: Optional[str] = Field(None, title="담당자 핸드폰 번호", max_length=30)
    staff_email: Optional[str] = Field(None, title="담당자 이메일", max_length=255)
    contents: Optional[str] = Field(None, title="상담문의 & 요청내용")
    state: Optional[str] = Field(None, title="100:상담문의, 200:상담중, 300:도입보류, 501:도입대기, 502:도입신청완료", max_length=30)
    create_at: Optional[datetime] = Field(None, title="등록일")
    update_at: Optional[datetime] = Field(None, title="수정일")
    delete_at: Optional[datetime] = Field(None, title="삭제일")
    memo: Optional[str] = Field(None, title="상담로그")
    class Config:
        orm_mode = True


        
class DreamCounselInput(BaseModel):
    mode: Optional[str] = Field("", title="REG/MOD/DEL")
    uid: Optional[int] = Field(0, title="uid")
    company_name: Optional[str] = Field(None, title="기업명", max_length=100)
    homepage_url: Optional[str] = Field(None, title="홈페이지url", max_length=255)
    staff_count: Optional[int] = Field(None, title="직원수")
    wish_build_at: Optional[date] = Field(None, title="구축희망일")
    staff_name: Optional[str] = Field(None, title="담당자명", max_length=30)
    staff_dept: Optional[str] = Field(None, title="담당자 부서", max_length=30)
    staff_position: Optional[str] = Field(None, title="담당자 직급", max_length=30)
    staff_position2: Optional[str] = Field(None, title="담당자 직책", max_length=30)
    staff_mobile: Optional[str] = Field(None, title="담당자 핸드폰 번호", max_length=30)
    staff_email: Optional[str] = Field(None, title="담당자 이메일", max_length=255)
    contents: Optional[str] = Field(None, title="상담문의 & 요청내용")
    state: Optional[str] = Field(None, title="100:상담문의, 200:상담중, 300:도입보류, 501:도입대기, 502:도입신청완료", max_length=30)
    memo: Optional[str] = Field(None, title="상담로그")
    class Config:
        orm_mode = True