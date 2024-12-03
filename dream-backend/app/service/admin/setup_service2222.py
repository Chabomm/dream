from fastapi import Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Optional
from inspect import currentframe as frame
from sqlalchemy.dialects import mysql as mysql_dialetct
from pymysql.converters import conversions, escape_item, encoders
from sqlalchemy import func, select, update, delete, Table, MetaData, and_
import math

from app.core import exceptions as ex
from app.core import util
from app.core.database import format_sql
from app.models.admin import *
from app.models.menu import *
from app.schemas.admin.admin import *
from app.service.log_service import *

def test(request: Request) :
    request.state.inspect = frame()
    db = request.state.db

    print (
        db.query(T_ADMIN)
        .filter(func.json_contains(T_ADMIN.roles, f'[13]'))
        .count()
    )

    # SELECT  
    #     * 
    # FROM T_ADMIN
    # WHERE json_contains(T_ADMIN.roles, '[13]')

# 최고 관리자 list 
def admin_user_list(request: Request, page_param: PPage_param):
    request.state.inspect = frame()
    db = request.state.db

    # filters = []
    # filters.append(getattr(T_ADMIN, "delete_at") == None)

    # sql = (
    #     db.query(
    #          T_ADMIN.uid
    #         ,T_ADMIN.user_id
    #         ,T_ADMIN.user_name
    #         ,T_ADMIN.tel
    #         ,T_ADMIN.mobile
    #         ,T_ADMIN.email
    #         ,T_ADMIN.depart
    #         ,T_ADMIN.state
    #         ,T_ADMIN.role
    #         ,T_ADMIN.roles
    #         ,func.date_format(T_ADMIN.create_at, '%Y-%m-%d %T').label('create_at')
    #         ,func.date_format(T_ADMIN.last_at, '%Y-%m-%d %T').label('last_at')
    #     )
    #     .filter(*filters)
    #     .order_by(T_ADMIN.uid.desc())
    #     .offset((page_param.page-1)*page_param.page_view_size)
    #     .limit(page_param.page_view_size)
    # )

    # format_sql(sql)

    # rows = []
    # for c in sql.all():
    #     rows.append(dict(zip(c.keys(), c)))

    # # [ S ] 페이징 처리
    # page_param.page_total = (
    #     db.query(T_ADMIN)
    #     .filter(*filters)
    #     .count()
    # )
    # page_param.page_last = math.ceil(
    #     page_param.page_total / page_param.page_view_size)
    # page_param.page_size = len(rows)  # 현재 페이지에 검색된 수
    # # [ E ] 페이징 처리

    # jsondata = {}
    # jsondata.update(page_param)
    # jsondata.update({"list": rows})
    
    sql = """
        SELECT 
             uid
            ,user_id
            ,user_name
            ,mobile
            ,email
            ,role
            ,depart
            ,DATE_FORMAT(create_at, '%Y-%m-%d %T') as create_at
            ,state
            ,roles
            ,( 
                select GROUP_CONCAT(name SEPARATOR ', ') AS result  
                From T_ADMIN_ROLE 
                where uid MEMBER OF(roles->>'$')
            ) as roles_txt
        FROM T_ADMIN
        WHERE delete_at is NULL
        ORDER BY uid DESC
        LIMIT {start}, {end}
    """.format(start=(page_param.page-1)*page_param.page_view_size, end=page_param.page_view_size)

    res = db.execute(text(sql)).fetchall()

    rows = []
    for c in res :
        rows.append(dict(zip(c.keys(), c)))

    page_param.page_total = db.execute(text("select count(uid) as cnt from T_MEMBER where delete_at is NULL")).scalar()

    page_param.page_last = math.ceil(
        page_param.page_total / page_param.page_view_size)
    page_param.page_size = len(rows) 

    jsondata = {}
    jsondata.update(page_param)
    jsondata.update({"list": rows})

    return jsondata

# 최고 관리자 역할 전체 리스트
def admin_rols_list(request: Request):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    # filters = []
    # filters.append(getattr(T_ADMIN_ROLE, "site_id") == "admin")

    # sql = (
    #     db.query(
    #          T_ADMIN_ROLE.uid
    #         ,T_ADMIN_ROLE.name
    #         ,T_ADMIN_ROLE.menus
    #     )
    #     .filter(*filters)
    # ) 

    # return sql.all()
    
    sql = """
        SELECT 
            uid
            ,name
            ,menus
            ,( 
                select GROUP_CONCAT(name SEPARATOR ', ') AS result  
                From T_ADMIN_MENU 
                where uid MEMBER OF(menus->>'$')
            ) as roles_txt 
        FROM T_ADMIN_ROLE
        ORDER BY uid DESC
    """.format()

    res = db.execute(text(sql)).fetchall()

    rows = []
    for c in res :
        rows.append(dict(zip(c.keys(), c)))

    jsondata = {}
    jsondata.update({"list": rows})

    return jsondata


# 최고 관리자 상세보기
def admin_user_read(request: Request, uid: int = 0, user_id: str = ""):
    request.state.inspect = frame()
    db = request.state.db

    filters = []
    filters.append(getattr(T_ADMIN, "delete_at") == None)

    if uid > 0:
        filters.append(getattr(T_ADMIN, "uid") == uid)
    elif user_id != "":
        filters.append(getattr(T_ADMIN, "user_id") == user_id)
    else:
        return None
    
    sql = (
        db.query(
             T_ADMIN.uid
            ,T_ADMIN.user_id
            ,T_ADMIN.user_name
            ,T_ADMIN.tel
            ,T_ADMIN.mobile
            ,T_ADMIN.email
            ,T_ADMIN.depart
            ,T_ADMIN.state
            ,T_ADMIN.role
            ,T_ADMIN.roles
            ,func.date_format(T_ADMIN.create_at, '%Y-%m-%d %T').label('create_at')
            ,func.date_format(T_ADMIN.last_at, '%Y-%m-%d %T').label('last_at')
        )
        .filter(*filters)
    )
    format_sql(sql)
    res = sql.first()
    if res is not None:
        res = dict(zip(res.keys(), res))
    return res

# 최고 관리자 편집 - 수정
def admin_user_edit(request: Request, adminInput: Admin):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    # 기존 등록된 관리자 select
    res = db.query(T_ADMIN).filter(T_ADMIN.uid == adminInput.uid).first()

    if res is None:
        raise ex.NotFoundUser

    if adminInput.state is not None and res.state != adminInput.state:
        create_log(request, adminInput.uid, "T_ADMIN", "state", "상태 수정", res.state, adminInput.state, user.user_id)
        request.state.inspect = frame()
        res.state = adminInput.state

    if adminInput.user_name is not None and res.user_name != adminInput.user_name:
        create_log(request, adminInput.uid, "T_ADMIN", "user_name", "이름 수정", res.user_name, adminInput.user_name, user.user_id)
        request.state.inspect = frame()
        res.user_name = adminInput.user_name

    if adminInput.tel is not None and res.tel != adminInput.tel:
        create_log(request, adminInput.uid, "T_ADMIN", "tel", "일반전화번호 수정", res.tel, adminInput.tel, user.user_id)
        request.state.inspect = frame()
        res.tel = adminInput.tel

    if adminInput.mobile is not None and res.mobile != adminInput.mobile:
        create_log(request, adminInput.uid, "T_ADMIN", "mobile", "휴대전화번호 수정", res.mobile, adminInput.mobile, user.user_id)
        request.state.inspect = frame()
        res.mobile = adminInput.mobile

    if adminInput.email is not None and res.email != adminInput.email:
        create_log(request, adminInput.uid, "T_ADMIN", "email", "이메일 수정", res.email, adminInput.email, user.user_id)
        request.state.inspect = frame()
        res.email = adminInput.email

    if adminInput.depart is not None and res.depart != adminInput.depart:
        create_log(request, adminInput.uid, "T_ADMIN", "depart", "부서 수정", res.depart, adminInput.depart, user.user_id)
        request.state.inspect = frame()
        res.depart = adminInput.depart

    if adminInput.role is not None and res.role != adminInput.role:
        create_log(request, adminInput.uid, "T_ADMIN", "role", "관리자 권한 수정", res.role, adminInput.role, user.user_id)
        request.state.inspect = frame()
        res.role = adminInput.role

    if adminInput.roles is not None and res.roles != adminInput.roles:
        create_log(request, adminInput.uid, "T_ADMIN", "roles", "역할 수정", res.roles, adminInput.roles, user.user_id)
        request.state.inspect = frame()
        res.roles = adminInput.roles

    res.update_at = util.getNow()
    return res

# 최고 관리자 편집 - 등록
def admin_user_create(request: Request, adminInput: Admin):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    user_data = admin_user_read(request, 0, adminInput.user_id)
    request.state.inspect = frame()

    if user_data is not None:
        return ex.ReturnOK(300, "이미 등록된 아이디 입니다.", request)

    db_item = T_ADMIN(
         user_id = adminInput.user_id
        ,user_name = adminInput.user_name
        ,tel = adminInput.tel
        ,mobile = adminInput.mobile
        ,email = adminInput.email
        ,role = adminInput.role
        ,depart = adminInput.depart
        ,roles = adminInput.roles
    )
    db.add(db_item)
    db.flush()
    
    create_log(request, db_item.uid, "T_ADMIN", "INSERT", "관리자 등록", 0, db_item.uid, user.user_id)
    request.state.inspect = frame()

    return db_item

# 관리자_역할관리_리스트_필터조건 - 소메뉴 리스트
def menu_list_for_filter(request:Request):
    request.state.inspect = frame()
    db = request.state.db
    
    jsondata = {}
    sql1 = (
        db.query(
             T_ADMIN_MENU.uid
            ,T_ADMIN_MENU.name
            ,T_ADMIN_MENU.depth
            ,T_ADMIN_MENU.parent
        )
        .filter(T_ADMIN_MENU.depth == 1, T_ADMIN_MENU.site_id == 'admin')
        .order_by(T_ADMIN_MENU.sort.asc())
    )
    depth1 = []
    for c in sql1.all() :
        depth1.append(dict(zip(c.keys(), c)))
    jsondata.update({"depth1": depth1})
    sql2 = (
        db.query(
             T_ADMIN_MENU.uid
            ,T_ADMIN_MENU.name
            ,T_ADMIN_MENU.depth
            ,T_ADMIN_MENU.parent
        )
        .filter(T_ADMIN_MENU.depth == 2, T_ADMIN_MENU.site_id == 'admin')
        .order_by(T_ADMIN_MENU.sort.asc())
    )
    depth2 = []
    for c in sql2.all() :
        depth2.append(dict(zip(c.keys(), c)))
    jsondata.update({"depth2": depth2})
    return jsondata
    # return jsondata

    # admin_menu_stmt = (
    #     db.query(
    #          T_ADMIN_MENU.uid
    #         ,T_ADMIN_MENU.sort.label('parent_sort')
    #         ,T_ADMIN_MENU.name.label('parent_name')
    #     )
    #     .filter(T_ADMIN_MENU.depth == 1, T_ADMIN_MENU.site_id == "admin")
    #     .subquery()
    # )

    # sql = (
    #     db.query(
    #          T_ADMIN_MENU.uid
    #         ,T_ADMIN_MENU.name
    #         ,T_ADMIN_MENU.depth
    #         ,T_ADMIN_MENU.parent
    #         ,T_ADMIN_MENU.sort
    #         ,admin_menu_stmt.c.parent_name
    #     )
    #     .join(
    #         admin_menu_stmt,
    #         T_ADMIN_MENU.parent == admin_menu_stmt.c.uid
    #     )
    #     .order_by(admin_menu_stmt.c.parent_sort.asc() , T_ADMIN_MENU.sort)
    # )

    # return sql.all()

# 고객사 관리자 역할관리 - 상세
def admin_roles_read(request: Request, uid: int):
    db = request.state.db
    user = request.state.user

    sql = (
        db.query(
             T_ADMIN_ROLE.uid
            ,T_ADMIN_ROLE.name
            ,T_ADMIN_ROLE.menus
        )
        .filter(T_ADMIN_ROLE.uid == uid)
    )

    format_sql(sql)
    res = sql.first()
    if res is not None:
        res = dict(zip(res.keys(), res))
    return res

# 고객사 관리자 역할관리_편집 - 등록
def admin_roles_create(request: Request, adminRolesInput: AdminRolesInput) :
    request.state.inspect = frame()
    db = request.state.db 
    user = request.state.user

    db_item = T_ADMIN_ROLE (
         name = adminRolesInput.name
        ,menus = adminRolesInput.menus
        ,partner_uid = 0
        ,site_id = "admin"
    )
    db.add(db_item)
    db.flush()

    create_log(request, db_item.uid, "T_ADMIN_ROLE", "INSERT", "관리자 역할관리 등록", 0, db_item.uid, user.user_id)
    request.state.inspect = frame()

    return db_item

# 고객사 관리자 역할관리_편집 - 수정
def admin_roles_update(request: Request, adminRolesInput: AdminRolesInput) :
    request.state.inspect = frame()
    db = request.state.db 
    user = request.state.user

    res = db.query(T_ADMIN_ROLE).filter(T_ADMIN_ROLE.uid == adminRolesInput.uid).first()

    if res is None :
        raise ex.NotFoundUser

    if adminRolesInput.name is not None and res.name != adminRolesInput.name : 
        create_log(request, adminRolesInput.uid, "T_ADMIN_ROLE", "name", "역할명 수정", res.name, adminRolesInput.name, user.user_id)
        request.state.inspect = frame()
        res.name = adminRolesInput.name

    if adminRolesInput.menus is not None and res.menus != adminRolesInput.menus : 
        create_log(request, adminRolesInput.uid, "T_ADMIN_ROLE", "menus", "배정된 메뉴 수정", res.menus, adminRolesInput.menus, user.user_id)
        request.state.inspect = frame()
        res.menus = adminRolesInput.menus

    return res

# 고객사 관리자 역할관리_편집 - 삭제  
def admin_roles_delete(request: Request, uid: int):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user
    
    db.query(T_ADMIN_ROLE).filter(T_ADMIN_ROLE.uid == uid).delete()
    
    create_log(request, uid, "T_ADMIN_ROLE", "DELETE", "관리자 역할관리 삭제", uid, '', user.user_id)
    request.state.inspect = frame()

    return


## ========== 관리자 메뉴설정 start ========
# 관리자 메뉴설정 리스트
def admin_menu_list(request: Request, parent: int):
    request.state.inspect = frame()
    db = request.state.db

    filters = []
    filters.append(getattr(T_ADMIN_MENU, "site_id") == 'admin')
    if parent > 0:
        filters.append(getattr(T_ADMIN_MENU, "depth") == 2)
        filters.append(getattr(T_ADMIN_MENU, "parent") == parent)
    else :
        filters.append(getattr(T_ADMIN_MENU, "depth") == 1)

    sql = (
        db.query(
             T_ADMIN_MENU.uid
            ,T_ADMIN_MENU.name
            ,T_ADMIN_MENU.icon
            ,T_ADMIN_MENU.to
            ,T_ADMIN_MENU.sort
            ,T_ADMIN_MENU.depth
            ,T_ADMIN_MENU.parent
        )
        .filter(*filters)
        .order_by(T_ADMIN_MENU.sort.asc())
    )

    return sql.all()

# 관리자_메뉴설정_편집 - 등록
def admin_menu_create(request: Request, adminMenuInput: AdminMenuInput) :
    request.state.inspect = frame()
    db = request.state.db 
    user = request.state.user

    db_item = T_ADMIN_MENU (
         name = adminMenuInput.name
        ,icon = adminMenuInput.icon
        ,to = adminMenuInput.to
        ,depth = adminMenuInput.depth
        ,parent = adminMenuInput.parent
        ,site_id = 'admin'
    )
    db.add(db_item)
    db.flush()

    create_log(request, db_item.uid, "T_ADMIN_MENU", "INSERT", "어드민 메뉴 등록", 0, db_item.uid, user.user_id)
    request.state.inspect = frame()

    return db_item

# 관리자_메뉴설정_편집 - 수정
def admin_menu_update(request: Request, adminMenuInput: AdminMenuInput) :
    request.state.inspect = frame()
    db = request.state.db 
    user = request.state.user

    res = db.query(T_ADMIN_MENU).filter(T_ADMIN_MENU.uid == adminMenuInput.uid, T_ADMIN_MENU.site_id == 'admin').first()

    if res is None :
        raise ex.NotFoundUser

    if adminMenuInput.name is not None and res.name != adminMenuInput.name : 
        create_log(request, adminMenuInput.uid, "T_ADMIN_MENU", "name", "메뉴명", res.name, adminMenuInput.name, user.user_id)
        request.state.inspect = frame()
        res.name = adminMenuInput.name

    if adminMenuInput.icon is not None and res.icon != adminMenuInput.icon : 
        create_log(request, adminMenuInput.uid, "T_ADMIN_MENU", "icon", "아이콘", res.icon, adminMenuInput.icon, user.user_id)
        request.state.inspect = frame()
        res.icon = adminMenuInput.icon

    if adminMenuInput.to is not None and res.to != adminMenuInput.to : 
        create_log(request, adminMenuInput.uid, "T_ADMIN_MENU", "to", "링크", res.to, adminMenuInput.to, user.user_id)
        request.state.inspect = frame()
        res.to = adminMenuInput.to

    return res

# 관리자_메뉴설정_편집 - 순서정렬
def admin_menu_sort(request: Request, adminMenuInput: AdminMenuInput) :
    request.state.inspect = frame()
    db = request.state.db

    filters = []
    filters.append(getattr(T_ADMIN_MENU, "site_id") == 'admin')
    if adminMenuInput.parent > 0:
        filters.append(getattr(T_ADMIN_MENU, "parent") == adminMenuInput.parent)
    else :
        filters.append(getattr(T_ADMIN_MENU, "depth") == 1)

    res = (
        db.query(
            T_ADMIN_MENU
        )
        .filter(*filters)
        .all()
    )
    
    for c in res :
        for i in adminMenuInput.sort_array :
            if c.uid == i :
                c.sort = adminMenuInput.sort_array.index(i)+1

    return

# 관리자_메뉴설정-상세
def admin_menu_read(request: Request, uid: int):
    request.state.inspect = frame()
    db = request.state.db
    
    sql = (
        db.query(
             T_ADMIN_MENU.uid
            ,T_ADMIN_MENU.name
            ,T_ADMIN_MENU.icon
            ,T_ADMIN_MENU.to
            ,T_ADMIN_MENU.sort
            ,T_ADMIN_MENU.parent
            ,T_ADMIN_MENU.depth
        )
        .filter(T_ADMIN_MENU.uid == uid)
    )
    format_sql(sql)
    return sql.first()


## ========== 내 정보 start ========
# 내 정보 보기
def info_read(request: Request):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    sql = (
        db.query(
             T_ADMIN.uid
            ,T_ADMIN.user_id
            ,T_ADMIN.user_name
            ,T_ADMIN.mobile
            ,T_ADMIN.email
            ,T_ADMIN.tel
            ,T_ADMIN.depart
            ,T_ADMIN.create_at
            ,T_ADMIN.state
        )
        .filter(T_ADMIN.user_id == user.user_id)
    )
    format_sql(sql)
    res = sql.first()
    if res is not None:
        res = dict(zip(res.keys(), res))
    return res

# 내 정보 보기 - 수정
def info_update(request: Request, myInfoInput: MyInfoInput) :
    request.state.inspect = frame()
    db = request.state.db 
    user = request.state.user

    res = db.query(T_ADMIN).filter(T_ADMIN.user_id == user.user_id).first()

    if res is None :
        return ex.ReturnOK(404, "정보를 찾을 수 없습니다.", request)

    if myInfoInput.tel is not None and res.tel != myInfoInput.tel : 
        create_log(request, res.uid, "T_ADMIN", "tel", "일반전화번호", res.tel, myInfoInput.tel, user.user_id)
        request.state.inspect = frame()
        res.tel = myInfoInput.tel

    if myInfoInput.mobile is not None and res.mobile != myInfoInput.mobile : 
        create_log(request, res.uid, "T_ADMIN", "mobile", "핸드폰번호", res.mobile, myInfoInput.mobile, user.user_id)
        request.state.inspect = frame()
        res.mobile = myInfoInput.mobile

    res.update_at = util.getNow()

    return res


## ========== 로그리스트 start ========

# 로그 list
def log_list(request: Request, table_name:str, logListInput: LogListInput):
    request.state.inspect = frame()
    db = request.state.db

    filters = []
    if table_name != '' :
        filters.append(T_CHANGE_LOG.table_name.in_(table_name))
        filters.append(T_CHANGE_LOG.table_uid == logListInput.table_uid)

    if logListInput.filters :
        if logListInput.filters["skeyword"] :
            if logListInput.filters["skeyword_type"] != "" :
                filters.append(getattr(T_CHANGE_LOG, logListInput.filters["skeyword_type"]).like("%"+logListInput.filters["skeyword"]+"%"))
            else : 
                filters.append(
                    T_CHANGE_LOG.table_uid.like("%"+logListInput.filters["skeyword"]+"%") 
                    | T_CHANGE_LOG.table_name.like("%"+logListInput.filters["skeyword"]+"%")
                    | T_CHANGE_LOG.column_key.like("%"+logListInput.filters["skeyword"]+"%")
                    | T_CHANGE_LOG.column_name.like("%"+logListInput.filters["skeyword"]+"%")
                    | T_CHANGE_LOG.cl_before.like("%"+logListInput.filters["skeyword"]+"%")
                    | T_CHANGE_LOG.cl_after.like("%"+logListInput.filters["skeyword"]+"%")
                    | T_CHANGE_LOG.create_user.like("%"+logListInput.filters["skeyword"]+"%")
                )

        if logListInput.filters["create_at"]["startDate"] and logListInput.filters["create_at"]["endDate"] :
            filters.append(
                and_(
                    T_CHANGE_LOG.create_at >= logListInput.filters["create_at"]["startDate"]
                    ,T_CHANGE_LOG.create_at <= logListInput.filters["create_at"]["endDate"] + " 23:59:59"
                )
            )
    
    sql = (
        db.query(
             T_CHANGE_LOG.uid
            ,T_CHANGE_LOG.table_uid
            ,T_CHANGE_LOG.table_name
            ,T_CHANGE_LOG.column_key
            ,T_CHANGE_LOG.column_name
            ,T_CHANGE_LOG.cl_before
            ,T_CHANGE_LOG.cl_after
            ,T_CHANGE_LOG.create_user
            ,func.date_format(T_CHANGE_LOG.create_at, '%Y-%m-%d %T').label('create_at')
            ,func.left(T_CHANGE_LOG.cl_before, 75).label('cl_before_left')
            ,func.left(T_CHANGE_LOG.cl_after, 75).label('cl_after_left')
        )
        .filter(*filters)
        .order_by(T_CHANGE_LOG.uid.desc())
        .offset((logListInput.page-1)*logListInput.page_view_size)
        .limit(logListInput.page_view_size)
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        list = dict(zip(c.keys(), c))
        if list["cl_before"] is not None and len(list["cl_before"]) > 75 : 
            list["cl_before"] = list["cl_before_left"]+"..."
        if list["cl_after"] is not None and len(list["cl_after"]) > 75 : 
            list["cl_after"] = list["cl_after_left"]+"..."
        rows.append(list)

    # [ S ] 페이징 처리
    logListInput.page_total = (
        db.query(T_CHANGE_LOG)
        .filter(*filters)
        .count()
    )
    logListInput.page_last = math.ceil(logListInput.page_total / logListInput.page_view_size)
    logListInput.page_size = len(rows) # 현재 페이지에 검색된 수
    # [ E ] 페이징 처리

    jsondata = {}
    jsondata.update(logListInput)
    jsondata.update({"list": rows})

    return jsondata











