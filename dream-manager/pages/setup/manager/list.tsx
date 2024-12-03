import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect, useRef } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import useForm from '@/components/form/useForm';
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
    EditFormCheckboxList,
} from '@/components/UIcomponent/form/EditFormA';
import { ListTable, ListTableHead, ListTableBody, ListTableCaption, Callout } from '@/components/UIcomponent/table/ListTableA';
import { checkNumeric } from '@/libs/utils';
import ListPagenation from '@/components/bbs/ListPagenation';

const SetupManagerList: NextPage = (props: any) => {
    const nav_id = 78;
    const crumbs = ['환경설정', '관리자 내역'];
    const title_sub = '관리자 내역을 확인 및 관리할 수 있습니다.';
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
            const { data } = await api.post(`/be/manager/setup/manager/list`, p);
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

    function openAdminUserEdit(uid: any) {
        window.open(`/setup/manager/edit?uid=${uid}`, '관리자 정보', 'width=1120,height=800,location=no,status=no,scrollbars=yes,left=400%,top=50%');
    }

    return (
        <Layout nav_id={nav_id} crumbs={crumbs} title={crumbs[crumbs.length - 1]} user={props.user}>
            <Callout title={crumbs[crumbs.length - 1]} title_sub={title_sub} callout={callout} />
            <EditForm onSubmit={fn.handleSubmit}>
                <EditFormTable className="grid-cols-6">
                    <EditFormTH className="col-span-1">상태</EditFormTH>
                    <EditFormTD className="col-span-5">
                        <EditFormRadioList input_name="state" values={s.values?.state} filter_list={filter.state} errors={s.errors} handleChange={fn.handleChange} />
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
                    <EditFormTH className="col-span-1">관리자 역할</EditFormTH>
                    <EditFormTD className="col-span-2 border-e-0">
                        <EditFormCheckboxList
                            input_name="roles"
                            values={s.values?.roles}
                            filter_list={filter.roles}
                            cols={2}
                            handleChange={fn.handleCheckboxGroupForInteger}
                            errors={s.errors}
                        />
                    </EditFormTD>
                    <EditFormTD className="col-span-3"> </EditFormTD>
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
                            openAdminUserEdit(0);
                        }}
                        className="text-sm text-blue-600"
                    >
                        <i className="far fa-plus-square me-2"></i>관리자 등록
                    </button>
                </div>
            </ListTableCaption>
            <ListTable>
                <ListTableHead>
                    <th>고유번호</th>
                    <th>관리자ID</th>
                    <th>이름</th>
                    <th>부서</th>
                    <th>역할</th>
                    <th>상태</th>
                    <th>날짜</th>
                    <th>상세보기</th>
                </ListTableHead>
                <ListTableBody>
                    {posts?.map((v: any, i: number) => (
                        <tr key={`list-table-${i}`} className="">
                            <td className="text-center">{v.uid}</td>
                            <td className="">{v.login_id}</td>
                            <td className="">{v.name}</td>
                            <td className="text-center">{v.depart}</td>
                            <td className="">{v.role == 'master' ? <div className="font-bold text-red-500">{v.role}</div> : <div>{v.roles_txt}</div>}</td>
                            <td className="text-center">{v.state == 100 ? '승인대기' : v.state == 200 ? '정상' : v.state == 900 && '탈퇴'}</td>
                            <td className="text-center">{v.create_at}</td>
                            <td className="text-center">
                                <button
                                    type="button"
                                    className="text-blue-500 underline"
                                    onClick={() => {
                                        openAdminUserEdit(v.uid);
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
        const { data } = await api.post(`/be/manager/setup/manager/init`, request);
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

export default SetupManagerList;
