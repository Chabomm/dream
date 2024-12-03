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

const EntryCounselList: NextPage = (props: any) => {
    const nav_id = 88;
    const crumbs = ['구축관리', '상담신청'];
    const title_sub = '복지몰 구축 상담신청 내역을 확인할 수 있습니다.';
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
            const { data } = await api.post(`/be/admin/entry/counsel/list`, p);
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
        window.open(`/entry/counsel/edit?uid=${item.uid}`, '수기상담 수정', 'width=1120,height=800,location=no,status=no,scrollbars=yes');
    };

    const getValueToText = (name, value) => {
        if (name == 'rec_type') {
            switch (value) {
                case 'A':
                    return '앱사용자전체';
                case 'P':
                    return '고객사';
                case 'S':
                    return '개별';
                default:
                    return value;
            }
        } else if (name == 'state') {
            switch (value) {
                case '100':
                    return '상담문의';
                case '200':
                    return '상담중';
                case '300':
                    return '도입보류';
                case '501':
                    return '도입대기';
                case '502':
                    return '도입신청완료';
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
                    <EditFormTH className="col-span-1">진행상태</EditFormTH>
                    <EditFormTD className="col-span-2 border-e-0">
                        <EditFormCheckboxList
                            input_name="state"
                            values={s.values?.state}
                            filter_list={filter?.state}
                            cols={2}
                            errors={s.errors}
                            handleChange={fn.handleCheckboxGroupForInteger}
                        />
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
                <div className="">
                    <button
                        onClick={() => {
                            goEdit({ uid: 0 });
                        }}
                        className="text-sm text-blue-600"
                    >
                        <i className="far fa-plus-square me-2"></i>수기상담 등록
                    </button>
                </div>
            </ListTableCaption>

            <ListTable>
                <ListTableHead>
                    <th>고유번호</th>
                    <th>진행상태</th>
                    <th style={{ width: '400px' }}>기업명</th>
                    <th>임직원수</th>
                    <th>담당자명</th>
                    <th>작성일</th>
                    <th>수정일</th>
                    <th>상세보기</th>
                </ListTableHead>
                <ListTableBody>
                    {posts?.map((v: any, i: number) => (
                        <tr key={`list-table-${i}`} className="">
                            <td className="text-center">{v.uid}</td>
                            <td className="text-center">{getValueToText('state', v.state)}</td>
                            <td className="text-center">{v.company_name}</td>
                            <td className="text-center">{v.staff_count}</td>
                            <td className="text-center">{v.staff_name}</td>
                            <td className="text-center">{v.create_at}</td>
                            <td className="text-center">{v.update_at}</td>
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
        const { data } = await api.post(`/be/admin/entry/counsel/init`, request);
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

export default EntryCounselList;
