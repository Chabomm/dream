import type { GetServerSideProps, NextPage } from 'next';
import React, { useEffect, useState } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import ConfirmStateEdit from '@/components/modal/confirmStateEdit';

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
import { checkNumeric, cls } from '@/libs/utils';
import ExcelModal from '@/components/modal/excel';

const PointExuseConfirmList: NextPage = (props: any) => {
    const nav_id = 130;
    const crumbs = ['소명신청 관리', '소명승인'];
    const title_sub = '복지카드 사용 건 중 소명신청한 내역 확인 및 승인(포인트 차감)처리 또는 미승인(포인트 차감 반려)처리할 수 있습니다.';
    const callout = [
        '복지항목에 적합한 소명신청 건은 승인(포인트 차감) 처리, 부적합한 소명신청 건은 미승인(포인트차감 반려)처리할 수 있습니다.',
        '승인(포인트 차감) 처리 완료된 건을 ‘소명승인 취소’를 통해 미승인(포인트차감 반려) 처리로 변경할 수 있습니다.',
        '미승인 처리(포인트차감 반려)된 건을 ‘재차감 설정’을 통해 사용자가 다시 소명 신청 진행할 수 있도록 변경할 수 있습니다. (단, 카드 사용일로부터 90일 이내의 건만 소명신청 가능)',
        '미승인 처리(포인트차감 반려)된 건을 ‘소명신청 전환’ 을 통해 최초 소명신청한 상태로 돌려 다시 승인(포인트 차감)처리할 수 있습니다.',
        '소명승인 또는 미승인처리 시 결과 내용을 신청자에게 메일 전송할 수 있습니다. ',
        '복수 선택 후 일괄 처리가 가능합니다.',
        '사용내역 항목에 마우스를 올려 놓으면 상세 사용내역 확인이 가능합니다.',
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
            const { data } = await api.post(`/be/manager/point/exuse/confirm/list`, p);
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
        // s.setValues({ ...s.values, checked: [] });
    };

    const StateButton = props => {
        const [state, setState] = useState(props.state);

        switch (state) {
            case '소명신청':
                return (
                    <>
                        <button className="text-sm text-blue-600" onClick={() => openConfirmEdit('소명승인완료')}>
                            <i className="far fa-plus-square me-1"></i> 선택항목 승인
                        </button>
                        <button className="text-sm text-blue-600" onClick={() => openConfirmEdit('미승인(반려)')}>
                            <i className="far fa-plus-square me-1"></i> 선택항목 미승인
                        </button>
                    </>
                );
            case '소명승인완료':
                return (
                    <>
                        <button className="text-sm text-blue-600" onClick={() => openConfirmEdit('소명신청 전환')}>
                            <i className="far fa-plus-square me-1"></i> 선택항목 승인취소
                        </button>
                    </>
                );
            case '미승인(반려)':
                return (
                    <>
                        <button className="text-sm text-blue-600" onClick={() => openConfirmEdit('소명신청')}>
                            <i className="far fa-plus-square me-1"></i> 소명신청 전환
                        </button>
                        <button className="text-sm text-blue-600" onClick={() => openConfirmEdit('재차감 설정')}>
                            <i className="far fa-plus-square me-1"></i> 재차감 설정
                        </button>
                    </>
                );
            case '':
                return (
                    <>
                        <button className="text-sm text-blue-600" onClick={() => openConfirmEdit('소명승인완료')}>
                            <i className="far fa-plus-square me-1"></i> 선택항목 승인
                        </button>
                        <button className="text-sm text-blue-600" onClick={() => openConfirmEdit('미승인(반려)')}>
                            <i className="far fa-plus-square me-1"></i> 선택항목 미승인
                        </button>
                        <button className="text-sm text-blue-600" onClick={() => openConfirmEdit('미승인(반려)')}>
                            <i className="far fa-plus-square me-1"></i> 선택항목 승인취소
                        </button>
                        <button className="text-sm text-blue-600" onClick={() => openConfirmEdit('소명신청')}>
                            <i className="far fa-plus-square me-1"></i> 소명신청 전환
                        </button>
                        <button className="text-sm text-blue-600" onClick={() => openConfirmEdit('재차감 설정')}>
                            <i className="far fa-plus-square me-1"></i> 재차감 설정
                        </button>
                    </>
                );
            default:
                return null;
        }
    };

    // [ S ] 상태변경 모달
    const [confirmEditOpen, setConfirmEditOpen] = useState(false);
    const [stateInfo, setStateInfo] = useState<any>();
    const openConfirmEdit = (state: string) => {
        setConfirmEditOpen(true);
        setStateInfo({
            state,
            uid: s.values.checked,
        });
    };
    // [ E ] 상태변경 모달

    const goEdit = (item: any) => {
        window.open(`/point/exuse/confirm/edit?uid=${item.uid}`, '소명승인 상세', 'width=1500,height=800, location=no,status=no,scrollbars=yes,left=200%,top=50%');
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
                        <EditFormTH className="col-span-1">카드결제일</EditFormTH>
                        <EditFormTD className="col-span-5">
                            <EditFormDateRange input_name="pay_at" values={s.values?.pay_at} errors={s.errors} handleChange={fn.handleChangeDateRange} />
                        </EditFormTD>
                        <EditFormTH className="col-span-1">소명신청일</EditFormTH>
                        <EditFormTD className="col-span-5">
                            <EditFormDateRange input_name="create_at" values={s.values?.create_at} errors={s.errors} handleChange={fn.handleChangeDateRange} />
                        </EditFormTD>
                        <EditFormTH className="col-span-1">처리완료일</EditFormTH>
                        <EditFormTD className="col-span-5">
                            <EditFormDateRange input_name="confirm_at" values={s.values?.confirm_at} errors={s.errors} handleChange={fn.handleChangeDateRange} />
                        </EditFormTD>
                        <EditFormTH className="col-span-1">결제취소일</EditFormTH>
                        <EditFormTD className="col-span-5">
                            <EditFormDateRange input_name="pay_cancel_at" values={s.values?.pay_cancel_at} errors={s.errors} handleChange={fn.handleChangeDateRange} />
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
                        <th>번호</th>
                        <th>이름</th>
                        <th>생년월일</th>
                        <th>부서</th>
                        <th>직급</th>
                        <th>카드 결제일</th>
                        <th>포인트종류</th>
                        <th>소명신청일</th>
                        <th>업종명</th>
                        <th>사용내역</th>
                        <th>결제금액</th>
                        <th>차감신청금액</th>
                        <th>처리상태</th>
                        <th>처리완료일</th>
                        <th>결제취소일</th>
                    </ListTableHead>
                    <ListTableBody>
                        {posts?.map((v: any, i: number) => (
                            <tr key={`list-table-${i}`} className="">
                                <td className="text-center">{v.uid}</td>
                                <td className="text-center">{v.user_name}</td>
                                <td className="text-center">{v.birth}</td>
                                <td className="text-center">{v.depart}</td>
                                <td className="text-center">{v.position}</td>
                                <td className="text-center">{v.pay_at}</td>
                                {v.point_type == null ? (
                                    <td className="text-center">{v.point_type}</td>
                                ) : (
                                    <>
                                        {v.point_type == '식권포인트' ? (
                                            <td className="text-center" style={{ color: '#51c1be' }}>
                                                {v.point_type}
                                            </td>
                                        ) : (
                                            <td className="text-center" style={{ color: '#496cef' }}>
                                                {v.point_type}
                                            </td>
                                        )}
                                    </>
                                )}
                                <td className="text-center">{v.create_at}</td>
                                <td className="text-center">{v.biz_item}</td>
                                <td className="text-center">
                                    <span
                                        onClick={() => {
                                            goEdit(v);
                                        }}
                                    >
                                        <i className="fas fa-external-link-alt me-1"></i>
                                        {v.detail}
                                    </span>
                                </td>
                                <td className="num2Cur">{checkNumeric(v.pay_amount)}원</td>
                                <td className="num2Cur">{checkNumeric(v.exuse_amount)}원</td>
                                <td className="text-center">{v.state}</td>
                                <td className="text-center">{v.confirm_at}</td>
                                <td className="text-center">{v.pay_cancel_at}</td>
                            </tr>
                        ))}
                    </ListTableBody>
                </ListTable>

                <ListPagenation props={params} getPagePost={getPagePost} />
                {confirmEditOpen && <ConfirmStateEdit setConfirmEditOpen={setConfirmEditOpen} stateInfo={stateInfo} />}
            </Layout>
            {excelModalOpen && <ExcelModal setExcelModalOpen={setExcelModalOpen} params={params} url={'/be/manager/point/exuse/confirm/xlsx/download'} title={'소명승인내역'} />}
        </>
    );
};

export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {};
    var response: any = {};
    try {
        const { data } = await api.post(`/be/manager/point/exuse/confirm/init`, request);
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

export default PointExuseConfirmList;
