import json
import logging
from fastapi.logger import logger
from fastapi.requests import Request
from datetime import timedelta, datetime
from time import time

from app.core import util

logger.setLevel(logging.INFO)

async def api_logger(request: Request, response=None, error=None):
    time_format = "%Y-%m-%d %H:%M:%S"
    t = time() - request.state.start
    status_code = error.status_code if error else response.status_code
    error_log = None

    if error:
        if request.state.inspect:
            frame = request.state.inspect
            error_file = frame.f_code.co_filename
            error_func = frame.f_code.co_name
            error_line = frame.f_lineno
        else:
            error_func = error_file = error_line = "UNKNOWN"

        error_log = dict(
            errorFunc=error_func,
            location="{} line in {}".format(str(error_line), error_file),
            raised=str(error.__class__.__name__),
            msg=str(error.ex),
        )

    if request.state.user is None :
        user_log = None
    else :
        user_log = dict(request.state.user)

    log_dict = dict(
        time=util.getNow(),
        user_ip=request.state.user_ip,
        url=util.get_request_url_pure(request),
        request_body = request.state.body,
        method=str(request.method),
        status_code=status_code,
        error_detail=error_log,
        current_user=user_log,
        processed_time=str(round(t * 1000, 5)) + "ms",
        response=dict(status=error.status_code, msg=error.msg, detail=error.detail, code=error.code)
    )

    if error and error.status_code >= 500:
        print(json.dumps(log_dict, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(log_dict, ensure_ascii=False, indent=2))

    timestr = util.getNow("%Y-%m-%d")
    file_name = timestr + ".log"
    logm = json.dumps(log_dict, ensure_ascii=False, indent=4) + ","

    util.file_open (
        "/usr/src/app/data/dream-backend/middleware/"
        ,file_name
        ,logm
    )