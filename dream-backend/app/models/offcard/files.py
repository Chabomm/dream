from sqlalchemy import Column, String, Integer, ForeignKey, text, DateTime, Boolean, JSON
from app.core.database import Base
  
class FT_SLS00390(Base): # 신한카드 복지대상 고객정보
    __tablename__ = "FT_SLS00390"
    uid             = Column(Integer, primary_key=True, index=True)
    is_send         = Column(String, comment="전송여부")
    is_ban          = Column(String, comment="반송건여부")
    IPN_LIK_N       = Column(String, comment="아이핀연계번호")
    QY_STD          = Column(String, comment="조회시작일자")
    QY_EDD          = Column(String, comment="조회종료일자")
    AFL_CRD_C       = Column(String, comment="제휴카드구분")
    IE_TI_F         = Column(String, comment="기관전송여부")
    SLT_WF_FIM_CD   = Column(String, comment="선택복지업체코드")
    create_at       = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")

class FT_EDI06982(Base): # 신한카드 복지대상 고객정보 오류건 반송
    __tablename__ = "FT_EDI06982"
    uid             = Column(Integer, primary_key=True, index=True)
    IPN_LIK_N       = Column(String, comment="아이핀연계번호")
    QY_STD          = Column(String, comment="조회시작일자")
    QY_EDD          = Column(String, comment="조회종료일자")
    ERO_CD          = Column(String, comment="에러코드")
    SLT_WF_FIM_CD   = Column(String, comment="선택복지업체코드")
    create_at       = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")

class FT_EDI06983(Base): # 신한카드 복지대상 매출 (카드사용내역)
    __tablename__ = "FT_EDI06983"
    uid = Column(Integer, primary_key=True, index=True)
    TG_SEQNUM       = Column(String, comment="전문일련번호")
    CDO_CD          = Column(String, comment="카드사코드")
    IPN_LIK_N       = Column(String, comment="아이핀연계번호")
    CRD_N           = Column(String, comment="카드번호")
    SI_N            = Column(String, comment="전표번호")
    AQ_D            = Column(String, comment="매입일자")
    APV_D           = Column(String, comment="승인일자")
    APV_N           = Column(String, comment="승인번호")
    MCT_NM          = Column(String, comment="가맹점명")
    RY_CCD          = Column(String, comment="업종구분코드")
    SEA             = Column(String, comment="사용금액")
    SLT_F           = Column(String, comment="선택여부")
    CRD_AFL_CD      = Column(String, comment="카드제휴코드")
    MCT_N           = Column(String, comment="가맹점번호")
    SBE_K_RGN       = Column(String, comment="SUB사업자등록번호")
    SBE_K_NM        = Column(String, comment="SUB사업자명")
    MCT_ETK_N       = Column(String, comment="가맹점사업자번호")
    WF_ITM_CCD      = Column(String, comment="복지항목구분코드")
    GNR_AFL_CRD_C   = Column(String, comment="일반제휴카드구분")
    SLT_WF_FIM_CD   = Column(String, comment="선택복지업체코드")
    create_at       = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
  
class FT_EDI06984(Base): # 신한카드 복지대상 매출 취소건 (카드취소내역)
    __tablename__ = "FT_EDI06984"
    uid = Column(Integer, primary_key=True, index=True)
    R_LSP_RID   = Column(String, comment="원매출전표접수일자")
    R_LSP_N     = Column(String, comment="원매출전표번호")
    CE_RID      = Column(String, comment="취소접수일자")
    SLS_OR_D    = Column(String, comment="매출발생일자")
    SAA         = Column(String, comment="매출금액")
    IPN_LIK_N   = Column(String, comment="아이핀연계번호")
    MCT_N       = Column(String, comment="가맹점번호")
    MCT_NM      = Column(String, comment="가맹점명")
    create_at   = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")


class FT_SLS00391(Base): # 신한카드 복지 신청대상 (포인트차감신청)
    __tablename__ = "FT_SLS00391"
    is_send     = Column(String, comment="전송여부")
    LSP_RID     = Column(String, comment="매출전표접수일자")
    LSP_N       = Column(String, comment="매출전표번호", primary_key=True, index=True)
    SLS_OR_D    = Column(String, comment="매출발생일자")
    MCT_N       = Column(String, comment="가맹점번호")
    SAA         = Column(String, comment="매출금액")
    CRP_CRD_N   = Column(String, comment="법인카드번호")
    CRP_BLA     = Column(String, comment="법인청구금액")
    CHN_CP_CD   = Column(String, comment="계열회사코드")
    LSV_PNT_SEA = Column(String, comment="근속포인트사용금액")
    WF_SLT_SEA  = Column(String, comment="복지선택사용금액")
    create_at   = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")

class FT_EDI06985(Base): # 신한카드 복지 신청대상 오류건 반송 (포인트차감신청 오류건)
    __tablename__ = "FT_EDI06985"
    uid = Column(Integer, primary_key=True, index=True)
    LSP_RID         = Column(String, comment="매출전표접수일자")
    LSP_N           = Column(String, comment="매출전표번호")
    SLS_OR_D        = Column(String, comment="매출발생일자")
    MCT_N           = Column(String, comment="가맹점번호")
    SAA             = Column(String, comment="매출금액")
    CRP_CRD_N       = Column(String, comment="법인카드번호")
    CRP_BLA         = Column(String, comment="법인청구금액")
    ERO_CD          = Column(String, comment="에러코드")
    FMY_CP_CD_N     = Column(String, comment="패밀리회사코드번호")
    LTM_LSV_PNT_SEA = Column(String, comment="장기근속포인트사용금액")
    WF_SLT_SEA      = Column(String, comment="복지선택사용금액")
    create_at   = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")


class FT_SLS00392(Base): # 신한카드 법인취소매출/개인재매출 (포인트차감취소)
    __tablename__ = "FT_SLS00392"
    is_send         = Column(String, comment="전송여부")
    PSN_R_LSP_RID   = Column(String, comment="개인원매출전표접수일자")
    PSN_R_LSP_N     = Column(String, comment="개인원매출전표번호", primary_key=True, index=True)
    PSN_CLA         = Column(String, comment="개인취소금액")
    CRP_R_LSP_RID   = Column(String, comment="법인원매출전표접수일자")
    CRP_R_LSP_N     = Column(String, comment="법인원매출전표번호")
    CRP_CLA         = Column(String, comment="법인취소금액")
    CRP_CLN_DFR_N   = Column(String, comment="법인고객구별번호")
    MCT_N           = Column(String, comment="가맹점번호")
    create_at       = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")


class FT_EDI06986(Base): # 신한카드 법인취소매출/개인재매출 오류건 반송 (포인트차감취소 오류건)
    __tablename__ = "FT_EDI06986"
    uid = Column(Integer, primary_key=True, index=True)
    PSN_R_LSP_RID   = Column(String, comment="개인원매출전표접수일자")
    PSN_R_LSP_N     = Column(String, comment="개인원매출전표번호")
    PSN_CLA         = Column(String, comment="개인취소금액")
    CRP_R_LSP_RID   = Column(String, comment="법인원매출전표접수일자")
    CRP_R_LSP_N     = Column(String, comment="법인원매출전표번호")
    CRP_CLA         = Column(String, comment="법인취소금액")
    CRP_CLNN        = Column(String, comment="법인고객번호")
    MCT_N           = Column(String, comment="가맹점번호")
    ERO_CD          = Column(String, comment="에러코드")
    create_at       = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
