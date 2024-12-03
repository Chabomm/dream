from sqlalchemy import Column, String, Integer, ForeignKey, text, DateTime, Boolean, JSON, Text

from app.core.dbSCM import Base

class T_DREAM_COUNSEL(Base):
    __tablename__ = "T_DREAM_COUNSEL"
    uid = Column(Integer, primary_key=True, index=True)
    company_name = Column(String) 
    homepage_url = Column(String) 
    staff_count = Column(Integer) 
    wish_build_at = Column(DateTime) 
    staff_name = Column(String) 
    staff_dept = Column(String) 
    staff_position = Column(String) 
    staff_position2 = Column(String) 
    staff_mobile = Column(String) 
    staff_email = Column(String) 
    contents = Column(String)
    state = Column(String, default='100') 
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    update_at = Column(DateTime) 
    delete_at = Column(DateTime)