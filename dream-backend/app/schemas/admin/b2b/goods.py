from typing import List, Dict, Any, Union, Optional
from datetime import date, datetime, time, timedelta

from app.schemas.schema import *


class MemoList(BaseModel) : 
    table_uid: Optional[int] = Field(0, title="테이블 고유번호")
    memo: Optional[str] = Field(0, title="메모내용")
    file_url: Optional[int] = Field(0, title="파일 url")
    file_name: Optional[str] = Field("", title="파일명")

class B2BGoods(BaseModel):
    uid: int = Field(0, title="T_B2B_GOODS.uid")
    seller_id: Optional[str] = Field("", title='판매자아이디')
    seller_name: Optional[str] = Field("", title='판매자명')
    service_type: Optional[str] = Field("C", title='서비스 구분 C:고객사혜택, D:드림클럽')
    sort: Optional[int] = Field(0, title='진열순서')
    is_display: Optional[str] = Field("T", title='진열여부')
    start_date: Optional[str] = Field("", title="판매기간 시작일")
    end_date: Optional[str] = Field("", title="판매기간 종료일")
    category: Optional[str] = Field("", title='카테고리')
    title: Optional[str] = Field("", title='상품명')
    sub_title: Optional[str] = Field("", title='서브타이틀')
    keyword: Optional[str] = Field("", title='키워드')
    str_market_price: Optional[str] = Field("", title='정가(문자열)')
    str_price: Optional[str] = Field("", title='판매가(문자열)')
    commission_type: str = Field("A", title='복지드림 수수료 타입')
    commission: Optional[int] = Field(0, title='복지드림 수수료')
    str_sale_percent: Optional[str] = Field("", title='세일가(문자열)')
    option_value: Optional[str] = Field("", title='옵션항목 콤마구분')
    option_yn: Optional[str] = Field("", title='option_yn으로구분')
    contents: Optional[str] = Field("", title='상세내용')
    benefit: Optional[str] = Field("", title='복지드림 멤버십 혜택')
    attention: Optional[str] = Field("", title='유의사항')
    thumb: Optional[str] = Field("", title='메인 이미지')
    other_service: Optional[str] = Field("", title='추가상품')
    state: str = Field("200", title='상태')
    memo_list: Optional[MemoList] = Field([], title='메모리스트')
    etc_images: Optional[List] = Field([], title='추가이미지')
    option_list: Optional[List] = Field([], title='option_list')
    class Config:
        orm_mode = True

        
class B2BGoodsInput(BaseModel): # b2b상품리스트
    uid: int = Field(0, title="T_B2B_GOODS 고유번호")
    seller_id: Optional[str] = Field("", title='판매자아이디')
    seller_name: Optional[str] = Field("", title='판매자명')
    service_type: Optional[str] = Field("C", title='서비스 구분 C:고객사혜택, D:드림클럽')
    sort: Optional[int] = Field(0, title='진열순서')
    is_display: Optional[str] = Field("T", title='진열여부')
    start_date: Optional[str] = Field(None, title="판매기간 시작일")
    end_date: Optional[str] = Field(None, title="판매기간 종료일")
    category: Optional[str] = Field("기업지원", title='카테고리')
    title: Optional[str] = Field("", title='상품명')
    sub_title: Optional[str] = Field("", title='서브타이틀')
    keyword: Optional[str] = Field("", title='키워드')
    str_market_price: Optional[str] = Field("", title='정가(문자열)')
    str_price: Optional[str] = Field("", title='판매가(문자열)')
    commission_type: str = Field("A", title='복지드림 수수료 타입')
    commission: Optional[int] = Field(0, title='복지드림 수수료')
    str_sale_percent: Optional[str] = Field("", title='세일가(문자열)')
    option_value: Optional[str] = Field("", title='옵션항목 콤마구분')
    thumb: Optional[str] = Field("", title='메인 이미지')
    etc_images: Optional[List] = Field([], title='추가이미지')
    contents: Optional[str] = Field("", title='상세내용')
    benefit: Optional[str] = Field("", title='복지드림 멤버십 혜택')
    attention: Optional[str] = Field("", title='유의사항')
    option_list: Optional[List] = Field([], title='option_list')
    other_service: Optional[str] = Field("", title='추가상품')
    goods_option_yn: Optional[str] = Field("Y", title='option_yn으로구분')
    option_yn: Optional[str] = Field("Y", title='option_yn으로구분')
    memo: Optional[str] = Field("", title="메모내용")
    sale_at: Optional[object] = Field(None, title="판매기간 filter")
    mode: Optional[str] = Field("", title="REG/MOD/DEL")
    class Config:
        orm_mode = True