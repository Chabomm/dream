from fastapi import Response, Request

PROXY_PREFIX = "/be"

AT_USER_ID = "indendkorea"
def getATprofileKey(profile) :
    if profile == "indend" :
        return "0000000000000000000000000000000000000000" # ' @indendkorea / cfgPflag : 0
    elif profile == "eum" :
        return "0000000000000000000000000000000000000000" # ' @인천e몰 / cfgPflag : 1
    elif profile == "goolbi" :
        return "0000000000000000000000000000000000000000" # ' @굴비몰 / cfgPflag : 2
    elif profile == "welfaredream" :
        return "0000000000000000000000000000000000000000" # ' @복지드림 / cfgPflag : 3
    else :
        return ""
    
EMAIL_FROM = "noreply@indend.co.kr"
EMAIL_SERVER = 'smtp.office365.com'
EMAIL_PORT = 587
EMAIL_USER = "security@indend.co.kr"
EMAIL_PASS = ""

def api_same_origin(
    request:Request,
    response:Response):

    return True


