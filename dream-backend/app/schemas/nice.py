from typing import Optional, List
from pydantic import BaseModel, Field

from app.schemas.schema import *

class CheckplusInput(AppModel):
    client_id : Optional[str] = Field("")
    partner_id : Optional[str] = Field("")
    user_id : Optional[str] = Field("")
    method :  Optional[str] = Field("")

class resultInput(BaseModel):
    method :  str = Field("")
    client_id : str = Field("")
    encode_data :  str = Field("")


class UserciInput(BaseModel):
    user_id : Optional[str] = Field("")
    partner_id : Optional[str] = Field("")

