from sqlalchemy import Column, String, Integer, ForeignKey, text, DateTime, Boolean, JSON

from app.core.database import Base

class T_CARD_USED_REMAINING(Base):
    __tablename__ = "T_CARD_USED_REMAINING"
    uid = Column(Integer, primary_key=True, index=True)
    card_used_uid = Column(Integer)
    partner_uid = Column(Integer)
    partner_id = Column(String) 
    user_uid = Column(Integer)
    user_id = Column(String) 
    user_name = Column(String) 
    birth = Column(String) 
    depart = Column(String) 
    position = Column(String) 
    biz_item = Column(String) 
    detail = Column(String) 
    confirm_at = Column(DateTime, comment="차감승인일")
    remaining_at = Column(DateTime, comment="환급일")
    input_amount = Column(Integer)
    card = Column(String) 
    input_bank = Column(String) 
    input_name = Column(String) 
    input_bank_num = Column(String) 
    state = Column(String) 
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="신청일")
    update_at = Column(DateTime, comment="수정일")
    delete_at = Column(DateTime, comment="삭제일")