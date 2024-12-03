import math, json
from fastapi import APIRouter, Depends, Request, Body
from inspect import currentframe as frame
from app.core.config import PROXY_PREFIX, api_same_origin
from app.core.files import files
from app.core import util
from app.core.lib.KoreaHolidays import KoreaHolidays

from app.schemas.offcard.send import *
from app.service.offcard import send_service, holiday_service

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/offcard"],
)

# /be/offcard/send/create
@router.post("/offcard/send/create", dependencies=[Depends(api_same_origin)])
async def 보낼파일생성 (
    request:Request
    ,offcardSendFiles:OffcardSendFiles = Body(
        ...,
        examples = {
            "SLS00390" : {
                "summary": "고객정보 전송",
                "description": "신한카드한테 보낼 고객정보 데이터",
                "value": {
                    "filename" : "SLS00390"
                }
            },
            "SLS00391" : {
                "summary": "복리적용대상",
                "description": "복리적용대상",
                "value": {
                    "filename" : "SLS00391"
                }
            },
            "SLS00392" : {
                "summary": "법인취소매출",
                "description": "법인취소매출",
                "value": {
                    "filename" : "SLS00392"
                }
            },
        }
    )
):
    request.state.inspect = frame()

    filename = offcardSendFiles.filename
    filedate = util.getNow('%Y-%m-%d')
    f = files(filename, filedate)

    f.log_write("send", f"START {filename} {filedate}")

    # ### 공휴일 넣는 구문 (2025년도에 다시 시도) ####
    # koreaHolidays = KoreaHolidays(request)
    # koreaHolidays.save_holiday(request, "2026")
    # ### 공휴일 넣는 구문 (2025년도에 다시 시도) ####
    
    if filename == None or filename == "" :
        f.log_write("send", f"파일명 empty")
        return "파일명 empty"

    # 내일이 공휴일인지 판별
    if holiday_service.get_holidays(request, 'today') :
        if filename == "SLS00390" : # QY_EDD 조회종료일자 늘려주기
            send_service.set_SLS00390(request, True)
        f.log_write("send", f"오늘은 공휴일")
        return "오늘은 공휴일"
    
    fileobject = Fileobject()

    헤더크기, 본문크기, 테일크기 = get전문사이즈(filename)
    할당가능크기 = 4000-(헤더크기+테일크기)
    page_view = math.floor(할당가능크기/본문크기)

    블록 = 1
    시퀀스 = 1 # 현재페이지

    # 일단 한번 가져오고
    page_param = PPage_param(page = 시퀀스, page_view_size = page_view)
    res = getServiceData(request, filename, page_param)
    request.state.inspect = frame()

    if res == None :
        f.log_write("send", f"보낼 데이터 없음")
        return "보낼 데이터 없음"

    f.log_write("send", f"[ S ] 파일 쓰기 시작")
    fileinfo = {"res_size":len(res["list"]), "filename":filename, "블록" : 블록, "시퀀스" : 시퀀스, "헤더크기" : 헤더크기, "본문크기" : 본문크기, "테일크기" : 테일크기}
    res.update(fileinfo)
    f.log_write("send", f"[ fileinfo ] {json.dumps(fileinfo, indent=4, ensure_ascii=False)}")
    
    func = getattr(fileobject, filename)
    func(request, res)

    f.file_wirte(블록, fileobject.H헤더+fileobject.수신전문+fileobject.T풋터, 'w')

    # 추가 페이지가 있으면 이어서 가져오기
    for i in range(res["params"].page_last-1) :
        page_param.page = page_param.page + 1
        res = getServiceData(request, filename, page_param)
        request.state.inspect = frame()
        fileinfo = {"filename":filename, "블록" : 블록, "시퀀스" : 시퀀스, "헤더크기" : 헤더크기, "본문크기" : 본문크기, "테일크기" : 테일크기}
        f.log_write("send", f"[ fileinfo ] {json.dumps(fileinfo, indent=4, ensure_ascii=False)}")
        res.update(fileinfo)

        몫, 나머지 = divmod(page_param.page, 100)
        
        func = getattr(fileobject, filename)
        func(request, res)
        f.file_wirte(블록, fileobject.H헤더+fileobject.수신전문+fileobject.T풋터, 'a')

        if 몫 == 블록 and 나머지 == 0 : 
            블록 = 블록 + 1

    f.log_write("send", f"[ E ] 파일 쓰기 종료")
    return offcardSendFiles.filename

class Fileobject : 
    def SLS00390(self, request, res): # 신한카드한테 보낼 고객정보 데이터
        request.state.inspect = frame()
        self.수신전문 = ""
        H레코드구분 = "H".ljust(1)
        H파일구분코드 = res["filename"].ljust(8)
        H전송일자 = util.YYYYMMDD().ljust(8)
        H공백 = "".ljust(133)
        self.H헤더 = (H레코드구분+H파일구분코드+H전송일자+H공백).ljust(res["헤더크기"])
        for data in res["list"] : 
            D레코드구분 = "D".ljust(1)
            D아이핀연계번호 = data["IPN_LIK_N"].ljust(88)
            D조회시작일자 = data["QY_STD"].ljust(8)
            D조회종료일자 = data["QY_EDD"].ljust(8)
            D제휴카드구분 = data["AFL_CRD_C"].ljust(1)
            D기관전송여부 = data["IE_TI_F"].ljust(1)
            D선택복지업체코드 = data["SLT_WF_FIM_CD"].ljust(3)
            D공백 = "".ljust(40)
            self.D본문 = (D레코드구분+D아이핀연계번호+D조회시작일자+D조회종료일자+D제휴카드구분+D기관전송여부+D선택복지업체코드+D공백).ljust(res["본문크기"])
            self.수신전문 = self.수신전문 + self.D본문

        T레코드구분 = "T".ljust(1)
        T총건수 = str(len(res["list"])).zfill(13) 
        T공백 = "".ljust(136)
        self.T풋터 = (T레코드구분+T총건수+T공백).ljust(res["테일크기"])
    
    def SLS00391(self, request, res): # 복리적용대상
        request.state.inspect = frame()
        self.수신전문 = ""
        H레코드구분 = "H".ljust(1)
        H파일구분코드 = res["filename"].ljust(8)
        H전송일자 = util.YYYYMMDD().ljust(8)
        H공백 = "".ljust(183)
        self.H헤더 = (H레코드구분+H파일구분코드+H전송일자+H공백).ljust(res["헤더크기"])

        for data in res : 
            D레코드구분 = "D".ljust(1)
            D매출전표접수일자 = "20230726".ljust(8)
            D매출전표번호 = "0069EP8620315".ljust(13)
            D매출발생일자 = "20230725".ljust(8)
            D가맹점번호 = "0000000327".ljust(10)
            D매출금액 = "9000".zfill(13)
            D법인카드번호 = "1234567890".ljust(16)
            D법인청구금액 = "9000".zfill(13)
            D계열회사코드 = "766".ljust(3)
            D근속포인트사용금액 = "".zfill(13)
            D복지선택사용금액 = "9000".zfill(13)
            D공백 = "".ljust(89)
            self.D본문 = (D레코드구분+D매출전표접수일자+D매출전표번호+D매출발생일자+D가맹점번호+D매출금액+D법인카드번호+D법인청구금액+D계열회사코드+D근속포인트사용금액+D복지선택사용금액+D공백).ljust(res["본문크기"])
            self.수신전문 = self.수신전문 + self.D본문

        T레코드구분 = "T".ljust(1)
        T총건수 = str(len(res)).zfill(13)
        T총매출금액 = "9000".zfill(13)
        T총법인청구금액 = "9000".zfill(13)
        T공백 = "".ljust(160)
        self.T풋터 = (T레코드구분+T총건수+T총매출금액+T총법인청구금액+T공백).ljust(res["테일크기"])

    def SLS00392(self, request, res): # 법인취소매출
        request.state.inspect = frame()
        self.수신전문 = ""
        H레코드구분 = "H".ljust(1)
        H파일명 = res["filename"].ljust(8)
        H전송일자 = util.YYYYMMDD().ljust(8)
        H공백 = "".ljust(183)
        self.H헤더 = (H레코드구분+H파일명+H전송일자+H공백).ljust(res["헤더크기"])

        for data in res : 
            D레코드구분 = "D".ljust(1)
            D개인원매출전표접수일자 = "20230726".ljust(8)
            D개인원매출전표번호 = "0069EP8620315".ljust(13)
            D개인취소금액 = "-54451".ljust(13)
            D법인원매출전표접수일자 = "".ljust(8)
            D법인원매출전표번호 = "".ljust(13)
            D법인취소금액 = "-54451".ljust(13)
            D법인고객구별번호 = "".ljust(10)
            D가맹점번호 = "0109641084".ljust(10)
            D공백 = "".ljust(111)
            self.D본문 = (D레코드구분+D개인원매출전표접수일자+D개인원매출전표번호+D개인취소금액+D법인원매출전표접수일자+D법인원매출전표번호+D법인취소금액+D법인고객구별번호+D가맹점번호+D공백).ljust(res["본문크기"])
            self.수신전문 = self.수신전문 + self.D본문

        T레코드구분 = "T".ljust(1)
        T총건수 = str(len(res)).zfill(13)
        T총개인취소금액 = "9000".zfill(13)
        T총법인취소금액 = "9000".zfill(13)
        T공백 = "".ljust(160)
        self.T풋터 = (T레코드구분+T총건수+T총개인취소금액+T총법인취소금액+T공백).ljust(res["테일크기"])


    def EDI06982(self, request, res): # (임시) 고객정보반송 테스트 위한
        request.state.inspect = frame()
        self.수신전문 = ""
        H레코드구분 = "H".ljust(1)
        H파일구분코드 = res["filename"].ljust(8)
        H전송일자 = util.YYYYMMDD().ljust(8)
        H공백 = "".ljust(133)
        self.H헤더 = (H레코드구분+H파일구분코드+H전송일자+H공백).ljust(res["헤더크기"])
        for data in res["list"] : 
            D레코드구분 = "D".ljust(1)
            D아이핀연계번호 = data["IPN_LIK_N"].ljust(88)
            D조회시작일자 = data["QY_STD"].ljust(8)
            D조회종료일자 = data["QY_EDD"].ljust(8)
            D에러코드 = "0001".ljust(4)
            D선택복지업체코드 = data["SLT_WF_FIM_CD"].ljust(3)
            D공백 = "".ljust(38)
            self.D본문 = (D레코드구분+D아이핀연계번호+D조회시작일자+D조회종료일자+D에러코드+D선택복지업체코드+D공백).ljust(res["본문크기"])
            self.수신전문 = self.수신전문 + self.D본문

        T레코드구분 = "T".ljust(1)
        T반송총건수 = str(len(res["list"])).zfill(13) 
        T공백 = "".ljust(136)
        self.T풋터 = (T레코드구분+T반송총건수+T공백).ljust(res["테일크기"])

    def EDI06983(self, request, res): # (임시) 카드내역 테스트 위한
        request.state.inspect = frame()
        self.수신전문 = ""
        H레코드구분 = "H".ljust(1)  
        H전문일련번호 = "0000000".ljust(7)
        H카드사코드 = "B".ljust(1)
        H파일명 = "6983".ljust(4)
        H작성일자 = util.YYYYMMDD().ljust(8)
        H작성시간 = util.hhmmss().ljust(6)
        H공백 = "".ljust(373)

        self.H헤더 = (H레코드구분+H전문일련번호+H카드사코드+H파일명+H작성일자+H작성시간+H공백).ljust(res["헤더크기"])
        for data in res["list"] : 
            D레코드구분 = "D".ljust(1)
            D전문일련번호 = "0000001".ljust(7)
            D카드사코드 = "B".ljust(1)
            D아이핀연계번호 = data["IPN_LIK_N"].ljust(88)
            D카드번호 = "0000000000000000".ljust(16)
            D전표번호 = "0069EUP100001".ljust(50)
            D매입일자 = "20230801".ljust(8)
            D승인일자 = "20230801".ljust(8)
            D승인번호 = "34360725".ljust(8)
            D가맹점명 = "수이비인후과의원".ljust(50) # ABC123
            D업종구분코드 = "812".ljust(8)
            D사용금액 = "39500".zfill(12)
            D선택여부 = "N".ljust(1)
            D카드제휴코드 = "BAEAHM".ljust(10)
            D가맹점번호 = "0057270233".ljust(15)
            DSUB사업자등록번호 = "".ljust(10)
            DSUB사업자명 = "".ljust(40)
            D가맹점사업자번호 = "1059138755".ljust(10)
            D복지항목구분코드 = "2".ljust(1)
            D일반제휴카드구분 = "Y".ljust(1)
            D선택복지업체코드 = "503".ljust(3)
            D공백 = "".ljust(52)
            self.D본문 = (D레코드구분+D전문일련번호+D카드사코드+D아이핀연계번호+D카드번호+D전표번호+D매입일자+D승인일자+D승인번호+D가맹점명+D업종구분코드+D사용금액+D선택여부+D카드제휴코드+D가맹점번호+DSUB사업자등록번호+DSUB사업자명+D가맹점사업자번호+D복지항목구분코드+D일반제휴카드구분+D선택복지업체코드+D공백).ljust(res["본문크기"])
            self.수신전문 = self.수신전문 + self.D본문

        T레코드구분 = "T".ljust(1)
        T전문일련번호 = "9999999".ljust(7)
        T카드사코드 = "B".ljust(1)
        T총레코드건수 = str(len(res)).zfill(7)
        T총금액 = "1".zfill(15) 
        T공백 = "".ljust(369)
        self.T풋터 = (T레코드구분+T전문일련번호+T카드사코드+T총레코드건수+T총금액+T공백).ljust(res["테일크기"])




def getServiceData(request, filename, page_param) :
    if filename == "SLS00390" : 
        return send_service.get_SLS00390(request, page_param)
    
    elif filename == "SLS00391" : 
        return send_service.offcard_member_list(request, page_param)
    
    elif filename == "SLS00392" : 
        return send_service.offcard_member_list(request, page_param)
    
    elif filename == "EDI06982" : # (임시) 고객정보반송 테스트 위한
        return send_service.get_SLS00390(request, page_param)
    
    elif filename == "EDI06983" : # (임시) 카드내역 테스트 위한
        return send_service.get_SLS00390(request, page_param)
    
    else :
        return None

def get전문사이즈(filename) :
    # 헤더크기, 본문크기, 테일크기
    if filename == "SLS00390" or filename == "EDI06982" : 
        return 150, 150, 150 
    elif filename == "SLS00391" or filename == "SLS00392" : 
        return 200, 200, 200 
    elif filename == "EDI06983" :
        return 200, 200, 200 
    else :
        return 0, 0, 0