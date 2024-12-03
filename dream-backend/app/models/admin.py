from sqlalchemy import Column, String, Integer, ForeignKey, text, DateTime, Boolean, JSON

from app.core.database import Base

class T_ADMIN(Base):
    __tablename__ = "T_ADMIN"
    uid = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    user_name = Column(String)
    tel = Column(String)
    mobile = Column(String)
    email = Column(String)
    position1 = Column(String)
    position2 = Column(String)
    depart = Column(String)
    role = Column(String)
    roles = Column(JSON, default=[])
    state = Column(String, default='200')
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    delete_at = Column(DateTime, comment="삭제일") 
    update_at = Column(DateTime, comment="수정일")
    last_at = Column(DateTime, comment="마지막 접속일")