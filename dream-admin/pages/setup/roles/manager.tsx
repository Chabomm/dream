import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';

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
import { checkNumeric } from '@/libs/utils';
import ListPagenation from '@/components/bbs/ListPagenation';
import useForm from '@/components/form/useForm';
import Layout from '@/components/Layout';

const SetupManagerRolesList: NextPage = (props: any) => {
    const nav_id = 145;
    const crumbs = ['환경설정', '고객사 역할관리'];
    const title_sub = '고객사 관리자(master)의 역할을 관리합니다.';
    const callout = ['고객사 관리자(master)의 역할을 관리합니다.', '고객사 관리자의 매니저의 역할은 고객사관리자페이지에서 관리 가능합니다'];
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
            const { data } = await api.post(`/be/admin/setup/roles/list`, p);
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

    function openAdminRolesEdit(uid: any) {
        window.open(
            `/setup/roles/edit?uid=${uid}&partner_uid=${params.partner_uid}&site_id=${params.site_id}`,
            '역할정보',
            'width=1120,height=800,location=no,status=no,scrollbars=yes,left=400%,top=50%'
        );
    }

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
                <div className="">
                    <button
                        onClick={() => {
                            openAdminRolesEdit(0);
                        }}
                        className="text-sm text-blue-600"
                    >
                        <i className="far fa-plus-square me-2"></i>관리자 역할 등록
                    </button>
                </div>
            </ListTableCaption>

            <ListTable>
                <ListTableHead>
                    <th>고유번호</th>
                    <th>역할명</th>
                    <th>배정된 메뉴</th>
                    <th>수정하기</th>
                </ListTableHead>
                <ListTableBody>
                    {posts?.map((v: any, i: number) => (
                        <tr key={`list-table-${i}`} className="">
                            <td className="text-center">{v.uid}</td>
                            <td className="text-center">{v.name}</td>
                            <td className="text-center">{v.roles_txt}</td>
                            <td className="text-center">
                                <button
                                    type="button"
                                    className="text-blue-500 underline"
                                    onClick={() => {
                                        openAdminRolesEdit(v.uid);
                                    }}
                                >
                                    수정
                                </button>
                            </td>
                        </tr>
                    ))}
                </ListTableBody>
            </ListTable>
        </Layout>
    );
};
export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {
        partner_uid: 0,
        site_id: 'manager',
    };
    var response: any = {};
    try {
        const { data } = await api.post(`/be/admin/setup/roles/init`, request);
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

export default SetupManagerRolesList;
