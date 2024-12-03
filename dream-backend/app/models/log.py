from sqlalchemy import Column, String, Integer, ForeignKey, text, DateTime, Boolean, JSON

from app.core.database import Base

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
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    file_url = Column(String)
    file_name = Column(String)


class T_FAIL_PASSWORD(Base):
    __tablename__ = "T_FAIL_PASSWORD"
    uid = Column(Integer, primary_key=True, index=True)
    table_uid = Column(Integer)
    table_name = Column(String)
    input_value = Column(String)
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    user_ip = Column(String)

class T_FAIL_PASSWORD_HISTORY(Base):
    __tablename__ = "T_FAIL_PASSWORD_HISTORY"
    uid = Column(Integer, primary_key=True, index=True)
    table_uid = Column(Integer)
    table_name = Column(String)
    input_value = Column(String)
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    user_ip = Column(String)

class T_EXCEL_DOWNLOAD(Base):
    __tablename__ = "T_EXCEL_DOWNLOAD"
    uid = Column(Integer, primary_key=True, index=True)
    token_name = Column(String)
    user_id = Column(String)
    user_name = Column(String)
    user_ip = Column(String)
    reason = Column(String)
    url = Column(String)
    params = Column(JSON, default=[], comment='')
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))