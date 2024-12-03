from typing import List, Dict, Any, Union, Optional
from datetime import date, datetime, time, timedelta

from app.schemas.schema import *

class AssignBalanceInput(BaseModel):
    save_point: Optional[str] = Field(None, title="직원수")
    input_bank: Optional[str] = Field(None, title="입금은행")
    input_name: Optional[str] = Field(None, title="입금자명")
    reason: Optional[str] = Field(None, title="관리자 메모")
    class Config:
        orm_mode = True