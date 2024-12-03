
from typing import Optional, List
from pydantic import BaseModel, Field

class PointInfo(BaseModel):
    user_id: str = Field("")

class PointUse(BaseModel):
    user_id: str = Field("")
    order_no: str = Field("")
    order_uid: str = Field("")
    use_point: str = Field("")
    reason: str = Field("")

class PointCancel(BaseModel):
    user_id: str = Field("")
    order_no: str = Field("")
    order_uid: str = Field("")
    cancel_point: str = Field("")
    reason: str = Field("")
