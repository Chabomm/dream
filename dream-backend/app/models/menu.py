from sqlalchemy import Column, String, Integer, ForeignKey, text, DateTime, Boolean, JSON

from app.core.database import Base

class T_ADMIN_MENU(Base):
    __tablename__ = "T_ADMIN_MENU"
    uid = Column(Integer, primary_key=True, index=True)
    site_id = Column(String, comment="admin, manager, member")
    name = Column(String, comment="메뉴명")
    icon = Column(String, comment="아이콘")
    to = Column(String, comment="링크")
    sort = Column(Integer, comment="순서")
    depth = Column(Integer, comment="단계", default=1)
    parent = Column(Integer, comment="부모uid", default=0)

class T_ADMIN_ROLE(Base):
    __tablename__ = "T_ADMIN_ROLE"
    uid = Column(Integer, primary_key=True, index=True)
    name = Column(String, comment="역할명")
    menus = Column(JSON, comment="배정된메뉴 uids")
    partner_uid = Column(Integer, comment="파트너 uid")
    site_id = Column(String, comment="admin, manager, member")
