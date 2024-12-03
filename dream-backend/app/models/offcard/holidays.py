from sqlalchemy import Column, String, Integer, ForeignKey, text, DateTime, Boolean, JSON
from app.core.database import Base

class T_HOLIDAYS(Base): # 공휴일
    __tablename__ = "T_HOLIDAYS"
    uid = Column(Integer, primary_key=True, index=True)
    date_name = Column(String, comment="명칭")
    locdate = Column(String, comment="공휴일")