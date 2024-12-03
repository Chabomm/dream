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
import ExcelModal from '@/components/modal/excel';

const PointExuseRemainingList: NextPage = (props: any) => {
    const nav_id = 131;
    const crumbs = ['소명신청 관리', '환급내역'];
    const title_sub = '';
    const callout = [
        '복지카드 차감신청/소명신청한 건 중 차감승인 완료된 건들의 환급일/환급금액을 확인할 수 있습니다.',
        '환급(입금)예정내역이 없으면 조회되지 않습니다.',
        '차감승인 완료된 금액은 지정계좌로 환급(입금)처리 됩니다.',
        '자세한 사용내역은 복지포인트 사용관리 > 복지카드 포인트 사용내역에서 조회 가능합니다.',
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
            const { data } = await api.post(`/be/manager/point/exuse/remaining/list`, p);
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
                        <EditFormTH className="col-span-1">환급일</EditFormTH>
                        <EditFormTD className="col-span-2">
                            <EditFormDateRange input_name="remaining_at" values={s.values?.remaining_at} errors={s.errors} handleChange={fn.handleChangeDateRange} />
                        </EditFormTD>
                        <EditFormTH className="col-span-1">차감승인일</EditFormTH>
                        <EditFormTD className="col-span-2">
                            <EditFormDateRange input_name="confirm_at" values={s.values?.confirm_at} errors={s.errors} handleChange={fn.handleChangeDateRange} />
                        </EditFormTD>
                        <EditFormTH className="col-span-1">처리상태</EditFormTH>
                        <EditFormTD className="col-span-5">
                            <EditFormRadioList input_name="state" values={s.values?.state} filter_list={filter?.state} errors={s.errors} handleChange={fn.handleChange} />
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
                        <th>이름</th>
                        <th>생년월일</th>
                        <th>부서</th>
                        <th>직급</th>
                        <th>사용내역</th>
                        <th>차감승인일</th>
                        <th>환급일</th>
                        <th>입금(예정)금액</th>
                        <th>카드</th>
                        <th>입금은행</th>
                        <th>입금계좌번호</th>
                        <th>처리상태</th>
                    </ListTableHead>
                    <ListTableBody>
                        {posts?.map((v: any, i: number) => (
                            <tr key={`list-table-${i}`} className="">
                                <td className="text-center">{v.user_name}</td>
                                <td className="text-center">{v.birth}</td>
                                <td className="text-center">{v.depart}</td>
                                <td className="text-center">{v.position}</td>
                                <td className="text-center">{v.detail}</td>
                                <td className="text-center">{v.confirm_at}</td>
                                <td className="text-center">{v.remaining_at}</td>
                                <td className="text-center">{v.input_amount}</td>
                                <td className="text-center">{v.card}</td>
                                <td className="text-center">{v.input_bank}</td>
                                <td className="text-center">{v.input_bank_num}</td>
                                <td className="text-center">{v.state}</td>
                            </tr>
                        ))}
                    </ListTableBody>
                </ListTable>

                <ListPagenation props={params} getPagePost={getPagePost} />
            </Layout>
            {excelModalOpen && <ExcelModal setExcelModalOpen={setExcelModalOpen} params={params} url={'/be/manager/point/exuse/remaining/xlsx/download'} title={'환급내역'} />}
        </>
    );
};

export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {};
    var response: any = {};
    try {
        const { data } = await api.post(`/be/manager/point/exuse/remaining/init`, request);
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

export default PointExuseRemainingList;
