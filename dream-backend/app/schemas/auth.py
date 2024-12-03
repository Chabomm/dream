
from typing import Optional, List
from pydantic import BaseModel, Field

# Outbound 유저 정보 ()
class TokenDataOutbound(BaseModel):
    token_name: Optional[str] = Field("")
    user_uid: Optional[int] = Field(0)
    user_id: Optional[str] = Field("")
    user_name: Optional[str] = Field("")
    sosok_uid: Optional[int] = Field(0)
    sosok_id: Optional[str] = Field("")
    access_token: Optional[str] = Field("")

def getTokenDataOutbound(user) :
    return TokenDataOutbound (
         token_name = user.token_name
        ,user_uid = user.user_uid
        ,user_id = user.user_id
        ,user_name = user.user_name
        ,sosok_uid = user.sosok_uid
        ,sosok_id = user.sosok_id
        ,access_token = user.access_token
    )