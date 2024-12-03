from sqlalchemy import Column, String, Integer, ForeignKey, text, DateTime, Boolean

from app.core.database import Base
from app.schemas.schema import *


class T_NICE_CHECKPLUS(Base):
    __tablename__ = "T_NICE_CHECKPLUS"
    uid = Column(Integer, primary_key=True, index=True)
    req_seq = Column(String)
    client_id = Column(String)
    method = Column(String)
    success_url = Column(String)
    fail_url = Column(String)
    client_ip = Column(String)
    err_code = Column(String)
    err_msg = Column(String) 
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    update_at = Column(DateTime)
    delete_at = Column(DateTime)