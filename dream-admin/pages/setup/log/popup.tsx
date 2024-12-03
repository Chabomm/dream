import type { GetServerSideProps, NextPage } from 'next';
import React, { useEffect, useState } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import LayoutPopup from '@/components/LayoutPopup';
import ListPagenation from '@/components/bbs/ListPagenation';

import { EditForm, EditFormTable, EditFormTH, EditFormTD, EditFormKeyword, EditFormDateRange, EditFormSubmitSearch } from '@/components/UIcomponent/form/EditFormA';
import EditFormCallout from '@/components/UIcomponent/form/EditFormCallout';
import { ListTable, ListTableHead, ListTableBody, ListTableCaption } from '@/components/UIcomponent/table/ListTableA';
import useForm from '@/components/form/useForm';

const SetupLogPopup: NextPage = (props: any) => {
    const crumbs = ['로그리스트'];
    const title_sub = '로그 리스트를 확인 할 수 있습니다.';
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
            const { data } = await api.post(`/be/admin/setup/logs/list`, p);
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

    return (
        <LayoutPopup title={crumbs[crumbs.length - 1]} className="px-6">
            <EditFormCallout title={crumbs[crumbs.length - 1]} title_sub={title_sub} callout={callout} />
            <div className="w-full mx-auto py-10">
                <div className="px-9">
                    <EditForm onSubmit={fn.handleSubmit}>
                        <EditFormTable className="grid-cols-6">
                            <EditFormTH className="col-span-1">등록일</EditFormTH>
                            <EditFormTD className="col-span-5">
                                <EditFormDateRange input_name="create_at" values={s.values?.create_at} handleChange={fn.handleChangeDateRange} errors={s.errors} />
                            </EditFormTD>
                            <EditFormTH className="col-span-1">검색어</EditFormTH>
                            <EditFormTD className="col-span-5">
                                <EditFormKeyword
                                    skeyword_values={s.values?.skeyword}
                                    skeyword_type_values={s.values?.skeyword_type}
                                    skeyword_type_filter={filter?.skeyword_type}
                                    handleChange={fn.handleChange}
                                    errors={s.errors}
                                ></EditFormKeyword>
                            </EditFormTD>
                        </EditFormTable>
                        <EditFormSubmitSearch button_name="조회하기" submitting={s.submitting}></EditFormSubmitSearch>
                    </EditForm>
                    {posts.length <= 0 ? (
                        <div className="border p-24 m-24 text-center">로그 내역이 없습니다.</div>
                    ) : (
                        <>
                            <ListTableCaption>
                                <div className="">
                                    검색 결과 : 총 {params?.page_total}개 중 {posts?.length}개
                                </div>
                                <div className="text-right"></div>
                            </ListTableCaption>
                            <ListTable className="px-3">
                                <ListTableHead className="!top-0">
                                    <th>내용</th>
                                    <th>전</th>
                                    <th>후</th>
                                    <th>등록자</th>
                                </ListTableHead>
                                <ListTableBody>
                                    {posts?.map((v: any, i: number) => (
                                        <tr key={`list-table-${i}`}>
                                            <td className="">{v.column_name}</td>
                                            <td className="!justify-start">{v.cl_before}</td>
                                            <td className="break-all ">{v.cl_after}</td>
                                            <td className="break-all ">{v.create_user}</td>
                                        </tr>
                                    ))}
                                </ListTableBody>
                            </ListTable>
                            <ListPagenation props={params} getPagePost={getPagePost} />
                        </>
                    )}
                </div>
            </div>
        </LayoutPopup>
    );
};
export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {
        table_name: ctx.query.table_name,
        table_uid: ctx.query.table_uid,
    };
    var response: any = {};
    try {
        const { data } = await api.post(`/be/admin/setup/logs/init`, request);
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

export default SetupLogPopup;
