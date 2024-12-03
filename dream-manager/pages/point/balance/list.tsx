import type { GetServerSideProps, NextPage } from 'next';
import React, { useEffect, useState } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import useForm from '@/components/form/useForm';
import Layout from '@/components/Layout';
import { checkNumeric, cls } from '@/libs/utils';

import ListPagenation from '@/components/bbs/ListPagenation';

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
import PointBalanceReg from './reg';
import PointBalanceFin from './fin';
import { numToKorean } from 'num-to-korean';
import Status from '../status';
import ExcelModal from '@/components/modal/excel';

const PointBalanceList: NextPage = (props: any) => {
    const nav_id = 57;
    const crumbs = ['포인트 지급관리', '예치금 충전관리'];
    const title_sub = '포인트 지급을 위한 예치금을 충전/관리 합니다';
    const callout = [
        '입금은행과 입금자명은 <span class="text-red-500">반드시 일치해야합니다.</span> ',
        '최대 5분 이내 입금사실이 적용됩니다.',
        '오류 또는 입금은행/입금자명 불일치로 인해 적용이 안되면, 문의하기를 통해 문의 남겨주시기 바랍니다.',
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
            const { data } = await api.post(`/be/manager/point/balance/list`, p);
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

    const [open_fin, set_open_fin] = useState<any>(false);
    const callback_point_balance_reg = () => {
        set_open_fin(true);
    };

    const [balanceInfo, setBalanceInfo] = useState<any>();
    const getDataValue = (data: any) => {
        setBalanceInfo(data);
    };

    const reload_page = () => {
        router.reload();
    };

    const [excelModalOpen, setExcelModalOpen] = useState<boolean>(false);
    const fnExcelDownReason = async () => {
        setExcelModalOpen(true);
    };

    return (
        <>
            <Layout nav_id={nav_id} crumbs={crumbs} title={crumbs[crumbs.length - 1]} user={props.user}>
                <Callout title={crumbs[crumbs.length - 1]} title_sub={title_sub} callout={callout} />
                <Status point_type={'bokji'} />
                <EditForm onSubmit={fn.handleSubmit}>
                    <EditFormTable className="grid-cols-6">
                        <EditFormTH className="col-span-1">등록일조회</EditFormTH>
                        <EditFormTD className="col-span-2">
                            <EditFormDateRange input_name="create_at" values={s.values?.create_at} errors={s.errors} handleChange={fn.handleChangeDateRange} />
                        </EditFormTD>
                        <EditFormTH className="col-span-1">처리상태</EditFormTH>
                        <EditFormTD className="col-span-2">
                            <EditFormRadioList
                                input_name="input_state"
                                values={s.values?.input_state}
                                filter_list={filter.input_state}
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
                    <div className="flex items-center gap-3">
                        <PointBalanceReg callback={callback_point_balance_reg} getDataValue={getDataValue} />
                        <PointBalanceFin open={open_fin} setOpen={set_open_fin} balanceInfo={balanceInfo} reload_page={reload_page} />

                        <div className="" onClick={() => fnExcelDownReason()}>
                            <button className="text-sm text-green-600">
                                <i className="far fa-file-excel me-1"></i> 엑셀다운로드
                            </button>
                        </div>
                    </div>
                </ListTableCaption>

                <ListTable>
                    <ListTableHead>
                        <th>신청일</th>
                        <th>신청복지포인트</th>
                        <th>입금은행</th>
                        <th>입금자명</th>
                        <th>입금액</th>
                        <th>입금일</th>
                        <th style={{ width: '300px' }}>입금메모</th>
                        <th>처리상태</th>
                        <th>확인증</th>
                    </ListTableHead>
                    <ListTableBody>
                        {posts?.map((v: any, i: number) => (
                            <tr key={`list-table-${i}`} className="">
                                <td className="text-center">{v.create_at}</td>
                                <td className="num2Cur">{checkNumeric(v.save_point)}</td>
                                <td className="text-center">{v.input_bank}</td>
                                <td className="text-center">{v.input_name}</td>
                                <td className="num2Cur">{checkNumeric(v.sum_of_pmoney)}원</td>
                                <td className="text-center">{v.max_of_at}</td>
                                <td className="">{v.reason}</td>
                                <td className="">{v.input_state}</td>
                                <td className=""></td>
                            </tr>
                        ))}
                    </ListTableBody>
                </ListTable>

                <ListPagenation props={params} getPagePost={getPagePost} />
            </Layout>
            {excelModalOpen && <ExcelModal setExcelModalOpen={setExcelModalOpen} params={params} url={'/be/manager/point/balance/xlsx/download'} title={'예치금충전내역'} />}
        </>
    );
};

export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {};
    var response: any = {};
    try {
        const { data } = await api.post(`/be/manager/point/balance/init`, request);
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

export default PointBalanceList;
