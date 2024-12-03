from sqlalchemy import Column, String, Integer, ForeignKey, text, DateTime, Boolean, JSON, Date

from app.core.database import Base

class T_PARTNER(Base):
    __tablename__ = "T_PARTNER"
    uid = Column(Integer, primary_key=True, index=True)
    partner_type = Column(String)
    partner_id = Column(String)
    roles = Column(JSON, default=[])
    mall_name = Column(String)
    company_name = Column(String)
    sponsor = Column(String)
    partner_code = Column(String)
    prefix = Column(String)
    logo = Column(String)
    is_welfare = Column(String, default='T')
    is_dream = Column(String, default='T')
    state = Column(String, default='100')
    mem_type = Column(String, default='임직원')
    mall_type = Column(String, default='임직원몰')
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    delete_at = Column(DateTime, comment="삭제일") 
    update_at = Column(DateTime, comment="수정일")

class T_PARTNER_INFO(Base):
    __tablename__ = "T_PARTNER_INFO"
    partner_uid = Column(Integer, primary_key=True, index=True)
    counsel_uid = Column(Integer)
    build_uid = Column(Integer)
    company_name = Column(String) 
    ceo_name = Column(String) 
    staff_name = Column(String) 
    staff_dept = Column(String) 
    staff_position = Column(String) 
    staff_position2 = Column(String) 
    staff_mobile = Column(String) 
    staff_email = Column(String)
    account_email = Column(String) 
    post = Column(String) 
    addr = Column(String) 
    addr_detail = Column(String) 
    company_hp = Column(String) 
    biz_kind = Column(String) 
    biz_item = Column(String) 
    biz_no = Column(String) 
    biz_service = Column(String) 
    mall_name = Column(String) 
    host = Column(String) 
    file_biz_no = Column(String) 
    file_bank = Column(String) 
    file_logo = Column(String) 
    file_mall_logo = Column(String) 
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    update_at = Column(DateTime) 
    delete_at = Column(DateTime)

class T_PARTNER_WORDS(Base):
    __tablename__ = "T_PARTNER_WORDS"
    partner_uid = Column(Integer, primary_key=True, index=True)
    partner_id = Column(String) 
    mall_type = Column(String)
    mall_tltle = Column(String)
    member_name = Column(String)
    point_name = Column(String)
    notice = Column(String)
    intro = Column(String)
    employee_card = Column(String)
    benefit = Column(String) 
    b2b_goods = Column(String) 

class T_DREAM_CONFIG(Base):
    __tablename__ = "T_DREAM_CONFIG"
    partner_uid = Column(Integer, primary_key=True, index=True)
    partner_id = Column(String)
    give_point = Column(Integer, default=100000)
    exp_date = Column(Integer, default=90)
    end_date = Column(DateTime)
    memo = Column(String)