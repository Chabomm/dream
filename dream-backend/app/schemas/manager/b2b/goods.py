from typing import List, Dict, Any, Union, Optional
from datetime import date, datetime, time, timedelta

from app.schemas.schema import *

class GoodsListType(PPage_param):
    svc_type: Optional[str] = Field(None, title="서비스타입")
    class Config:
        orm_mode = True
        
class GoodsReadInput(BaseModel):
    guid: int
    method: str
    company_name : Optional[str]
    depart : Optional[str]
    position1 : Optional[str]
    mobile: Optional[str]
    email : Optional[str]
    