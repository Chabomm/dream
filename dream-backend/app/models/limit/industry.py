from sqlalchemy import Column, String, Integer, ForeignKey, text, DateTime, Boolean, JSON

from app.core.database import Base

class T_INDUSTRY_CODE(Base):
    __tablename__ = "T_INDUSTRY_CODE"
    uid = Column(Integer, primary_key=True, index=True)
    card_name = Column(String, comment="카드사명") 
    group = Column(String, comment="업종그룹") 
    code = Column(String, comment="업종코드(MCT_RY_CD)")
    name = Column(String, comment="업종명(MCT_RY_NM)")
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    delete_at = Column(DateTime, comment="삭제일") 
    update_at = Column(DateTime, comment="수정일")

class T_INDUSTRY_OFFCARD(Base):
    __tablename__ = "T_INDUSTRY_OFFCARD"
    uid = Column(Integer, primary_key=True, index=True)
    indus_uid = Column(Integer, comment="T_INDUSTRY_CODE.uid") 
    code = Column(String)
    std_class = Column(String)
    partner_uid = Column(Integer)
    partner_id = Column(String) 
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    delete_at = Column(DateTime, comment="삭제일") 
    update_at = Column(DateTime, comment="수정일")

class T_INDUSTRY_SIKWON(Base):
    __tablename__ = "T_INDUSTRY_SIKWON"
    uid = Column(Integer, primary_key=True, index=True)
    indus_uid = Column(Integer, comment="T_INDUSTRY_CODE.uid") 
    code = Column(String) 
    std_class = Column(String) 
    partner_uid = Column(Integer)
    partner_id = Column(String) 
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    delete_at = Column(DateTime, comment="삭제일") 
    update_at = Column(DateTime, comment="수정일")