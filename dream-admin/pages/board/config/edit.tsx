import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import { cls, checkNumeric } from '@/libs/utils';
import useForm from '@/components/form/useForm';
import LayoutPopup from '@/components/LayoutPopup';

const BoardConfigEdit: NextPage = (props: any) => {
    const router = useRouter();
    const [filter, setFilter] = useState<any>([]);

    useEffect(() => {
        if (props) {
            s.setValues(props.response.values);
            setFilter(props.response.filter);
        }
    }, [props]);

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
            const { data } = await api.post(`/be/admin/board/edit`, params);
            s.setSubmitting(false);
            if (data.code == 200) {
                alert(data.msg);
                router.push('/board/config/edit?uid=' + data.uid);
            } else {
                alert(data.msg);
            }
        } catch (e: any) {}
    };

    return (
        <LayoutPopup title="게시판 상세정보">
            <div className="w-full bg-slate-100 mx-auto py-10">
                <form onSubmit={fn.handleSubmit} noValidate>
                    <div className="px-9">
                        <div className="flex justify-between">
                            <div className="text-2xl font-semibold">회원 {s.values.uid > 0 ? '수정' : '등록'}</div>
                        </div>

                        <div className="border py-4 px-6 rounded shadow-md bg-white mt-5">
                            <div className="card_area">
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="col-span-1">
                                        <label className="form-label">프로젝트</label>
                                        <select
                                            name="site_id"
                                            value={s.values?.site_id || ''}
                                            onChange={fn.handleChange}
                                            className={cls(s.errors['site_id'] ? 'border-danger' : '', 'form-select')}
                                        >
                                            {filter.site_id?.map((v, i) => (
                                                <option key={i} value={v.key}>
                                                    {v.value}
                                                </option>
                                            ))}
                                        </select>
                                    </div>

                                    <div className="col-span-1">
                                        <label className="form-label">게시판 유형</label>
                                        <select
                                            name="board_type"
                                            value={s.values?.board_type || ''}
                                            onChange={fn.handleChange}
                                            className={cls(s.errors['board_type'] ? 'border-danger' : '', 'form-select')}
                                        >
                                            {filter.board_type?.map((v, i) => (
                                                <option key={i} value={v.key}>
                                                    {v.value}
                                                </option>
                                            ))}
                                        </select>
                                    </div>

                                    <div className="col-span-1">
                                        <label className="form-label">게시판 이름</label>
                                        <input
                                            type="text"
                                            name="board_name"
                                            {...attrs.is_mand}
                                            value={s.values?.board_name || ''}
                                            placeholder=""
                                            onChange={fn.handleChange}
                                            className={cls(s.errors['board_name'] ? 'border-danger' : '', 'form-control')}
                                        />
                                        {s.errors['board_name'] && <div className="form-error">{s.errors['board_name']}</div>}
                                    </div>

                                    <div className="col-span-1">
                                        <label className="form-label">프론트 URL</label>
                                        <input
                                            type="text"
                                            name="front_url"
                                            value={s.values?.front_url || ''}
                                            placeholder="도메인을 제외한 / 부터 입력해주세요"
                                            onChange={fn.handleChange}
                                            className={cls(s.errors['front_url'] ? 'border-danger' : '', 'form-control')}
                                        />
                                    </div>

                                    <div className="col-span-1">
                                        <label className="form-label">댓글여부</label>
                                        <select
                                            name="is_comment"
                                            value={s.values?.is_comment || ''}
                                            onChange={fn.handleChange}
                                            className={cls(s.errors['is_comment'] ? 'border-danger' : '', 'form-select')}
                                        >
                                            <option value="F">미사용</option>
                                            <option value="T">사용</option>
                                        </select>
                                    </div>

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
                                        <label className="form-label">읽기권한</label>
                                        <div className="grid grid-cols-2 checkbox_filter !m-0 !p-0 !border-t-0">
                                            {filter?.roles?.map((v: any, i: number) => (
                                                <div className="checkboxs_wrap" key={i} style={{ height: 'auto' }}>
                                                    <label>
                                                        <input
                                                            id={`permission-${i}`}
                                                            checked={s.values?.permission_read.filter(p => p == v.uid) == checkNumeric(v.uid) ? true : false}
                                                            onChange={fn.handleCheckboxGroupForInteger}
                                                            type="checkbox"
                                                            value={v.uid}
                                                            name="permission_read"
                                                        />
                                                        <span className="ml-3">
                                                            {v.name} ({JSON.parse(v.menus).length})
                                                        </span>
                                                    </label>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    <div className="col-span-1">
                                        <label className="form-label">쓰기권한</label>
                                        <div className="grid grid-cols-2 checkbox_filter !m-0 !p-0 !border-t-0">
                                            {filter?.roles?.map((v: any, i: number) => (
                                                <div className="checkboxs_wrap" key={i} style={{ height: 'auto' }}>
                                                    <label>
                                                        <input
                                                            id={`permission-${i}`}
                                                            checked={s.values?.permission_write.filter(p => p == v.uid) == checkNumeric(v.uid) ? true : false}
                                                            onChange={fn.handleCheckboxGroupForInteger}
                                                            type="checkbox"
                                                            value={v.uid}
                                                            name="permission_write"
                                                        />
                                                        <span className="ml-3">
                                                            {v.name} ({JSON.parse(v.menus).length})
                                                        </span>
                                                    </label>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="mt-5 w-full text-center">
                            <button className="mr-3 px-5 bg-blue-500 rounded-md py-2 text-white text-center" disabled={s.submitting}>
                                저장
                            </button>
                            {s.values?.uid > 0 && (
                                <button className="btn-del text-red-500" type="button" onClick={deleting}>
                                    삭제
                                </button>
                            )}
                        </div>
                    </div>
                </form>
            </div>
        </LayoutPopup>
    );
};
export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {
        uid: ctx.query.uid,
    };
    var response: any = {};
    try {
        const { data } = await api.post(`/be/admin/board/read`, request);
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

export default BoardConfigEdit;
