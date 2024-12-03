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

const PointUsedCardList: NextPage = (props: any) => {
    const nav_id = 125;
    const crumbs = ['포인트 사용관리', '복지카드 사용내역'];
    const title_sub = '복지카드 사용내역을 확인할 수 있습니다.';
    const callout = [
        '복지카드를 사용내역 중 복지포인트로 차감완료/차감취소한 내역을 확인할 수 있습니다.',
        '사용내역이 없는 경우 조회되지 않습니다.',
        '소명승인 신청 건의 내역만 확인하고 싶은 경우에는 복지포인트관리 > 소명신청관리 > 소명승인에서 확인 가능합니다.',
        '온라인 복지몰에서 복지포인트로 바로 차감-결제한 내역은 조회되지 않습니다. ',
        '온라인 복지몰 사용내역만 확인하고 싶은 경우 복지포인트관리 > 복지포인트 사용관리 > 복지몰 포인트 사용내역에서 확인 가능합니다',
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
            const { data } = await api.post(`/be/manager/point/used/card/list`, p);
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
                        <EditFormTH className="col-span-1">조회기간 (차감승인일)</EditFormTH>
                        <EditFormTD className="col-span-5">
                            <EditFormDateRange input_name="create_at" values={s.values?.create_at} errors={s.errors} handleChange={fn.handleChangeDateRange} />
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

                <div className="hidden">검색 결과 처리상태 값/비고란 참조</div>
                <div className="shadow mb-5 border hidden">
                    <div className="bd-callout-info text-sm">
                        {[
                            '처리상태-차감완료 / 비고란-공란 : 복지카드 사용 건을 차감신청 후 차감 완료된 내역.',
                            '처리상태-차감완료 / 비고란-소명승인완료 : 복지카드 사용 건을 소명신청 후 소명 승인 완료되어 포인트 차감된 내역.',
                            '처리상태-차감취소 / 비고란-차감취소 : 복지카드 사용 건 차감신청 후 신청 월 내에 차감신청 취소한 내역.',
                            '처리상태-차감취소 / 비고란-결제취소 : 복지카드 소명승인 완료된 건을 가맹점 카드 결제 취소한 내역. ',
                        ].map((v: any, i: number) => (
                            <div className="bd-callout-item text-slate-600" key={`callout-${i}`} dangerouslySetInnerHTML={{ __html: v }}></div>
                        ))}
                    </div>
                </div>

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

                {/* <div>※ 조회한 기간 내 최종 사용 포인트 합계가 표시됩니다.</div>
            <EditFormTable className="grid-cols-6 mb-5">
                <EditFormTH className="col-span-1">조회기간</EditFormTH>
                <EditFormTD className="col-span-2">2024-01-01 ~ 2024-01-31</EditFormTD>
                <EditFormTH className="col-span-1">복지포인트 사용 합계</EditFormTH>
                <EditFormTD className="col-span-2">18,000원</EditFormTD>
            </EditFormTable> */}

                <ListTable>
                    <ListTableHead>
                        <th>이름</th>
                        <th>생년월일</th>
                        <th>부서</th>
                        <th>직급</th>
                        <th>차감/소명 신청일</th>
                        <th>포인트차감 승인일</th>
                        <th>사용내역</th>
                        <th>포인트 차감금액</th>
                        <th>카드</th>
                        <th>처리상태</th>
                        <th>비고</th>
                    </ListTableHead>
                    <ListTableBody>
                        {posts?.map((v: any, i: number) => (
                            <tr key={`list-table-${i}`} className="">
                                <td className="text-center">{v.user_name}</td>
                                <td className="text-center">{v.birth}</td>
                                <td className="text-center">{v.depart}</td>
                                <td className="text-center">{v.position}</td>
                                <td className="text-center">{v.create_at}</td>
                                <td className="text-center">{v.confirm_at}</td>
                                <td className="text-center">{v.detail}</td>
                                <td className="num2Cur">{checkNumeric(v.confirm_point)}원</td>
                                <td className="text-center">{v.card}</td>
                                <td className="text-center">{v.state}</td>
                                <td className="text-center">{v.note}</td>
                            </tr>
                        ))}
                    </ListTableBody>
                </ListTable>

                <ListPagenation props={params} getPagePost={getPagePost} />
            </Layout>
            {excelModalOpen && (
                <ExcelModal setExcelModalOpen={setExcelModalOpen} params={params} url={'/be/manager/point/used/bokji/card/xlsx/download'} title={'복지카드사용내역'} />
            )}
        </>
    );
};

export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {
        use_type: 'bokji',
    };
    var response: any = {};
    try {
        const { data } = await api.post(`/be/manager/point/used/card/init`, request);
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

export default PointUsedCardList;
