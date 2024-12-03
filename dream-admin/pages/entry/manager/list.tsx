import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import { cls } from '@/libs/utils';
import Layout from '@/components/Layout';
import useForm from '@/components/form/useForm';

import {
    EditForm,
    EditFormTable,
    EditFormTH,
    EditFormTD,
    EditFormKeyword,
    EditFormDateRange,
    EditFormSubmitSearch,
    EditFormRadioList,
    EditFormCheckboxList,
} from '@/components/UIcomponent/form/EditFormA';

import { ListTable, ListTableHead, ListTableBody, ListTableCaption, Callout } from '@/components/UIcomponent/table/ListTableA';
import ListPagenation from '@/components/bbs/ListPagenation';
import Datepicker from 'react-tailwindcss-datepicker';
import ButtonSearch from '@/components/UIcomponent/ButtonSearch';

const EntryManagerList: NextPage = (props: any) => {
    const nav_id = 146;
    const crumbs = ['구축관리', '고객사 관리자'];
    const title_sub = '복지몰 고객사의 관리자 내역을 확인할 수 있습니다.';
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
            const { data } = await api.post(`/be/admin/entry/manager/list`, p);
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

    const goEdit = (item: any) => {
        // window.open(`/entry/manager/edit?uid=${item.uid}`, '고객사 관리자', 'width=1500,height=800, location=no,status=no,scrollbars=yes,left=200%,top=50%');
        alert('준비중');
    };

    const getValueToText = (name, value) => {
        if (name == 'state') {
            switch (value) {
                case '100':
                    return '대기';
                case '200':
                    return '운영중';
                case '300':
                    return '일시중지';
                case '400':
                    return '폐쇄';
                default:
                    return value;
            }
        }
        return value;
    };

    return (
        <Layout nav_id={nav_id} crumbs={crumbs} title={crumbs[crumbs.length - 1]} user={props.user}>
            <Callout title={crumbs[crumbs.length - 1]} title_sub={title_sub} callout={callout} />
            <EditForm onSubmit={fn.handleSubmit}>
                <EditFormTable className="grid-cols-6">
                    <EditFormTH className="col-span-1">등록일</EditFormTH>
                    <EditFormTD className="col-span-5">
                        <EditFormDateRange input_name="create_at" values={s.values?.create_at} errors={s.errors} handleChange={fn.handleChangeDateRange} />
                    </EditFormTD>
                    <EditFormTH className="col-span-1">관리자유형</EditFormTH>
                    <EditFormTD className="col-span-2 border-e-0">
                        <EditFormRadioList input_name="role" values={s.values?.role} filter_list={filter.role} errors={s.errors} handleChange={fn.handleChange} />
                    </EditFormTD>
                    <EditFormTD className="col-span-3"> </EditFormTD>
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
            </ListTableCaption>

            <ListTable>
                <ListTableHead>
                    <th>고유번호</th>
                    <th>기업명</th>
                    <th>복지몰명</th>
                    <th>역할</th>
                    <th>실아이디</th>
                    <th>담당자명</th>
                    <th>등록일</th>
                    <th>상세보기</th>
                </ListTableHead>
                <ListTableBody>
                    {posts?.map((v: any, i: number) => (
                        <tr key={`list-table-${i}`} className="">
                            <td className="text-center">{v.uid}</td>
                            <td className="text-center">{v.company_name}</td>
                            <td className="text-center">{v.mall_name}</td>
                            <td className="text-center">{v.role == 'master' ? <div className="font-bold text-red-500">{v.role}</div> : <div>{v.roles_txt}</div>}</td>
                            <td className="text-center">{v.user_id}</td>
                            <td className="text-center">{v.name}</td>
                            <td className="text-center">{v.create_at}</td>
                            <td className="text-center">
                                <button
                                    type="button"
                                    className="text-blue-500 underline"
                                    onClick={() => {
                                        goEdit(v);
                                    }}
                                >
                                    수정
                                </button>
                            </td>
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
        const { data } = await api.post(`/be/admin/entry/manager/init`, request);
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

export default EntryManagerList;
