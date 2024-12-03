import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import Datepicker from 'react-tailwindcss-datepicker';
import { cls } from '@/libs/utils';

import useForm from '@/components/form/useForm';
import ListPagenation from '@/components/bbs/ListPagenation';

function IntranetBoardPostGallery(props: any) {
    const [filter, setFilter] = useState<any>({});
    const [params, setParams] = useState<any>({});
    const [posts, setPosts] = useState<any>([]);
    const [board, setBoard] = useState<any>({});

    useEffect(() => {
        getPostsInit({ uid: props.board_uid });
    }, []);

    const getPostsInit = async p => {
        try {
            const { data } = await api.post(`/be/admin/posts/intranet`, p);
            setBoard(data.board);
            setFilter(data.filter);
            setParams(data.params);
            getPagePost(data.params);
        } catch (e: any) {}
    };

    const getPagePost = async p => {
        let newPosts = await getPostsData(p);
        setPosts(newPosts.list);
    };

    const getPostsData = async p => {
        try {
            const { data } = await api.post(`/be/admin/posts/list`, p);
            setParams(data.params);
            return data;
        } catch (e: any) {}
    };

    const { s, fn } = useForm({
        initialValues: {},
        onSubmit: async () => {
            await searching();
        },
    });

    const searching = async () => {
        let board_uid = params.filters.board_uid;
        params.filters = s.values;
        params.filters.board_uid = board_uid;
        let newPosts = await getPostsData(params);
        setPosts(newPosts.list);
    };

    const handleImgError = e => {
        e.target.src = '';
    };

    const goEdit = (item: any) => {
        window.open(`/board/posts/edit?uid=${item.uid}`, '게시물 등록/수정', 'width=1120,height=800,location=no,status=no,scrollbars=yes');
    };

    const viewPosts = (item: any) => {
        window.open(`/board/posts/view?uid=${item.uid}`, '게시물 상세', 'width=1120,height=800,location=no,status=no,scrollbars=yes');
    };
    return (
        <>
            <form onSubmit={fn.handleSubmit} noValidate className="w-full border py-4 px-6 rounded shadow-md bg-white mt-5">
                <div className="grid grid-cols-4 gap-6">
                    <div className="col-span-1">
                        <label className="form-label">등록일 조회</label>
                        <Datepicker
                            containerClassName="relative w-full text-gray-700 border border-gray-300 rounded"
                            inputName="create_at"
                            value={s.values.create_at}
                            i18n={'ko'}
                            onChange={fn.handleChangeDateRange}
                            primaryColor={'blue'}
                        />
                    </div>
                    <div className="col-span-3">
                        <label className="form-label">키워드 조회</label>
                        <div className="flex">
                            <select
                                name="skeyword_type"
                                value={s.values?.skeyword_type || ''}
                                onChange={fn.handleChange}
                                className={cls(s.errors['skeyword_type'] ? 'border-danger' : '', 'form-select mr-3')}
                                style={{ width: 'auto' }}
                            >
                                <option value="">전체</option>
                                {filter.skeyword_type?.map((v, i) => (
                                    <option key={i} value={v.key}>
                                        {v.value}
                                    </option>
                                ))}
                            </select>
                            <input
                                type="text"
                                name="skeyword"
                                value={s.values?.skeyword || ''}
                                placeholder=""
                                onChange={fn.handleChange}
                                className={cls(s.errors['skeyword'] ? 'border-danger' : '', 'form-control mr-3')}
                                style={{ width: 'auto' }}
                            />
                            <button className="btn-search col-span-2" disabled={s.submitting}>
                                <i className="fas fa-search mr-3" style={{ color: '#ffffff' }}></i> 검색
                            </button>
                        </div>
                    </div>
                </div>
            </form>

            <div className="border-t py-3 grid grid-cols-2 h-16 items-center">
                <div className="text-left">
                    총 {params.page_total} 개 중 {params.page_size}개
                </div>
                <div className="text-right">
                    {board?.poss_insert && (
                        <button
                            type="button"
                            className="btn-funcs"
                            onClick={() => {
                                goEdit({ uid: 0 });
                            }}
                        >
                            <i className="fas fa-pen me-2"></i> 게시물 등록하기
                        </button>
                    )}
                </div>
            </div>

            <div className="grid grid-cols-3">
                {posts?.map((v: any, i: number) => (
                    <div
                        key={v.uid}
                        onClick={e => {
                            viewPosts(v);
                        }}
                        className="p-4 w-full mb-5 cursor-pointer"
                    >
                        <div className="rounded-lg h-64 overflow-hidden">
                            <img
                                onError={handleImgError}
                                alt="img"
                                className="object-cover object-center h-full w-full transition hover:duration-500 hover:scale-125"
                                src={v?.thumb ? v.thumb : '/images/no_image.jpg'}
                            />
                        </div>

                        <h2 className="text-xl font-medium title-font text-gray-900 mt-3 line-two">{v.title}</h2>

                        <div className="mt-2 text-start text-sm text-zinc-400">
                            <span className="">{v.create_at.replace('<br>', ' ')}</span>
                        </div>
                    </div>
                ))}
            </div>
            <ListPagenation props={params} getPagePost={getPagePost} />
        </>
    );
}

export default IntranetBoardPostGallery;
