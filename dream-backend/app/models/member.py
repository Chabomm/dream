from sqlalchemy import Column, String, Integer, ForeignKey, text, DateTime, Boolean, JSON

from app.core.database import Base

class T_MEMBER(Base):
    __tablename__ = "T_MEMBER"
    uid = Column(Integer, primary_key=True, index=True)
    site_id = Column(String)
    login_id = Column(String)
    user_id = Column(String)
    partner_uid = Column(Integer)
    partner_id = Column(String)
    prefix = Column(String)
    user_name = Column(String)
    mobile = Column(String)
    email = Column(String)
    aff_uid = Column(Integer)
    user_ci = Column(String)
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    delete_at = Column(DateTime, comment="삭제일") 
    update_at = Column(DateTime, comment="수정일")
    # last_at = Column(DateTime, comment="마지막 접속일")

class T_MEMBER_INFO(Base):
    __tablename__ = "T_MEMBER_INFO"
    uid = Column(Integer, ForeignKey('T_MEMBER.uid'), primary_key=True, index=True)
    user_id = Column(String)
    login_id = Column(String)
    user_name = Column(String)
    prefix = Column(String)
    partner_uid = Column(Integer, ForeignKey('T_PARTNER.uid'))
    partner_id = Column(String)
    mem_uid = Column(Integer)
    serve = Column(String, default="재직")
    birth = Column(String)
    gender = Column(String)
    anniversary = Column(String)
    emp_no = Column(String)
    depart = Column(String)
    position = Column(String)
    position2 = Column(String)
    join_com = Column(String)
    post = Column(String)
    addr = Column(String)
    addr_detail = Column(String)
    tel = Column(String)
    affiliate = Column(String)
    state = Column(String, default="100")
    is_login = Column(String, default="T")
    is_point = Column(String, default="T")
    is_pw_reset = Column(String, default="T")
    user_ci = Column(String)
    user_di = Column(String)
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    delete_at = Column(DateTime, comment="삭제일") 
    update_at = Column(DateTime, comment="수정일")

class T_TEST(Base):
    __tablename__ = "T_TEST"
    uid = Column(Integer, primary_key=True, index=True)
    user_ci = Column(String)