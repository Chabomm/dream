from typing import List, Dict, Any, Union, Optional
from datetime import date, datetime, time, timedelta

from app.schemas.schema import *

class LimitIndustryInput(BaseModel):
    mode: Optional[str] = Field("", title="REG/MOD/DEL")
    uids: Optional[List[int]] = Field([])
    class Config:
        orm_mode = True