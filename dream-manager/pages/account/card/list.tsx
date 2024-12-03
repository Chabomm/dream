import type { GetServerSideProps, NextPage } from 'next';
import React, { useEffect, useState } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';

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
import ListPagenation from '@/components/bbs/ListPagenation';
import useForm from '@/components/form/useForm';

const AccountCardList: NextPage = (props: any) => {
    const nav_id = 135;
    const crumbs = ['정산', '복지카드 사용내역'];
    const title_sub = '';
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
            const { data } = await api.post(`/be/manager/account/card/list`, p);
            setParams(data.params);
            return data;
        } catch (e: any) {}
    };

    const { s, fn } = useForm({
        onSubmit: async () => {
            await searching();
        },
    });

    const searching = async () => {
        params.filters = s.values;
        let newPosts = await getPostsData(params);
        setPosts(newPosts.list);
    };

    return (
        <Layout nav_id={nav_id} crumbs={crumbs} title={crumbs[crumbs.length - 1]} user={props.user}>
            <Callout title={crumbs[crumbs.length - 1]} title_sub={title_sub} callout={callout} />
            <EditForm onSubmit={fn.handleSubmit}>
                <EditFormTable className="grid-cols-6">
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
                <div className="flex gap-x-5">
                    <button className="text-sm text-green-600">
                        <i className="far fa-file-excel me-1"></i> 엑셀다운로드
                    </button>
                </div>
            </ListTableCaption>

            <ListTable>
                <ListTableHead>
                    <th>이름</th>
                    <th>생년월일</th>
                    <th>부서</th>
                    <th>직급</th>
                    <th>카드</th>
                    <th>업종명</th>
                    <th>가맹점명</th>
                    <th>카드 결제일</th>
                    <th>차감 사용 포인트</th>
                    <th>포인트 차감일자</th>
                    <th>카드 승인번호</th>
                </ListTableHead>
                <ListTableBody>
                    {posts?.map((v: any, i: number) => (
                        <tr key={`list-table-${i}`} className="">
                            <td className="text-center">{v.depart}</td>
                            <td className="text-center">{v.position}</td>
                            <td className="text-center">{v.login_id}</td>
                            <td className="text-center">{v.mobile}</td>
                            <td className="text-center">{v.birth}</td>
                            <td className="text-center">{v.depart}</td>
                            <td className="text-center">{v.position}</td>
                            <td className="text-center">{v.login_id}</td>
                            <td className="text-center">{v.mobile}</td>
                            <td className="text-center">{v.birth}</td>
                            <td className="text-center">{v.birth}</td>
                        </tr>
                    ))}
                </ListTableBody>
            </ListTable>

            <ListPagenation props={params} getPagePost={getPagePost} />
        </Layout>
    );
};

export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {};
    var response: any = {};
    try {
        const { data } = await api.post(`/be/manager/account/card/init`, request);
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

export default AccountCardList;
