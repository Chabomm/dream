
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Optional
from inspect import currentframe as frame
from sqlalchemy.dialects import mysql as mysql_dialetct
from pymysql.converters import conversions, escape_item, encoders
from sqlalchemy import func, select, update, delete, Table, MetaData
import math

import smtplib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders

from app.core.config import *
from app.core import util
from app.core.database import format_sql
from app.models.ums import *

# ums 템플릿 상세정보
def read_ums_tmpl(request: Request, ums_uid: int):
    request.state.inspect = frame()
    db = request.state.db
    sql = (
        db.query( 
             T_UMS_TEMPLATE.uid
            ,T_UMS_TEMPLATE.ums_type
            ,T_UMS_TEMPLATE.platform
            ,T_UMS_TEMPLATE.template_code
            ,T_UMS_TEMPLATE.subject
            ,T_UMS_TEMPLATE.content
            ,T_UMS_TEMPLATE.profile
            ,T_UMS_TEMPLATE.layout_uid
        )
        .filter(T_UMS_TEMPLATE.uid == ums_uid)
    )
    format_sql(sql)
    res = sql.first()
    if res is not None :
        res = dict(zip(res.keys(), res))
    return res

def getAtSendData(send_obj) :
    msgId = ""
    if "msgId" in send_obj and send_obj['msgId'] != "" :
        msgId = send_obj['msgId'] 
    
    if "at_msgId" in send_obj and send_obj['at_msgId'] != "" :
        msgId = send_obj['at_msgId'] 

    template_code = send_obj['template_code'] 
    toMobile = send_obj['toMobile'] 
    subject = send_obj['title'] 
    content = send_obj['content'] 
    sms_kind = "L"

    oData = {}
    oData["msgid"] = msgId
    oData["profile_key"] = send_obj["PROFILE_KEY"]
    oData["message_type"] = "AT"
    oData["template_code"] = template_code
    oData["receiver_num"] = toMobile
    oData["message"] = content
    oData["reserved_time"] = "00000000000000"
    oData["sms_title"] = subject
    oData["sms_message"] = content
    oData["sms_kind"] = sms_kind
    oData["sender_num"] = "01030342581"

    return oData

def getSmsSendData(send_obj) :
    
    msgId = ""

    if "msgId" in send_obj and send_obj['msgId'] != "" :
        msgId = send_obj['msgId'] 
    
    if "at_msgId" in send_obj and send_obj['at_msgId'] != "" : 
        msgId = send_obj['at_msgId'] 

    toMobile = send_obj['toMobile'] 
    subject = send_obj['title'] 
    content = send_obj['content'] 
    sms_kind = "S"

    oData = {}
    oData["msgid"] = msgId
    oData["profile_key"] = send_obj["PROFILE_KEY"]
    oData["receiver_num"] = toMobile
    oData["reserved_time"] = "00000000000000"
    oData["sms_only"] = "Y"
    oData["sms_message"] = content
    oData["sms_title"] = subject
    oData["sms_kind"] = sms_kind
    oData["sender_num"] = "01030342581"

    return oData

def send_mail(send_obj):
    send_cc = [] # 사용안하지만 선언은 해둠
    send_to = []
    send_to.append(send_obj["toEmail"])
    send_bcc = []

    if "bccEmail" in send_obj and send_obj["bccEmail"] != "" :
        send_bcc.append(send_obj["bccEmail"]) 
    
    elif "bcc_list" in send_obj and len(send_obj["bcc_list"]) > 0 :
        send_bcc = send_obj["bcc_list"] # 리스트

    if not util.emailVaild(send_obj["toEmail"]) :
        send_obj["result"] = "주소형식이 올바르지 않습니다"
        return send_obj

    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = ', '.join(send_to)
    msg['Cc'] = ', '.join(send_cc)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = send_obj["title"]
    msg.attach(MIMEText(send_obj["content"], 'html'))
    
    files=[] # 사용안하지만 선언은 해둠
    for path in files:
        part = MIMEBase('application', "octet-stream")
        with open(path, 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename=Path(path).name)
        msg.attach(part)
    
    rcpt = send_cc + send_bcc + send_to
    try : 
        smtp = smtplib.SMTP(EMAIL_SERVER, EMAIL_PORT)
        smtp.starttls()
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.sendmail(EMAIL_FROM, rcpt, msg.as_string())
        smtp.quit()
        send_obj["result"] = "OK"
        
    except smtplib.SMTPSenderRefused as ssre:
        send_obj["result"] = "발신자 주소가 거부되었습니다. 모든 SMTPResponseException 예외에 의해 설정된 어트리뷰트 외에도, 이것은 ‘sender’를 SMTP 서버가 거부한 문자열로 설정합니다.", str(ssre)

    except smtplib.SMTPHeloError as she:
        send_obj["result"] = "서버가 HELO 메시지를 거부했습니다.", str(she)

    except smtplib.SMTPDataError as sde:
        send_obj["result"] = "SMTP 서버가 메시지 데이터 수락을 거부했습니다.", str(sde)

    except smtplib.SMTPConnectError as sce:
        send_obj["result"] = "서버와의 연결을 설정하는 동안 에러가 발생했습니다.", str(sce)

    except smtplib.SMTPServerDisconnected as ssde:
        send_obj["result"] = "이 예외는 예기치 않게 서버와의 연결이 끊어지거나, 서버에 연결하기 전에 SMTP 인스턴스를 사용하려고 할 때 발생합니다.", str(ssde)

    except smtplib.SMTPAuthenticationError as sae:
        send_obj["result"] = "SMTP 인증이 잘못되었습니다. 서버가 제공된 username/password 조합을 수락하지 않았을 가능성이 높습니다.", str(sae)
    
    except smtplib.SMTPResponseException as sre:
        send_obj["result"] = "SMTP 에러 코드가 포함된 모든 예외의 베이스 클래스. 이러한 예외는 SMTP 서버가 에러 코드를 반환하는 일부 경우에 생성됩니다. 에러 코드는 에러의 smtp_code 어트리뷰트에 저장되며, smtp_error 어트리뷰트는 에러 메시지로 설정됩니다.", str(sre)

    except smtplib.SMTPRecipientsRefused as srre:
        send_obj["result"] = "모든 수신자 주소가 거부되었습니다. 각 수신자의 에러는 SMTP.sendmail()이 반환하는 것과 정확히 같은 종류의 딕셔너리인 recipients 어트리뷰트를 통해 액세스 할 수 있습니다.", str(srre)

    except smtplib.SMTPNotSupportedError as snse:
        send_obj["result"] = "시도한 명령이나 옵션이 서버에서 지원되지 않습니다.", str(snse)

    except smtplib.SMTPException as se:
        send_obj["result"] = "이 모듈에서 제공하는 다른 모든 예외에 대한 베이스 예외 클래스인 OSError의 서브 클래스.", str(se)

    return send_obj



def create_umslog(request: Request, log_param: T_UMS_LOG):
    request.state.inspect = frame()
    db = request.state.db
    db_item = log_param 
    db.add(db_item)
    db.flush()
    db.commit()
    return db_item