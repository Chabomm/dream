from typing import List, Dict, Any, Union, Optional
from datetime import date, datetime, time, timedelta

from app.schemas.schema import *

class OffcardSendFiles(BaseModel):
    filename: str = Field("")
    class Config:
        orm_mode = True
