from sqlalchemy import Column, String, Integer, ForeignKey, text, DateTime, Boolean

from app.core.dbSCM import Base

class T_CHANGE_LOG(Base):
    __tablename__ = "T_CHANGE_LOG"
    uid = Column(Integer, primary_key=True, index=True)
    table_uid = Column(Integer)
    table_name = Column(String)
    column_key = Column(String)
    column_name = Column(String)
    cl_before = Column(String)
    cl_after = Column(String)
    create_user = Column(String)
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

class T_MEMO(Base):
    __tablename__ = "T_MEMO"
    uid = Column(Integer, primary_key=True, index=True)
    table_uid = Column(Integer)
    table_name = Column(String)
    memo = Column(String)
    create_user = Column(String)
    token_name = Column(String)
    sosok_id = Column(String)
    sosok_uid = Column(Integer)
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    file_url = Column(String)
    file_name = Column(String)