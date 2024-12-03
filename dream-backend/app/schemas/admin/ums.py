from typing import List, Dict, Any, Union, Optional
from datetime import date, datetime, time, timedelta

from app.schemas.schema import *

class UmsLayout(Status):
    uid: int = Field(0, title="T_UMS_LAYOUT 고유번호")
    layout_name: Optional[str] = Field("", title="레이아웃명")
    content: Optional[str] = Field("", title="내용")
    create_at: Optional[datetime] = Field(None, title="등록일")
    delete_at: Optional[datetime] = Field(None, title="삭제일")
    update_at: Optional[datetime] = Field(None, title="수정일")

class UmsTmpl(Status):
    uid: int = Field(0, title="T_UMS_TEMPLATE 고유번호")
    ums_type : Optional[str] = Field("", title="email/at")
    platform : Optional[str] = Field("", title="사용처")
    layout_uid : Optional[int] = Field("", title="T_UMS_LAYOUT 고유번호")
    template_code : Optional[str] = Field("", title="알림톡코드")
    subject : Optional[str] = Field("", title="제목")
    content : Optional[str] = Field("", title="내용")
    memo : Optional[str] = Field("", title="관리자메모")
    profile : Optional[str] = Field("", title="알림톡 프로필")
    create_at: Optional[datetime] = Field(None, title="등록일")
    delete_at: Optional[datetime] = Field(None, title="삭제일")
    update_at: Optional[datetime] = Field(None, title="수정일")
    mode: Optional[str] = Field("", title="edit mode")
    class Config:
        orm_mode = True

class UmsPreviewInput(AppModel):
    uid: int
    layout_uid: int

class PushBooking(AppModel):
    uid : int= Field(0)
    img: Optional[str] = Field("")
    send_type: Optional[str] = Field("00000000000000")
    rec_type: Optional[str] = Field("P")
    rec_list: Optional[List[int]]
    push_title: Optional[str] = Field("")
    push_msg: Optional[str] = Field("")
    push_img: Optional[str] = Field("")
    push_link: Optional[str] = Field("")
    state: Optional[str] = Field("100")
    send_count: Optional[int] = Field(0)
    success_count: Optional[int] = Field(0)
    mode: Optional[str] = Field(None, title="REG/MOD/DEL")
    partners: Optional[List[int]] = Field([])
    devices: Optional[List[int]] = Field([])
    booking_at: Optional[datetime] = Field(None)
    booking_at_date: Optional[Dict] = Field(default_factory=dict)
    booking_at_time: Optional[str] = Field("08:00:00")

class PushBookingMsgListInput(PPage_param):
    booking_uid : int= Field(0)
    class Config:
        orm_mode = True

class PushTesterInput(AppModel):
    push_msg_uid : int= Field(0)
    tester_uid : int= Field(0)
    class Config:
        orm_mode = True