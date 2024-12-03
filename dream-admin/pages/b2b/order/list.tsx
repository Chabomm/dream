import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import { checkNumeric, cls } from '@/libs/utils';
import Layout from '@/components/Layout';
import useForm from '@/components/form/useForm';
import ListPagenation from '@/components/bbs/ListPagenation';
import Datepicker from 'react-tailwindcss-datepicker';

import {
    EditForm,
    EditFormTable,
    EditFormTH,
    EditFormTD,
    EditFormKeyword,
    EditFormDateRange,
    EditFormSubmitSearch,
    EditFormRadioList,
} from '@/components/UIcomponent/form/EditFormA';
import { ListTable, ListTableHead, ListTableBody, ListTableCaption, Callout } from '@/components/UIcomponent/table/ListTableA';

const B2BOrderList: NextPage = (props: any) => {
    const nav_id = 114;
    const crumbs = ['기업혜택', '신청내역'];
    const title_sub = '신청내역을 확인/수정 할 수 있습니다.';
    const callout = [];

    const router = useRouter();
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
            const { data } = await api.post(`/be/admin/b2b/order/list`, p);
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
        params.filters = s.values;

        let newPosts = await getPostsData(params);
        setPosts(newPosts.list);
    };

    const openB2BOrderDetail = (ouid: number) => {
        window.open(`/b2b/order/detail?uid=${ouid}`, '신청내역상세', 'width=1120,height=800,location=no,status=no,scrollbars=yes');
    };

    return (
        <>
            <Layout nav_id={nav_id} crumbs={crumbs} title={crumbs[crumbs.length - 1]} user={props.user}>
                <Callout title={crumbs[crumbs.length - 1]} title_sub={title_sub} callout={callout} />
                <EditForm onSubmit={fn.handleSubmit}>
                    <EditFormTable className="grid-cols-6">
                        <EditFormTH className="col-span-1">최근등록일</EditFormTH>
                        <EditFormTD className="col-span-2">
                            <EditFormDateRange input_name="create_at" values={s.values?.create_at} handleChange={fn.handleChangeDateRange} errors={s.errors} />
                        </EditFormTD>
                        <EditFormTH className="col-span-1">처리상태</EditFormTH>
                        <EditFormTD className="col-span-2">
                            <EditFormRadioList input_name="state" values={s.values?.state} filter_list={filter.state} handleChange={fn.handleChange} errors={s.errors} />
                        </EditFormTD>
                        <EditFormTH className="col-span-1">검색어</EditFormTH>
                        <EditFormTD className="col-span-5">
                            <EditFormKeyword
                                skeyword_values={s.values?.skeyword}
                                skeyword_type_values={s.values?.skeyword_type}
                                skeyword_type_filter={filter.skeyword_type}
                                handleChange={fn.handleChange}
                                errors={s.errors}
                            ></EditFormKeyword>
                        </EditFormTD>
                    </EditFormTable>
                    <EditFormSubmitSearch button_name="조회하기" submitting={s.submitting}></EditFormSubmitSearch>
                </EditForm>

                <ListTableCaption>
                    <div className="">
                        검색 결과 : 총 {params?.page_total}개 중 {posts?.length}개
                    </div>
                    <div className=""></div>
                </ListTableCaption>
                <ListTable>
                    <ListTableHead>
                        <th>번호</th>
                        <th>처리상태</th>
                        <th>카테고리</th>
                        <th>상품명</th>
                        <th>유입경로</th>
                        <th>작성자</th>
                        <th>판매자</th>
                        <th>담당MD</th>
                        <th>등록일</th>
                        <th>상세보기</th>
                    </ListTableHead>

                    <ListTableBody>
                        {posts?.map((v: any, i: number) => (
                            <tr key={`list-table-${i}`} className="">
                                <td className="">{v.uid}</td>
                                <td className="">{v.state}</td>
                                <td className="break-all">{v.category}</td>
                                <td className="">{v.title}</td>
                                <td className="">{v.token_name == 'DREAM-MANAGER' ? '고객사어드민' : '판매자센터'}</td>
                                <td className="flex-col !items-start">
                                    <div className="mb-1">{v.apply_company}</div>
                                    <div>{v.apply_name}</div>
                                </td>
                                <td className="flex-col !items-start">
                                    <div className="mb-1">{v.seller_id}</div>
                                    <div>{v.seller_name}</div>
                                </td>
                                <td className="flex-col !items-start">
                                    <div className="mb-1">{v.indend_md}</div>
                                    <div className="">{v.indend_md_name}</div>
                                </td>
                                <td className="">{v.create_at}</td>
                                <td className="">
                                    <button type="button" className="btn-filter" onClick={() => openB2BOrderDetail(v.uid)}>
                                        상세보기
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </ListTableBody>
                </ListTable>
                <ListPagenation props={params} getPagePost={getPagePost} />
            </Layout>
        </>
    );
};
export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {};
    var response: any = {};
    try {
        const { data } = await api.post(`/be/admin/b2b/order/init`, request);
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

export default B2BOrderList;
