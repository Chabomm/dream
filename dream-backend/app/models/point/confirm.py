from sqlalchemy import Column, String, Integer, ForeignKey, text, DateTime, Boolean, JSON

from app.core.database import Base

class T_EXUSE(Base):
    __tablename__ = "T_EXUSE"
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
    pay_at = Column(DateTime, comment="카드결제일")
    pay_cancel_at = Column(DateTime, comment="결제취소일")
    biz_item = Column(String) 
    detail = Column(String) 
    pay_amount = Column(Integer)
    exuse_amount = Column(Integer)
    state = Column(String) 
    confirm_at = Column(DateTime, comment="처리완료일")
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="신청일")
    update_at = Column(DateTime, comment="수정일")
    delete_at = Column(DateTime, comment="삭제일")
    point_type = Column(String)  
    welfare_type = Column(String) 
    exuse_detail = Column(String) 
    attch_file = Column(String)
