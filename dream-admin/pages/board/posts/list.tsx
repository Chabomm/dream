import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import { cls, checkNumeric } from '@/libs/utils';
import Layout from '@/components/Layout';
import useForm from '@/components/form/useForm';
import Datepicker from 'react-tailwindcss-datepicker';
import ListPagenation from '@/components/bbs/ListPagenation';

const BoardPostsList: NextPage = (props: any) => {
    const router = useRouter();
    const { board_uid } = router.query;
    const [filter, setFilter] = useState<any>({});
    const [params, setParams] = useState<any>({});
    const [posts, setPosts] = useState<any>([]);

    useEffect(() => {
        setFilter(props.response.filter);
        setParams(props.response.params);
        s.setValues(props.response.params.filters);
        getPagePost(props.response.params);
    }, []);

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
        initialValues: {
            skeyword: '',
            skeyword_type: '',
            site_id: '',
            cate_uid: 0,
            board_uid: 0,
            create_at: {
                startDate: null,
                endDate: null,
            },
        },
        onSubmit: async () => {
            await searching();
        },
    });

    const searching = async () => {
        params.filters = s.values;
        let newPosts = await getPostsData(params);
        setPosts(newPosts.list);
    };

    const openPostsEdit = (uid: any) => {
        window.open(`/board/posts/edit?uid=${uid}`, '게시물 등록/수정', 'width=1120,height=800,location=no,status=no,scrollbars=yes');
    };

    const viewPosts = (item: any) => {
        window.open(`/board/posts/view?uid=${item.uid}`, '게시물 상세', 'width=1120,height=800,location=no,status=no,scrollbars=yes');
    };

    return (
        <Layout user={props.user} title="indendkorea admin console" nav_id={105} crumbs={['게시판관리', '게시물리스트']}>
            <form onSubmit={fn.handleSubmit} noValidate className="w-full border py-4 px-6 rounded shadow-md bg-white mt-5 relative">
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
                    <div className="col-span-1">
                        <label className="form-label">게시판</label>
                        <select
                            name="board_uid"
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
                    </div>
                    <div className="col-span-4">
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
            </form>

            <div className="border-t py-3 grid grid-cols-2 h-16 items-center">
                <div className="text-left">총 {posts?.length} 개</div>
                <div className="text-right">
                    <button
                        type="button"
                        className="btn-funcs"
                        onClick={() => {
                            openPostsEdit(0);
                        }}
                    >
                        <i className="fas fa-pen me-2"></i> 게시물 등록하기
                    </button>
                </div>
            </div>

            <div className="col-table">
                <div className="col-table-th grid grid-cols-11 sticky top-16 bg-gray-100">
                    <div className="">번호</div>
                    <div className="">게시판 유형</div>
                    <div className="">게시판 이름</div>
                    <div className="col-span-5">게시물 제목</div>
                    <div className="">등록일</div>
                    <div className="">진열</div>
                    <div className="">상세보기</div>
                </div>

                {posts?.map((v: any, i: number) => (
                    <div key={i} className="col-table-td grid grid-cols-11 bg-white transition duration-300 ease-in-out hover:bg-gray-100">
                        <div className="">{v.uid}</div>
                        <div className="">{v.board_type}</div>
                        <div className="">{v.board_name}</div>
                        <div
                            onClick={() => {
                                viewPosts(v);
                            }}
                            className={cls('!justify-start text-left truncate col-span-5')}
                        >
                            {v.thumb == '' || v.thumb == null ? '' : <i className="far fa-image mr-3 text-blue-400"></i>}
                            <span className="cursor-pointer">
                                <span className="">{v.title}</span>
                                {v.reply_count > 0 && (
                                    <span className="text-green-600 ms-3">
                                        <i className="far fa-comment-dots"></i> {v.reply_count}
                                    </span>
                                )}
                                {v.file_count > 0 && (
                                    <span className="text-blue-600 ms-3">
                                        <i className="fas fa-save"></i> {v.file_count}
                                    </span>
                                )}
                            </span>
                        </div>
                        <div className="">
                            <div dangerouslySetInnerHTML={{ __html: v.create_at }}></div>
                        </div>
                        <div className="">{v.is_display == 'T' ? '진열' : '미진열'}</div>
                        <div className="">
                            <button
                                type="button"
                                className="text-blue-500 underline"
                                onClick={() => {
                                    openPostsEdit(v.uid);
                                }}
                            >
                                수정
                            </button>
                        </div>
                    </div>
                ))}
            </div>
            <ListPagenation props={params} getPagePost={getPagePost} />
        </Layout>
    );
};
export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {
        uid: checkNumeric(ctx.query.board_uid),
        is_board_master: true,
    };
    var response: any = {};
    try {
        const { data } = await api.post(`/be/admin/posts/init`, request);
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

export default BoardPostsList;
