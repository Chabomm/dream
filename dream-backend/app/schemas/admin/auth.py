
from typing import Optional, List
from pydantic import BaseModel, Field

# 최고 관리자
class TokenDataAdmin(BaseModel):
    token_name: Optional[str] = Field("DREAM-ADMIN")
    user_uid: Optional[int] = Field(0)
    user_id: Optional[str] = Field("")
    user_name: Optional[str] = Field("")
    user_depart: Optional[str] = Field("")
    role: Optional[str] = Field("")
    roles: Optional[List[int]] = Field([], title="권한")
    access_token: Optional[str] = Field("")

def getTokenDataAdmin(user) :
    return TokenDataAdmin (
         token_name = user["token_name"]
        ,user_uid = user["user_uid"]
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

