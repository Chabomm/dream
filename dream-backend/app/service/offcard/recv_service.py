from fastapi import Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Optional
from inspect import currentframe as frame
from sqlalchemy.dialects import mysql as mysql_dialetct
from pymysql.converters import conversions, escape_item, encoders
from sqlalchemy import func, select, update, delete, Table, MetaData, and_, insert, literal_column
import math
from datetime import datetime, timedelta
from app.core import exceptions as ex
from app.core import util
from app.core.database import format_sql
from app.models.session import *

from app.models.member import *
from app.models.offcard.files import *
from app.models.limit.industry import *
from app.schemas.manager.point.offcard.used import *

def set_EDI06982(request: Request, datas: any) :
    request.state.inspect = frame()
    db = request.state.db
    bulks = []
    for item in datas :
        bulk_item = {}
        bulk_item["IPN_LIK_N"] = item["D아이핀연계번호"]
        bulk_item["QY_STD"] = item["D조회시작일자"]
        bulk_item["QY_EDD"] = item["D조회종료일자"]
        bulk_item["ERO_CD"] = item["D에러코드"]
        bulk_item["SLT_WF_FIM_CD"] = item["D선택복지업체코드"]
        bulks.append(bulk_item)

    db.execute(FT_EDI06982.__table__.insert(), bulks)

def set_EDI06983(request: Request, datas: any) :
    request.state.inspect = frame()
    db = request.state.db
    bulks = []
    for item in datas :
        bulk_item = {}
        bulk_item["TG_SEQNUM"] = item["D전문일련번호"]
        bulk_item["CDO_CD"] = item["D카드사코드"]
        bulk_item["IPN_LIK_N"] = item["D아이핀연계번호"]
        bulk_item["CRD_N"] = item["D카드번호"]
        bulk_item["SI_N"] = item["D전표번호"]
        bulk_item["AQ_D"] = item["D매입일자"]
        bulk_item["APV_D"] = item["D승인일자"]
        bulk_item["APV_N"] = item["D승인번호"]
        bulk_item["MCT_NM"] = item["D가맹점명"]
        bulk_item["RY_CCD"] = item["D업종구분코드"]
        bulk_item["SEA"] = item["D사용금액"]
        bulk_item["SLT_F"] = item["D선택여부"]
        bulk_item["CRD_AFL_CD"] = item["D카드제휴코드"]
        bulk_item["MCT_N"] = item["D가맹점번호"]
        bulk_item["SBE_K_RGN"] = item["DSUB사업자등록번호"]
        bulk_item["SBE_K_NM"] = item["DSUB사업자명"]
        bulk_item["MCT_ETK_N"] = item["D가맹점사업자번호"]
        bulk_item["WF_ITM_CCD"] = item["D복지항목구분코드"]
        bulk_item["GNR_AFL_CRD_C"] = item["D일반제휴카드구분"]
        bulk_item["SLT_WF_FIM_CD"] = item["D선택복지업체코드"]
        bulks.append(bulk_item)

    db.execute(FT_EDI06983.__table__.insert(), bulks)

def set_EDI06984(request: Request, datas: any) :
    request.state.inspect = frame()
    db = request.state.db
    bulks = []
    for item in datas :
        bulk_item = {}
        bulk_item["R_LSP_RID"]  = item["D원매출전표접수일자"]
        bulk_item["R_LSP_N"]    = item["D원매출전표번호"]
        bulk_item["CE_RID"]     = item["D취소접수일자"]
        bulk_item["SLS_OR_D"]   = item["D매출발생일자"]
        bulk_item["SAA"]        = item["D매출금액"]
        bulk_item["IPN_LIK_N"]  = item["D아이핀연계번호"]
        bulk_item["MCT_N"]      = item["D가맹점번호"]
        bulk_item["MCT_NM"]     = item["D가맹점명"]
        bulks.append(bulk_item)

    db.execute(FT_EDI06984.__table__.insert(), bulks)

def set_EDI06985(request: Request, datas: any) :
    request.state.inspect = frame()
    db = request.state.db
    bulks = []
    for item in datas :
        bulk_item = {}
        bulk_item["LSP_RID"]         = item["D매출전표접수일자"]
        bulk_item["LSP_N"]           = item["D매출전표번호"]
        bulk_item["SLS_OR_D"]        = item["D매출발생일자"]
        bulk_item["MCT_N"]           = item["D가맹점번호"]
        bulk_item["SAA"]             = item["D매출금액"]
        bulk_item["CRP_CRD_N"]       = item["D법인카드번호"]
        bulk_item["CRP_BLA"]         = item["D법인청구금액"]
        bulk_item["ERO_CD"]          = item["D에러코드"]
        bulk_item["FMY_CP_CD_N"]     = item["D패밀리회사코드번호"]
        bulk_item["LTM_LSV_PNT_SEA"] = item["D장기근속포인트사용금액"]
        bulk_item["WF_SLT_SEA"]      = item["D복지선택사용금액"]
        bulks.append(bulk_item)

    db.execute(FT_EDI06985.__table__.insert(), bulks)

def set_EDI06986(request: Request, datas: any) :
    request.state.inspect = frame()
    db = request.state.db
    bulks = []
    for item in datas :
        bulk_item = {}
        bulk_item["PSN_R_LSP_RID"]  = item["D개인원매출전표접수일자"]
        bulk_item["PSN_R_LSP_N"]    = item["D개인원매출전표번호"]
        bulk_item["PSN_CLA"]        = item["D개인취소금액"]
        bulk_item["CRP_R_LSP_RID"]  = item["D법인원매출전표접수일자"]
        bulk_item["CRP_R_LSP_N"]    = item["D법인원매출전표번호"]
        bulk_item["CRP_CLA"]        = item["D법인취소금액"]
        bulk_item["CRP_CLNN"]       = item["D법인고객번호"]
        bulk_item["MCT_N"]          = item["D가맹점번호"]
        bulk_item["ERO_CD"]         = item["D에러코드"]
        bulks.append(bulk_item)

    db.execute(FT_EDI06986.__table__.insert(), bulks)



# 카드 사용 내역
def get_EDI06983(request: Request, cardUsedListInput:CardUsedListInput, user:T_MEMBER_INFO) :
    request.state.inspect = frame()
    db = request.state.db

    filters = []
    filters.append(getattr(FT_EDI06983, "IPN_LIK_N") == user.user_ci)

    # if cardUsedListInput.filters :
    #     if cardUsedListInput.filters["create_at"]["startDate"] and cardUsedListInput.filters["create_at"]["endDate"] :
    #         filters.append(
    #             and_(
    #                 func.date_format(T_CARD_USED.APV_D, '%Y-%m-%d').label('APV_D') >= cardUsedListInput.filters["create_at"]["startDate"]
    #                 ,func.date_format(T_CARD_USED.APV_D, '%Y-%m-%d').label('APV_D') <= cardUsedListInput.filters["create_at"]["endDate"] + " 23:59:59"
    #             )
    #         )

    industry_stmt = (
        db.query(
             T_INDUSTRY_OFFCARD.uid
            ,T_INDUSTRY_OFFCARD.code
        )
        .filter(T_INDUSTRY_OFFCARD.partner_uid == user.partner_uid)
        .subquery()
    )

    sql = (
        db.query(
             FT_EDI06983.uid
            ,func.date_format(FT_EDI06983.APV_D, '%Y-%m-%d').label('APV_D')
            ,FT_EDI06983.RY_CCD
            ,FT_EDI06983.MCT_NM
            ,FT_EDI06983.SEA
            ,literal_column("'신한카드'").label('card_name')
        )
        .join (
            industry_stmt, 
            FT_EDI06983.RY_CCD == industry_stmt.c.code
        )
        .filter(*filters)
        .order_by(FT_EDI06983.uid.desc())
        .offset((cardUsedListInput.page-1)*cardUsedListInput.page_view_size)
        .limit(cardUsedListInput.page_view_size)
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    # [ S ] 페이징 처리
    cardUsedListInput.page_total = (db.query(FT_EDI06983).join(industry_stmt, FT_EDI06983.RY_CCD == industry_stmt.c.code).filter(*filters).count())
    cardUsedListInput.page_last = math.ceil(cardUsedListInput.page_total / cardUsedListInput.page_view_size)
    cardUsedListInput.page_size = len(rows) # 현재 페이지에 검색된 수
    # [ E ] 페이징 처리

    jsondata = {}
    jsondata.update({"params" : cardUsedListInput})
    jsondata.update({"list": rows})

    return jsondata


