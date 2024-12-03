import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import { cls } from '@/libs/utils';
import Layout from '@/components/Layout';
import useForm from '@/components/form/useForm';
import Datepicker from 'react-tailwindcss-datepicker';
import ListPagenation from '@/components/bbs/ListPagenation';

const UmsTmplList: NextPage = (props: any) => {
    const router = useRouter();
    const [params, setParams] = useState(props.request);
    const [posts, setPosts] = useState(props.response.list);

    useEffect(() => {
        if (sessionStorage.getItem(router.asPath) || '{}' !== '{}') {
            setParams(JSON.parse(sessionStorage.getItem(router.asPath) || '{}').params);
            setPosts(JSON.parse(sessionStorage.getItem(router.asPath) || '{}').data);
            return () => {
                const scroll = parseInt(JSON.parse(sessionStorage.getItem(router.asPath) || '{}').scroll_y, 10);
                window.scrollTo(0, scroll);
                sessionStorage.removeItem(router.asPath);
            };
        }
    }, [posts, router.asPath]);

    const getPagePost = async p => {
        let newPosts = await getPostsData(p);
        setPosts(newPosts.list);
        setParams(newPosts.params);
    };

    const getPostsData = async p => {
        console.log(p);
        try {
            const { data } = await api.post(`/ums/tmpl/list`, p);
            return data;
        } catch (e: any) {}
    };

    const { s, fn } = useForm({
        initialValues: {
            skeyword: '',
            skeyword_type: '',
            ums_type: [],
            profile: [],
            platform: [],
            create_at: {
                startDate: null,
                endDate: null,
            },
        },
        onSubmit: async () => {
            await searching();
        },
    });

    const [filter, setFilter] = useState<any>({});
    const [search, setSearch] = useState<any>({});

    useEffect(() => {
        getFilterContidion();
    }, []);

    const getFilterContidion = async () => {
        try {
            const { data } = await api.post(`/ums/tmpl/filter`);
            setFilter(data);

            const copy = { ...s.values };
            copy.ums_type = data.ums_type.map(row => row.checked && row.key);
            copy.profile = data.profile.map(row => row.checked && row.key);
            copy.platform = data.platform.map(row => row.checked && row.key);
            s.setValues(copy);
        } catch (e: any) {}
    };

    const searching = async () => {
        params.filters = s.values;
        let newPosts = await getPostsData(params);
        setPosts(newPosts.list);
        setParams(newPosts.params);
    };

    const goEdit = (item: any) => {
        window.open(`/message/tmpl/edit?uid=${item.uid}`, 'UMS 템플릿 상세', 'width=1120,height=800,location=no,status=no,scrollbars=yes');
    };

    return (
        <Layout user={props.user} title="indendkorea admin console" nav_id={84} crumbs={['UMS관리', 'UMS 템플릿']}>
            <form onSubmit={fn.handleSubmit} noValidate className="w-full border py-4 px-6 rounded shadow-md bg-white mt-5 relative">
                <div className="grid grid-cols-4 gap-6">
                    <div className="col-span-1">
                        <div className="col-span-1">
                            <label className="form-label">등록일</label>
                            <Datepicker
                                inputName="create_at"
                                value={s.values.create_at}
                                i18n={'ko'}
                                onChange={fn.handleChangeDateRange}
                                containerClassName="relative w-full text-gray-700 border border-gray-300 rounded"
                            />
                        </div>
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
                            {filter.skeyword_type?.map((v: any, i: number) => (
                                <option key={i} value={v.key}>
                                    {v.text}
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
                        <button type="button" className="btn-filter ml-3">
                            <i className="fas fa-stream"></i> 필터
                        </button>
                    </div>
                </div>

                <div className="checkbox_filter">
                    <div className="grid grid-cols-5 gap-6">
                        <div className="col-span-1">
                            <div className="title">분류</div>
                            <div className="checkboxs_wrap h-24 overflow-y-auto">
                                {filter.ums_type?.map((v: any, i: number) => (
                                    <label key={i}>
                                        <input
                                            id={`ums_type-${i}`}
                                            onChange={fn.handleCheckboxGroup}
                                            type="checkbox"
                                            value={v.key}
                                            checked={s.values.ums_type.includes(v.key)}
                                            name="ums_type"
                                        />
                                        <span className="font-bold">{v.text}</span>
                                    </label>
                                ))}
                            </div>
                        </div>
                        <div className="col-span-1">
                            <div className="title">프로필</div>
                            <div className="checkboxs_wrap h-24 overflow-y-auto">
                                {filter.profile?.map((v: any, i: number) => (
                                    <label key={i}>
                                        <input
                                            id={`profile-${i}`}
                                            onChange={fn.handleCheckboxGroup}
                                            type="checkbox"
                                            value={v.key}
                                            checked={s.values.profile.includes(v.key)}
                                            name="profile"
                                        />
                                        <span className="font-bold">{v.text}</span>
                                    </label>
                                ))}
                            </div>
                        </div>
                        <div className="col-span-1">
                            <div className="title">플랫폼</div>
                            <div className="checkboxs_wrap h-24 overflow-y-auto">
                                {filter.platform?.map((v: any, i: number) => (
                                    <label key={i}>
                                        <input
                                            id={`platform-${i}`}
                                            onChange={fn.handleCheckboxGroup}
                                            type="checkbox"
                                            value={v.key}
                                            checked={s.values.platform.includes(v.key)}
                                            name="platform"
                                        />
                                        <span className="font-bold">{v.text}</span>
                                    </label>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </form>

            <div className="border-t py-3 grid grid-cols-2 h-16 items-center">
                <div className="text-left">
                    총 {params.page_total} 개 중 {params.page_size}개
                </div>
                <div className="text-right">
                    <button
                        type="button"
                        className="btn-funcs"
                        onClick={() => {
                            goEdit({ uid: 0 });
                        }}
                    >
                        등록
                    </button>
                </div>
            </div>

            <div className="col-table">
                <div className="col-table-th grid grid-cols-9 sticky top-16 bg-gray-100">
                    <div className="">ums_uid</div>
                    <div className="">분류</div>
                    <div className="">템플릿코드</div>
                    <div className="col-span-3">제목</div>
                    <div className="">플랫폼</div>
                    <div className="">프로필</div>
                    <div className="">상세보기</div>
                </div>

                {posts?.map((v: any, i: number) => (
                    <div key={i} className="col-table-td grid grid-cols-9 bg-white transition duration-300 ease-in-out hover:bg-gray-100">
                        <div className="">{v.uid}</div>
                        <div className="">{v.ums_type}</div>
                        <div className="">{v.template_code}</div>
                        <div className="col-span-3">{v.subject}</div>
                        <div className="">{v.platform}</div>
                        <div className="">{v.profile}</div>
                        <div className="">
                            <button
                                type="button"
                                className="text-blue-500 underline"
                                onClick={() => {
                                    goEdit(v);
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
        page: 1,
        page_size: 0,
        page_view_size: 0,
        page_total: 0,
        page_last: 0,
    };
    var response: any = {};
    try {
        const { data } = await api.post(`/be/admin/ums/tmpl/list`, request);
        response = data;
        request = response.params;
    } catch (e: any) {
        if (typeof e.redirect !== 'undefined') {
            return { redirect: e.redirect };
        }
    }
    return {
        props: { request, response },
    };
};

export default UmsTmplList;
