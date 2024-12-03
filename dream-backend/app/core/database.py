import os
import sqlparse
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pygments import highlight
from pygments.formatters.terminal import TerminalFormatter
from pygments.lexers import SqlLexer  # to highlight SQL statements
from sqlalchemy.orm import Query
from urllib.parse import quote_plus

DATABASE_USER = os.environ['MYSQL_USER']
DATABASE_PASSWORD = quote_plus(os.environ['MYSQL_PASSWORD']) # 비밀번호에 @들어간경우 방지
DATABASE_HOST = os.environ['MYSQL_HOST']
DATABASE_PORT = os.environ['MYSQL_PORT']
DATABASE_NAME = os.environ['MYSQL_DATABASE']
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

engine = create_engine (
    SQLALCHEMY_DATABASE_URL
    ,pool_size=20
    ,pool_recycle=500
    ,max_overflow=20
    ,echo=True if os.environ['PROFILE']=="development" else False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_session():
    with Session(engine) as session:
        yield session

def format_sql(query: Query): 
    if os.environ.get('PROFILE') == 'development' :
        print("┏───────────────SQL QUERY───────────────────┓")
        compiled = query.statement.compile(
            engine, compile_kwargs={"literal_binds": True})
        parsed = sqlparse.format(str(compiled), reindent=True, keyword_case='upper')
        print(highlight(parsed, SqlLexer(), TerminalFormatter()))
        print("└───────────────────────────────────────────┘")