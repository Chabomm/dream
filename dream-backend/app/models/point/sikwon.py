from sqlalchemy import Column, String, Integer, ForeignKey, text, DateTime, Boolean, JSON

from app.core.database import Base

class T_SIKWON(Base):
    __tablename__ = "T_SIKWON"
    uid = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer)
    saved_type = Column(String)
    point = Column(Integer)
    saved_point = Column(Integer)
    expiration_date = Column(String) 
    user_id = Column(String) 
    manager_id = Column(String) 
    partner_uid = Column(Integer)
    partner_id = Column(String) 
    reason = Column(String) 
    admin_memo = Column(String) 
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    delete_at = Column(DateTime, comment="삭제일") 
    update_at = Column(DateTime, comment="수정일")

class T_SIKWON_GROUP(Base):
    __tablename__ = "T_SIKWON_GROUP"
    uid = Column(Integer, primary_key=True, index=True)
    group_name = Column(String) 
    group_type = Column(String) 
    reason = Column(String) 
    manager_id = Column(String) 
    partner_uid = Column(Integer)
    partner_id = Column(String)
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    delete_at = Column(DateTime, comment="삭제일") 
    update_at = Column(DateTime, comment="수정일")

class T_SIKWON_USED(Base):
    __tablename__ = "T_SIKWON_USED"
    uid = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer)
    point_id  = Column(Integer)
    used_type = Column(String)
    used_point = Column(Integer)
    remaining_point = Column(Integer)
    order_no = Column(String)
    order_uid = Column(Integer)
    order_info_uid = Column(Integer)
    reason = Column(String)
    user_id = Column(String)
    partner_uid = Column(Integer)
    partner_id = Column(String)
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    delete_at = Column(DateTime, comment="삭제일") 
    update_at = Column(DateTime, comment="수정일")