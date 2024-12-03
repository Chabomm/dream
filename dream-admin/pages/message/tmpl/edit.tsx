import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect, useRef } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import { cls, dateformatYYYYMMDD } from '@/libs/utils';
import useForm from '@/components/form/useForm';
import dynamic from 'next/dynamic';

const CKEditor = dynamic(() => import('@/components/editor/CKEditor'), { ssr: false });

const UmsTmplEdit: NextPage = (props: any) => {
    const router = useRouter();
    const [filter, setFilter] = useState<any>([]);

    useEffect(() => {
        if (props) {
            s.setValues(props.response.values);
            setFilter(props.response.filter);
        }
    }, [props]);

    // useEffect(() => {
    //     const editor_instance = contentRef.current;
    //     // typeof editor_instance.retry === 'undefined'
    //     if (typeof editor_instance === 'undefined') {
    //         contentRef.current.getInstance()?.setHTML(s.values.contents);
    //     }
    // });

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
            params.board_uid = 1;
            const { data } = await api.post(`/ums/tmpl/edit`, params);
            s.setSubmitting(false);
            if (data.code == 200) {
                alert(data.msg);
                router.push('/message/tmpl/edit?uid=' + data.uid);
            } else {
                alert(data.msg);
            }
        } catch (e: any) {}
    };

    const openPreview = () => {
        window.open(
            `/message/tmpl/preview?uid=${s.values.uid}&layout_uid=${s.values.layout_uid}`,
            'UMS 템플릿 프리뷰',
            'width=1120,height=800,location=no,status=no,scrollbars=yes'
        );
    };

    return (
        <>
            <form onSubmit={fn.handleSubmit} noValidate>
                <div className="edit_popup w-full bg-slate-100 mx-auto py-10" style={{ minHeight: '100vh' }}>
                    <div className="px-9">
                        <div className="text-2xl font-semibold">UMS 템플릿</div>

                        {process.env.NODE_ENV == 'development' && (
                            <pre className="">
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <div className="font-bold mb-3 text-red-500">filter</div>
                                        {JSON.stringify(filter, null, 4)}
                                    </div>
                                    <div>
                                        <div className="font-bold mb-3 text-red-500">s.values</div>
                                        {JSON.stringify(s.values, null, 4)}
                                    </div>
                                </div>
                            </pre>
                        )}

                        <div className=" bg-slate-400 border p-5">SMS또는 알림톡 선택시 프로필 필 수 ! SMS는 indend 자동 ?</div>

                        <div className="card_area">
                            <div className="grid grid-cols-2 gap-4">
                                <div className="col-span-2">
                                    <label className="form-label">관리자메모</label>
                                    <textarea
                                        name="memo"
                                        rows={3}
                                        value={s.values?.memo || ''}
                                        placeholder=""
                                        onChange={fn.handleChange}
                                        className={cls(s.errors['memo'] ? 'border-danger' : '', 'form-control')}
                                    />
                                </div>
                                <div className="col-span-1">
                                    <label className="form-label">등록일</label>
                                    <input
                                        readOnly
                                        type="text"
                                        value={s.values?.create_at || ''}
                                        placeholder=""
                                        className={cls(s.errors['create_at'] ? 'border-danger' : '', 'form-control')}
                                    />
                                </div>
                                <div className="col-span-1">
                                    <div className="form-label">수정일</div>
                                    <input
                                        readOnly
                                        type="text"
                                        value={s.values?.update_at || ''}
                                        placeholder=""
                                        className={cls(s.errors['update_at'] ? 'border-danger' : '', 'form-control')}
                                    />
                                </div>
                                <div className="col-span-1">
                                    <label className="form-label">분류</label>
                                    <select
                                        name="ums_type"
                                        value={s.values?.ums_type || ''}
                                        onChange={fn.handleChange}
                                        className={cls(s.errors['ums_type'] ? 'border-danger' : '', 'form-select')}
                                    >
                                        <option value="">선택해주세요</option>
                                        {filter.ums_type?.map((v, i) => (
                                            <option key={i} value={v.key}>
                                                {v.text}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                                <div className="col-span-1">
                                    {s.values.ums_type == 'email' ? (
                                        <>
                                            <label className="form-label">레이아웃번호</label>
                                            <select
                                                name="layout_uid"
                                                value={s.values?.layout_uid || ''}
                                                onChange={fn.handleChange}
                                                className={cls(s.errors['layout_uid'] ? 'border-danger' : '', 'form-select')}
                                            >
                                                <option value="">선택해주세요</option>
                                                {filter.layout_uid?.map((v, i) => (
                                                    <option key={i} value={v.uid}>
                                                        {v.layout_name}
                                                    </option>
                                                ))}
                                            </select>
                                        </>
                                    ) : (
                                        <>
                                            <label className="form-label">알림톡코드</label>
                                            <input
                                                type="text"
                                                name="template_code"
                                                value={s.values?.template_code || ''}
                                                placeholder=""
                                                onChange={fn.handleChange}
                                                className={cls(s.errors['template_code'] ? 'border-danger' : '', 'form-control')}
                                            />
                                        </>
                                    )}
                                </div>
                                <div className="col-span-1">
                                    <label className="form-label">플랫폼</label>
                                    <select
                                        name="platform"
                                        value={s.values?.platform || ''}
                                        onChange={fn.handleChange}
                                        className={cls(s.errors['platform'] ? 'border-danger' : '', 'form-select')}
                                    >
                                        <option value="">선택해주세요</option>
                                        {filter.platform?.map((v, i) => (
                                            <option key={i} value={v.key}>
                                                {v.text}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                                <div className="col-span-1">
                                    <label className="form-label">프로필</label>
                                    <select
                                        name="profile"
                                        value={s.values?.profile || ''}
                                        onChange={fn.handleChange}
                                        className={cls(s.errors['profile'] ? 'border-danger' : '', 'form-select')}
                                    >
                                        <option value="">선택해주세요</option>
                                        {filter.profile?.map((v, i) => (
                                            <option key={i} value={v.key}>
                                                {v.text}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                                <div className="col-span-2">
                                    <label className="form-label">제목</label>
                                    <input
                                        type="text"
                                        name="subject"
                                        {...attrs.is_mand}
                                        value={s.values?.subject || ''}
                                        placeholder=""
                                        onChange={fn.handleChange}
                                        className={cls(s.errors['subject'] ? 'border-danger' : '', 'form-control')}
                                    />
                                    {s.errors['subject'] && <div className="form-error">{s.errors['subject']}</div>}
                                </div>
                                <div className="col-span-2">
                                    <label className="form-label">
                                        <div>내용</div>
                                        {s.values.layout_uid > 0 && (
                                            <button type="button" onClick={openPreview} className="text-blue-600 underline">
                                                preview
                                            </button>
                                        )}
                                    </label>
                                    {s.values.ums_type == 'email' ? (
                                        <CKEditor
                                            initialData={s.values?.content || ''}
                                            onChange={(event, editor) => {
                                                s.setValues({ ...s.values, ['content']: editor.getData() });
                                            }}
                                            // upload_path={'/board/editor/' + dateformatYYYYMMDD()}
                                        />
                                    ) : (
                                        <textarea
                                            name="content"
                                            rows={10}
                                            {...attrs.is_mand}
                                            value={s.values?.content || ''}
                                            placeholder=""
                                            onChange={fn.handleChange}
                                            className={cls(s.errors['content'] ? 'border-danger' : '', 'form-control')}
                                        />
                                    )}
                                </div>
                            </div>
                            {/* end grid */}
                        </div>
                        {/* card_area */}

                        <div className="offcanvas-footer grid grid-cols-3 gap-4 !p-0 my-5">
                            <button className="btn-del" type="button" onClick={deleting}>
                                삭제
                            </button>
                            <button className="btn-save col-span-2 hover:bg-blue-600" disabled={s.submitting}>
                                저장
                            </button>
                        </div>
                    </div>
                </div>
            </form>
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
        const { data } = await api.post(`/ums/tmpl/read`, request);
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

export default UmsTmplEdit;
