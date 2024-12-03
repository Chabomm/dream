from typing import List, Dict, Any, Union, Optional
from datetime import date, datetime, time, timedelta

from app.schemas.schema import *

# 카드사용_소명신청 input
class CardExuseInput(BaseModel):
    card_used_uid: Optional[int] = Field(None, title="카드 사용 uid")
    user_id: Optional[str] = Field(None, title="사용자아이디")
    point_type: Optional[str] = Field(None, title="포인트 종류")
    welfare_type: Optional[str] = Field(None, title="복지항목")
    exuse_detail: Optional[str] = Field(None, title="소명내용")
    exuse_amount: Optional[int] = Field(0, title="신청금액")
    attch_file: Optional[str] = Field(None, title="증빙자료")
    class Config:
        orm_mode = True

# 소명신청내역 init input
class CardExuseInitInput(BaseModel):
    user_id: Optional[str] = Field(None, title="사용자아이디")

# 소명신청내역 list input
class CardExuseListInput(PPage_param):
    user_id: Optional[str] = Field(None, title="사용자아이디")
    class Config:
        orm_mode = True

# 소명신청내역 상세 input
class CardExuseReadInput(BaseModel):
    user_id: Optional[str] = Field(None, title="사용자아이디")
    card_uid: Optional[int] = Field(None, title="T_CARD_USED.uid")
    class Config:
        orm_mode = True