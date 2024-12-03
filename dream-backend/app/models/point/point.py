from sqlalchemy import Column, String, Integer, ForeignKey, text, DateTime, Boolean, JSON

from app.core.database import Base

class T_POINT(Base):
    __tablename__ = "T_POINT"
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

class T_POINT_GROUP(Base):
    __tablename__ = "T_POINT_GROUP"
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

class T_POINT_USED(Base):
    __tablename__ = "T_POINT_USED"
    uid = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer)
    point_id  = Column(Integer)
    used_type = Column(String, comment="1:사용, 2:환불, 3:차감")
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

class T_POINT_LIMIT(Base):
    __tablename__ = "T_POINT_LIMIT"
    uid = Column(Integer, primary_key=True, index=True)
    point_type = Column(String)
    partner_uid = Column(Integer)
    partner_id = Column(String)
    cate = Column(String)
    word = Column(String)
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    delete_at = Column(DateTime, comment="삭제일") 
    update_at = Column(DateTime, comment="수정일")

class T_POINT_EXP(Base):
    __tablename__ = "T_POINT_EXP"
    uid = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer)
    point_id  = Column(Integer)
    exp_type = Column(String)
    exp_point = Column(Integer) 
    reason = Column(String) 
    user_id = Column(String)
    partner_uid = Column(Integer)
    partner_id = Column(String)
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    delete_at = Column(DateTime, comment="삭제일") 
    update_at = Column(DateTime, comment="수정일")


