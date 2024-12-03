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

const PointLimitCard: NextPage = (props: any) => {
    const nav_id = 127;
    const crumbs = ['포인트 사용제한', '복지카드 허용 업종 조회'];
    const title_sub = '';
    const callout = [
        '복지카드 사용 건을 포인트로 차감신청 가능한 복지 허용 업종을 확인할 수 있습니다. ',
        '업종코드 및 표준산업분류코드는 홈텍스를 기준으로 합니다. ',
        '복지카드 허용 업종 수정요청은 공지/문의 > 문의하기에서 가능합니다.',
        '해당 페이지에서 조회되는 복지카드 허용 업종 리스트는 사용자 시스템의 포인트차감 > 소명신청 > 상단의  ‘복지카드 허용항목’ 버튼을 눌러 나오는 항목과 동일합니다.',
    ];
    const router = useRouter();

    const [filter, setFilter] = useState<any>({});
    const [params, setParams] = useState<any>({});
    const [posts, setPosts] = useState<any>([]);

    useEffect(() => {
        props.response.params.filters.type = 'card';
        setFilter(props.response.filter);
        setParams(props.response.params);
        s.setValues(props.response.params.filters);
        getPagePost(props.response.params);
    }, []);

    const getPagePost = async p => {
        let copy: any = {};
        if (JSON.stringify({ ...s.values }) != '{}') {
            copy = { ...s.values };
            copy.checked = [];
            s.setValues(copy);
        } else {
            copy = { ...props.response.params.filters };
        }

        let newPosts = await getPostsData(p);
        setPosts(newPosts.list);
    };

    const getPostsData = async p => {
        try {
            const { data } = await api.post(`/be/manager/point/limit/card/list`, p);
            setParams(data.params);
            return data;
        } catch (e: any) {}
    };

    const { s, fn } = useForm({
        onSubmit: async () => {
            await searching();
        },
    });

    const fnEditcode = async (mode: string) => {
        try {
            if (s.values.checked.length == 0) {
                alert('선택된 업종이 없습니다.');
                return;
            }

            if (mode == 'REG') {
                let confirm_msg = '선택 업종코드를 허용 하시겠습니까 ? ';
                if (!confirm(confirm_msg)) {
                    return;
                }
            } else {
                let confirm_msg = '선택 업종코드를 제외 하시겠습니까 ? ';
                if (!confirm(confirm_msg)) {
                    return;
                }
            }

            const edit_params = {
                uids: s.values.checked,
                mode: mode,
            };

            const { data } = await api.post(`/be/manager/point/limit/card/edit`, edit_params);
            s.setSubmitting(false);
            if (data.code == 200) {
                alert(data.msg);
                let copy = { ...s.values };
                copy.checked = [];
                s.setValues(copy);
                params.filters = s.values;
                let newPosts = await getPostsData(params);
                setPosts(newPosts.list);
            } else {
                alert(data.msg);
            }
        } catch (e: any) {}
    };

    const searching = async () => {
        let copy = { ...s.values };
        copy.checked = [];
        s.setValues(copy);
        params.filters = s.values;
        params.page = 1;
        let newPosts = await getPostsData(params);
        setPosts(newPosts.list);
    };

    const fnAllChecked = el => {
        let params = { ...s.values.checked };
        params = [];
        if (el.target.checked) {
            posts.map((v: any) => {
                params.push(v.uid);
            });
        }
        s.setValues({ ...s.values, checked: params });
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
                        <EditFormTH className="col-span-1">허용여부</EditFormTH>
                        <EditFormTD className="col-span-5">
                            <EditFormRadioList input_name="yn" values={s.values?.yn} filter_list={filter?.yn} errors={s.errors} handleChange={fn.handleChange} />
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

                    <div className="flex gap-4">
                        <button onClick={() => fnEditcode('REG')} className="text-sm text-blue-600 me-2">
                            <i className="far fa-plus-square me-2"></i>선택업종 {s.values?.checked.length}개 허용
                        </button>
                        <button onClick={() => fnEditcode('DEL')} className="text-sm text-red-600 me-2">
                            <i className="far fa-plus-square me-2"></i>선택업종 {s.values?.checked.length}개 제외
                        </button>
                    </div>
                    <div className="" onClick={() => fnExcelDownReason()}>
                        <button className="text-sm text-green-600">
                            <i className="far fa-file-excel me-1"></i> 엑셀다운로드
                        </button>
                    </div>
                </ListTableCaption>

                <ListTable>
                    <ListTableHead>
                        <th className="label-wrap">
                            <label>
                                <input
                                    id="all_check"
                                    type="checkbox"
                                    name="all_check"
                                    onClick={e => {
                                        fnAllChecked(e);
                                    }}
                                />
                            </label>
                        </th>
                        <th>업종명</th>
                        <th>업종코드</th>
                        <th>복지카드허용여부</th>
                        <th>최근허용일</th>
                    </ListTableHead>
                    <ListTableBody>
                        {posts?.map((v: any, i: number) => (
                            <tr key={`list-table-${i}`} className="">
                                <td className="text-center label-wrap">
                                    <label>
                                        <input
                                            id={`checked-${i}`}
                                            checked={s.values?.checked.filter(p => p == v.uid) == checkNumeric(v.uid) ? true : false}
                                            onChange={fn.handleCheckboxGroupForInteger}
                                            type="checkbox"
                                            value={v.uid}
                                            name="checked"
                                        />
                                    </label>
                                </td>
                                <td className="text-start">{v.name}</td>
                                <td className="text-center">{v.code}</td>
                                <td className="text-center">{v.create_at == null ? '제한' : '허용'}</td>
                                <td className="text-center">{v.create_at}</td>
                            </tr>
                        ))}
                    </ListTableBody>
                </ListTable>

                <ListPagenation props={params} getPagePost={getPagePost} />
            </Layout>
            {excelModalOpen && (
                <ExcelModal setExcelModalOpen={setExcelModalOpen} params={params} url={'/be/manager/point/limit/card/xlsx/download'} title={'복지카드허용업종내역'} />
            )}
        </>
    );
};

export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {};
    var response: any = {};
    try {
        const { data } = await api.post(`/be/manager/point/limit/card/init`, request);
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

export default PointLimitCard;
