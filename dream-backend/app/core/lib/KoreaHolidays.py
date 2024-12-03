from datetime import datetime
import requests
import json
import pandas as pd
from pandas import json_normalize
from inspect import currentframe as frame
from app.service.offcard import holiday_service

# b%2Fq6%2Fuo%2FO2O8gkZ63FsqbrjBntPwyg0W1g6hfhakwuq3q1xtopAckpBBeQSTT8FtBJnF%2BNuf%2BugUQecnAhYQPQ%3D%3D
# b/q6/uo/O2O8gkZ63FsqbrjBntPwyg0W1g6hfhakwuq3q1xtopAckpBBeQSTT8FtBJnF+Nuf+ugUQecnAhYQPQ==
# 2024-03-28 ~ 2026-03-28
# https://www.data.go.kr/iim/api/selectAPIAcountView.do
# https://uipath.tistory.com/200

class KoreaHolidays:
    def __init__(self, request):
        request.state.inspect = frame()
        pass

    def get_holidays(self, request):
        request.state.inspect = frame()
        today = datetime.today().strftime("%Y%m%d")
        today_year = datetime.today().year

        KEY = "b%2Fq6%2Fuo%2FO2O8gkZ63FsqbrjBntPwyg0W1g6hfhakwuq3q1xtopAckpBBeQSTT8FtBJnF%2BNuf%2BugUQecnAhYQPQ%3D%3D"
        url = (
            "http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo?_type=json&numOfRows=50&solYear="
            + str(today_year)
            + "&ServiceKey="
            + str(KEY)
        )
        response = requests.get(url)
        if response.status_code == 200:
            print(response.text)
            json_ob = json.loads(response.text)
            holidays_data = json_ob["response"]["body"]["items"]["item"]
            dataframe = json_normalize(holidays_data)
        # dateName = dataframe.loc[dataframe["locdate"] == int(today), "dateName"]
        # print(dateName)
        return dataframe["locdate"].to_list()
    
    def save_holiday(self, request, year):
        request.state.inspect = frame()

        if year == None or year == "" :
            return
        
        KEY = "b%2Fq6%2Fuo%2FO2O8gkZ63FsqbrjBntPwyg0W1g6hfhakwuq3q1xtopAckpBBeQSTT8FtBJnF%2BNuf%2BugUQecnAhYQPQ%3D%3D"
        url = (
            "http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo?_type=json&numOfRows=50&solYear="
            + str(year)
            + "&ServiceKey=" + str(KEY)
        )
        response = requests.get(url)
        if response.status_code == 200:
            print(response.text)
            json_ob = json.loads(response.text)
            holiday_service.add_holidays(request, json_ob)


    def today_is_holiday(self, request):
        request.state.inspect = frame()
        _today = datetime.now().strftime("%Y%m%d")
        holidays = self.get_holidays(request)
        holidays.append(20240328) # 강제 휴일 박기
        print(holidays)
        is_holiday = False
        if int(_today) in holidays:
            is_holiday = True
        print(is_holiday)
        return is_holiday