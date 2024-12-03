from typing import List, Dict, Any, Union, Optional
from datetime import date, datetime, time, timedelta

from app.schemas.schema import *

class AssignSingleRead(BaseModel):
    save_type: Optional[str] = Field("", title="1:대량지급, 2:개별지급, 3:회수")
    user_uids: Optional[str] = Field("")
    class Config:
        orm_mode = True

class AssignSingleInput(BaseModel):
    user_uids: Optional[List[int]] = Field([])
    group_id : Optional[int] = Field(0, title="T_POINT_GROUP.uid")
    reason : Optional[str] = Field("", title="지급사유")
    saved_point : Optional[str] = Field(0, title="지급포인트")
    admin_memo : Optional[str] = Field("", title="관리자메모")
    expiration_date: Optional[str] = Field(None, title="삭제일")
    is_exp_date: Optional[bool] = Field(False, title="소명일 없음 유무")
    save_type : Optional[str] = Field(0, title="2:지급, 3:회수")
    class Config:
        orm_mode = True