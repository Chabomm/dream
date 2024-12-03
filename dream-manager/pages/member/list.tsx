import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect, useRef } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import { cls } from '@/libs/utils';
import useForm from '@/components/form/useForm';
import Datepicker from 'react-tailwindcss-datepicker';
import Layout from '@/components/Layout';

import {
    EditForm,
    EditFormTable,
    EditFormTH,
    EditFormTD,
    EditFormKeyword,
    EditFormDateRange,
    EditFormSubmitSearch,
    EditFormCheckboxList,
    EditFormSelect,
} from '@/components/UIcomponent/form/EditFormA';
import { ListTable, ListTableHead, ListTableBody, ListTableCaption, Callout } from '@/components/UIcomponent/table/ListTableA';
import ListPagenation from '@/components/bbs/ListPagenation';
import ExcelModal from '@/components/modal/excel';

const MemberList: NextPage = (props: any) => {
    const nav_id = 56;
    const crumbs = ['임직원 관리', '임직원 내역'];
    const title_sub = '임직원의 내역을 확인하고 관리할 수 있습니다.';
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
            const { data } = await api.post(`/be/manager/member/list`, p);
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

    const goEdit = (uid: any) => {
        window.open(`/member/edit?uid=${uid}`, '상세보기', 'width=1120,height=800,location=no,status=no,scrollbars=yes');
    };

    const [excelModalOpen, setExcelModalOpen] = useState<boolean>(false);
    const fnExcelDownReason = async () => {
        setExcelModalOpen(true);
    };

    return (
        <>
            <Layout nav_id={nav_id} crumbs={crumbs} title={crumbs[crumbs.length - 1]} user={props.user}>
                <Callout title={crumbs[crumbs.length - 1]} title_sub={title_sub} callout={callout} />
                <EditForm onSubmit={fn.handleSubmit}>
                    <EditFormTable className="grid-cols-6">
                        <EditFormTH className="col-span-1">등록일 조회</EditFormTH>
                        <EditFormTD className="col-span-2">
                            <EditFormDateRange input_name="create_at" values={s.values?.create_at} errors={s.errors} handleChange={fn.handleChangeDateRange} />
                        </EditFormTD>
                        <EditFormTH className="col-span-1">생년월일</EditFormTH>
                        <EditFormTD className="col-span-2">
                            <EditFormSelect
                                input_name="birth_type"
                                value={s.values?.birth_type || ''}
                                filter_list={filter.birth_type}
                                onChange={fn.handleChange}
                                className="w-full"
                            />
                        </EditFormTD>

                        <EditFormTH className="col-span-1">재직상태</EditFormTH>
                        <EditFormTD className="col-span-2">
                            <EditFormCheckboxList
                                input_name="serve_type"
                                values={s.values?.serve_type}
                                filter_list={filter.serve_type}
                                cols={3}
                                handleChange={fn.handleCheckboxGroup}
                                errors={s.errors}
                            />
                        </EditFormTD>

                        <EditFormTH className="col-span-1">검색어</EditFormTH>
                        <EditFormTD className="col-span-2">
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
                    <div className="flex gap-3">
                        <button
                            onClick={() => {
                                goEdit(0);
                            }}
                            className="text-sm text-blue-600"
                        >
                            <i className="far fa-plus-square me-2"></i>회원등록
                        </button>
                        <div className="" onClick={() => fnExcelDownReason()}>
                            <button className="text-sm text-green-600">
                                <i className="far fa-file-excel me-1"></i> 엑셀다운로드
                            </button>
                        </div>
                    </div>
                </ListTableCaption>

                <ListTable>
                    <ListTableHead>
                        <th>번호</th>
                        <th>이름</th>
                        <th>부서</th>
                        <th>직급</th>
                        <th>아이디</th>
                        <th>연락처</th>
                        <th>생년월일</th>
                        <th>회원등록일</th>
                        <th>상세보기</th>
                    </ListTableHead>
                    <ListTableBody>
                        {posts?.map((v: any, i: number) => (
                            <tr key={`list-table-${i}`} className="">
                                <td className="text-center">{v.uid}</td>
                                <td className="text-center">{v.user_name}</td>
                                <td className="text-center">{v.depart}</td>
                                <td className="text-center">{v.position}</td>
                                <td className="text-center">{v.login_id}</td>
                                <td className="text-center">{v.mobile}</td>
                                <td className="text-center">{v.birth}</td>
                                <td className="text-center">{v.create_at}</td>
                                <td className="text-center">
                                    <button
                                        type="button"
                                        className="text-blue-500 underline"
                                        onClick={() => {
                                            goEdit(v.uid);
                                        }}
                                    >
                                        상세보기
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </ListTableBody>
                </ListTable>

                <ListPagenation props={params} getPagePost={getPagePost} />
            </Layout>
            {excelModalOpen && <ExcelModal setExcelModalOpen={setExcelModalOpen} params={params} url={'/be/manager/member/xlsx/download'} title={'임직원내역'} />}
        </>
    );
};

export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {};
    var response: any = {};
    try {
        const { data } = await api.post(`/be/manager/member/init`, request);
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

export default MemberList;
