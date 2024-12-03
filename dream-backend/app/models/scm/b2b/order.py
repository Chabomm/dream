from sqlalchemy import Column, String, Integer, ForeignKey, text, DateTime, Boolean, JSON, Text

from app.core.dbSCM import Base

class T_B2B_ORDER(Base):
    __tablename__ = "T_B2B_ORDER"
    uid = Column(Integer, primary_key=True, index=True)
    guid = Column(String, comment='T_B2B_GOODS.uid')
    seller_id = Column(String, comment='판매자아이디')
    service_type = Column(String, comment='서비스 구분 C:고객사혜택, D:드림클럽')
    category = Column(String, comment='카테고리')
    title = Column(String, comment='상품명')
    state = Column(String, comment='상태')
    commission_type = Column(String, comment='복지드림 수수료 타입')
    commission = Column(String, comment='복지드림 수수료')
    token_name = Column(String, comment='신청타입(DREAM-MANAGER, SCM-SELLER)')
    sosok_uid = Column(String, comment='신청자 소속의 uid')
    sosok_id = Column(String, comment='신청자 소속의 아이디')
    apply_user_uid = Column(String, comment='신청자uid')
    apply_user_id = Column(String, comment='신청자아이디')
    apply_company = Column(String, comment='신청자회사명')
    apply_name = Column(String, comment='신청자명')
    apply_depart = Column(Integer, comment='신청자부서')
    apply_position = Column(Integer, comment='신청자직급')
    apply_phone = Column(Integer, comment='신청자연락처')
    apply_email = Column(String, comment='신청자이메일')
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    update_at = Column(DateTime, comment="수정일")
    delete_at = Column(DateTime, comment="삭제일")
    
class T_B2B_ORDER_INFO(Base):
    __tablename__ = "T_B2B_ORDER_INFO"
    uid = Column(Integer, primary_key=True, index=True, nullable=False)
    ouid = Column(Integer, ForeignKey('T_B2B_ORDER.uid'))
    guid = Column(Integer, ForeignKey('T_B2B_GOODS.uid'))
    option_num = Column(String, comment='항목번호')
    option_type = Column(String, comment='추가항목타입 A:한글입력폼, B:문장입력폼, C:드롭박스, D:라디오버튼, E:날짜, F:파일업로드, G:고객안내형 설정사항')
    option_title = Column(String, comment='항목명')
    option_yn = Column(String, comment='필수유무')
    placeholder = Column(String, comment='[E] single, range / [F] images, allfile')
    apply_value = Column(String, comment='신청값')
    file_name = Column(String, comment='파일첨부인경우 파일명')
    

class T_B2B_ORDER_CONT(Base):
    __tablename__ = "T_B2B_ORDER_CONT"
    ouid = Column(Integer, ForeignKey('T_B2B_ORDER.uid'), primary_key=True, index=True, nullable=False, comment='T_B2B_ORDER.uid')
    guid = Column(Integer, comment='T_B2B_GOODS.uid')
    cont_state = Column(String, comment='계약상태')
    contract_date = Column(DateTime, comment='계약일')
    contract_price = Column(Integer, comment='계약금액')
    contract_code = Column(String, comment='계약코드')
    start_date = Column(DateTime, comment='시작일')
    end_date = Column(DateTime, comment='종료일')
    cont_staff_name = Column(String, comment='계약담당자명')
    cont_staff_depart = Column(String, comment='계약담당자부서')
    cont_staff_position = Column(String, comment='계약담당자직급/직책')
    cont_staff_phone = Column(String, comment='계약담당자연락처')
    cont_staff_email = Column(String, comment='계약담당자이메일')
    seller_id = Column(String, comment='판매자아이디')
    create_user = Column(String, comment='계약진행 담당자')
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    update_at = Column(DateTime, comment="수정일")
    delete_at = Column(DateTime, comment="삭제일")
    

class T_B2B_ORDER_ACCOUNT(Base):
    __tablename__ = "T_B2B_ORDER_ACCOUNT"
    ouid = Column(Integer, ForeignKey('T_B2B_ORDER.uid'), primary_key=True, index=True, nullable=False, comment='T_B2B_ORDER.uid')
    guid = Column(Integer, comment='T_B2B_GOODS.uid')
    contract_code = Column(String, comment='계약코드')
    account_state = Column(String, comment='상태')
    tax_invoice_date = Column(DateTime, comment='세금계약서발행일')
    account_date = Column(DateTime, comment='정산일')
    contract_date = Column(DateTime, comment='계약일')
    contract_price = Column(Integer, comment='계약금액')
    commission_type = Column(String, comment='복지드림수수료타입')
    commission = Column(Integer, comment='복지드림수수료')
    confirm_commission = Column(Integer, comment='정산수수료')
    create_user = Column(String, comment='등록자')
    seller_id = Column(String, comment='판매자아이디')
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    update_at = Column(DateTime, comment="수정일")
    delete_at = Column(DateTime, comment="삭제일")
    

class T_B2B_ORDER_CANCEL(Base):
    __tablename__ = "T_B2B_ORDER_CANCEL"
    uid = Column(Integer, primary_key=True, index=True, nullable=False)
    ouid = Column(Integer, comment='T_B2B_ORDER.uid')
    guid = Column(Integer, comment='T_B2B_GOODS.uid')
    cancel_price = Column(Integer, comment='상태')
    cancel_reason = Column(String, comment='세금계약서발행일')
    cancel_state = Column(String, comment='정산일')
    cancel_file_name = Column(String, comment='계약일')
    cancel_file_url = Column(String, comment='계약금액')
    cancel_tax = Column(String, comment='복지드림수수료타입')
    create_user = Column(String, comment='등록자')
    seller_id = Column(String, comment='판매자아이디')
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    update_at = Column(DateTime, comment="수정일")
    delete_at = Column(DateTime, comment="삭제일")
    

class T_B2B_ORDER_GAGAM(Base):
    __tablename__ = "T_B2B_ORDER_GAGAM"
    uid = Column(Integer, primary_key=True, index=True, nullable=False)
    ouid = Column(Integer, comment='T_B2B_ORDER.uid')
    guid = Column(Integer, comment='T_B2B_GOODS.uid')
    gagam_price = Column(Integer, comment='가감금액')
    gagam_state = Column(String, comment='가감상태')
    gagam_reason = Column(String, comment='가감이유')
    gagam_tax = Column(String, comment='면세/과세')
    account_date = Column(DateTime, comment='정산일')
    create_user = Column(String, comment='등록자')
    seller_id = Column(String, comment='판매자아이디')