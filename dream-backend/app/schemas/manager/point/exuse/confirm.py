from typing import List, Dict, Any, Union, Optional
from datetime import date, datetime, time, timedelta

from app.schemas.schema import *

class ConfirmStateInput(Status):
    uid : Optional[List[int]] = Field([], title="소명신청 고유번호")
    state : str = Field(None, title="소명신청, 승인완료, 미승인, 재차감설정, 결제취소", max_length=10)
    class Config:
        orm_mode = True

class ConfirmInput(Status):
    uid : Optional[int] = Field(None, title="소명신청 고유번호")
    card_used_uid : Optional[int] = Field(None, title="T_CARD_USED.uid")
    exuse_amount : Optional[int] = Field(None, title="소명신청금액")
    state : Optional[str] = Field(None, title="소명신청, 승인완료, 미승인, 재차감설정, 결제취소", max_length=10)
    point_type: Optional[str] = Field(None, title="포인트타입")
    memo: Optional[str] = Field(None, title="상담로그")
    class Config:
        orm_mode = True