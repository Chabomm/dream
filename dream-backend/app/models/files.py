
from sqlalchemy import Column, String, Integer, ForeignKey, text, DateTime, JSON

from app.core.database import Base
from app.schemas.schema import *

class T_FILES_ATTACH(Base):
    __tablename__ = "T_FILES_ATTACH"
    uid = Column(Integer, primary_key=True, index=True)
    table_name = Column(String)
    table_uid = Column(Integer)
    fake_name = Column(String)
    file_name = Column(String)
    file_ext = Column(String)
    upload_path = Column(String)
    sort = Column(Integer)
    token_name = Column(String)
    sosok_uid = Column(Integer)
    sosok_id = Column(String)
    user_uid = Column(Integer)
    user_id = Column(String)
    user_name = Column(String)
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    update_at = Column(DateTime)
    delete_at = Column(DateTime)

