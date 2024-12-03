import json

async def exception_handler(error: Exception):
    if not isinstance(error, APIException):
        error = APIException(ex=error, detail=str(error))
    return error

class StatusCode:
    HTTP_200 = 200
    HTTP_500 = 500
    HTTP_400 = 400
    HTTP_401 = 401
    HTTP_403 = 403
    HTTP_404 = 404
    HTTP_405 = 405
    HTTP_505 = 505

class APIException(Exception):
    status_code: int
    code: str
    msg: str
    detail: str
    ex: Exception

    def __init__(
        self,
        *,
        status_code: int = StatusCode.HTTP_500,
        code: str = 500, # code: str = "000000",
        msg: str = "예기치 못한 오류가 발생하였습니다. 다시 시도해 주세요.",
        detail: str = None, 
        ex: Exception = None,
    ):
        self.status_code = status_code
        self.code = code
        self.msg = msg
        self.detail = detail
        self.ex = ex
        super().__init__(ex)

class APIExceptionCustom(APIException):
    def __init__(self, status_code: int = 500, msg: str = None, detail: str = None):
        super().__init__(
            status_code=status_code,
            msg = f"{msg}",
            detail = f"{detail}",
            code = f"{status_code}{'1'.zfill(4)}",
            ex=None,
        )

# (1) APIException를 상속받아서 NotFoundUserEx실행했을 때 부모클래스를 다 변경하고 아래 내용을 넣어줌
class NotFoundUser(APIException):
    def __init__(self, user_id: int = None, ex: Exception = None):
        super().__init__(
            status_code=StatusCode.HTTP_404,
            msg=f"해당 유저를 찾을 수 없습니다.",
            detail=f"Not Found User ID : {user_id}",
            code=f"{StatusCode.HTTP_400}{'1'.zfill(4)}",
            ex=ex,
        )

class NotAuthorized(APIException):
    def __init__(self, ex: Exception = None):
        super().__init__(
            status_code=StatusCode.HTTP_401,
            msg=f"로그인이 필요한 서비스 입니다.",
            detail="Authorization Required",
            code=f"{StatusCode.HTTP_401}{'1'.zfill(4)}",
            ex=ex,
        )

class NotFoundData(APIException):
    def __init__(self, ex: Exception = None):
        super().__init__(
            status_code=StatusCode.HTTP_401,
            msg=f"데이터를 찾을 수 없습니다.",
            detail="Data empty on database",
            code=f"{StatusCode.HTTP_401}{'1'.zfill(4)}",
            ex=ex,
        )

class TokenExpiredEx(APIException):
    def __init__(self, ex: Exception = None):
        super().__init__(
            status_code=StatusCode.HTTP_400,
            msg=f"세션이 만료되어 로그아웃 되었습니다.",
            detail="Token Expired",
            code=f"{StatusCode.HTTP_400}{'1'.zfill(4)}",
            ex=ex,
        )

class TokenDecodeEx(APIException):
    def __init__(self, ex: Exception = None):
        super().__init__(
            status_code=StatusCode.HTTP_400,
            msg=f"비정상적인 접근입니다.",
            detail="Token has been compromised.",
            code=f"{StatusCode.HTTP_400}{'2'.zfill(4)}",
            ex=ex,
        )

class InvalidTokenError(APIException):
    def __init__(self, ex: Exception = None):
        super().__init__(
            status_code=StatusCode.HTTP_505,
            msg=f"비정상적인 접근입니다.",
            detail="access_token jwt.InvalidTokenError.",
            code=f"{StatusCode.HTTP_505}{'2'.zfill(4)}",
            ex=ex,
        )

class InvalidApiKeyError(APIException):
    def __init__(self, ex: Exception = None):
        super().__init__(
            status_code=StatusCode.HTTP_505,
            msg=f"Authorization fail",
            detail="Authorization fail",
            code=f"{StatusCode.HTTP_505}{'1'.zfill(4)}",
            ex=ex,
        )

from fastapi import Request
def ReturnOK(code, message, request: Request, addobject={}, is_print=True):
    return_json = {
        "status": StatusCode.HTTP_200,
        "code": code,
        "msg": message,
    }

    return_json.update(addobject) 

    if is_print :
        print("─────────────────RETURN OK─────────────────┓")
        print(json.dumps(return_json, ensure_ascii=False, indent=2))
        print("───────────────────────────────────────────┘")

    if return_json["code"] != 200 :
        request.state.db.rollback()
        request.state.db.close()
        
        # SCM DB conn 있으면 롤백
        if hasattr(request.state, 'db_scm'):
            request.state.db_scm.rollback()
            request.state.db_scm.close()

    return return_json