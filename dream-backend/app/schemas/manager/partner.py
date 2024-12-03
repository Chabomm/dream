from typing import List, Dict, Any, Union, Optional
from datetime import date, datetime, time, timedelta

from app.schemas.schema import *

class PartnerInput(BaseModel):
    uid: int = Field(0, title="T_PARTNER 고유번호")
    partner_type: Optional[str] = Field(None, title="100 : 개방형, 200 : 직접회원가입, 201 : 직접회원가입 승인제도, 300 : 관리자가 회원등록, 400 : 자동로그인", max_length=20)
    partner_id: str = Field(None, title="고객사 아이디", max_length=100)
    mall_name: str = Field(None, title="고객사 복지몰명", max_length=100)
    company_name: str = Field(None, title="고객사 회사명", max_length=100)
    sponsor: str = Field(None, title="스폰서", max_length=50)
    partner_code: str = Field(None, title="고객사 코드", max_length=50)
    prefix: str = Field(None, title="아이디 프리픽스", max_length=21)
    logo: str = Field(None, title="로고 이미지", max_length=255)
    is_welfare: str = Field(None, title="복지포인트 사용여부", max_length=1)
    is_dream: str = Field(None, title="드림포인트 사용여부", max_length=1)
    state: str = Field(None, title="100 : 대기, 200 : 운영중, 300 : 일시중지, 400 : 폐쇄", max_length=10)
    mem_type: str = Field(None, title="회원유형", max_length=50)
    in_user_id: Optional[str] = Field(None, title="inbound용")
    mode: Optional[str] = Field(None, title="REG/MOD/DEL")
    class Config:
        orm_mode = True
