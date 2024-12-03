from sqlalchemy import Column, String, Integer, ForeignKey, text, DateTime, JSON

from app.core.database import Base
from app.schemas.schema import *

class T_APP_DEVICE(Base):
    __tablename__ = "T_APP_DEVICE"
    uid = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    partner_id = Column(String)
    bars_uuid = Column(String)
    device_os = Column(String)
    gender = Column(String)
    birth = Column(String)
    mobile = Column(String)
    email = Column(String)
    is_sms = Column(String)
    is_mailing = Column(String)
    is_push = Column(String)
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    update_at = Column(DateTime)
    delete_at = Column(DateTime)