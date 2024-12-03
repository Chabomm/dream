from typing import List, Dict, Any, Union, Optional
from datetime import date, datetime, time, timedelta

from app.schemas.schema import *

class PointStatusInput(BaseModel):
    point_type: Optional[str] = Field(None, title="bokji: 복지포인트, sikwon: 식권포인트")
    class Config:
        orm_mode = True