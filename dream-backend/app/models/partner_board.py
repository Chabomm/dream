from sqlalchemy import Column, String, Integer, ForeignKey, text, DateTime, Boolean, JSON, Text

from app.core.database import Base

class T_PARTNER_BOARD(Base): # 게시판
    __tablename__ = "T_PARTNER_BOARD"
    uid = Column(Integer, primary_key=True, index=True)
    board_type = Column(String, default='common')
    board_name = Column(String)
    per_write = Column(String)
    per_read = Column(String)
    is_comment = Column(String)
    is_display = Column(String)
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    delete_at = Column(DateTime, comment="삭제일") 
    update_at = Column(DateTime, comment="수정일")
    front_url = Column(String)

class T_PARTNER_BOARD_POSTS(Base): # 게시물
    __tablename__ = "T_PARTNER_BOARD_POSTS"
    uid = Column(Integer, primary_key=True, index=True, nullable=False)
    partner_uid = Column(Integer, ForeignKey('T_PARTNER.uid'))
    partner_id = Column(String)
    board_uid = Column(Integer, ForeignKey('T_PARTNER_BOARD.uid'), nullable=False)
    cate_uid = Column(Integer)
    thumb  = Column(String, comment="썸네일")
    title  = Column(String, comment="게시물 제목")
    contents  = Column(Text, comment="게시물 본문")
    tags  = Column(String, comment="태그")
    is_display = Column(String, default='T', comment="공개여부")
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    update_at = Column(DateTime, comment="수정일")
    delete_at = Column(DateTime, comment="삭제일")
    create_user  = Column(String, comment="작성자 아이디")

# class T_BOARD(Base): # 게시판
#     __tablename__ = "T_BOARD"
#     uid = Column(Integer, primary_key=True, index=True)
#     partner_uid = Column(Integer)
#     partner_id = Column(String)
#     board_type = Column(String, default='common')
#     board_name = Column(String)
#     per_write = Column(String)
#     per_read = Column(String)
#     is_comment = Column(String)
#     is_display = Column(String)
#     create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
#     delete_at = Column(DateTime, comment="삭제일") 
#     update_at = Column(DateTime, comment="수정일")
#     front_url = Column(String)