from typing import List, Dict, Any, Union, Optional
from datetime import date, datetime, time, timedelta

from app.schemas.schema import *
        
# 카드허용업종내역_init input
class CardAllowInitInput(BaseModel):
    use_type: Optional[str] = Field(None, title="사용종류(bokji, sikwon)")
        
# 카드허용업종내역_list input
class CardAllowListInput(BaseModel):
    use_type: Optional[str] = Field(None, title="사용종류(bokji, sikwon)")
    user_id: Optional[str] = Field(None, title="사용자아이디")