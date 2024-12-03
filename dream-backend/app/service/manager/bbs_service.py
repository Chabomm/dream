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
from app.deps import auth
from app.models.session import *
from app.models.board import *
from app.schemas.schema import *
from app.schemas.manager.board import *
from app.service.log_service import *

# 게시물 리스트 
def posts_list(request: Request, page_param: PPage_param, board_uid: int):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    filters = []
    filters.append(getattr(T_BOARD_POSTS, "delete_at") == None)
    filters.append(getattr(T_BOARD_POSTS, "partner_uid") == user.partner_uid)
    filters.append(getattr(T_BOARD_POSTS, "board_uid") == board_uid)

    # [ S ] search filter start
    if page_param.filters :
        if page_param.filters["skeyword"] :
            if page_param.filters["skeyword_type"] != "" :
                filters.append(getattr(T_BOARD_POSTS, page_param.filters["skeyword_type"]).like("%"+page_param.filters["skeyword"]+"%"))
            else : 
                filters.append(
                      T_BOARD_POSTS.title.like("%"+page_param.filters["skeyword"]+"%")
                    | T_BOARD_POSTS.contents.like("%"+page_param.filters["skeyword"]+"%")
                    | T_BOARD_POSTS.create_name.like("%"+page_param.filters["skeyword"]+"%")
                )

        if page_param.filters["create_at"]["startDate"] and page_param.filters["create_at"]["endDate"] :
            filters.append(
                and_(
                    T_BOARD_POSTS.create_at >= page_param.filters["create_at"]["startDate"]
                    ,T_BOARD_POSTS.create_at <= page_param.filters["create_at"]["endDate"] + " 23:59:59"
                )
            )
        # if page_param.filters["input_state"] :
        #     filters.append(T_BALANCE.input_state == page_param.filters["input_state"])
    # [ E ] search filter end

    sql = (
        db.query(
             T_BOARD_POSTS.uid
            ,T_BOARD_POSTS.board_uid
            ,T_BOARD_POSTS.site_id
            ,T_BOARD_POSTS.cate_uid
            ,T_BOARD_POSTS.partner_uid
            ,T_BOARD_POSTS.thumb
            ,T_BOARD_POSTS.youtube
            ,T_BOARD_POSTS.title
            ,T_BOARD_POSTS.contents
            ,T_BOARD_POSTS.tags
            ,T_BOARD_POSTS.is_display
            ,T_BOARD_POSTS.state
            ,T_BOARD_POSTS.user_ip
            ,T_BOARD_POSTS.create_user
            ,T_BOARD_POSTS.create_name
            ,func.date_format(T_BOARD_POSTS.create_at, '%Y-%m-%d %T').label('create_at')
            ,func.date_format(T_BOARD_POSTS.update_at, '%Y-%m-%d %T').label('update_at')
            ,func.date_format(T_BOARD_POSTS.delete_at, '%Y-%m-%d %T').label('delete_at')
        )
        .filter(*filters)
        .order_by(T_BOARD_POSTS.uid.desc())
        .offset((page_param.page-1)*page_param.page_view_size)
        .limit(page_param.page_view_size)
    )

    # format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    # [ S ] 페이징 처리
    page_param.page_total = (
        db.query(T_BOARD_POSTS)
        .filter(*filters)
        .count()
    )
    page_param.page_last = math.ceil(
        page_param.page_total / page_param.page_view_size)
    page_param.page_size = len(rows)  # 현재 페이지에 검색된 수
    # [ E ] 페이징 처리

    jsondata = {}
    jsondata.update({"params": page_param})
    jsondata.update({"list": rows})

    return jsondata
    
def board_list(request: Request, boardListInput: BoardListInput):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    filters = []
    filters.append(getattr(T_BOARD_POSTS, "delete_at") == None)
    filters.append(getattr(T_BOARD_POSTS, "partner_uid") == user.partner_uid)
    filters.append(getattr(T_BOARD_POSTS, "board_uid") == boardListInput.board_uid)

    if boardListInput.filters :
        if boardListInput.filters["skeyword"] :
            if boardListInput.filters["skeyword_type"] != "" :
                filters.append(getattr(T_BOARD_POSTS, boardListInput.filters["skeyword_type"]).like("%"+boardListInput.filters["skeyword"]   +"%"))
            else : 
                filters.append(
                    T_BOARD_POSTS.title.like("%"+boardListInput.filters["skeyword"]+"%") 
                    | T_BOARD_POSTS.contents.like("%"+boardListInput.filters["skeyword"]+"%") 
                    | T_BOARD_POSTS.create_user.like("%"+boardListInput.filters["skeyword"]+"%") 
                )
    
        if boardListInput.filters["create_at"]["startDate"] and boardListInput.filters["create_at"]["endDate"] :
            filters.append(
                and_(
                T_BOARD_POSTS.create_at >= boardListInput.filters["create_at"]["startDate"]
                ,T_BOARD_POSTS.create_at <= boardListInput.filters["create_at"]["endDate"] + " 23:59:59"
            )
        )
            
    file_count_stmt = (
        db.query(
            T_BOARD_FILES.posts_uid.label("posts_uid")
            ,func.count(T_BOARD_FILES.uid).label('file_count')
        )
        .filter(T_BOARD_FILES.delete_at == None)
        .group_by(T_BOARD_FILES.uid)
        .subquery()
    )
            
    reply_count_stmt = (
        db.query(
            T_BOARD_POSTS_REPLY.posts_uid.label("posts_uid")
            ,func.count(T_BOARD_POSTS_REPLY.uid).label('reply_count')
        )
        .filter(T_BOARD_POSTS_REPLY.delete_at == None)
        .group_by(T_BOARD_POSTS_REPLY.uid)
        .subquery()
    )

    sql = (
        db.query(
             T_BOARD_POSTS.uid
            ,T_BOARD_POSTS.board_uid
            ,T_BOARD_POSTS.site_id
            ,T_BOARD_POSTS.cate_uid
            ,T_BOARD_POSTS.partner_uid
            ,T_BOARD_POSTS.thumb
            ,T_BOARD_POSTS.youtube
            ,T_BOARD_POSTS.title
            ,T_BOARD_POSTS.contents
            ,T_BOARD_POSTS.tags
            ,T_BOARD_POSTS.is_display
            ,T_BOARD_POSTS.state
            ,T_BOARD_POSTS.user_ip
            ,T_BOARD_POSTS.create_user
            ,T_BOARD_POSTS.create_name
            ,func.date_format(T_BOARD_POSTS.create_at, '%Y-%m-%d %T').label('create_at')
            ,func.date_format(T_BOARD_POSTS.update_at, '%Y-%m-%d %T').label('update_at')
            ,func.date_format(T_BOARD_POSTS.delete_at, '%Y-%m-%d %T').label('delete_at')
            ,file_count_stmt.c.file_count
            ,reply_count_stmt.c.reply_count
        )
        .join(
            file_count_stmt, 
            T_BOARD_POSTS.uid == file_count_stmt.c.posts_uid,
            isouter = True 
        )
        .join(
            reply_count_stmt, 
            T_BOARD_POSTS.uid == reply_count_stmt.c.posts_uid,
            isouter = True 
        )
        .filter(*filters)
        .order_by(T_BOARD_POSTS.uid.desc())
        .offset((boardListInput.page-1)*boardListInput.page_view_size)
        .limit(boardListInput.page_view_size)
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    # [ S ] 페이징 처리
    boardListInput.page_total = (
        db.query(T_BOARD_POSTS)
        .filter(*filters)
        .count()
    )
    boardListInput.page_last = math.ceil(
        boardListInput.page_total / boardListInput.page_view_size)
    boardListInput.page_size = len(rows)  # 현재 페이지에 검색된 수
    # [ E ] 페이징 처리

    jsondata = {}
    jsondata.update(boardListInput)
    jsondata.update({"list": rows})

    return jsondata
    
# 게시물_상세
def read(request: Request, uid: int):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user

    sql = ( 
        db.query(
             T_BOARD_POSTS.uid
            ,T_BOARD_POSTS.board_uid
            ,T_BOARD_POSTS.cate_uid
            ,T_BOARD_POSTS.create_user
            ,T_BOARD_POSTS.partner_uid
            ,T_BOARD_POSTS.thumb
            ,T_BOARD_POSTS.youtube
            ,T_BOARD_POSTS.title
            ,T_BOARD_POSTS.contents
            ,T_BOARD_POSTS.tags
            ,T_BOARD_POSTS.is_display
            ,func.date_format(T_BOARD_POSTS.create_at, '%Y-%m-%d %T').label('create_at')
            ,func.date_format(T_BOARD_POSTS.update_at, '%Y-%m-%d %T').label('update_at')
            ,func.date_format(T_BOARD_POSTS.delete_at, '%Y-%m-%d %T').label('delete_at')
        )
        .filter(
            T_BOARD_POSTS.uid == uid
            ,T_BOARD_POSTS.delete_at == None
            ,T_BOARD_POSTS.partner_uid == user.partner_uid
        )
    )
    # format_sql(sql)
    return sql.first()

# 게시물 첨부파일 리스트
def files_list(request: Request, uid: int):
    request.state.inspect = frame()
    user = request.state.user
    db = request.state.db

    sql = (
        db.query(
             T_BOARD_FILES.uid
            ,T_BOARD_FILES.board_uid
            ,T_BOARD_FILES.posts_uid
            ,T_BOARD_FILES.fake_name
            ,T_BOARD_FILES.file_url
            ,T_BOARD_FILES.sort
        )
        .filter(
            T_BOARD_FILES.posts_uid == uid
        )
        .order_by(T_BOARD_FILES.sort.asc())
    )
    format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))
        
    return rows

# 게시물의 답변리스트
def reply_list(request: Request, uid: int) :
    request.state.inspect = frame()
    db = request.state.db

    sql = (
        db.query(
             T_BOARD_POSTS_REPLY.uid
            ,T_BOARD_POSTS_REPLY.reply
            ,T_BOARD_POSTS_REPLY.user_id
            ,T_BOARD_POSTS_REPLY.user_name
            ,func.date_format(T_BOARD_POSTS_REPLY.create_at, '%Y-%m-%d %T').label('create_at')
        )
        .filter(
            T_BOARD_POSTS_REPLY.delete_at == None,
            T_BOARD_POSTS_REPLY.posts_uid == uid
        )
        .order_by(T_BOARD_POSTS_REPLY.uid.desc())
    )

    format_sql(sql)

    rows = []
    for c in sql.all():
        rows.append(dict(zip(c.keys(), c)))

    jsondata = {}
    jsondata.update({"list": rows})

    return jsondata

# 게시물의 이전글, 다음글
def read_prev_next(request: Request, posts_uid: int, board_uid: int):
    request.state.inspect = frame()
    db = request.state.db
    
    sql = """
        SELECT 
            uid
            ,title 
            ,DATE_FORMAT(create_at, '%Y-%m-%d %T') as create_at
        FROM T_BOARD_POSTS 
        where uid = (
            SELECT MAX(uid)
            FROM T_BOARD_POSTS
            WHERE uid < {posts_uid}
            and board_uid = {board_uid}
        )
    """.format(board_uid=board_uid, posts_uid=posts_uid)
    prev_posts = db.execute(text(sql)).first()

    sql = """
        SELECT 
            uid
            ,title 
            ,DATE_FORMAT(create_at, '%Y-%m-%d %T') as create_at
        FROM T_BOARD_POSTS 
        where uid = (
            SELECT MIN(uid)
            FROM T_BOARD_POSTS
            WHERE uid > {posts_uid} 
            and board_uid = {board_uid}
        )
    """.format(board_uid=board_uid, posts_uid=posts_uid)
    next_posts = db.execute(text(sql)).first()

    if prev_posts is None:
        prev_posts = {"uid":0, "title": "이전 게시물이 없습니다.", "create_at": ""}
    else :
        prev_posts = dict(zip(prev_posts.keys(), prev_posts))

    if next_posts is None:
        next_posts = {"uid":0, "title": "다음 게시물이 없습니다.", "create_at": ""}
    else :
        next_posts = dict(zip(next_posts.keys(), next_posts))

    jsondata = {}
    jsondata.update({"prev_posts": prev_posts})
    jsondata.update({"next_posts": next_posts})
    return jsondata



# 게시물_편집 - create  
def create(request: Request, board: Board):
    request.state.inspect = frame()
    db = request.state.db 
    user = request.state.user

    db_item = T_BOARD_POSTS (
         board_uid = board.board_uid
        ,site_id = ''
        ,cate_uid = board.cate_uid
        ,thumb = board.thumb
        ,youtube = board.youtube
        ,title = board.title
        ,contents = board.contents
        ,tags = board.tags
        ,is_display = board.is_display
        ,partner_uid = user.partner_uid
        ,create_user = user.user_id
        ,create_name = user.user_name
    )
    db.add(db_item)
    db.flush()

    create_log(request, board.uid, "T_BOARD_POSTS", "INSERT", "게시물 등록", 0, db_item.uid, user.user_id)
    request.state.inspect = frame()



    if board.files[0].uid >= 0 :
        for idx, val in enumerate(board.files) :
            files_db_item = T_BOARD_FILES (
                board_uid = board.board_uid
                ,posts_uid = db_item.uid
                ,fake_name = val.fake_name
                ,file_url = val.file_url
                ,sort = idx+1
            )
            db.add(files_db_item)
            db.flush()
    db_item = ''
    return db_item

# # 게시물_편집 - update  
def update(request: Request, board: Board):
    request.state.inspect = frame()
    db = request.state.db 
    user = request.state.user

    res = db.query(T_BOARD_POSTS).filter(T_BOARD_POSTS.uid == board.uid).first()

    if res is None :
        return ex.ReturnOK(404, "게시물이 존재하지 않습니다.", request)

    if board.board_uid is not None and res.board_uid != board.board_uid : 
        create_log(request, board.uid, "T_BOARD_POSTS", "board_uid", "게시판 번호", res.board_uid, board.board_uid, user.user_id)
        request.state.inspect = frame()
        res.board_uid = board.board_uid

    if board.cate_uid is not None and res.cate_uid != board.cate_uid : 
        create_log(request, board.uid, "T_BOARD_POSTS", "cate_uid", "카테고리 번호", res.cate_uid, board.cate_uid, user.user_id)
        request.state.inspect = frame()
        res.cate_uid = board.cate_uid

    if board.thumb is not None and res.thumb != board.thumb : 
        create_log(request, board.uid, "T_BOARD_POSTS", "thumb", "썸네일", res.thumb, board.thumb, user.user_id)
        request.state.inspect = frame()
        res.thumb = board.thumb

    if board.youtube is not None and res.youtube != board.youtube : 
        create_log(request, board.uid, "T_BOARD_POSTS", "youtube", "유튜브링크", res.youtube, board.youtube, user.user_id)
        request.state.inspect = frame()
        res.youtube = board.youtube

    if board.title is not None and res.title != board.title : 
        create_log(request, board.uid, "T_BOARD_POSTS", "title", "게시물 제목", res.title, board.title, user.user_id)
        request.state.inspect = frame()
        res.title = board.title

    if board.contents is not None and res.contents != board.contents : 
        create_log(request, board.uid, "T_BOARD_POSTS", "contents", "게시물 본문", res.contents, board.contents, user.user_id)
        request.state.inspect = frame()
        res.contents = board.contents

    if board.tags is not None and res.tags != board.tags : 
        create_log(request, board.uid, "T_BOARD_POSTS", "tags", "게시물 태그", res.tags, board.tags, user.user_id)
        request.state.inspect = frame()
        res.tags = board.tags

    if board.is_display is not None and res.is_display != board.is_display : 
        create_log(request, board.uid, "T_BOARD_POSTS", "is_display", "노출여부", res.is_display, board.is_display, user.user_id)
        request.state.inspect = frame()
        res.is_display = board.is_display

    if board.create_at is not None and res.create_at != board.create_at : 
        create_log(request, board.uid, "T_BOARD_POSTS", "create_at", "등록일", res.create_at, board.create_at, user.user_id)
        request.state.inspect = frame()
        res.create_at = board.create_at

    # 첨부파일 수정
    before_uids = []
    res_files = db.query(T_BOARD_FILES).filter(T_BOARD_FILES.board_uid == board.board_uid, T_BOARD_FILES.posts_uid == board.uid).all()
    for files in res_files :
        before_uids.append(files.uid)
        for idx, val in enumerate(board.files) :
            if val.uid == files.uid :
                files.sort = idx+1
                if val.file_url is not None and files.file_url != val.file_url : 
                    create_log(request, board.uid, "T_BOARD_FILES", "file_url", "파일경로", files.file_url, val.file_url, user.user_id)
                    request.state.inspect = frame()
                    files.file_url = val.file_url

                if val.fake_name is not None and files.fake_name != val.fake_name : 
                    create_log(request, board.uid, "T_BOARD_FILES", "fake_name", "파일이름", files.fake_name, val.fake_name, user.user_id)
                    request.state.inspect = frame()
                    files.fake_name = val.fake_name


    # 첨부파일 추가 또는 삭제
    after_uids = []
    for idx, val in enumerate(board.files) :
        if val.uid == 0 :
            files_db_item = T_BOARD_FILES (
                 board_uid = board.board_uid
                ,posts_uid = board.uid
                ,fake_name = val.fake_name
                ,file_url = val.file_url
                ,sort = idx+1
            )
            db.add(files_db_item)
            db.flush()

        else :
            after_uids.append(val.uid)

    
    difference_uids = list(set(before_uids).difference(set(after_uids)))
    for idx, val in enumerate(difference_uids) :
        db.query(T_BOARD_FILES).filter(T_BOARD_FILES.uid == val).delete()
        create_log(request, val, "T_BOARD_FILES", "DELETE", "첨부파일 삭제", files.file_url, "", user.user_id)

    # for before, after in zip(before_uids, after_uids):
    #     print(before, after)
            
    res.update_at = util.getNow()
    return res

# # 게시물_편집 - delete  
def delete(request: Request, uid: int):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user
    
    db_item = db.query(T_BOARD_POSTS).filter(T_BOARD_POSTS.uid == uid).first()

    db_item.is_display = 'F'
    db_item.delete_at = util.getNow()

    create_log(request, uid, "T_BOARD_POSTS", "DELETE", "게시물 삭제", 0, db_item.uid, user.user_id)
    request.state.inspect = frame()

    return db_item