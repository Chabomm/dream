import os
import socket
import datetime
from pytz import timezone
import time
import re
from datetime import datetime, timedelta, date
from fastapi.encoders import jsonable_encoder
from fastapi import Request
from sqlalchemy import inspect

# 현재 시간 get
def getNow(f = "%Y-%m-%d %H:%M:%S"):
    current_time = datetime.today() # 2021-08-15 20:58:43.302125
    current_time =  current_time.strftime(f) # 2021-08-15 20:58:43
    return current_time

def getUnixTime() :
    return time.time()

# 클라이언트 IP get
def getClientIP(request: Request):
    real_ip = str(request.headers.get('x-real-ip'))
    forwarded_ip = request.headers.get('x-forwarded-for')
    ip = request.client.host
    # print(real_ip, forwarded_ip, ip)
    # print(request.__dict__)
    return real_ip

def getDateTimeToUnixTimeStamp(date_time):
    # print("date_time", date_time)
    return time.mktime(date_time.timetuple())

def emailVaild(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if(re.fullmatch(regex, email)):
        return True
    else:
        return False

# 파일 생성 및 작성
def file_open(file_path, file_name, file_cont):
    makedirs(file_path)
    f = open(file_path+file_name, 'a', encoding='utf-8')
    f.write(file_cont + "\n\n")
    f.close()
    return

def makedirs(path): 
   try: 
        os.makedirs(path) 
   except OSError: 
       if not os.path.isdir(path): 
           raise

# utc+9시간
def convert_kst(utc_string):
	# datetime 값으로 변환
	dt_tm_utc = datetime.strptime(utc_string,'%Y-%m-%d %H:%M:%S')
	
	# +9 시간
	tm_kst = dt_tm_utc + timedelta(hours=9)
	
	# 일자 + 시간 문자열로 변환
	str_datetime = tm_kst.strftime('%Y-%m-%d %H:%M:%S')
	
	return str_datetime

# 테이블 조인
# 이제 안씀
def joinTable(q) :
    rows = []
    for c in q.all():
        cols = {}
        # print("c", dict(zip(c.keys(), c)))
        for o in jsonable_encoder(c):
            if o is not None :
                cols.update(o) 
        rows.append(cols)
    return rows


from Cryptodome.Cipher import AES
import base64

def encrypt_aes_128(clear_text, key, iv):
    
    key_byte = key.encode('utf-8')
    key_byte = key_byte.ljust(16, "\0".encode('utf-8'))
    if len(key_byte) > 16:
        key_byte = key_byte[:16]
    iv_byte = iv.encode('utf-8')
    iv_byte = iv_byte.ljust(16, "\0".encode('utf-8'))
    if len(iv_byte) > 16:
        key_byte = key_byte[:16]

    # PKCS#5
    pad_len = 16 - len(str.encode(clear_text)) % 16
    padding = chr(pad_len) * pad_len
    clear_text += padding

    cryptor = AES.new(key_byte, AES.MODE_CBC, iv_byte)
    data = cryptor.encrypt(str.encode(clear_text))

    return str(base64.b64encode(data).decode('utf-8'))

def decrypt_aes_128(data, key, iv):

    if data is None :
        return None

    data_byte = base64.b64decode(data.encode('utf-8'))
    key_byte = key.encode('utf-8')
    key_byte = key_byte.ljust(16, "\0".encode('utf-8'))
    if len(key_byte) > 16:
        key_byte = key_byte[:16]
    iv_byte = iv.encode('utf-8')
    iv_byte = iv_byte.ljust(16, "\0".encode('utf-8'))
    if len(iv_byte) > 16:
        key_byte = key_byte[:16]

    cryptor = AES.new(key_byte, AES.MODE_CBC, iv_byte)
    c_text = cryptor.decrypt(data_byte)

    # PKCS#5
    pad_len = ord(c_text.decode('utf-8')[-1])
    clear_text = c_text.decode('utf-8')[:-pad_len]
    return clear_text

import json
# BaseModel schema to json
def toJson(obj):
    # print("type of object : ", type(obj))
    try :
        if 'app.schemas' in str(type(obj)) :
            return json.loads(obj.json())

        if 'app.models' in str(type(obj)) :
            return json.dumps(jsonable_encoder(obj), ensure_ascii=False, indent=4)
        
        if 'dict' in str(type(obj)) :
            return json.dumps(jsonable_encoder(obj), ensure_ascii=False, indent=4)
        
        if 'list' in str(type(obj)) :
            return json.dumps(jsonable_encoder(obj), ensure_ascii=False, indent=4)
    except Exception as e :
        return obj

# request의 get,post body 가져오기
async def getRequestParams(request : Request) :
    res = {}
    try: # 기본적으로 post data를 받기 때문에
        res = await request.json() 
        if request.query_params:
            res.update({'query': request.query_params})

    except Exception as e :
        if request.query_params:
            res.update({'query': str(request.query_params)})

    print("┏────────────request.state.body─────────────┓")
    print(json.dumps(res, ensure_ascii=False, indent=2))
    print("└───────────────────────────────────────────┘")
    
    return res

def checkNumeric(n) :
    try :
        n = str(n).replace(",", "") # 쉼표제거
        if str(n).isnumeric :
            return int(n)
        else :
            return 0
    except Exception as e :
        return 0
    
def null2Blank(value) :
    try :
        if value == None :
            return ""
        else :
            return value
    except Exception as e :
        return ""
    
def get_request_url(request: Request) :
    if request.headers.get('x-forwarded-proto') == None :
        request_url = str(request._url)
    else :
        request_url = str(request.headers.get('x-forwarded-proto')) + "://"
        request_url = request_url + str(request.headers.get('x-forwarded-host'))
        request_url = request_url + str(request.url.path)
        request_url = request_url + ("?" + str(request.query_params) if str(request.query_params) != "" else "")
    return request_url
    
def get_request_url_pure(request: Request) :
    if request.headers.get('x-forwarded-proto') == None :
        request_url = str(request._url)
    else :
        request_url = str(request.headers.get('x-forwarded-proto')) + "://"
        request_url = request_url + str(request.headers.get('x-forwarded-host'))
        request_url = request_url + str(request.url.path)
        request_url = request_url + ("?" + str(request.query_params) if str(request.query_params) != "" else "")
    return request_url

# sql first할때 model을 통으로 first한 res를 dict(json) 으로 변환
# (ex) res = db.query(T_CONFIG).filter(T_CONFIG.uid == partner.uid).first()
#      jsondata['res'] = util.object_as_dict(res)
def object_as_dict(obj):
    return {
        c.key: getattr(obj, c.key)
        for c in inspect(obj).mapper.column_attrs
    }

# sql select 할때 컬럼을 지정한 res 는 -> dict(zip(res.keys(), res)) 
# sql select 할때 model을 통으로 지정한 res 는 -> util.object_as_dict(res)



def isEmptyObject(obj, key) :
    try :
        if obj[key] is None : 
            return True
        else :
            if str(obj[key]) == "" :
                return True
            else :
                return False
    except Exception as e:
        return True


def masking_user_ip(str) :
    try :
        user_ip = str.split('.')
        return user_ip[0] + "." + "***" + "." + "***" + "." + user_ip[3]
    except Exception as e:
        return ""
    
    

# 리턴할지말지
def is_exception_return(obj):

    # print(type(obj), str(type(obj)))

    if 'app.schemas' in str(type(obj)) :
        return False

    elif 'int' in str(type(obj)) :
        return False

    elif 'app.models' in str(type(obj)) :
        return False
    
    elif 'dict' in str(type(obj)) and  "code" in obj and obj["code"] != 200  :
        return True
    
    else :
        return False
    
    # if 'list' in str(type(obj)) :
    #     return json.dumps(jsonable_encoder(obj), ensure_ascii=False, indent=4)


def fn_masking_user_name(name) :
    return name[:1] + "*" * (len(name)-1)

def fn_masking_user_email(email) :
    if email is not None and "@" in email :
        arr_email = email.split("@")
        if len(arr_email) == 2 :
            return arr_email[0][:2] + "*"*(len(arr_email[0])-2) + "@" + arr_email[1]

def fn_masking_user_mobile(mobile) :
    if mobile is not None and "-" in mobile :
        arr_mobile = mobile.split("-")
        if len(arr_mobile) == 3 :
            return arr_mobile[0] + "-" + "*"*(len(arr_mobile[1])) + "-" + arr_mobile[2]
        


import datetime as dt
def MMDDhhmmss() :
    today = dt.datetime.now()
    return (
        str(today.month).zfill(2) + 
        str(today.day).zfill(2) + 
        str(today.hour).zfill(2) + 
        str(today.minute).zfill(2) + 
        str(today.second).zfill(2)
    )
       
def YYYYMMDD() :
    today = dt.datetime.now()
    return (
        str(today.year).zfill(4) + 
        str(today.month).zfill(2) + 
        str(today.day).zfill(2)
    )
       
def hhmmss() :
    today = dt.datetime.now()
    return (
        str(today.hour).zfill(2) + 
        str(today.minute).zfill(2) + 
        str(today.second).zfill(2)
    )

