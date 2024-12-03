
from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.schema import *

# [ S ] 고객사 담당자 
class TokenDataManager(BaseModel):
    token_name: Optional[str] = Field("DREAM-MANAGER")
    partner_uid: Optional[int] = Field(0)
    partner_id: Optional[str] = Field("")
    user_uid: Optional[int] = Field(0)
    prefix: Optional[str] = Field("")
    user_id: Optional[str] = Field("")
    user_name: Optional[str] = Field("")
    user_depart: Optional[str] = Field("")
    role: Optional[str] = Field("")
    roles: Optional[List[int]] = Field([], title="권한")
    access_token: Optional[str] = Field("")
    is_temp: bool = Field(False)

def getTokenDataManager(user) :
    return TokenDataManager (
         token_name = user["token_name"]
        ,partner_uid = user["partner_uid"]
        ,partner_id = user["partner_id"]
        ,user_uid = user["user_uid"]
        ,prefix = user["prefix"]
        ,user_id = user["user_id"]
        ,user_name = user["user_name"]
        ,user_depart = user["user_depart"]
        ,role = user["role"]
        ,roles = user["roles"]
        ,access_token = user["access_token"]
    )

class SignInRequest(BaseModel):
    user_id: str
    user_pw: str
    partner_id: str

class ExcelLogInput(BaseModel):
    download_reason: Optional[str] = Field("")
    url: str = Field("")
    params: Optional[PPage_param] = Field("")
    fail_list: Optional[List] = Field([])
    class Config:
        orm_mode = True

class ExcelJson(BaseModel):
    post: Optional[Dict] = Field(default_factory=dict)
    fail: int = Field(0)
    success: int = Field(0)
    gubun: Optional[str] = Field("")
    