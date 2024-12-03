import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import { cls } from '@/libs/utils';
import Layout from '@/components/Layout';
import useForm from '@/components/form/useForm';
import ListPagenation from '@/components/bbs/ListPagenation';
import Datepicker from 'react-tailwindcss-datepicker';
import PartnerSearch from '@/components/searchBox/PartnerSearch';

const MemberList: NextPage = (props: any) => {
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
            const { data } = await api.post(`/be/admin/member/list`, p);
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
            serve: '',
            partner_name: '',
            partner_uid: 0,
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
            const { data } = await api.post(`/be/admin/member/filter`);
            setFilter(data);
        } catch (e: any) {}
    };

    const openMemberEdit = (uid: number) => {
        window.open(`/member/edit?uid=${uid}`, '회원정보', 'width=1120,height=800,location=no,status=no,scrollbars=yes,left=200%,top=50%');
    };

    // [ S ] 고객사검색
    const [partnerSearchOpen, setPartnerSearchOpen] = useState(false);
    const partnerSubmit = () => {
        if (s.values?.partner_name == '') {
            alert('검색어를 입력해주세요');
            return;
        }
        setPartnerSearchOpen(true);
    };

    const getPartnerUid = (uid: number, partner_id: string, company_name: string, mall_name: string) => {
        const copy = { ...s.values };
        copy.partner_uid = uid;
        copy.partner_id = partner_id;
        copy.company_name = company_name;
        copy.mall_name = mall_name;
        s.setValues(copy);
    };
    // [ E ] 고객사검색

    return (
        <>
            <Layout user={props.user} title="indendkorea admin console" nav_id={90} crumbs={['회원관리', '회원리스트']}>
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
                            <label className="form-label">회원상태</label>
                            <div className="flex items-center gap-4 h-10">
                                {filter.serve?.map((v: any, i: number) => (
                                    <div key={i} className="flex items-center">
                                        <input
                                            id={`serve-${i}`}
                                            onChange={fn.handleChange}
                                            checked={s.values?.serve == v.key ? true : false}
                                            type="radio"
                                            value={v.key}
                                            name="serve"
                                            className="w-4 h-4"
                                        />
                                        <label htmlFor={`serve-${i}`} className="ml-2 text-sm font-medium">
                                            {v.text}
                                        </label>
                                    </div>
                                ))}
                            </div>
                        </div>
                        <div className="col-span-4">
                            <label className="form-label">고객사</label>
                            <div className="flex">
                                <input
                                    type="text"
                                    name="partner_name"
                                    value={s.values?.partner_name || ''}
                                    placeholder="고객사 아이디, 고객사명 또는 복지몰명"
                                    onChange={fn.handleChange}
                                    className="form-control mr-3"
                                    style={{ width: '300px' }}
                                />
                                <button className="btn-filter col-span-2" type="button" onClick={() => partnerSubmit()}>
                                    고객사 검색
                                </button>
                                <div className="ms-3">
                                    <input
                                        type="text"
                                        name="partner_id"
                                        value={s.values?.partner_id || ''}
                                        placeholder=""
                                        className="form-control mr-3 !text-red-500"
                                        style={{ width: 'auto' }}
                                        disabled
                                    />
                                    <input
                                        type="text"
                                        name="mall_name"
                                        value={s.values?.mall_name || ''}
                                        placeholder=""
                                        onChange={fn.handleChange}
                                        className="form-control mr-3 !text-red-500"
                                        style={{ width: 'auto' }}
                                        disabled
                                    />
                                </div>
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
                </div>

                <div className="col-table">
                    <div className="col-table-th grid grid-cols-12 sticky top-16 bg-gray-100">
                        <div className="">번호</div>
                        <div className="">고객사명</div>
                        <div className="">복지몰명</div>
                        <div className="">아이디</div>
                        <div className="">이름</div>
                        <div className="">재직상태</div>
                        <div className="">비밀번호</div>
                        <div className="">로그인</div>
                        <div className="">포인트</div>
                        <div className="">회원상태</div>
                        <div className="">회원등록일</div>
                        <div className="">정보수정</div>
                    </div>

                    {posts?.map((v: any, i: number) => (
                        <div key={i} className="col-table-td grid grid-cols-12 bg-white transition duration-300 ease-in-out hover:bg-gray-100">
                            <div className="">{v.uid}</div>
                            <div className="">{v.company_name}</div>
                            <div className="">{v.mall_name}</div>
                            <div className="break-all">{v.user_id}</div>
                            <div className="">{v.user_name}</div>
                            <div className="">{v.serve}</div>
                            <div className="">{v.is_pw_reset == 'T' ? <span className="text-red-500">초기화</span> : '정상'}</div>
                            <div className="">{v.is_login == 'T' ? '가능' : <span className="text-red-500">불가능</span>}</div>
                            <div className="">{v.is_point == 'T' ? '가능' : <span className="text-red-500">불가능</span>}</div>
                            <div className="">{v.state == 200 ? '정상' : <span className="text-blue-500">대기</span>}</div>
                            <div className="">{v.create_at}</div>
                            <div className="" onClick={() => openMemberEdit(v.uid)}>
                                <button type="button" className="btn-filter">
                                    상세보기
                                </button>
                            </div>
                        </div>
                    ))}
                </div>

                <ListPagenation props={params} getPagePost={getPagePost} />
            </Layout>
            {partnerSearchOpen && <PartnerSearch setPartnerSearchOpen={setPartnerSearchOpen} partnerName={s.values?.partner_name} sandPartnerUid={getPartnerUid} />}
        </>
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
        const { data } = await api.post(`/be/admin/member/list`, request);
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

export default MemberList;
