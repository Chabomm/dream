from sqlalchemy import Column, String, Integer, ForeignKey, text, DateTime, Boolean, JSON, Text

from app.core.dbSCM import Base # scm conn

class T_B2B_SELLER(Base):
    __tablename__ = "T_B2B_SELLER"
    uid = Column(Integer, primary_key=True, index=True, nullable=False)
    seller_id = Column(String, comment='판매자아이디')
    seller_name = Column(String, comment='판매자명')
    account_cycle = Column(String, comment='정산 사이클')
    indend_md = Column(String, comment='상품담당자아이디')
    indend_md_name = Column(String, comment='상품담당자명')
    indend_md_email = Column(String, comment='상품담당자 이메일')
    indend_md_tel = Column(String, comment='상품담당자 일반전화번호')
    indend_md_mobile = Column(String, comment='상품담당자 휴대전화번호')
    state = Column(String, comment='상태')
    ceo_name = Column(String, comment='대표자명')
    tel = Column(String, comment='대표번호')
    biz_no = Column(String, comment='사업자등록번호')
    biz_kind = Column(String, comment='업태')
    biz_item = Column(String, comment='종목')
    bank = Column(String, comment='정산 은행')
    account = Column(String, comment='정산 계좌번호')
    depositor = Column(String, comment='정산 계좌예금주')
    homepage = Column(String, comment='홈페이지')
    post = Column(String, comment='우편번호')
    addr = Column(String, comment='주소')
    addr_detail = Column(String, comment='주소상세')
    biz_file = Column(String, comment='사업자등록증')
    biz_hooper = Column(String, comment='통장사본')
    tax_email =  Column(String, comment='세금계산서이메일')
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    update_at = Column(DateTime, comment="수정일")
    delete_at = Column(DateTime, comment="삭제일")
    
class T_B2B_SELLER_STAFF(Base):
    __tablename__ = "T_B2B_SELLER_STAFF"
    uid = Column(Integer, primary_key=True, index=True, nullable=False)
    seller_uid = Column(Integer, comment='T_B2B_SELLER.uid')
    seller_id = Column(String, comment='판매자아이디')
    login_id = Column(String, comment='로그인아이디')
    login_pw = Column(String, comment='로그인비밀번호')
    user_id = Column(String, comment='유저아이디')
    name = Column(String, comment='담당자명')
    roles = Column(JSON, default=[], comment='담당업무 (상품,발주,CS,정산)')
    depart = Column(String, comment='담당자 부서')
    position = Column(String, comment='담당자 직급/직책')
    tel = Column(String, comment='일반전화번호')
    mobile = Column(String, comment='휴대전화번호')
    email = Column(String, comment='이메일')
    sort = Column(Integer, comment='정렬')
    alarm_email = Column(String, comment='이메일알림')
    alarm_kakao = Column(String, comment='카카오알림')
    state = Column(String, comment='상태')
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    update_at = Column(DateTime, comment="수정일")
    delete_at = Column(DateTime, comment="삭제일")
    
class T_B2B_SELLER_ROLE(Base):
    __tablename__ = "T_B2B_SELLER_ROLE"
    uid = Column(Integer, primary_key=True, index=True)
    name = Column(String, comment="역할명")
