from typing import List, Dict, Any, Union, Optional
from datetime import date, datetime, time, timedelta

from app.schemas.schema import *

# 환급_내역_init input
class CardRemainingInitInput(BaseModel):
    user_id: Optional[str] = Field(None, title="사용자아이디")

# 환급_내역 input
class CardRemainingListInput(PPage_param):
    user_id: Optional[str] = Field(None, title="사용자아이디")
    class Config:
        orm_mode = True
