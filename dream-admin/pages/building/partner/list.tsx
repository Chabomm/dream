import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import { cls } from '@/libs/utils';
import Layout from '@/components/Layout';
import useForm from '@/components/form/useForm';
import ListPagenation from '@/components/bbs/ListPagenation';
import Datepicker from 'react-tailwindcss-datepicker';

const BuildingPartnerList: NextPage = (props: any) => {
    const router = useRouter();
    const [params, setParams] = useState(props.request);
    const [posts, setPosts] = useState(props.response.list);
    const [filter, setFilter] = useState<any>({});

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

    useEffect(() => {
        getFilterContidion();
    }, []);

    const getPagePost = async p => {
        let newPosts = await getPostsData(p);
        setPosts(newPosts.list);
    };

    const getPostsData = async p => {
        try {
            const { data } = await api.post(`/be/admin/building/partner/list`, p);
            setParams(param => {
                param.page = data.page;
                param.page_size = data.page_size;
                param.page_view_size = data.page_view_size;
                param.page_total = data.page_total;
                param.page_last = data.page_last;
                return param;
            });
            return data;
        } catch (e: any) {}
    };

    const { s, fn } = useForm({
        initialValues: {
            skeyword: '',
            skeyword_type: '',
            state: '',
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
        params.page = 1;
        params.page_size = 0;
        params.page_view_size = 0;
        params.page_total = 0;
        params.page_last = 0;

        let newPosts = await getPostsData(params);
        setPosts(newPosts.list);
    };

    const getFilterContidion = async () => {
        try {
            const { data } = await api.post(`/be/admin/building/partner/filter`);
            setFilter(data);
        } catch (e: any) {}
    };

    const openPartnerEdit = (uid: number) => {
        window.open(`/building/partner/edit?uid=${uid}`, '고객사정보', 'width=1120,height=800,location=no,status=no,scrollbars=yes,left=200%,top=50%');
    };

    const openJoinMall = (uid: number) => {
        console.log('openJoinMall', uid);
    };

    return (
        <Layout user={props.user} title="indendkorea admin console" nav_id={102} crumbs={['구축관리', '고객사']}>
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
                    <div className="col-span-1">
                        <label className="form-label">복지몰상태</label>
                        <div className="flex items-center gap-4 h-10">
                            {filter.state?.map((v: any, i: number) => (
                                <div key={i} className="flex items-center">
                                    <input
                                        id={`state-${i}`}
                                        onChange={fn.handleChange}
                                        checked={s.values?.state == v.key ? true : false}
                                        type="radio"
                                        value={v.key}
                                        name="state"
                                        className="w-4 h-4"
                                    />
                                    <label htmlFor={`state-${i}`} className="ml-2 text-sm font-medium">
                                        {v.text}
                                    </label>
                                </div>
                            ))}
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
                            openPartnerEdit(0);
                        }}
                    >
                        <i className="fas fa-pen me-2"></i> 등록
                    </button>
                </div>
            </div>

            <div className="col-table">
                <div className="col-table-th grid grid-cols-12 sticky top-16 bg-gray-100">
                    <div className="">join</div>
                    <div className="">복지몰상태</div>
                    <div className="">HOST</div>
                    <div className="">고객사코드</div>
                    <div className="">고객사명</div>
                    <div className="">복지몰명</div>
                    <div className="">회원수</div>
                    <div className="">누적예치금</div>
                    <div className="">담당자</div>
                    <div className="">연락처</div>
                    <div className="">이메일</div>
                    <div className="">상세정보</div>
                </div>

                {posts?.map((v: any, i: number) => (
                    <div key={i} className="col-table-td grid grid-cols-12 bg-white transition duration-300 ease-in-out hover:bg-gray-100">
                        <div className="" onClick={() => openJoinMall(v.uid)}>
                            <button type="button" className="btn-filter">
                                join
                            </button>
                        </div>
                        <div className="">{v.state == 100 ? '대기' : v.state == 200 ? '운영중' : v.state == 300 ? '일시중지' : v.state == 400 && '폐쇄'}</div>
                        <div className="">{v.partner_id}</div>
                        <div className="">{v.partner_code}</div>
                        <div className="">{v.company_name}</div>
                        <div className="">{v.mall_name}</div>
                        <div className="">{v.member_count == null ? 0 : v.member_count}</div>
                        <div className="">0</div>
                        <div className=""></div>
                        <div className=""></div>
                        <div className=""></div>
                        <div className="" onClick={() => openPartnerEdit(v.uid)}>
                            <button type="button" className="btn-filter">
                                상세정보
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
        const { data } = await api.post(`/be/admin/building/partner/list`, request);
        response = data;
        request.page = response.page;
        request.page_size = response.page_size;
        request.page_view_size = response.page_view_size;
        request.page_total = response.page_total;
        request.page_last = response.page_last;
    } catch (e: any) {
        if (typeof e.redirect !== 'undefined') {
            return { redirect: e.redirect };
        }
    }
    return {
        props: { request, response },
    };
};

export default BuildingPartnerList;
