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
import { checkNumeric } from '@/libs/utils';
import ExcelModal from '@/components/modal/excel';

const PointUsedSikwonUsedList: NextPage = (props: any) => {
    const nav_id = 143;
    const crumbs = ['포인트 사용관리', '식권포인트 사용내역'];
    const title_sub = '식권포인트 사용내역을 확인할 수 있습니다.';
    const callout = [
        '온라인 복지몰에서 식권포인트를 사용하여 결제한 내역을 확인할 수 있습니다.',
        '사용내역이 없는 경우에는 조회되지 않습니다.',
        '결제 시 사용한 식권포인트 금액은 검색결과>식권포인트 항목에 (-)로 표시됩니다.',
        '결제완료: 식권포인트 차감하여 결제 완료 상태.',
        '환불: 구매한 서비스 및 상품을 환불한 상태.',
        '포인트 지급/회수 내역은 식권포인트 지급내역에서 확인 가능합니다. ',
    ];
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

    useEffect(() => {
        if ([...posts].length > 0) {
            const num2Curs: any = document.querySelectorAll('.num2Cur') || undefined;
            num2Curs.forEach(function (v) {
                v.innerText = v.innerText.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
            });
        }
    }, [posts]);

    const getPagePost = async p => {
        let newPosts = await getPostsData(p);
        setPosts(newPosts.list);
    };

    const getPostsData = async p => {
        try {
            const { data } = await api.post(`/be/manager/point/used/sikwon_point/list`, p);
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
                        <EditFormTH className="col-span-1">결제일</EditFormTH>
                        <EditFormTD className="col-span-5">
                            <EditFormDateRange input_name="create_at" values={s.values?.create_at} errors={s.errors} handleChange={fn.handleChangeDateRange} />
                        </EditFormTD>

                        <EditFormTH className="col-span-1">결제상태</EditFormTH>
                        <EditFormTD className="col-span-5">
                            <EditFormRadioList
                                input_name="used_type"
                                values={s.values?.used_type}
                                filter_list={filter?.used_type}
                                errors={s.errors}
                                handleChange={fn.handleChange}
                            />
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
                    <div className="" onClick={() => fnExcelDownReason()}>
                        <button className="text-sm text-green-600">
                            <i className="far fa-file-excel me-1"></i> 엑셀다운로드
                        </button>
                    </div>
                </ListTableCaption>

                <ListTable>
                    <ListTableHead>
                        <th>고유번호</th>
                        <th>주문일자</th>
                        <th>결제상태</th>
                        <th style={{ width: '320px' }}>사유</th>
                        <th>이름</th>
                        <th>아이디</th>
                        <th>주문번호</th>
                        <th>사용포인트</th>
                        <th>환불포인트</th>
                    </ListTableHead>
                    <ListTableBody>
                        {posts?.map((v: any, i: number) => (
                            <tr key={`list-table-${i}`} className="">
                                <td className="text-center">{v.uid}</td>
                                <td className="text-center">{v.create_at}</td>
                                <td className="text-center">{v.used_type}</td>
                                <td className="text-center">{v.reason}</td>
                                <td className="text-center">{v.user_name}</td>
                                <td className="text-center">{v.user_id}</td>
                                <td className="text-center">{v.order_no}</td>
                                <td className="num2Cur">{checkNumeric(v.used_point)}원</td>
                                <td className="num2Cur">{checkNumeric(v.remaining_point)}원</td>
                            </tr>
                        ))}
                    </ListTableBody>
                </ListTable>

                <ListPagenation props={params} getPagePost={getPagePost} />
            </Layout>
            {excelModalOpen && (
                <ExcelModal setExcelModalOpen={setExcelModalOpen} params={params} url={'/be/manager/point/used/sikwon_point/xlsx/download'} title={'식권포인트사용내역'} />
            )}
        </>
    );
};

export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {};
    var response: any = {};
    try {
        const { data } = await api.post(`/be/manager/point/used/sikwon_point/init`, request);
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

export default PointUsedSikwonUsedList;
