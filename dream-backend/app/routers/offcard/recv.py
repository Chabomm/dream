import math, json, os
from fastapi import APIRouter, Depends, Request, Body
from inspect import currentframe as frame
from app.core.config import PROXY_PREFIX, api_same_origin
from app.core.files import files
from app.core import util
from app.core.lib.KoreaHolidays import KoreaHolidays

from app.schemas.offcard.recv import *
from app.service.offcard import recv_service, holiday_service

router = APIRouter (
    prefix = PROXY_PREFIX, 
    tags=["/offcard"],
)

# /be/offcard/recv/add
@router.post("/offcard/recv/add", dependencies=[Depends(api_same_origin)])
async def 받은파일디비에적재 (
    request:Request
    ,offcardRecvFiles:OffcardRecvFiles = Body(
        ...,
        examples = {
            "EDI06982" : {
                "summary": "고객정보반송데이터 수신",
                "description": "고객정보반송데이터 수신",
                "value": {
                    "filename" : "EDI06982"
                    ,"filedate" : ""
                }
            },
        }
    )
):
    request.state.inspect = frame()

    if offcardRecvFiles.filedate == None or offcardRecvFiles.filedate == "" :
        offcardRecvFiles.filedate = util.getNow('%Y-%m-%d')

    filename = offcardRecvFiles.filename
    filedate = offcardRecvFiles.filedate
    f = files(filename, filedate)

    f.log_write("recv", f"START {filename} {filedate}")

    # ### 공휴일 넣는 구문 (2025년도에 다시 시도) ####
    # koreaHolidays = KoreaHolidays(request)
    # koreaHolidays.save_holiday(request, "2026")
    # ### 공휴일 넣는 구문 (2025년도에 다시 시도) ####
    
    if filename == None or filename == "" :
        f.log_write("recv", f"파일명 empty")
        return "파일명 empty"
    
    # 내일이 공휴일인지 판별
    if holiday_service.get_holidays(request, 'today') :
        f.log_write("recv", f"오늘은 공휴일")
        return "오늘은 공휴일"
    
    # 오늘 처리할 파일이 있는지 판별
    if len(f.recv_list()) == 0 :
        f.log_write("recv", f"처리할 파일 없음")
        return "처리할 파일 없음"
    
    fileobject = Fileobject()
    
    f.log_write("recv", f"[ S ] 파일 읽기 시작")
    f.log_write("recv", f"{f.recv_list()}")
    for recv_filename in f.recv_list():
        name, ext = os.path.splitext(recv_filename)
        if ext == ".txt" :
            recv_file = open(f"{f.recv_path}{recv_filename}", 'r')
            for line in recv_file.readlines() :
                f.log_write("recv", f"{line}")
                line = line[:len(line)-1]
                func = getattr(fileobject, filename)
                func(request, line, f)
            recv_file.close()
    f.log_write("recv", f"[ E ] 파일 읽기 종료")
    
class Fileobject : 

    def __init__(self):
        pass

    def getRangeData(self, size) : 
        returnData = self.mData[0:size]
        self.mData = self.mData[size:len(self.mData)] 
        return returnData
    
    def EDI06982(self, request, line, f): # SLS00390에서 보낸 고객정보 오류반송
        request.state.inspect = frame()
        self.mData = line
        if self.mData[0] == "H" :
            H레코드구분 = self.getRangeData(1)
            H파일구분코드 = self.getRangeData(8)
            H전송일자 = self.getRangeData(8)
            H공백 = self.getRangeData(133)

        """
        에러코드
        - 0001 : 아이핀정보가 없을경우 
        - 0002 : 현재일자보다 요청시작일자가 클경우 오류코드 
        - 0003 : 현재일자보다 요청종료일자가 클경우 오류코드 
        - 0004 : 중복된데이터인경우 
        """
        
        datas = []
        while True :
            if self.mData[0] == "D" :
                datas.append({
                     "D레코드구분" : self.getRangeData(1).rstrip()
                    ,"D아이핀연계번호" : self.getRangeData(88).rstrip()
                    ,"D조회시작일자" : self.getRangeData(8).rstrip()
                    ,"D조회종료일자" : self.getRangeData(8).rstrip()
                    ,"D에러코드" : self.getRangeData(4).rstrip()
                    ,"D선택복지업체코드" : self.getRangeData(3).rstrip()
                    ,"D공백" : self.getRangeData(38).rstrip()
                })
            else :
                break

        f.log_write("recv", f"[ datas ] {json.dumps(datas, indent=4, ensure_ascii=False)}")
        if self.mData[0] == "T" :
            T레코드구분 = self.getRangeData(1)
            T반송총건수 = self.getRangeData(13)
            T공백 = self.getRangeData(136)

        recv_service.set_EDI06982(request, datas)

    def EDI06983(self, request, line, f): # 카드매출수신
        request.state.inspect = frame()
        self.mData = line
        if self.mData[0] == "H" :
            H레코드구분 = self.getRangeData(1)
            H전문일련번호 = self.getRangeData(7)
            H카드사코드 = self.getRangeData(1)
            H파일명 = self.getRangeData(4)
            H작성일자 = self.getRangeData(8)
            H작성시간 = self.getRangeData(6)
            H공백 = self.getRangeData(373)
        
        datas = []
        while True :
            if self.mData[0] == "D" :
                datas.append({
                     "D레코드구분" : self.getRangeData(1).rstrip()
                    ,"D전문일련번호" : self.getRangeData(7).rstrip()
                    ,"D카드사코드" : self.getRangeData(1).rstrip()
                    ,"D아이핀연계번호" : self.getRangeData(88).rstrip()
                    ,"D카드번호" : self.getRangeData(16).rstrip()
                    ,"D전표번호" : self.getRangeData(50).rstrip()
                    ,"D매입일자" : self.getRangeData(8).rstrip()
                    ,"D승인일자" : self.getRangeData(8).rstrip()
                    ,"D승인번호" : self.getRangeData(8).rstrip()
                    ,"D가맹점명" : self.getRangeData(50).rstrip()
                    ,"D업종구분코드" : self.getRangeData(8).rstrip()
                    ,"D사용금액" : self.getRangeData(12).rstrip()
                    ,"D선택여부" : self.getRangeData(1).rstrip()
                    ,"D카드제휴코드" : self.getRangeData(10).rstrip()
                    ,"D가맹점번호" : self.getRangeData(15).rstrip()
                    ,"DSUB사업자등록번호" : self.getRangeData(10).rstrip()
                    ,"DSUB사업자명" : self.getRangeData(40).rstrip()
                    ,"D가맹점사업자번호" : self.getRangeData(10).rstrip()
                    ,"D복지항목구분코드" : self.getRangeData(1).rstrip()
                    ,"D일반제휴카드구분" : self.getRangeData(1).rstrip()
                    ,"D선택복지업체코드" : self.getRangeData(3).rstrip()
                    ,"D공백" : self.getRangeData(52).rstrip()
                })
            else :
                break

        f.log_write("recv", f"[ datas ] {json.dumps(datas, indent=4, ensure_ascii=False)}")
        if self.mData[0] == "T" :
            T레코드구분 = self.getRangeData(1)
            T전문일련번호 = self.getRangeData(7)
            T카드사코드 = self.getRangeData(1)
            T총레코드건수 = self.getRangeData(7)
            T총금액 = self.getRangeData(15)
            T공백 = self.getRangeData(369)

        recv_service.set_EDI06983(request, datas)

    def EDI06984(self, request, line, f): # 카드취소수신
        request.state.inspect = frame()
        self.mData = line
        if self.mData[0] == "H" :
            H레코드구분 = self.getRangeData(1)
            H파일구분코드 = self.getRangeData(8)
            H전송일자 = self.getRangeData(8)
            H공백 = self.getRangeData(283)
        
        datas = []
        while True :
            if self.mData[0] == "D" :
                datas.append({
                     "D레코드구분" : self.getRangeData(1).rstrip()
                    ,"D원매출전표접수일자" : self.getRangeData(8).rstrip()
                    ,"D원매출전표번호" : self.getRangeData(13).rstrip()
                    ,"D취소접수일자" : self.getRangeData(8).rstrip()
                    ,"D매출발생일자" : self.getRangeData(8).rstrip()
                    ,"D매출금액" : self.getRangeData(13).rstrip()
                    ,"D아이핀연계번호" : self.getRangeData(88).rstrip()
                    ,"D가맹점번호" : self.getRangeData(10).rstrip()
                    ,"D가맹점명" : self.getRangeData(40).rstrip()
                    ,"D공백" : self.getRangeData(111).rstrip()
                })
            else :
                break
            
        f.log_write("recv", f"[ datas ] {json.dumps(datas, indent=4, ensure_ascii=False)}")
        if self.mData[0] == "T" :
            T레코드구분 = self.getRangeData(1)
            T총건수 = self.getRangeData(13)
            T총금액 = self.getRangeData(13)
            T공백 = self.getRangeData(273)

        recv_service.set_EDI06984(request, datas)

    def EDI06985(self, request, line, f): # SLS00391에서 보낸 복리적용 오류반송
        request.state.inspect = frame()
        self.mData = line
        if self.mData[0] == "H" :
            H레코드구분 = self.getRangeData(1)
            H파일구분코드 = self.getRangeData(8)
            H전송일자 = self.getRangeData(8)
            H공백 = self.getRangeData(283)
        
        datas = []
        while True :
            if self.mData[0] == "D" :
                datas.append({
                     "D레코드구분" : self.getRangeData(1).rstrip()
                    ,"D매출전표접수일자" : self.getRangeData(8).rstrip()
                    ,"D매출전표번호" : self.getRangeData(13).rstrip()
                    ,"D매출발생일자" : self.getRangeData(8).rstrip()
                    ,"D가맹점번호" : self.getRangeData(10).rstrip()
                    ,"D매출금액" : self.getRangeData(13).rstrip()
                    ,"D법인카드번호" : self.getRangeData(16).rstrip()
                    ,"D법인청구금액" : self.getRangeData(13).rstrip()
                    ,"D에러코드" : self.getRangeData(4).rstrip()
                    ,"D패밀리회사코드번호" : self.getRangeData(3).rstrip()
                    ,"D장기근속포인트사용금액" : self.getRangeData(13).rstrip()
                    ,"D복지선택사용금액" : self.getRangeData(13).rstrip()
                    ,"D공백" : self.getRangeData(85).rstrip()
                })
            else :
                break
            
        f.log_write("recv", f"[ datas ] {json.dumps(datas, indent=4, ensure_ascii=False)}")
        if self.mData[0] == "T" :
            T레코드구분 = self.getRangeData(1)
            T반송총건수 = self.getRangeData(13)
            T공백 = self.getRangeData(186)

        recv_service.set_EDI06985(request, datas)

    def EDI06986(self, request, line, f): # SLS00392에서 보낸 법인취소 오류반송
        request.state.inspect = frame()
        self.mData = line
        if self.mData[0] == "H" :
            H레코드구분 = self.getRangeData(1)
            H파일명 = self.getRangeData(8)
            H전송일자 = self.getRangeData(8)
            H공백 = self.getRangeData(183)
        
        datas = []
        while True :
            if self.mData[0] == "D" :
                datas.append({
                     "D레코드구분" : self.getRangeData(1).rstrip()
                    ,"D개인원매출전표접수일자" : self.getRangeData(8).rstrip()
                    ,"D개인원매출전표번호" : self.getRangeData(13).rstrip()
                    ,"D개인취소금액" : self.getRangeData(13).rstrip()
                    ,"D법인원매출전표접수일자" : self.getRangeData(8).rstrip()
                    ,"D법인원매출전표번호" : self.getRangeData(13).rstrip()
                    ,"D법인취소금액" : self.getRangeData(13).rstrip()
                    ,"D법인고객번호" : self.getRangeData(10).rstrip()
                    ,"D가맹점번호" : self.getRangeData(10).rstrip()
                    ,"D에러코드" : self.getRangeData(4).rstrip()
                    ,"D공백" : self.getRangeData(107).rstrip()
                })
            else :
                break
            
        f.log_write("recv", f"[ datas ] {json.dumps(datas, indent=4, ensure_ascii=False)}")
        if self.mData[0] == "T" :
            T레코드구분 = self.getRangeData(1)
            T반송총건수 = self.getRangeData(13)
            T공백 = self.getRangeData(186)

        recv_service.set_EDI06986(request, datas) 


    
            




