from fastapi import Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Optional
from inspect import currentframe as frame
from sqlalchemy.dialects import mysql as mysql_dialetct
from pymysql.converters import conversions, escape_item, encoders
from sqlalchemy import func, select, update, delete, Table, MetaData, and_
import math
from datetime import datetime, timedelta

from app.core import exceptions as ex
from app.core import util
from app.core.database import format_sql
from app.models.session import *

from app.models.offcard.holidays import *

# 공공데이터에서 가져온 공휴일, 임시공휴일 INSERT
def add_holidays(request: Request, json_ob: any) :
    request.state.inspect = frame()
    db = request.state.db

    bulks = []
    for item in json_ob["response"]["body"]["items"]["item"] :
        # bulks.append(T_HOLIDAYS(date_name=item["dateName"], locdate=item["locdate"])) 
        bulk_item = {}
        bulk_item["date_name"] = item["dateName"]
        bulk_item["locdate"] = str(item["locdate"])
        bulks.append(bulk_item)
    db.execute(T_HOLIDAYS.__table__.insert(), bulks)

# 내일이 공휴일인지 판별
def get_holidays(request: Request, mode: str) :
    request.state.inspect = frame()
    db = request.state.db
    today = datetime.today()
    ddate = ""
    if mode == "tomorrow" :
        tomorrow = today + timedelta(days=1)
        ddate = tomorrow.strftime("%Y%m%d")
        # 월요일 : 0, 화요일 : 1, 수요일 : 2, 목요일 : 3, 금요일 : 4, 토요일 : 5, 일요일 : 6
        if tomorrow.weekday() > 4 : # 주말
            return True
        
    elif mode == "today" :
        ddate = today.strftime("%Y%m%d")
        # 월요일 : 0, 화요일 : 1, 수요일 : 2, 목요일 : 3, 금요일 : 4, 토요일 : 5, 일요일 : 6
        if today.weekday() > 4 : # 주말
            return True

    if ddate == "" :
        return True
    
    res = db.query(T_HOLIDAYS).filter(T_HOLIDAYS.locdate == ddate).first()

    if res == None : 
        return False

    elif res != None :
        return True