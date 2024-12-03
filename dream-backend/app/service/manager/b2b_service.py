from fastapi import Request
from inspect import currentframe as frame
from app.core.database import format_sql
import math

from app.schemas.schema import *
from app.models.scm.b2b.seller import *

def list_test(request: Request, pPage_param: PPage_param):
    request.state.inspect = frame()
    db_scm = request.state.db_scm

    filters = []
    filters.append(getattr(T_B2B_SELLER, "delete_at") == None)

    sql = (
        db_scm.query(
             T_B2B_SELLER.seller_id
            ,T_B2B_SELLER.seller_name
            ,T_B2B_SELLER.ceo_name
        )
        .filter(*filters)
        .order_by(T_B2B_SELLER.uid.desc())
        .offset((pPage_param.page-1)*pPage_param.page_view_size)
        .limit(pPage_param.page_view_size)
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        list = dict(zip(c.keys(), c))
        rows.append(list)

    # [ S ] 페이징 처리
    pPage_param.page_total = (
        db_scm.query(T_B2B_SELLER)
        .filter(*filters)
        .count()
    )
    pPage_param.page_last = math.ceil(
        pPage_param.page_total / pPage_param.page_view_size)
    pPage_param.page_size = len(rows)  # 현재 페이지에 검색된 수
    # [ E ] 페이징 처리

    jsondata = {}
    jsondata.update({"params" : pPage_param})
    jsondata.update({"list": rows})

    print(jsondata)

    return jsondata

def update_test(request: Request, pRead: PRead):
    request.state.inspect = frame()
    db_scm = request.state.db_scm
    
    res = (
        db_scm.query(T_B2B_SELLER)
        .filter(T_B2B_SELLER.uid == 1234)
    ).first()

    res.ceo_name = "123456"

    print(res.seller_id)