from sqlalchemy import Column, String, Integer, ForeignKey, text, DateTime, Boolean, JSON

from app.core.database import Base

class T_BALANCE(Base):
    __tablename__ = "T_BALANCE"
    uid = Column(Integer, primary_key=True, index=True)
    partner_uid = Column(Integer)
    partner_id = Column(String) 
    point = Column(Integer, default=0)
    save_point = Column(Integer, default=0)
    reason = Column(String) 
    order_no = Column(String) 
    input_bank = Column(String, comment='입금은행')
    input_name = Column(String, comment='입금자명')
    input_state = Column(String, comment='입금전')
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    delete_at = Column(DateTime, comment="삭제일") 
    update_at = Column(DateTime, comment="수정일")

class T_BALANCE_RTPAY(Base):
    __tablename__ = "T_BALANCE_RTPAY"
    uid = Column(Integer, primary_key=True, index=True)
    balance_uid = Column(Integer)
    partner_uid = Column(Integer)
    partner_id = Column(String) 
    pmoney = Column(Integer, default=0)
    rt_code = Column(String) 
    tall = Column(String) 
    pbank = Column(String) 
    pname = Column(String) 
    pnum = Column(String) 
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")