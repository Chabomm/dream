import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import { cls } from '@/libs/utils';
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

const SellerList: NextPage = (props: any) => {
    const nav_id = 116;
    const crumbs = ['기업혜택', 'B2B 판매자 리스트'];
    const title_sub = 'B2B 판매자 리스트를 확인/수정 할 수 있습니다.';
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
            const { data } = await api.post(`/be/admin/b2b/seller/list`, p);
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

    const openSellerEdit = (seller_uid: number) => {
        window.open(`/b2b/seller/edit?seller_uid=${seller_uid}`, 'B2B판매자정보', 'width=1500,height=800,location=no,status=no,scrollbars=yes,left=200%,top=50%');
    };

    return (
        <>
            <Layout nav_id={nav_id} crumbs={crumbs} title={crumbs[crumbs.length - 1]} user={props.user}>
                <Callout title={crumbs[crumbs.length - 1]} title_sub={title_sub} callout={callout} />
                <EditForm onSubmit={fn.handleSubmit}>
                    <EditFormTable className="grid-cols-6">
                        <EditFormTH className="col-span-1">등록일</EditFormTH>
                        <EditFormTD className="col-span-2">
                            <EditFormDateRange input_name="create_at" values={s.values?.create_at} handleChange={fn.handleChangeDateRange} errors={s.errors} />
                        </EditFormTD>
                        <EditFormTH className="col-span-1">퇴점일</EditFormTH>
                        <EditFormTD className="col-span-2">
                            <EditFormDateRange input_name="delete_at" values={s.values?.delete_at} handleChange={fn.handleChangeDateRange} errors={s.errors} />
                        </EditFormTD>
                        <EditFormTH className="col-span-1">상태</EditFormTH>
                        <EditFormTD className="col-span-5">
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
                    <div className="text-right">
                        <button
                            type="button"
                            className="btn-funcs"
                            onClick={() => {
                                openSellerEdit(0);
                            }}
                        >
                            등록
                        </button>
                    </div>
                </ListTableCaption>
                <ListTable>
                    <ListTableHead>
                        <th>번호</th>
                        <th>담당MD</th>
                        <th>B2B판매자아이디</th>
                        <th>B2B판매자명</th>
                        <th>사업자번호</th>
                        <th>담당자이름</th>
                        <th>담당자전화</th>
                        <th>담당자휴대폰</th>
                        <th>담당자이메일</th>
                        <th>등록일</th>
                    </ListTableHead>
                    <ListTableBody>
                        {posts?.map((v: any, i: number) => (
                            <tr key={`list-table-${i}`} className="">
                                <td className="text-center">{v.uid}</td>
                                <td className="text-center">{v.indend_md}</td>
                                <td className="text-center">{v.seller_id}</td>
                                <td className="text-center font-bold underline cursor-pointer" onClick={() => openSellerEdit(v.uid)}>
                                    {v.seller_name} <i className="fas fa-external-link-alt"></i>
                                </td>
                                <td className="text-center">{v.biz_no}</td>
                                <td className="text-center">{v.name}</td>
                                <td className="text-center">{v.tel}</td>
                                <td className="text-center">{v.mobile}</td>
                                <td className="text-center">{v.email}</td>
                                <td className="text-center">{v.create_at}</td>
                            </tr>
                        ))}
                    </ListTableBody>
                </ListTable>

                <ListPagenation props={params} getPagePost={getPagePost} />
            </Layout>
            {/* {sellerSearchOpen && <SellerSearch setSellerSearchOpen={setSellerSearchOpen} seller={s.values?.seller} sandSellerUid={getSellerUid} />} */}
        </>
    );
};
export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {};
    var response: any = {};
    try {
        const { data } = await api.post(`/be/admin/b2b/seller/init`, request);
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

export default SellerList;
