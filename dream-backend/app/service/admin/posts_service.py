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
from app.schemas.schema import *
from app.service.log_service import *
from app.schemas.admin.board import *
from app.models.board import *

# 관리자 게시판 상세
def board_read(request: Request, uid: int):
    request.state.inspect = frame()
    db = request.state.db

    sql = ( 
        db.query(
             T_BOARD.uid
            ,T_BOARD.site_id
            ,T_BOARD.board_type
            ,T_BOARD.board_name
            ,T_BOARD.permission_read
            ,T_BOARD.permission_write
            ,T_BOARD.is_comment
            ,T_BOARD.is_display
            ,T_BOARD.front_url
            ,func.date_format(T_BOARD.create_at, '%Y-%m-%d %T').label('create_at')
            ,func.date_format(T_BOARD.update_at, '%Y-%m-%d %T').label('update_at')
            ,func.date_format(T_BOARD.delete_at, '%Y-%m-%d %T').label('delete_at')
        )
        .filter(T_BOARD.uid == uid)
    )
    format_sql(sql)
    return sql.first()

# 관리자 게시물 리스트
def posts_list(request: Request, page_param: PPage_param, board: Any):
    request.state.inspect = frame()
    db = request.state.db

    where = ""
    where = where + "WHERE BP.delete_at is NULL "

    if not util.isEmptyObject(page_param.filters, "board_uid") and util.checkNumeric(page_param.filters["board_uid"]) > 0 :
        where = where + "AND BP.board_uid = " + str(page_param.filters["board_uid"]) + " "
    
    if not util.isEmptyObject(page_param.filters, "cate_uid") and util.checkNumeric(page_param.filters["cate_uid"]) > 0 :
        where = where + "AND BP.cate_uid = " + str(page_param.filters["cate_uid"]) + " "

    # [ S ] search filter start
    if not util.isEmptyObject(page_param.filters, "skeyword") :
        if not util.isEmptyObject(page_param.filters, "skeyword_type") :
            where = where + "AND "+page_param.filters["skeyword_type"]+" like '%"+page_param.filters["skeyword"]+"%'"
        else : 
            where = where + "AND ("
            where = where + "   BP.title like '%"+page_param.filters["skeyword"]+"%'"
            where = where + "   or BP.contents like '%"+page_param.filters["skeyword"]+"%'"
            where = where + ") "
    
    # [ E ] search filter end

    partner_column = ""
    partner_join = ""
    partner_where = ""
    if board is not None and board.site_id == "manager" :
        partner_column = ",P.company_name"
        partner_join = "JOIN T_PARTNER as P on P.uid = BP.partner_uid"
        if not util.isEmptyObject(page_param.filters, "partner_uid") and util.checkNumeric(page_param.filters["partner_uid"]) > 0 :
            print('page_param.filters["partner_uid"]',str(page_param.filters["partner_uid"]))
            partner_where = partner_where + "AND P.uid = "+str(page_param.filters["partner_uid"])

    sql = """
        SELECT 
             BP.uid
            ,BP.board_uid
            ,BP.cate_uid
            ,BP.partner_uid
            ,BP.thumb
            ,BP.title
            ,BP.state
            ,BP.create_user
            ,BP.create_name
            ,DATE_FORMAT(BP.create_at, '%Y-%m-%d<br>%T') as create_at
            ,(select count(uid) from T_BOARD_FILES as F where F.posts_uid = BP.uid and F.delete_at is null) as file_count
            ,(select count(uid) from T_BOARD_POSTS_REPLY as R where R.posts_uid = BP.uid and R.delete_at is null) as reply_count
            ,B.board_type
            ,B.board_name
            ,BP.is_display {partner_column}
        FROM T_BOARD_POSTS as BP
        JOIN T_BOARD as B on B.uid = BP.board_uid {partner_join}
        {where} {partner_where}
        ORDER BY uid DESC
        LIMIT {start}, {end}
    """.format( 
            partner_column=partner_column
            ,partner_join=partner_join
            ,where=where
            ,partner_where=partner_where
            ,start=(page_param.page-1)*page_param.page_view_size
            ,end=page_param.page_view_size
        )

    res = db.execute(text(sql)).fetchall()

    rows = []
    for c in res :
        row = dict(zip(c.keys(), c))
        rows.append(row)

    # [ S ] 페이징 처리
    page_param.page_total = db.execute(text("select count(BP.uid) as cnt from T_BOARD_POSTS as BP JOIN T_BOARD as B on B.uid = BP.board_uid " + where)).scalar()
    page_param.page_last = math.ceil(page_param.page_total / page_param.page_view_size)
    page_param.page_size = len(rows) # 현재 페이지에 검색된 수
    # [ E ] 페이징 처리

    jsondata = {}
    jsondata.update({"params" : page_param})
    jsondata.update({"list": rows})

    return jsondata

# 게시물_상세
def posts_read(request: Request, uid: int):
    request.state.inspect = frame()
    db = request.state.db
    sql = ( 
        db.query(
             T_BOARD_POSTS.uid
            ,T_BOARD_POSTS.board_uid
            ,T_BOARD_POSTS.cate_uid
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
        )
    )
    format_sql(sql)
    return sql.first()

# 게시물_편집 - create  
def posts_create(request: Request, posts: Posts):
    request.state.inspect = frame()
    db = request.state.db 
    user = request.state.user

    db_item = T_BOARD_POSTS (
         board_uid = posts.board_uid
        ,site_id = ''
        ,cate_uid = posts.cate_uid
        ,thumb = posts.thumb
        ,youtube = posts.youtube
        ,title = posts.title
        ,contents = posts.contents
        ,tags = posts.tags
        ,is_display = posts.is_display
        ,partner_uid = 115
        # ,partner_uid = user.partner_id
        ,create_user = user.user_id
        ,create_name = user.user_name
    )
    db.add(db_item)
    db.flush()

    create_log(request, posts.uid, "T_BOARD_POSTS", "INSERT", "게시물 등록", 0, db_item.uid, user.user_id)
    request.state.inspect = frame()

    if posts.files[0].uid >= 0 :
        for idx, val in enumerate(posts.files) :
            
            files_db_item = T_BOARD_FILES (
                board_uid = posts.board_uid
                ,posts_uid = db_item.uid
                ,fake_name = val.fake_name
                ,file_url = val.file_url
                ,sort = idx+1
            )
            db.add(files_db_item)
            db.flush()


    return db_item

# 게시물_편집 - update  
def posts_update(request: Request, posts: Posts):
    request.state.inspect = frame()
    db = request.state.db 
    user = request.state.user

    res = db.query(T_BOARD_POSTS).filter(T_BOARD_POSTS.uid == posts.uid).first()

    if res is None :
        return ex.ReturnOK(404, "게시물이 존재하지 않습니다.", request)

    if posts.board_uid is not None and res.board_uid != posts.board_uid : 
        create_log(request, posts.uid, "T_BOARD_POSTS", "board_uid", "게시판 번호", res.board_uid, posts.board_uid, user.user_id)
        request.state.inspect = frame()
        res.board_uid = posts.board_uid

    if posts.cate_uid is not None and res.cate_uid != posts.cate_uid : 
        create_log(request, posts.uid, "T_BOARD_POSTS", "cate_uid", "카테고리 번호", res.cate_uid, posts.cate_uid, user.user_id)
        request.state.inspect = frame()
        res.cate_uid = posts.cate_uid

    if posts.thumb is not None and res.thumb != posts.thumb : 
        create_log(request, posts.uid, "T_BOARD_POSTS", "thumb", "썸네일", res.thumb, posts.thumb, user.user_id)
        request.state.inspect = frame()
        res.thumb = posts.thumb

    if posts.youtube is not None and res.youtube != posts.youtube : 
        create_log(request, posts.uid, "T_BOARD_POSTS", "youtube", "유튜브링크", res.youtube, posts.youtube, user.user_id)
        request.state.inspect = frame()
        res.youtube = posts.youtube

    if posts.title is not None and res.title != posts.title : 
        create_log(request, posts.uid, "T_BOARD_POSTS", "title", "게시물 제목", res.title, posts.title, user.user_id)
        request.state.inspect = frame()
        res.title = posts.title

    if posts.contents is not None and res.contents != posts.contents : 
        create_log(request, posts.uid, "T_BOARD_POSTS", "contents", "게시물 본문", res.contents, posts.contents, user.user_id)
        request.state.inspect = frame()
        res.contents = posts.contents

    if posts.tags is not None and res.tags != posts.tags : 
        create_log(request, posts.uid, "T_BOARD_POSTS", "tags", "게시물 태그", res.tags, posts.tags, user.user_id)
        request.state.inspect = frame()
        res.tags = posts.tags

    if posts.is_display is not None and res.is_display != posts.is_display : 
        create_log(request, posts.uid, "T_BOARD_POSTS", "is_display", "노출여부", res.is_display, posts.is_display, user.user_id)
        request.state.inspect = frame()
        res.is_display = posts.is_display

    if posts.create_at is not None and res.create_at != posts.create_at : 
        create_log(request, posts.uid, "T_BOARD_POSTS", "create_at", "등록일", res.create_at, posts.create_at, user.user_id)
        request.state.inspect = frame()
        res.create_at = posts.create_at

    # 첨부파일 수정
    before_uids = []
    res_files = db.query(T_BOARD_FILES).filter(T_BOARD_FILES.board_uid == posts.board_uid, T_BOARD_FILES.posts_uid == posts.uid).all()
    for files in res_files :
        before_uids.append(files.uid)
        for idx, val in enumerate(posts.files) :
            if val.uid == files.uid :
                files.sort = idx+1
                if val.file_url is not None and files.file_url != val.file_url : 
                    create_log(request, posts.uid, "T_BOARD_FILES", "file_url", "파일경로", files.file_url, val.file_url, user.user_id)
                    request.state.inspect = frame()
                    files.file_url = val.file_url

                if val.fake_name is not None and files.fake_name != val.fake_name : 
                    create_log(request, posts.uid, "T_BOARD_FILES", "fake_name", "파일이름", files.fake_name, val.fake_name, user.user_id)
                    request.state.inspect = frame()
                    files.fake_name = val.fake_name


    # 첨부파일 추가 또는 삭제
    after_uids = []
    for idx, val in enumerate(posts.files) :
        if val.uid == 0 :
            files_db_item = T_BOARD_FILES (
                 board_uid = posts.board_uid
                ,posts_uid = posts.uid
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

# 게시물_편집 - delete  
def posts_delete(request: Request, uid: int):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user
    
    db_item = db.query(T_BOARD_POSTS).filter(T_BOARD_POSTS.uid == uid).first()

    db_item.is_display = 'F'
    db_item.delete_at = util.getNow()

    create_log(request, uid, "T_BOARD_POSTS", "DELETE", "게시물 삭제", 0, db_item.uid, user.user_id)
    request.state.inspect = frame()

    return db_item

# 게시물 첨부파일 리스트
def posts_files_list(request: Request, uid: int):
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

    # jsondata = {}
    # jsondata.update(mainListInput)
    # jsondata.update({"list": rows})

    return rows

# 게시물의 등록자 상세
def posts_person_read(request: Request, posts_uid: int) :
    request.state.inspect = frame()
    db = request.state.db

    sql = ( 
        db.query(
             T_BOARD_POSTS_PERSON.name
            ,T_BOARD_POSTS_PERSON.email
            ,T_BOARD_POSTS_PERSON.mobile
            ,T_BOARD_POSTS_PERSON.create_user
        )
        .filter(
            T_BOARD_POSTS_PERSON.uid == posts_uid
        )
    )
    format_sql(sql)
    return sql.first()

# 게시물의 답변리스트
def posts_reply_list(request: Request, posts_uid: int) :
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
            T_BOARD_POSTS_REPLY.posts_uid == posts_uid
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
def read_prev_next_posts(request: Request, posts_uid: int, board_uid: int):
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

# 게시물의 댓글(답변) - 등록
def posts_reply_create(request: Request, postsReplyInput: PostsReplyInput):
    request.state.inspect = frame()
    db = request.state.db 
    user = request.state.user

    db_item = T_BOARD_POSTS_REPLY (
         board_uid = postsReplyInput.board_uid
        ,posts_uid = postsReplyInput.posts_uid
        ,reply = postsReplyInput.reply
        ,user_id = user.user_id
        ,user_name = user.user_name
    )
    db.add(db_item)
    db.flush()

    create_log(request, db_item.uid, "T_BOARD_POSTS_REPLY", "INSERT", "게시물 댓글 등록", 0, db_item.uid, user.user_id)
    request.state.inspect = frame()

    posts = db.query(T_BOARD_POSTS).filter(T_BOARD_POSTS.uid == postsReplyInput.posts_uid).first()

    if posts is None :
        return db_item

    if posts.state != "200" : # T_BOARD_POSTS의 state값 변경
        create_log(request, postsReplyInput.uid, "T_BOARD_POSTS", "state", "상태값 변경", posts.state, "200", user.user_id)
        request.state.inspect = frame()
        posts.state = "200"

    return db_item

# 게시물의 댓글(답변) - 삭제
def posts_reply_delete(request: Request, uid: int):
    request.state.inspect = frame()
    db = request.state.db
    user = request.state.user
    
    db_item = db.query(T_BOARD_POSTS_REPLY).filter(T_BOARD_POSTS_REPLY.uid == uid).first()

    db_item.delete_at = util.getNow()

    create_log(request, uid, "T_BOARD_POSTS_REPLY", "DELETE", "게시물 댓글 삭제", 0, db_item.uid, user.user_id)
    request.state.inspect = frame()

    return db_item

# 게시물 첨부파일 상세
def posts_files_read(request: Request, uid: int):
    request.state.inspect = frame()
    db = request.state.db
    sql = ( 
        db.query(
             T_BOARD_FILES
        )
        .filter(
            T_BOARD_FILES.uid == uid
        )
    )
    format_sql(sql)

    return sql.first()

# 게시물 첨부파일 다운로드 로그
def insert_posts_files_log(request: Request, posts_files: T_BOARD_FILES):
    request.state.inspect = frame()
    user = request.state.user
    db = request.state.db

    db_item = T_BOARD_FILES_LOG (
         board_uid = posts_files.board_uid
        ,posts_uid = posts_files.posts_uid
        ,file_uid = posts_files.uid
        ,file_url = posts_files.file_url
        ,down_user = user.user_id
    )
    db.add(db_item)
    db.flush()
    return db_item



















