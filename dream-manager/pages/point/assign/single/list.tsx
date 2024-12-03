import type { GetServerSideProps, NextPage } from 'next';
import React, { useEffect, useState } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import useForm from '@/components/form/useForm';
import Status from '@/pages/point/status';

import { EditForm, EditFormTable, EditFormTH, EditFormTD, EditFormKeyword, EditFormSubmitSearch, EditFormRadioList } from '@/components/UIcomponent/form/EditFormA';

import { ListTable, ListTableHead, ListTableBody, ListTableCaption, Callout } from '@/components/UIcomponent/table/ListTableA';
import { checkNumeric, cls } from '@/libs/utils';
import ListPagenation from '@/components/bbs/ListPagenation';
import ExcelModal from '@/components/modal/excel';
const PointAssignSingleList: NextPage = (props: any) => {
    const nav_id = 59;
    const crumbs = ['포인트 지급관리', '복지 포인트 개별 지급'];
    const title_sub = '복지포인트 지급 및 회수 내역을 확인할 수 있습니다.';
    const callout = [];
    const router = useRouter();

    const [isCallback, setIsCallback] = useState<any>(false);
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
            const { data } = await api.post(`/be/manager/point/assign/single/list`, p);
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

    const goEdit = (save_type: number) => {
        if (s.values.checked.length == 0) {
            alert('지급/회수할 회원을 선택해 주세요');
            return;
        }

        var newForm = document.createElement('form');
        newForm.setAttribute('method', 'POST');

        var newInput = document.createElement('input');
        newInput.setAttribute('type', 'hidden');
        newInput.setAttribute('name', 'user_uids');
        newInput.setAttribute('value', s.values.checked.join(','));
        newForm.appendChild(newInput);

        document.body.appendChild(newForm);

        var objPopup = window.open('', '개별복지포인트지급', 'width=1120, height=800, scrollbars=no, toolbar=no, status=no, resizable=no');
        newForm.target = '개별복지포인트지급'; // 타겟 : 위의 창띄우기의 창이름과 같아야 한다.
        newForm.action = `/point/assign/single/edit?save_type=${save_type}`; // 액션경로
        if (objPopup == null) alert('차단된 팝업창을 허용해 주세요'); // 팝업이 뜨는지 확인
        else {
            newForm.submit();
            objPopup.focus(); //새로 띄워준 창에 포커스를 맞춰준다.
        }

        (window as any).assign_callback = async (data: any) => {
            // 라우터 새로고침 시키고
            router.reload();
            setIsCallback(true);
            // await searching();
            // fn_vaild_encdata('fail', data);
        };
    };

    useEffect(() => {
        if (isCallback) {
            searching();
            setIsCallback(false);
        }
    }, [isCallback]);

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
                <Status point_type={'bokji'} />
                <EditForm onSubmit={fn.handleSubmit}>
                    <EditFormTable className="grid-cols-6">
                        <EditFormTH className="col-span-1">포인트 사용상태</EditFormTH>
                        <EditFormTD className="col-span-2">
                            <EditFormRadioList input_name="is_point" values={s.values?.is_point} filter_list={filter.is_point} errors={s.errors} handleChange={fn.handleChange} />
                        </EditFormTD>
                        <EditFormTH className="col-span-1">재직여부</EditFormTH>
                        <EditFormTD className="col-span-2">
                            <EditFormRadioList input_name="serve" values={s.values?.serve} filter_list={filter.serve} errors={s.errors} handleChange={fn.handleChange} />
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
                        <button
                            onClick={() => {
                                goEdit(2);
                            }}
                            className="text-sm text-blue-600 me-2"
                        >
                            <i className="far fa-plus-square me-2"></i>선택회원 {s.values?.checked.length}명 지급
                        </button>
                        <button
                            onClick={() => {
                                goEdit(3);
                            }}
                            className="text-sm text-red-600 me-2"
                        >
                            <i className="far fa-plus-square me-2"></i>선택회원 {s.values?.checked.length}명 회수
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
                        <th>이름</th>
                        <th>아이디</th>
                        <th>부서</th>
                        <th>직급/직책</th>
                        <th>
                            지급완료
                            <br />
                            포인트
                        </th>
                        <th>
                            회수완료
                            <br />
                            포인트
                        </th>
                        <th>
                            사용완료
                            <br />
                            포인트
                        </th>
                        <th>
                            잔여
                            <br />
                            포인트
                        </th>
                        <th>
                            포인트
                            <br />
                            사용상태
                        </th>
                        <th>재직여부</th>
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
                                <td className="text-center">{v.user_name}</td>
                                <td className="text-center">{v.login_id}</td>
                                <td className="text-center">{v.depart}</td>
                                <td className="text-center">
                                    {v.position}
                                    {v.position && v.position2 && '/'}
                                    {v.position2}
                                </td>
                                <td className="num2Cur">{checkNumeric(v.saved_point)}원</td>
                                <td className="num2Cur">{checkNumeric(v.return_point)}원</td>
                                <td className="num2Cur">{checkNumeric(v.used_point)}원</td>
                                <td className="num2Cur">{checkNumeric(v.spare_point)}원</td>
                                <td className="text-center">
                                    <span className={cls(v.is_point == '불가능' ? 'text-red-500' : '')}>{v.is_point}</span>
                                </td>
                                <td className="text-center">{v.serve}</td>
                            </tr>
                        ))}
                    </ListTableBody>
                </ListTable>

                <ListPagenation props={params} getPagePost={getPagePost} />
            </Layout>
            {excelModalOpen && (
                <ExcelModal setExcelModalOpen={setExcelModalOpen} params={params} url={'/be/manager/point/assign/single/xlsx/download'} title={'복지포인트개별지급내역'} />
            )}
        </>
    );
};

export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {};
    var response: any = {};
    try {
        const { data } = await api.post(`/be/manager/point/assign/single/init`, request);
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

export default PointAssignSingleList;
