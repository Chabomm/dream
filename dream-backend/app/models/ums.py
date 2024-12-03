from sqlalchemy import Column, String, Integer, ForeignKey, text, DateTime, Boolean, JSON

from app.core.database import Base

class T_UMS_TEMPLATE(Base):
    __tablename__ = "T_UMS_TEMPLATE"
    uid = Column(Integer, primary_key=True, index=True)
    ums_type = Column(String, comment="email/at")
    platform = Column(String, comment="사용처")
    layout_uid = Column(Integer)
    template_code = Column(String, comment="알림톡코드")
    subject = Column(String, comment="제목")
    content = Column(String, comment="내용")
    memo = Column(String, comment="관리자메모")
    profile = Column(String, comment="알림톡 프로필")
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    delete_at = Column(DateTime, comment="삭제일") 
    update_at = Column(DateTime, comment="수정일")

class T_UMS_LAYOUT(Base):
    __tablename__ = "T_UMS_LAYOUT"
    uid = Column(Integer, primary_key=True, index=True)
    layout_name = Column(String, comment="레이아웃명")
    content = Column(String, comment="내용")
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    delete_at = Column(DateTime, comment="삭제일") 
    update_at = Column(DateTime, comment="수정일")

class T_UMS_LOG(Base):
    __tablename__ = "T_UMS_LOG"
    uid = Column(Integer, primary_key=True, index=True)
    ums_uid = Column(Integer)
    ums_type = Column(String)
    platform = Column(String)
    template_code = Column(String)
    profile = Column(String)
    req = Column(String)
    res = Column(String)
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

class T_PUSH_BOOKING(Base):
    __tablename__ = "T_PUSH_BOOKING"
    uid = Column(Integer, primary_key=True, index=True)
    send_type = Column(String, comment="예약일")
    rec_type = Column(String, comment="수신대상")
    push_title = Column(String, comment="푸시 제목")
    push_msg = Column(String, comment="푸시 내용")
    push_img = Column(String, comment="푸시 이미지")
    push_link = Column(String, comment="푸시 연결링크")
    state = Column(String, default='100', comment="상태")
    send_count = Column(Integer, default=0, comment="발송 수")
    success_count = Column(Integer, default=0, comment="발송 성공 수")
    send_at = Column(DateTime, comment="발송일")
    booking_at = Column(DateTime, comment="발송예약일")
    partners = Column(JSON, comment="수신대상 P 고객사")
    devices = Column(JSON, comment="수신대상 S 개별디바이스")
    create_user = Column(String, comment="등록자")
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    update_at = Column(DateTime, comment="수정일")
    delete_at = Column(DateTime, comment="삭제일")
    start_send_at = Column(DateTime, comment="발송시작일시")
    end_send_at = Column(DateTime, comment="발송종료일시")
  
class T_PUSH_BOOKING_MSG(Base):
    __tablename__ = "T_PUSH_BOOKING_MSG"
    uid = Column(Integer, primary_key=True, index=True)
    booking_uid = Column(Integer, comment="T_PUSH_BOOKING uid")
    bars_uuid = Column(String, comment="DEVICE UUID")
    user_id = Column(String, comment="로그인 아이디")
    partner_id = Column(String, comment="고객사 아이디")
    device_os = Column(String, comment="android/ios")
    push_title = Column(String, comment="푸시 제목")
    push_msg = Column(String, comment="푸시 내용")
    push_img = Column(String, comment="푸시 이미지")
    push_link = Column(String, comment="푸시 연결링크")
    push_result = Column(String, comment="전송결과")
    send_at = Column(DateTime, comment="전송예정일")
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
  
class T_PUSH_BOOKING_TESTER(Base):
    __tablename__ = "T_PUSH_BOOKING_TESTER"
    uid = Column(Integer, primary_key=True, index=True)
    tester_name = Column(String, comment="테스터명")
    bars_uuid = Column(String, comment="DEVICE UUID")
    user_id = Column(String, comment="로그인 아이디")
    partner_id = Column(String, comment="고객사 아이디")
    device_os = Column(String, comment="android / ios")
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    update_at = Column(DateTime, comment="수정일")
    delete_at = Column(DateTime, comment="삭제일")
  
class T_TEMP(Base):
    __tablename__ = "T_TEMP"
    uid = Column(Integer, primary_key=True, index=True)
    col_int = Column(Integer)
    col_str = Column(String)
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    update_at = Column(DateTime, comment="수정일")
