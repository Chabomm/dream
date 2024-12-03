from sqlalchemy import Column, String, Integer, ForeignKey, text, DateTime, Boolean, JSON, Text

from app.core.dbSCM import Base


class T_B2B_GOODS(Base):
    __tablename__ = "T_B2B_GOODS"
    uid = Column(Integer, primary_key=True, index=True)
    service_type = Column(String, comment='서비스 구분 C:고객사혜택, D:드림클럽')
    category = Column(String, comment='카테고리')
    seller_id = Column(String, comment='판매자아이디')
    seller_name = Column(String, comment='판매자명')
    title = Column(String, comment='상품명')
    sub_title = Column(String, comment='서브타이틀')
    contents = Column(String, comment='상세내용')
    benefit = Column(String, comment='복지드림 멤버십 혜택')
    attention = Column(String, comment='유의사항')
    keyword = Column(String, comment='키워드')
    thumb = Column(String, comment='메인 이미지')
    option_yn = Column(String, comment='옵션사용여부')
    option_value = Column(String, comment='옵션항목 콤마구분')
    option_cnt = Column(Integer, comment='옵션갯수')
    market_price = Column(Integer, comment='정가')
    price = Column(Integer, comment='')
    str_sale_percent = Column(String, comment='세일가')
    str_market_price = Column(String, comment='정가')
    str_price = Column(String, comment='판매가')
    commission_type = Column(String, comment='복지드림 수수료 타입')
    commission = Column(Integer, comment='복지드림 수수료')
    other_service = Column(String, comment='추가상품')
    sort = Column(Integer, comment='노출순서')
    start_date = Column(DateTime, comment='판매기간 시작일')
    end_date = Column(DateTime, comment='판매기간 종료일')
    is_display = Column(String, default='T', comment='진열여부')
    state = Column(String, default='200', comment='상태')
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    update_at = Column(DateTime, comment="수정일")
    delete_at = Column(DateTime, comment="삭제일")

class T_B2B_GOODS_CONTENTS(Base):
    __tablename__ = "T_B2B_GOODS_CONTENTS"
    uid = Column(Integer, primary_key=True, index=True, nullable=False)
    guid = Column(Integer, ForeignKey('T_B2B_GOODS.uid'))
    gubun = Column(String, comment='컨텐츠구분 : contents, benefit, attention')
    sort = Column(String, comment='블록순서')
    btype = Column(String, comment='블록타입 : html, img')
    html = Column(String)
    image_url = Column(String, comment='이미지주소')
    link = Column(String, comment='링크주소')
    link_target = Column(String, default='_self', comment='링크타겟 : ''_self'', ''_blank''')
    is_display = Column(String, default='T', comment='공개여부')
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    update_at = Column(DateTime, comment="수정일")
    delete_at = Column(DateTime, comment="삭제일")

class T_B2B_GOODS_IMAGE(Base):
    __tablename__ = "T_B2B_GOODS_IMAGE"
    guid = Column(Integer, primary_key=True, comment='T_B2B_GOODS.uid')
    img_url = Column(String, comment='이미지주소')
    sort = Column(String, comment='순서')

class T_B2B_GOODS_INFO(Base):
    __tablename__ = "T_B2B_GOODS_INFO"
    uid = Column(Integer, primary_key=True, index=True, nullable=False)
    guid = Column(Integer, ForeignKey('T_B2B_GOODS.uid'))
    option_num = Column(String, comment='항목번호')
    option_type = Column(String, comment='추가항목타입 A:한글입력폼, B:문장입력폼, C:드롭박스, D:라디오버튼, E:날짜, F:파일업로드, G:고객안내형 설정사항')
    option_title = Column(String, comment='항목명')
    option_yn = Column(String, comment='필수유무')
    placeholder = Column(String, comment='[E] single, range / [F] images, allfile')
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    