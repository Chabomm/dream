import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect, useRef } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import { cls, checkNumeric, dateformatYYYYMMDD } from '@/libs/utils';
import useForm from '@/components/form/useForm';
import BoardReply from '@/components/bbs/BoardReply';

import dynamic from 'next/dynamic';
const CKEditor = dynamic(() => import('@/components/editor/CKEditor'), { ssr: false });

const BoardPostsEdit: NextPage = (props: any) => {
    const router = useRouter();
    const [loading, setLoading] = useState<boolean>(false);
    const [filter, setFilter] = useState<any>([]);
    const [person, setPerson] = useState<any>([]);
    const [reply, setReply] = useState<any>([]);
    const [board, setBoard] = useState<any>({});

    useEffect(() => {
        if (props) {
            if (props.response.code == 200) {
                s.setValues(props.response.values);
                setFilter(props.response.filter);
                setPerson(props.response.person);
                setReply(props.response.reply);
                setBoard(props.response.board);
            } else {
                alert(props.response.msg);
                window.close();
            }
        }
    }, []);

    const contentRef = useRef<any>();
    const { s, fn, attrs } = useForm({
        initialValues: {},
        onSubmit: async () => {
            await editing('REG');
        },
    });

    const deleting = () => editing('DEL');

    const editing = async mode => {
        try {
            const params = { ...s.values };

            if (mode == 'REG' && params.uid > 0) {
                mode = 'MOD';
            }
            params.mode = mode;

            if (typeof params.board_uid == 'undefined' || params.board_uid + '' == 'null') {
                params.board_uid = checkNumeric(router.query.board_uid);
            }

            if (mode == 'DEL' && !confirm('게시물 삭제시 휴지통으로 이동되며, 게시물은 노출되지 않습니다. 계속 하시겠습니까 ?')) {
                return;
            }
            const { data } = await api.post(`/be/admin/posts/edit`, params);
            s.setSubmitting(false);
            if (data.code == 200) {
                alert(data.msg);
                router.push('/board/posts/edit?uid=' + data.uid);
            } else {
                alert(data.msg);
            }
        } catch (e: any) {}
    };

    const fnStartUploading = () => {
        setLoading(true);
    };

    const fnEndUploading = () => {
        setLoading(false);
    };

    const deleteFiles = idx => {
        const copy = { ...s.values };
        let temp_files: any = [];
        for (var i = 0; i < copy.files.length; i++) {
            if (i != idx) {
                temp_files.push(copy.files[i]);
            }
        }
        copy.files = temp_files;
        s.setValues(copy);
    };

    const download_file = async file => {
        try {
            let request = { uid: file.uid };
            await api({
                url: `/be/admin/posts/file/download/${file.uid}`,
                method: 'POST',
                responseType: 'blob',
            }).then(response => {
                var fileURL = window.URL.createObjectURL(new Blob([response.data]));
                var fileLink = document.createElement('a');
                fileLink.href = fileURL;
                fileLink.setAttribute('download', file.fake_name);
                document.body.appendChild(fileLink);
                fileLink.click();
            });
        } catch (e: any) {}
    };

    // 댓글 남기기
    const addReply = async item => {
        try {
            const params = { ...s.values };

            if (item > 0) {
                params.mode = 'DEL';
            } else {
                params.mode = 'REG';
            }
            params.posts_uid = params.uid;
            params.uid = item;

            var confirmMsg = '답변을 삭제하시겠습니까?';
            if (params.mode == 'DEL') {
                if (!confirm(confirmMsg)) {
                    return;
                }
            }

            if (params.mode == 'REG') {
                if (typeof params.reply === 'undefined' || params.reply == '') {
                    alert('답변내용을 입력해 주세요');
                    return;
                }
            }
            const { data } = await api.post(`/be/admin/medical/doctor_schedule/delete`, params);
            s.setSubmitting(false);
            if (data.code == 200) {
                alert(data.msg);
                router.push('/setup/manager/edit?uid=' + data.uid);
            } else {
                alert(data.msg);
            }
        } catch (e: any) {}
    };

    return (
        <>
            {loading && (
                <div className="fixed w-full h-screen bg-opacity-25 bg-white z-10 flex items-center justify-center">
                    <div className="text-lg bg-white px-5 py-3 border rounded">
                        <i className="fas fa-spinner me-2"></i>파일 업로드 중 ...
                    </div>
                </div>
            )}

            <form onSubmit={fn.handleSubmit} noValidate>
                <div className="edit_popup w-full bg-slate-100 mx-auto py-10" style={{ minHeight: '100vh' }}>
                    <div className="px-9">
                        <div className="card_area mb-20">
                            <div className="text-2xl font-semibold text-center mb-10">게시물 {s.values.uid > 0 ? '수정' : '등록'}</div>

                            <div className="grid grid-cols-2 gap-4">
                                <div className="col-span-2">
                                    <label className="form-label">제목</label>
                                    <input
                                        type="text"
                                        name="title"
                                        {...attrs.is_mand}
                                        value={s.values?.title || ''}
                                        placeholder=""
                                        onChange={fn.handleChange}
                                        className={cls(s.errors['title'] ? 'border-danger' : '', 'form-control')}
                                    />
                                    {s.errors['title'] && <div className="form-error">{s.errors['title']}</div>}
                                </div>
                                {filter?.is_board_master && (
                                    <>
                                        <div className="col-span-1">
                                            <label className="form-label">진열여부</label>
                                            <select
                                                name="is_display"
                                                value={s.values?.is_display || ''}
                                                onChange={fn.handleChange}
                                                className={cls(s.errors['is_display'] ? 'border-danger' : '', 'form-select')}
                                            >
                                                <option value="T">진열</option>
                                                <option value="F">미진열</option>
                                            </select>
                                        </div>

                                        <div className="col-span-1">
                                            <label className="form-label">게시판</label>
                                            <select
                                                name="board_uid"
                                                {...attrs.is_mand}
                                                value={s.values?.board_uid || ''}
                                                onChange={fn.handleChange}
                                                className={cls(s.errors['board_uid'] ? 'border-danger' : '', 'form-select')}
                                            >
                                                <option value="">전체</option>
                                                {filter.board_uid?.map((v, i) => (
                                                    <option key={i} value={v.key}>
                                                        {v.value}
                                                    </option>
                                                ))}
                                            </select>
                                            {s.errors['board_uid'] && <div className="form-error">{s.errors['board_uid']}</div>}
                                        </div>
                                    </>
                                )}

                                <div className="col-span-1">
                                    <label className="form-label">카테고리</label>
                                    <select
                                        name="cate_uid"
                                        value={s.values?.cate_uid || ''}
                                        onChange={fn.handleChange}
                                        className={cls(s.errors['cate_uid'] ? 'border-danger' : '', 'form-select')}
                                    >
                                        <option value="">없음</option>
                                        {filter.cate_uid?.map((v, i) => (
                                            <option key={i} value={v.key}>
                                                {v.value}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                <div className="col-span-1">
                                    <label className="form-label">등록일</label>
                                    <input
                                        type="text"
                                        name="create_at"
                                        value={s.values?.create_at || ''}
                                        placeholder=""
                                        onChange={fn.handleChange}
                                        className={cls(s.errors['create_at'] ? 'border-danger' : '', 'form-control')}
                                        disabled={s.values.uid == 0 ? true : false}
                                    />
                                </div>

                                <div className="w-full col-span-2 hidden">
                                    <label className="form-label">태그</label>
                                    <input
                                        type="text"
                                        name="tags"
                                        value={s.values?.tags || ''}
                                        placeholder=""
                                        onChange={fn.handleChange}
                                        className={cls(s.errors['tags'] ? 'border-danger' : '', 'form-control')}
                                    />
                                </div>

                                <div className="w-full col-span-2">
                                    <label className="form-label">게시물 썸네일</label>
                                    <input
                                        name="thumb-file"
                                        type="file"
                                        className={cls(s.errors['thumb'] ? 'border-danger' : '', 'form-control')}
                                        accept="image/*"
                                        onChange={e => {
                                            fn.handleFileUpload(e, { upload_path: '/board/thumb/', file_type: 'img' });
                                        }}
                                    />
                                    {s.values.thumb ? <img src={s.values.thumb} className="my-3" alt="area_thumb" /> : ''}
                                </div>

                                {s.values.files?.map((v, i) => (
                                    <div key={i} className="w-full col-span-2">
                                        <label className="form-label">첨부파일 #{i + 1}</label>
                                        <div className="grid grid-cols-3 items-center gap-3">
                                            <input
                                                name="files"
                                                type="file"
                                                multiple
                                                className={cls(s.errors['thumb'] ? 'border-danger' : '', 'form-control')}
                                                onChange={e => {
                                                    fn.handleBoardFileUpload(e, i, {
                                                        upload_path: '/board/files/',
                                                        file_type: 'all',
                                                        start: fnStartUploading,
                                                        end: fnEndUploading,
                                                    });
                                                }}
                                            />
                                            <div className="col-span-2 font-bold">
                                                {v.fake_name && (
                                                    <span
                                                        className="underline cursor-pointer text-red-500 me-3"
                                                        onClick={e => {
                                                            deleteFiles(i);
                                                        }}
                                                    >
                                                        [삭제]
                                                    </span>
                                                )}

                                                {v.uid > 0 ? (
                                                    <span
                                                        onClick={e => {
                                                            download_file(v);
                                                        }}
                                                        className="cursor-pointer underline"
                                                    >
                                                        첨부파일 : {v.fake_name ? v.fake_name : <span className="text-gray-500 font-normal">없음</span>}
                                                    </span>
                                                ) : (
                                                    <>첨부파일 : {v.fake_name ? v.fake_name : <span className="text-gray-500 font-normal">없음</span>}</>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                ))}

                                <div className="w-full col-span-2">
                                    <label className="form-label">유튜브</label>
                                    <input
                                        type="text"
                                        name="youtube"
                                        value={s.values?.youtube || ''}
                                        placeholder=""
                                        onChange={fn.handleChange}
                                        className={cls(s.errors['youtube'] ? 'border-danger' : '', 'form-control')}
                                    />
                                </div>

                                <div className="col-span-2">
                                    <label className="form-label">
                                        <div>내용</div>
                                    </label>

                                    <CKEditor
                                        initialData={s.values?.contents || ''}
                                        onChange={(event, editor) => {
                                            s.setValues({ ...s.values, ['contents']: editor.getData() });
                                        }}
                                        upload_path={'/board/editor/' + dateformatYYYYMMDD()}
                                    />
                                </div>
                            </div>
                            {/* end grid */}
                            <div className="offcanvas-footer grid grid-cols-3 gap-4 mt-5 !border-0 !px-0">
                                <button className="btn-del border" type="button" onClick={deleting}>
                                    삭제
                                </button>
                                <button className="btn-save col-span-2 hover:bg-blue-600" disabled={s.submitting}>
                                    저장
                                </button>
                            </div>
                        </div>
                        {/* card_area */}

                        {board.board_type == 'qna' && (
                            <div className="card_area mb-20">
                                <div className="text-2xl font-semibold text-center mb-10">등록자 개인정보</div>
                                <div className="grid grid-cols-3 gap-4 mb-4">
                                    <div className="col-span-1">
                                        <label className="form-label">등록자 성함</label>
                                        <div className="form-control">{person?.name}</div>
                                    </div>
                                    <div className="col-span-1">
                                        <label className="form-label">등록자 이메일</label>
                                        <div className="form-control">{person?.email}</div>
                                    </div>
                                    <div className="col-span-1">
                                        <label className="form-label">등록자 전화번호</label>
                                        <div className="form-control">{person?.mobile}</div>
                                    </div>
                                </div>
                            </div>
                        )}
                        <div className="card_area mb-20">
                            <BoardReply props={props} />
                        </div>
                    </div>
                </div>
            </form>
        </>
    );
};
export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    const refer: string = ctx.req?.headers.referer + '';
    let is_board_master = false;
    if (refer.indexOf('/board/posts/list') > 0) {
        is_board_master = true;
    } else {
        is_board_master = false;
    }
    var request = {
        uid: ctx.query.uid,
        is_board_master: is_board_master,
    };

    var response: any = {};
    try {
        const { data } = await api.post(`/be/admin/posts/read`, request);
        response = data;
    } catch (e: any) {
        if (typeof e.redirect !== 'undefined') {
            return { redirect: e.redirect };
        }
    }
    return {
        props: { request, response },
    };
};

export default BoardPostsEdit;
