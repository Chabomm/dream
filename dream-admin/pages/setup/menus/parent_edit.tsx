import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import { cls } from '@/libs/utils';
import useForm from '@/components/form/useForm';

const SetupMenusParentEdit: NextPage = (props: any) => {
    const router = useRouter();

    useEffect(() => {
        if (props) {
            props.response.depth = router.query.depth;
            props.response.parent = router.query.parent;
            s.setValues(props.response);
        }
    }, [props]);

    const { s, fn, attrs } = useForm({
        initialValues: {},
        onSubmit: async () => {
            await editing('REG');
        },
    });

    const editing = async mode => {
        try {
            if (mode == 'REG' && s.values.uid > 0) {
                mode = 'MOD';
            }
            s.values.mode = mode;
            const { data } = await api.post(`/be/admin/setup/menus/edit`, s.values);
            if (data.code == 200) {
                if (s.values.mode == 'REG') {
                    alert(data.msg);
                    router.replace(`/setup/menus/parent_edit?uid=${s.values.uid}&depth=${s.values.depth}&parent=${s.values.parent}`);
                } else {
                    alert(data.msg);
                    if (mode == 'MOD') {
                        router.replace(`/setup/menus/parent_edit?uid=${data.uid}&depth=${s.values.depth}&parent=${s.values.parent}`);
                    }
                }
            } else {
                alert(data.msg);
            }
            return;
        } catch (e: any) {}
    };

    return (
        <>
            <div className="w-full bg-slate-100 mx-auto py-10">
                <form onSubmit={fn.handleSubmit} noValidate>
                    <div className="px-9">
                        <div className="flex justify-between">
                            <div className="text-2xl font-semibold">메뉴 {s.values.uid > 0 ? '수정' : '등록'}</div>
                        </div>
                        <div className="border py-4 px-6 rounded shadow-md bg-white mt-5">
                            <div className="card_area">
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="col-span-1">
                                        <label className="form-label">메뉴명</label>
                                        <input
                                            type="text"
                                            name="name"
                                            {...attrs.is_mand}
                                            value={s.values?.name || ''}
                                            placeholder=""
                                            onChange={fn.handleChange}
                                            className={cls(s.errors['name'] ? 'border-danger' : '', 'form-control')}
                                        />
                                        {s.errors['name'] && <div className="form-error">{s.errors['name']}</div>}
                                    </div>
                                    <div className="col-span-1">
                                        <label className="form-label">메뉴아이콘</label>
                                        <input
                                            type="text"
                                            name="icon"
                                            value={s.values?.icon || ''}
                                            placeholder=""
                                            onChange={fn.handleChange}
                                            className={cls(s.errors['icon'] ? 'border-danger' : '', 'form-control')}
                                        />
                                    </div>
                                    <div className="col-span-1">
                                        <label className="form-label">링크</label>
                                        <input
                                            type="text"
                                            name="to"
                                            value={s.values?.to || ''}
                                            placeholder=""
                                            onChange={fn.handleChange}
                                            className={cls(s.errors['to'] ? 'border-danger' : '', 'form-control')}
                                        />
                                    </div>
                                </div>
                                {/* end grid */}
                            </div>
                            {/* card_area */}
                        </div>
                        <div className="mt-5 w-full text-center">
                            <button className="mr-3 px-5 bg-blue-500 rounded-md py-2 text-white text-center" disabled={s.submitting}>
                                저장
                            </button>
                            {/* {s.values.uid > 0 && (
                                    <button type="button" className="px-5 bg-red-500 rounded-md py-2 text-white text-center" onClick={deleting}>
                                        삭제
                                    </button>
                                )} */}
                        </div>
                    </div>
                </form>
            </div>
        </>
    );
};
export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {
        uid: ctx.query.uid,
    };
    var response: any = {};
    try {
        const { data } = await api.post(`/be/admin/setup/menus/read`, request);
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

export default SetupMenusParentEdit;
