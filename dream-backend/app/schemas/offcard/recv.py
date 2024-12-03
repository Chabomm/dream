from typing import List, Dict, Any, Union, Optional
from datetime import date, datetime, time, timedelta

from app.schemas.schema import *

class OffcardRecvFiles(BaseModel):
    filename: str = Field("")
    filedate: Optional[str] = Field("")
    class Config:
        orm_mode = True
