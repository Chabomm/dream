import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from urllib.parse import quote_plus

DATABASE_USER_SCM = os.environ['MYSQL_USER_SCM']
DATABASE_PASSWORD_SCM = quote_plus(os.environ['MYSQL_PASSWORD_SCM']) # 비밀번호에 @들어간경우 방지
DATABASE_HOST_SCM = os.environ['MYSQL_HOST_SCM']
DATABASE_PORT_SCM = os.environ['MYSQL_PORT_SCM']
DATABASE_NAME_SCM = os.environ['MYSQL_DATABASE_SCM']
SQLALCHEMY_DATABASE_URL_SCM = f"mysql+pymysql://{DATABASE_USER_SCM}:{DATABASE_PASSWORD_SCM}@{DATABASE_HOST_SCM}:{DATABASE_PORT_SCM}/{DATABASE_NAME_SCM}"

engine_scm = create_engine (
    SQLALCHEMY_DATABASE_URL_SCM
    ,pool_size=20
    ,pool_recycle=500
    ,max_overflow=20
    ,echo=True if os.environ['PROFILE']=="development" else False
)

SessionLocal_scm = sessionmaker(autocommit=False, autoflush=False, bind=engine_scm)

Base = declarative_base()

def get_session():
    with Session(engine_scm) as session:
        yield session
