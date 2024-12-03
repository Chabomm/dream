import { api, setContext } from '@/libs/axios';
import React, { useState, forwardRef, useImperativeHandle } from 'react';
import { checkNumeric, cls, getToken } from '@/libs/utils';
import useForm from '@/components/form/useForm';

const BoardPostsEdit = forwardRef((props, ref) => {
    useImperativeHandle(ref, () => ({
        init,
    }));

    let item: any = {};
    const [filter, setFilter] = useState<any>({ menus: [] });
    function init(v: any, f: any) {
        item = v;
        setFilter(f);
        getDataRead(f);
        setOpen(true);
    }
    const [open, setOpen] = useState<boolean>(false);
    const [show, setShow] = useState<boolean>(false);

    const onToggle = () => {
        setShow(!open);
        setOpen(!open);
    };

    const getDataRead = async f => {
        try {
            const { data } = await api.post(`/be/manager/partner_posts/read`, { uid: item.uid });
            s.setValues(data);

            setShow(true);
        } catch (e: any) {}
    };

    const { s, fn, attrs } = useForm({
        initialValues: {
            menus: [],
        },
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
            const { data } = await api.post(`/be/manager/partner_posts/edit`, params);
            s.setSubmitting(false);
            if (data.code == 200) {
                alert(data.msg);
            } else {
                alert(data.msg);
            }
        } catch (e: any) {}
    };

    return (
        <>
            {open && (
                <>
                    <form onSubmit={fn.handleSubmit} noValidate className={cls('offcanvas', show ? 'show' : '')}>
                        <div className="offcanvas-header">
                            <div className="">공지사항 {item.uid > 0 ? '수정' : '등록'}</div>
                            <i className="fas fa-times btn-close" onClick={onToggle}></i>
                        </div>

                        <div className="offcanvas-body">
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
                            <div className="grid grid-cols-2 gap-4 px-5 pt-5">
                                <div className="col-span-2">
                                    <label className="form-label">제목</label>
                                    <input
                                        type="text"
                                        name="title"
                                        autoComplete="new-password"
                                        {...attrs.is_mand}
                                        value={s.values?.title || ''}
                                        placeholder=""
                                        onChange={fn.handleChange}
                                        className={cls(s.errors['title'] ? 'border-danger' : '', 'form-control')}
                                    />
                                    {s.errors['title'] && <div className="form-error">{s.errors['title']}</div>}
                                </div>
                                <div className="col-span-2">
                                    <label className="form-label">태그</label>
                                    <input
                                        type="text"
                                        name="tags"
                                        autoComplete="new-password"
                                        value={s.values?.tags || ''}
                                        placeholder=""
                                        onChange={fn.handleChange}
                                        className={cls(s.errors['tags'] ? 'border-danger' : '', 'form-control')}
                                    />
                                </div>
                                <div className="w-full col-span-2">
                                    <label className="form-label">영역썸네일</label>
                                    <input
                                        name="thumb-file"
                                        type="file"
                                        className={cls(s.errors['thumb'] ? 'border-danger' : '', 'form-control')}
                                        accept="image/*"
                                        onChange={e => {
                                            fn.handleImage(e, '/partner/board/thumb/');
                                        }}
                                    />
                                    {s.values.thumb ? <img src={s.values.thumb} className="my-3" alt="area_thumb" /> : ''}
                                </div>
                                {/* <div className="w-full col-span-2">
                                    <label className="form-label">
                                        내용
                                        <button
                                            type="button"
                                            className="text-blue-500 underline ms-3"
                                            onClick={() => {
                                                openToastEditor();
                                            }}
                                        >
                                            수정 {'>'}
                                        </button>
                                    </label>
                                    <div className="border border-t-2 p-3 relative">
                                        <div
                                            onClick={() => {
                                                openToastEditor();
                                            }}
                                            className="absolute top-3 right-3 border cursor-pointer bg-amber-50 p-2 rounded hover:bg-amber-200"
                                        >
                                            <i className="far fa-edit"></i>
                                        </div>
                                        <div dangerouslySetInnerHTML={{ __html: s.values.contents }}></div>
                                    </div>
                                </div> */}
                            </div>
                        </div>

                        <div className="offcanvas-footer grid grid-cols-3 gap-4">
                            <button className="btn-del" type="button" onClick={deleting}>
                                삭제
                            </button>
                            <button className="btn-save col-span-2 hover:bg-blue-600" disabled={s.submitting}>
                                저장
                            </button>
                        </div>
                    </form>
                    {/* <div className={cls(EditorOpen ? '' : 'hidden', 'editor_wrap')}>
                        <div className="h-16">
                            <div className="offcanvas-footer grid grid-cols-3 gap-4">
                                <button
                                    className="btn-del"
                                    type="button"
                                    onClick={() => {
                                        setEditorOpen(false);
                                    }}
                                >
                                    {'<'} 뒤로가기
                                </button>
                                <button className="btn-save col-span-2 hover:bg-blue-600" onClick={saveToastEditor}>
                                    저장하기
                                </button>
                            </div>
                        </div>
                        <ToastEditor ref={contentRef} forwardedRef={contentRef} hooks={{ addImageBlobHook: fn.handleUploadImageEditor }} />
                    </div> */}
                    <div className="offcanvas-backdrop fade" onClick={onToggle}></div>
                </>
            )}
        </>
    );
});

BoardPostsEdit.displayName = 'BoardPostsEdit';
export default BoardPostsEdit;
