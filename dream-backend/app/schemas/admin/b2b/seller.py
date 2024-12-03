from typing import List, Dict, Any, Union, Optional
from datetime import date, datetime, time, timedelta

from app.schemas.schema import *

class SellerSearchInput(BaseModel):
    seller: Optional[str] = Field("")
    class Config:
        orm_mode = True
        
class SellerDetail(BaseModel): # 업체
    uid: int = Field(0, title="T_B2B_SELLER 고유번호")
    account_cycle: Optional[str] = Field("1", title='정산 사이클')
    memo: Optional[str] = Field(None, title='T_MEMO')
    create_at: Optional[datetime] = Field(None, title="등록일")
    update_at: Optional[datetime] = Field(None, title="수정일")
    delete_at: Optional[datetime] = Field(None, title="삭제일")
    sort_array: Optional[List[int]] = Field([], title="변경할 메뉴 순서")
    class Config:
        orm_mode = True
        
class SellerDetailInput(BaseModel):
    uid: int = Field(0, title="T_B2B_SELLER 고유번호")
    seller_id: Optional[str] = Field(None, title='판매자아이디')
    seller_name: Optional[str] = Field(None, title='판매자명')
    account_cycle: Optional[str] = Field("1", title='정산 사이클')
    indend_md: Optional[str] = Field(None, title='상품담당자아이디')
    indend_md_name: Optional[str] = Field(None, title='상품담당자명')
    indend_md_email : Optional[str] = Field(None, title='상품담당자 이메일')
    indend_md_tel : Optional[str] = Field(None, title='상품담당자 일반전화번호')
    indend_md_mobile : Optional[str] = Field(None, title='상품담당자 휴대전화번호')
    state: Optional[str] = Field("100", title='상태')
    ceo_name: Optional[str] = Field(None, title='대표자명')
    tel: Optional[str] = Field(None, title='대표번호')
    biz_no: Optional[str] = Field(None, title='사업자등록번호')
    biz_kind: Optional[str] = Field(None, title='업태')
    biz_item: Optional[str] = Field(None, title='종목')
    bank: Optional[str] = Field(None, title='정산 은행')
    account: Optional[str] = Field(None, title='정산 계좌번호')
    depositor: Optional[str] = Field(None, title='정산 계좌예금주')
    homepage: Optional[str] = Field(None, title='홈페이지')
    post: Optional[str] = Field(None, title='우편번호')
    addr: Optional[str] = Field(None, title='주소')
    addr_detail: Optional[str] = Field(None, title='주소상세')
    biz_file: Optional[str] = Field(None, title='사업자등록증')
    biz_hooper: Optional[str] = Field(None, title='통장사본')
    biz_file_fakename: Optional[str] = Field(None, title='사업자등록증 fakename')
    biz_hooper_fakename: Optional[str] = Field(None, title='통장사본 fakename')
    memo: Optional[str] = Field(None, title='T_MEMO')
    tax_email:  Optional[str] = Field(None, title='세금계산서메일')
    sort_array: Optional[List[int]] = Field([], title="변경할 메뉴 순서")
    mode: Optional[str] = Field(None, title="REG/MOD/DEL/SORT")
    class Config:
        orm_mode = True
        
class SellerStaff(BaseModel): # 담당자
    uid: int = Field(0, title="T_B2B_SELLER_STAFF 고유번호")
    seller_uid: int = Field(0, title="T_B2B_SELLER 고유번호")
    seller_id: Optional[str] = Field("", title='판매자아이디')
    alarm_email: Optional[str] = Field("T", title='이메일수신')
    alarm_kakao: Optional[str] = Field("T", title='알림톡수신')
    roles: Optional[List[int]] = Field([], title="구분")
    class Config:
        orm_mode = True
        
class SellerStaffInput(BaseModel): # 담당자
    uid: int = Field(0, title="T_B2B_SELLER_STAFF 고유번호")
    seller_uid: int = Field(0, title="T_B2B_SELLER 고유번호")
    seller_id: Optional[str] = Field("", title='판매자아이디')
    login_id: Optional[str] = Field(None, title='로그인 아이디')
    login_pw: Optional[str] = Field(None, title='로그인 비밀번호')
    name: Optional[str] = Field("", title='담당자명')
    roles: Optional[List[int]] = Field([], title="구분")
    depart: Optional[str] = Field(None, title='부서')
    position: Optional[str] = Field(None, title='직급/직책')
    tel: Optional[str] = Field(None, title='일반전화')
    mobile: Optional[str] = Field("", title='휴대전화')
    email: Optional[str] = Field("", title='이메일')
    sort: Optional[int] = Field(1, title='순서')
    alarm_email: Optional[str] = Field("T", title='이메일수신')
    alarm_kakao: Optional[str] = Field("T", title='알림톡수신')
    state: Optional[str] = Field(None, title='상태')
    mode: Optional[str] = Field(None, title="REG/MOD/DEL/COPY")
    class Config:
        orm_mode = True
        
class SellerStaffPwInput(BaseModel):
    uid: int = Field(0, title="T_B2B_SELLER_STAFF 고유번호")
    class Config:
        orm_mode = True

class StaffInput(BaseModel):
    mode: Optional[str] = Field(None, title="REG/MOD/DEL/COPY")
    uid: Optional[int] = Field(0)
    seller_uid: Optional[str] = Field("")
    seller_id: Optional[str] = Field("")
    seller_name: Optional[str] = Field("")
    class Config:
        orm_mode = True