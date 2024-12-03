from sqlalchemy import Column, String, Integer, ForeignKey, text, DateTime, Boolean, JSON

from app.core.database import Base


# 카드사용내역
class T_CARD_USED(Base):
    __tablename__ = "T_CARD_USED"
    uid = Column(Integer, primary_key=True, index=True)
    user_uid = Column(Integer, comment="T_MEMBER.uid")
    user_id = Column(String, comment="회원 아이디")
    RED_C_H         = Column(String, comment="레코드구분 H")
    TG_SEQNUM       = Column(Integer, comment="전문일련번호")
    CDO_CD          = Column(String, comment="카드사코드")
    FIL_NM          = Column(String, comment="파일명")
    WRT_D           = Column(String, comment="작성일자")
    WRT_TM          = Column(String, comment="작성시간")
    RED_C_D         = Column(String, comment="레코드구분 D")
    IPN_LIK_N       = Column(String, comment="아이핀연계번호")
    CRD_N           = Column(String, comment="카드번호")
    SI_N            = Column(String, comment="전표번호")
    AQ_D            = Column(String, comment="매입일자")
    APV_D           = Column(String, comment="승인일자")
    APV_N           = Column(String, comment="승인번호")
    MCT_NM          = Column(String, comment="가맹점명")
    RY_CCD          = Column(String, comment="업종구분코드")
    SEA             = Column(Integer, comment="사용금액")
    SLT_F           = Column(String, comment="선택여부")
    CRD_AFL_CD      = Column(String, comment="카드제휴코드")
    MCT_N           = Column(String, comment="가맹점번호")
    SBE_K_RGN       = Column(String, comment="SUB사업자등록번호")
    SBE_K_NM        = Column(String, comment="SUB사업자명")
    MCT_ETK_N       = Column(String, comment="가맹점사업자번호")
    WF_ITM_CCD      = Column(String, comment="복지항목구분코드")
    GNR_AFL_CRD_C   = Column(String, comment="일반제휴카드구분")
    SLT_WF_FIM_CD   = Column(String, comment="선택복지업체코드")
    RED_C_T         = Column(String, comment="레코드구분 T")
    TO_RED_CT       = Column(String, comment="총레코드건수")
    TO_AT           = Column(Integer, comment="총금액")
    state           = Column(String, comment="상태(차감신청완료)")
    create_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="등록일")
    delete_at = Column(DateTime, comment="삭제일") 
    update_at = Column(DateTime, comment="수정일")


# 포인트차감신청
class T_POINT_DEDUCT(Base):
    __tablename__ = "T_POINT_DEDUCT"
    uid = Column(Integer, primary_key=True, index=True)
    card_used_uid = Column(Integer, comment="T_CARD_USED.uid")
    use_type = Column(String, comment="사용종류(bokji, sikwon)") 
    partner_uid = Column(Integer, comment="T_PARTNER.uid")
    partner_id = Column(String, comment="고객사 아이디")
    user_uid = Column(Integer, comment="T_MEMBER.uid")
    user_id = Column(String, comment="회원 아이디")
    create_at = Column(DateTime, comment="차감신청일", server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    confirm_at = Column(DateTime, comment="차감승인일")
    detail = Column(String, comment="사용내역")
    request_point = Column(Integer, comment="포인트차감신청금액")
    confirm_point = Column(Integer, comment="포인트차감승인금액")
    card = Column(String, comment="카드")
    state = Column(String, comment="처리상태 (차감완료, 차감취소)")
    note = Column(String, comment="비고")
    delete_at = Column(DateTime, comment="삭제일") 
    update_at = Column(DateTime, comment="수정일")