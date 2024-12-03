from typing import List, Dict, Any, Union, Optional
from datetime import date, datetime, time, timedelta

from app.schemas.schema import *

class OrderInput(BaseModel):
    guid: Optional[int] = Field(0, title="T_B2B_GOODS.uid")
    partner_uid: Optional[int] = Field(0, title="T_PATNER.uid")
    user_uid: Optional[int] = Field(0, title="T_MANAGER.uid")
    manager: Optional[object] = Field({}, title="T_MANAGER 정보")
    company_name: Optional[str] = Field("", title="T_PARTNER.company_name")
    class Config:
        orm_mode = True

class B2BOrderInfo(BaseModel):
    ouid: Optional[int] = Field(0, title="T_B2B_ORDER.uid")
    guid: Optional[int] = Field(0, title="T_B2B_GOODS.uid")
    option_num: Optional[int] = Field(0, title="항목번호")
    option_type: Optional[str] = Field("", title="추가항목타입 A:한글입력폼, B:문장입력폼, C:드롭박스, D:라디오버튼, E:날짜, F:파일업로드, G:고객안내형 설정사항")
    option_title: Optional[str] = Field("", title="항목명")
    option_yn: Optional[str] = Field("", title="필수유무")
    placeholder: Optional[str] = Field("", title="[E] single, range / [F] images, allfile")
    apply_value: Optional[Any] = Field("", title="신청값")
    file_name: Optional[str] = Field("", title="파일첨부인경우 파일명")
    class Config:
            orm_mode = True

class B2BOrder(BaseModel):
    guid: Optional[int] = Field(0, title="T_B2B_GOODS.uid")
    seller_id: Optional[str] = Field("", title="판매자아이디")
    service_type: Optional[str] = Field("", title="서비스 구분 C:고객사혜택, D:드림클럽")
    category: Optional[str] = Field("", title="카테고리")
    title: Optional[str] = Field("", title="상품명")
    state: Optional[str] = Field("", title="상태")
    commission_type: Optional[str] = Field("", title="복지드림 수수료 타입")
    commission: Optional[int] = Field(0, title="복지드림 수수료")
    token_name: Optional[str] = Field("", title="신청타입(DREAM-MANAGER, SCM-SELLER)")
    sosok_uid: Optional[int] = Field(0, title="신청자 소속의 uid")
    sosok_id: Optional[str] = Field("", title="신청자 소속의 아이디")
    apply_user_uid: Optional[int] = Field(0, title="신청자uid")
    apply_user_id: Optional[str] = Field("", title="신청자아이디")
    apply_company: Optional[str] = Field("", title="신청자회사명")
    apply_name: Optional[str] = Field("", title="신청자명")
    apply_depart: Optional[str] = Field("", title="신청자부서")
    apply_position: Optional[str] = Field("", title="신청자직급")
    apply_phone: Optional[str] = Field("", title="신청자연락처")
    apply_email: Optional[str] = Field("", title="신청자이메일")
    create_at: Optional[str] = Field("", title="등록일")
    delete_at: Optional[str] = Field("", title="삭제일")
    update_at: Optional[str] = Field("", title="수정일")
    info_list: Optional[List[B2BOrderInfo]] = Field([], title="신정정보")
    class Config:
            orm_mode = True