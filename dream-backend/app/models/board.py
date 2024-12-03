from sqlalchemy import Column, String, Integer, ForeignKey, text, DateTime, Boolean, JSON, Text

from app.core.database import Base


class T_BOARD(Base):
    __tablename__ = "T_BOARD"
    uid = Column(Integer, primary_key=True, index=True)
    site_id= Column(String, comment="프로젝트")
    board_type = Column(String, default='common', comment="게시판 유형")
    board_name = Column(String, comment="게시판 이름")
    permission_read = Column(JSON, default=[], comment="읽기권한")
    permission_write = Column(JSON, default=[], comment="쓰기권한")
    is_comment = Column(String, default='F', comment="댓글여부")
    is_display = Column(String, default='T', comment="표시여부")
    front_url = Column(String, comment="프론트 URL")
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    update_at = Column(DateTime, comment="수정일")
    delete_at = Column(DateTime, comment="삭제일")


class T_BOARD_POSTS(Base): # 게시물
    __tablename__ = "T_BOARD_POSTS"
    uid = Column(Integer, primary_key=True, index=True, nullable=False)
    board_uid = Column(Integer, ForeignKey('T_BOARD.uid'))
    site_id = Column(String)
    cate_uid = Column(Integer)
    partner_uid = Column(String, comment='T_PARTNER.uid')
    thumb  = Column(String, comment="썸네일")
    youtube  = Column(String, comment="유튜브 링크")
    title  = Column(String, comment="게시물 제목")
    contents  = Column(Text, comment="게시물 본문")
    tags  = Column(String, comment="태그")
    is_display = Column(String, default='T', comment="공개여부")
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    update_at = Column(DateTime, comment="수정일")
    delete_at = Column(DateTime, comment="삭제일")
    state = Column(String, comment="100: 미답변, 200: 답변완료, 300: 공지")
    user_ip = Column(String, comment="아이피주소")
    create_user = Column(String, comment="등록자 아이디")
    create_name = Column(String, comment="등록자 이름")

class T_BOARD_FILES(Base):
    __tablename__ = "T_BOARD_FILES"
    uid = Column(Integer, primary_key=True, index=True, nullable=False)
    board_uid = Column(Integer)
    posts_uid = Column(Integer)
    fake_name  = Column(String, comment="파일명")
    file_url  = Column(String, comment="첨부파일 URL")
    sort = Column(Integer)
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    update_at = Column(DateTime, comment="수정일")
    delete_at = Column(DateTime, comment="삭제일")

class T_BOARD_FILES_LOG(Base):
    __tablename__ = "T_BOARD_FILES_LOG"
    uid = Column(Integer, primary_key=True, index=True, nullable=False)
    board_uid = Column(Integer)
    posts_uid = Column(Integer)
    file_uid = Column(Integer)
    file_url  = Column(String, comment="첨부파일 URL")
    down_user = Column(String)
    down_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


class T_BOARD_POSTS_PERSON(Base):
    __tablename__ = "T_BOARD_POSTS_PERSON"
    uid = Column(Integer, ForeignKey('T_BOARD_POSTS.uid'), primary_key=True, index=True, nullable=False)
    board_uid = Column(Integer)
    cate_uid = Column(Integer)
    password  = Column(String, comment="비밀번호")
    name  = Column(String, comment="이름")
    email  = Column(String, comment="이메일 주소")
    mobile  = Column(String, comment="휴대전화번호")
    create_user = Column(String, comment="등록자 아이디")

class T_BOARD_POSTS_REPLY(Base):
    __tablename__ = "T_BOARD_POSTS_REPLY"
    uid = Column(Integer, primary_key=True, index=True, nullable=False)
    board_uid = Column(Integer, ForeignKey('T_BOARD.uid'))
    cate_uid = Column(Integer)
    posts_uid = Column(Integer, ForeignKey('T_BOARD_POSTS.uid'))
    reply  = Column(String, comment="답변내용")
    user_id  = Column(String, comment="등록자 아이디")
    user_name  = Column(String, comment="등록자 이름")
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    update_at = Column(DateTime, comment="수정일")
    delete_at = Column(DateTime, comment="삭제일")












