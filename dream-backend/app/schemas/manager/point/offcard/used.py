from typing import List, Dict, Any, Union, Optional
from datetime import date, datetime, time, timedelta

from app.schemas.schema import *

# 카드사용_내역_init input
class CardUsedInitInput(BaseModel):
    user_id: Optional[str] = Field(None, title="사용자아이디")

# 카드사용_내역 input
class CardUsedListInput(PPage_param):
    user_id: Optional[str] = Field(None, title="사용자아이디")
    class Config:
        orm_mode = True


class PointDeductItem(BaseModel):
    card_used_uid: int = Field(0, title="T_CARD_USED.uid")
    request_point: Optional[int] = Field(0, title="request_point")
    class Config:
        orm_mode = True

# 카드사용_포인트차감신청 input
class CardUsedInput(BaseModel):
    user_id: Optional[str] = Field(None, title="사용자아이디")
    use_type: Optional[str] = Field(None, title="사용종류(bokji, sikwon)")
    deduct_list: List[PointDeductItem] = Field([], title="차감신청 리스트")





# 카드_포인트차감_init input
class CardDeductInitInput(BaseModel):
    use_type: Optional[str] = Field(None, title="사용종류(bokji, sikwon)")

# 카드_포인트차감_내역 input
class CardDeductListInput(PPage_param):
    use_type: Optional[str] = Field(None, title="사용종류(bokji, sikwon)")
    user_id: Optional[str] = Field(None, title="사용자아이디")
    class Config:
        orm_mode = True