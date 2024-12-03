
from typing import Optional, List
from pydantic import BaseModel, Field

# App 사용자 
class TokenDataDream(BaseModel):
    token_name: Optional[str] = Field("DREAM")
    partner_uid: Optional[int] = Field(0)
    partner_id: Optional[str] = Field("")
    user_uid: Optional[int] = Field(0)
    user_id: Optional[str] = Field("")
    user_name: Optional[str] = Field("")
    user_depart: Optional[str] = Field("")
    user_type: Optional[str] = Field("")
    access_token: Optional[str] = Field("")

def getTokenDataDream(user) :
    return TokenDataDream (
         token_name = user["token_name"]
        ,partner_uid = user["partner_uid"]
        ,partner_id = user["partner_id"]
        ,user_uid = user["user_uid"]
        ,user_id = user["user_id"]
        ,user_name = user["user_name"]
        ,user_depart = user["user_depart"]
        ,user_type = user["user_type"]
        ,access_token = user["access_token"]
    )

class AuthNum(BaseModel):
    send_type: str
    value: str
    login_id: str

class AuthNumInput(BaseModel):
    uid: Optional[int] = Field(0)
    mobile: Optional[str] = Field("")
    login_id: Optional[str] = Field("")
    partner_uid:Optional[int] = Field(0)
    
class IntroInput(BaseModel):
    user_id : Optional[str] = Field("")
    partner_id : Optional[str] = Field("")