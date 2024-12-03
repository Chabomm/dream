import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import { cls, checkNumeric } from '@/libs/utils';
import useForm from '@/components/form/useForm';
import Datepicker from 'react-tailwindcss-datepicker';

import {
    EditForm,
    EditFormTable,
    EditFormTH,
    EditFormTD,
    EditFormRadioList,
    EditFormSubmit,
    EditFormInput,
    EditFormLabel,
    EditFormAddr,
    EditFormInputGroup,
    EditFormDate,
    EditFormTextarea,
    EditFormCard,
    EditFormCardHead,
    EditFormCardBody,
} from '@/components/UIcomponent/form/EditFormA';
import EditFormCallout from '@/components/UIcomponent/form/EditFormCallout';
import LayoutPopup from '@/components/LayoutPopup';

const CounselEdit: NextPage = (props: any) => {
    const crumbs = ['구축관리', '상담신청 ' + (props.response.values?.uid > 0 ? '수정' : '등록')];
    const callout = [];
    const title_sub = '복지목 구축 상담신청 등록/수정을 할 수 있습니다';
    const router = useRouter();

    const [memo, setMemo] = useState<any>([]);
    const [posts, setPosts] = useState<any>({});
    const [filter, setFilter] = useState<any>({});

    useEffect(() => {
        if (props) {
            if (props.response.code == 200) {
                setPosts(props.response);
                setFilter(props.response.filter);
                s.setValues(props.response.values);
                setMemo(props.response.memo_list);
            } else {
                alert(props.response.msg);
                window.close();
            }
        }
    }, []);

    const { s, fn, attrs } = useForm({
        onSubmit: async () => {
            await editing('REG');
        },
    });

    const deleting = () => editing('DEL');

    const editing = async mode => {
        try {
            const params = { ...s.values };

            if (mode == 'REG' && params.uid > 0) {
                mode = 'MOD';
            }

            params.mode = mode;
            params.wish_build_at = params.wish_build_at?.startDate;
            const { data } = await api.post(`/be/admin/entry/counsel/edit`, params);
            s.setSubmitting(false);
            if (data.code == 200) {
                alert(data.msg);
                router.reload();
            } else {
                alert(data.msg);
            }
        } catch (e: any) {}
    };

    let entry_domain = `http://localhost:13020`;
    if (`${process.env.NODE_ENV}` == 'production') {
        entry_domain = `https://`;
    }
    const goBuild = (item: any) => {
        window.open(`${entry_domain}/dream/build?uid=${item.uid}`, '수기 구축정보 등록', 'width=1120,height=800,location=no,status=no,scrollbars=yes');
    };

    return (
        <LayoutPopup title={crumbs[crumbs.length - 1]} className="px-6 bg-slate-50">
            <EditFormCallout title={crumbs[crumbs.length - 1]} title_sub={title_sub} callout={callout} />

            {process.env.NODE_ENV == 'development' && (
                <pre className="">
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <div className="font-bold mb-3 text-red-500">filter</div>
                            {JSON.stringify(filter, null, 4)}
                        </div>
                        <div className="hidden">
                            <div className="font-bold mb-3 text-red-500">memo</div>
                            {JSON.stringify(memo, null, 4)}
                        </div>
                        <div>
                            <div className="font-bold mb-3 text-red-500">s.values</div>
                            {JSON.stringify(s.values, null, 4)}
                        </div>
                        <div className="hidden">
                            <div className="font-bold mb-3 text-red-500">posts</div>
                            {JSON.stringify(posts, null, 4)}
                        </div>
                    </div>
                </pre>
            )}

            <EditForm onSubmit={fn.handleSubmit}>
                <EditFormCard>
                    <EditFormCardHead>
                        <div className="text-lg">진행상태</div>
                    </EditFormCardHead>
                    <EditFormCardBody>
                        <EditFormTable className="grid-cols-6">
                            <EditFormTH className="col-span-1 mand">진행상태</EditFormTH>
                            <EditFormTD className="col-span-5">
                                <EditFormRadioList
                                    input_name="state"
                                    values={s.values?.state}
                                    filter_list={filter.state}
                                    is_mand={true}
                                    errors={s.errors}
                                    handleChange={fn.handleChange}
                                />
                            </EditFormTD>
                            <EditFormTH className="col-span-1">구축신청URL</EditFormTH>
                            <EditFormTD className="col-span-5">
                                {(posts?.state == '501' || posts?.state == '502') && (
                                    <EditFormLabel className="">
                                        <div
                                            onClick={() => {
                                                goBuild({ uid: s.values?.uid });
                                            }}
                                        >
                                            {entry_domain}/dream/build?uid={s.values?.uid}
                                            <i className="fas fa-external-link-alt ms-1"></i>
                                        </div>
                                    </EditFormLabel>
                                )}
                            </EditFormTD>
                            <EditFormTH className="col-span-1">상담신청일</EditFormTH>
                            <EditFormTD className="col-span-2">
                                <EditFormLabel className="">{posts?.create_at}</EditFormLabel>
                            </EditFormTD>
                            <EditFormTH className="col-span-1">최근수정일</EditFormTH>
                            <EditFormTD className="col-span-2">
                                <EditFormLabel className="">{posts?.update_at}</EditFormLabel>
                            </EditFormTD>
                        </EditFormTable>
                    </EditFormCardBody>
                </EditFormCard>

                <EditFormCard>
                    <EditFormCardHead>
                        <div className="text-lg">신청정보</div>
                    </EditFormCardHead>
                    <EditFormCardBody>
                        <EditFormTable className="grid-cols-6">
                            <EditFormTH className="col-span-1 mand">회사명</EditFormTH>
                            <EditFormTD className="col-span-2">
                                <EditFormInput
                                    type="text"
                                    name="company_name"
                                    value={s.values?.company_name || ''}
                                    is_mand={true}
                                    placeholder={'회사명을 입력하세요'}
                                    onChange={fn.handleChange}
                                    errors={s.errors}
                                    className=""
                                />
                            </EditFormTD>
                            <EditFormTH className="col-span-1">회사홈페이지(url)</EditFormTH>
                            <EditFormTD className="col-span-2">
                                <EditFormInput
                                    type="text"
                                    name="homepage_url"
                                    value={s.values?.homepage_url || ''}
                                    onChange={fn.handleChange}
                                    placeholder={'http로 시작하는 전체 주소'}
                                    errors={s.errors}
                                    className=""
                                />
                            </EditFormTD>
                            <EditFormTH className="col-span-1">임직원수</EditFormTH>
                            <EditFormTD className="col-span-2">
                                <EditFormInput
                                    type="text"
                                    name="staff_count"
                                    value={s.values?.staff_count || ''}
                                    onChange={fn.handleChange}
                                    placeholder={'임직원수를 입력하세요'}
                                    errors={s.errors}
                                    className=""
                                />
                            </EditFormTD>
                            <EditFormTH className="col-span-1 mand">구축희망일</EditFormTH>
                            <EditFormTD className="col-span-2">
                                <EditFormDate input_name="wish_build_at" values={s.values?.wish_build_at} is_mand={true} errors={s.errors} handleChange={fn.handleChangeDate} />
                            </EditFormTD>
                            <EditFormTH className="col-span-1 mand">담당자명</EditFormTH>
                            <EditFormTD className="col-span-2">
                                <EditFormInput
                                    type="text"
                                    name="staff_name"
                                    value={s.values?.staff_name || ''}
                                    is_mand={true}
                                    placeholder={'담당자명을 입력하세요'}
                                    onChange={fn.handleChange}
                                    errors={s.errors}
                                    className=""
                                />
                            </EditFormTD>
                            <EditFormTH className="col-span-1">부서</EditFormTH>
                            <EditFormTD className="col-span-2">
                                <EditFormInput
                                    type="text"
                                    name="staff_dept"
                                    value={s.values?.staff_dept || ''}
                                    onChange={fn.handleChange}
                                    placeholder={'부서를 입력하세요'}
                                    errors={s.errors}
                                    className=""
                                />
                            </EditFormTD>
                            <EditFormTH className="col-span-1">직급</EditFormTH>
                            <EditFormTD className="col-span-2">
                                <EditFormInput
                                    type="text"
                                    name="staff_position"
                                    value={s.values?.staff_position || ''}
                                    placeholder={'직급을 입력하세요'}
                                    onChange={fn.handleChange}
                                    errors={s.errors}
                                    className=""
                                />
                            </EditFormTD>
                            <EditFormTH className="col-span-1">직책</EditFormTH>
                            <EditFormTD className="col-span-2">
                                <EditFormInput
                                    type="text"
                                    name="staff_position2"
                                    value={s.values?.staff_position2 || ''}
                                    onChange={fn.handleChange}
                                    placeholder={'직책을 입력하세요'}
                                    errors={s.errors}
                                    className=""
                                />
                            </EditFormTD>
                            <EditFormTH className="col-span-1 mand">연락처</EditFormTH>
                            <EditFormTD className="col-span-2">
                                <EditFormInput
                                    type="text"
                                    name="staff_mobile"
                                    value={s.values?.staff_mobile || ''}
                                    is_mand={true}
                                    is_mobile={true}
                                    placeholder={'연락처를 입력하세요'}
                                    onChange={fn.handleChange}
                                    errors={s.errors}
                                    className=""
                                />
                            </EditFormTD>
                            <EditFormTH className="col-span-1 mand">이메일</EditFormTH>
                            <EditFormTD className="col-span-2">
                                <EditFormInput
                                    type="text"
                                    name="staff_email"
                                    value={s.values?.staff_email || ''}
                                    is_mand={true}
                                    is_email={true}
                                    onChange={fn.handleChange}
                                    placeholder={'이메일을 입력하세요'}
                                    errors={s.errors}
                                    className=""
                                />
                            </EditFormTD>
                            <EditFormTH className="col-span-1 mand">상담 문의 & 요청내용</EditFormTH>
                            <EditFormTD className="col-span-5">
                                <EditFormTextarea
                                    name="contents"
                                    value={s.values?.contents || ''}
                                    rows={4}
                                    placeholder="상담 문의 및 요청내용을 입력하세요"
                                    is_mand={true}
                                    errors={s.errors}
                                    values={s.values}
                                    set_values={s.setValues}
                                    max_length={1000}
                                />
                            </EditFormTD>
                        </EditFormTable>
                    </EditFormCardBody>
                </EditFormCard>

                <EditFormCard>
                    <EditFormCardHead>
                        <div className="text-lg">상담로그</div>
                    </EditFormCardHead>
                    <EditFormCardBody>
                        <EditFormTable className="grid-cols-6">
                            <EditFormTH className="col-span-1 mand">상담자 메모</EditFormTH>
                            <EditFormTD className="col-span-5">
                                <EditFormTextarea
                                    name="memo"
                                    value={s.values?.memo || ''}
                                    rows={4}
                                    placeholder="추가할 상담로그 내용을 입력하세요"
                                    errors={s.errors}
                                    values={s.values}
                                    set_values={s.setValues}
                                    max_length={1000}
                                />
                            </EditFormTD>
                        </EditFormTable>
                        {memo.list?.map((vv, ii) => (
                            <tr className="col-table grid grid-cols-6 text-center items-center border-b border-x" key={ii}>
                                <th className="col-span-1 py-4 h-full bg-gray-100 font-bold text-sm">
                                    {vv.create_user}
                                    <div className="text-xs text-slate-400">{vv.create_at}</div>
                                </th>
                                <td className="col-span-5 p-3 text-start">{vv.memo}</td>
                            </tr>
                        ))}
                    </EditFormCardBody>
                    <EditFormSubmit button_name={`${s.values?.uid > 0 ? '수정' : '등록'}하기`} submitting={s.submitting}></EditFormSubmit>
                </EditFormCard>
            </EditForm>
        </LayoutPopup>
    );
};
export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {
        uid: checkNumeric(ctx.query.uid),
    };
    var response: any = {};
    try {
        const { data } = await api.post(`/be/admin/entry/counsel/read`, request);
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

export default CounselEdit;
