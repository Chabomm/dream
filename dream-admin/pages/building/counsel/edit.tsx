import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import { cls, checkNumeric } from '@/libs/utils';
import useForm from '@/components/form/useForm';
import Datepicker from 'react-tailwindcss-datepicker';

const CounselEdit: NextPage = (props: any) => {
    const router = useRouter();
    const [filter, setFilter] = useState<any>([]);
    const [memo, setMemo] = useState<any>([]);

    useEffect(() => {
        if (props) {
            s.setValues(props.response.values);
            setFilter(props.response.filter);
            setMemo(props.response.memo_list);
        }
    }, [props]);

    const { s, fn, attrs } = useForm({
        initialValues: {
            wish_build_at: {
                startDate: '',
                endDate: '',
            },
        },
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

            const { data } = await api.post(`/be/admin/building/counsel/edit`, params);
            s.setSubmitting(false);
            if (data.code == 200) {
                alert(data.msg);
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
        <>
            <form onSubmit={fn.handleSubmit} noValidate className="w-full bg-slate-100 mx-auto">
                <div className="w-full bg-slate-100 mx-auto py-10" style={{ minHeight: '100vh' }}>
                    <div className="px-9">
                        <div className="text-2xl font-semibold">복지드림 상담문의</div>

                        {process.env.NODE_ENV == 'development' && (
                            <pre className="">
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <div className="font-bold mb-3 text-red-500">filter</div>
                                        {JSON.stringify(filter, null, 4)}
                                    </div>
                                    <div>
                                        <div className="font-bold mb-3 text-red-500">memo</div>
                                        {JSON.stringify(memo, null, 4)}
                                    </div>
                                    <div>
                                        <div className="font-bold mb-3 text-red-500">s.values</div>
                                        {JSON.stringify(s.values, null, 4)}
                                    </div>
                                </div>
                            </pre>
                        )}

                        <div className="border py-4 px-6 rounded shadow-md bg-white mt-5">
                            <div className="font-bold mb-4">진행상태</div>

                            <table className="border w-full">
                                <tbody>
                                    <tr className="col-table grid grid-cols-6 text-center items-center border-b">
                                        <th className="col-span-1 p-3 bg-gray-100 font-bold">진행상태</th>
                                        <td className="col-span-5 px-3">
                                            <div className="flex items-center gap-4 h-10">
                                                {filter.state?.map((v, i) => (
                                                    <div key={i} className="">
                                                        <input
                                                            id={'state_' + `${v.key}`}
                                                            checked={s.values.state == `${v.key}` ? true : false}
                                                            type="radio"
                                                            value={v.key}
                                                            {...attrs.is_mand}
                                                            name="state"
                                                            className="w-4 h-4 mr-1"
                                                            onChange={fn.handleChange}
                                                            disabled={s.values.state == '502' ? true : false}
                                                        />
                                                        <label htmlFor={'state_' + `${v.key}`} className="text-sm font-medium">
                                                            {v.text}
                                                        </label>
                                                    </div>
                                                ))}
                                                {s.errors['state'] && <div className="form-error">{s.errors['state']}</div>}
                                            </div>
                                        </td>
                                    </tr>
                                    {(props.response.values?.state == '501' || props.response.values?.state == '502') && (
                                        <tr className="col-table grid grid-cols-6 items-center border-b">
                                            <th className="must col-span-1 py-4 bg-gray-100 font-bold">구축신청 url</th>
                                            <td className="col-span-5 text-start px-3 cursor-pointer">
                                                <div
                                                    onClick={() => {
                                                        goBuild({ uid: s.values.uid });
                                                    }}
                                                >
                                                    {entry_domain}/dream/build?uid={s.values.uid}
                                                    <i className="fas fa-external-link-alt ms-1"></i>
                                                </div>
                                            </td>
                                        </tr>
                                    )}

                                    <tr className="col-table grid grid-cols-6 items-center border-b">
                                        <th className="must col-span-1 p-3 bg-gray-100 font-bold">상담신청일</th>
                                        <td className="col-span-2 px-3">
                                            <div>{s.values.create_at}</div>
                                        </td>
                                        <th className="must ol-span-1 p-3 bg-gray-100 font-bold">최근수정일</th>
                                        <td className="col-span-2 px-3">
                                            <div>{s.values.update_at}</div>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>

                        <div className="border py-4 px-6 rounded shadow-md bg-white mt-5">
                            <div className="font-bold mb-4">신청정보</div>

                            <table className="border w-full">
                                <tbody>
                                    <tr className="col-table grid grid-cols-6 items-center border-b">
                                        <th className="col-span-1 p-3 bg-gray-100 font-bold">회사명</th>
                                        <td className="col-span-2 px-3">
                                            <input
                                                type="text"
                                                name="company_name"
                                                autoComplete="new-password"
                                                {...attrs.is_mand}
                                                value={s.values?.company_name || ''}
                                                placeholder="회사명을 입력하세요"
                                                onChange={fn.handleChange}
                                                className={cls(s.errors['company_name'] ? 'border-danger' : '', 'form-control')}
                                            />
                                            {s.errors['company_name'] && <div className="form-error">{s.errors['company_name']}</div>}
                                        </td>
                                        <th className="col-span-1 py-4 bg-gray-100 font-bold">회사홈페이지(url)</th>
                                        <td className="col-span-2 text-start px-3">
                                            <input
                                                type="text"
                                                name="homepage_url"
                                                autoComplete="new-password"
                                                value={s.values?.homepage_url || ''}
                                                onChange={fn.handleChange}
                                                className={cls(s.errors['homepage_url'] ? 'border-danger' : '', 'form-control')}
                                            />
                                        </td>
                                    </tr>
                                    <tr className="col-table grid grid-cols-6 items-center border-b">
                                        <th className="col-span-1 p-3 bg-gray-100 font-bold">임직원수</th>
                                        <td className="col-span-2 px-3">
                                            <input
                                                type="text"
                                                name="staff_count"
                                                autoComplete="new-password"
                                                {...attrs.is_mand}
                                                value={s.values?.staff_count || ''}
                                                placeholder="임직원수를 입력하세요"
                                                onChange={fn.handleChange}
                                                className={cls(s.errors['staff_count'] ? 'border-danger' : '', 'form-control')}
                                            />
                                            {s.errors['staff_count'] && <div className="form-error">{s.errors['staff_count']}</div>}
                                        </td>
                                        <th className="col-span-1 p-3 bg-gray-100 font-bold">구축희망일</th>
                                        <td className="col-span-2 px-3">
                                            <Datepicker
                                                containerClassName="relative w-full text-gray-700 border border-gray-300 rounded"
                                                useRange={false}
                                                asSingle={true}
                                                inputName="wish_build_at"
                                                i18n={'ko'}
                                                value={{
                                                    startDate: s.values?.wish_build_at?.startDate || s.values?.wish_build_at,
                                                    endDate: s.values?.wish_build_at?.endDate || s.values?.wish_build_at,
                                                }}
                                                onChange={fn.handleChangeDateRange}
                                            />
                                            {s.errors['wish_build_at'] && <div className="form-error">{s.errors['wish_build_at']}</div>}
                                        </td>
                                    </tr>
                                    <tr className="col-table grid grid-cols-6 items-center border-b">
                                        <th className="col-span-1 p-3 bg-gray-100 font-bold">담당자명</th>
                                        <td className="col-span-2 px-3">
                                            <input
                                                type="text"
                                                name="staff_name"
                                                autoComplete="new-password"
                                                {...attrs.is_mand}
                                                value={s.values?.staff_name || ''}
                                                placeholder="담당자명을 입력하세요"
                                                onChange={fn.handleChange}
                                                className={cls(s.errors['staff_name'] ? 'border-danger' : '', 'form-control')}
                                            />
                                            {s.errors['staff_name'] && <div className="form-error">{s.errors['staff_name']}</div>}
                                        </td>
                                        <th className="col-span-1 p-3 bg-gray-100 font-bold">부서</th>
                                        <td className="col-span-2 px-3">
                                            <input
                                                type="text"
                                                name="staff_dept"
                                                autoComplete="new-password"
                                                value={s.values?.staff_dept || ''}
                                                placeholder="부서를 입력하세요"
                                                onChange={fn.handleChange}
                                                className={cls(s.errors['staff_dept'] ? 'border-danger' : '', 'form-control')}
                                            />
                                        </td>
                                    </tr>
                                    <tr className="col-table grid grid-cols-6 items-center border-b">
                                        <th className="col-span-1 p-3 bg-gray-100 font-bold">직급</th>
                                        <td className="col-span-2 px-3">
                                            <input
                                                type="text"
                                                name="staff_position"
                                                autoComplete="new-password"
                                                value={s.values?.staff_position || ''}
                                                placeholder="직급을 입력하세요"
                                                onChange={fn.handleChange}
                                                className={cls(s.errors['staff_position'] ? 'border-danger' : '', 'form-control')}
                                            />
                                            {s.errors['staff_position'] && <div className="form-error">{s.errors['staff_position']}</div>}
                                        </td>
                                        <th className="col-span-1 p-3 bg-gray-100 font-bold">직급/직책</th>
                                        <td className="col-span-2 px-3">
                                            <input
                                                type="text"
                                                name="staff_position2"
                                                autoComplete="new-password"
                                                value={s.values?.staff_position2 || ''}
                                                placeholder="직급/직책을 입력하세요"
                                                onChange={fn.handleChange}
                                                className={cls(s.errors['staff_position2'] ? 'border-danger' : '', 'form-control')}
                                            />
                                        </td>
                                    </tr>
                                    <tr className="col-table grid grid-cols-6 items-center border-b">
                                        <th className="col-span-1 py-4 bg-gray-100 font-bold">연락처</th>
                                        <td className="col-span-2 px-3">
                                            <input
                                                type="text"
                                                name="staff_mobile"
                                                autoComplete="new-password"
                                                {...attrs.is_mobile}
                                                {...attrs.is_mand}
                                                value={s.values?.staff_mobile || ''}
                                                placeholder="ex) 010-1234-1234"
                                                onChange={fn.handleChange}
                                                className={cls(s.errors['staff_mobile'] ? 'border-danger' : '', 'form-control')}
                                            />
                                            {s.errors['staff_mobile'] && <div className="form-error">{s.errors['staff_mobile']}</div>}
                                        </td>
                                        <th className="col-span-1 py-4 bg-gray-100 font-bold">이메일</th>
                                        <td className="col-span-2 px-3">
                                            <input
                                                type="text"
                                                name="staff_email"
                                                autoComplete="new-password"
                                                {...attrs.is_mand}
                                                {...attrs.is_email}
                                                value={s.values?.staff_email || ''}
                                                placeholder="ex) example@naver.com"
                                                onChange={fn.handleChange}
                                                className={cls(s.errors['staff_email'] ? 'border-danger' : '', 'form-control')}
                                            />
                                            {s.errors['staff_email'] && <div className="form-error">{s.errors['staff_email']}</div>}
                                        </td>
                                    </tr>

                                    <tr className="col-table grid grid-cols-6 text-center items-center border-b">
                                        <th className="col-span-1 py-4 h-full bg-gray-100 font-bold">상담 문의 & 요청내용</th>
                                        <td className="col-span-5 p-3">
                                            <textarea
                                                name="contents"
                                                {...attrs.is_mand}
                                                rows={4}
                                                placeholder="상담 문의 및 요청내용을 입력하세요"
                                                onChange={fn.handleChange}
                                                value={s.values?.contents || ''}
                                                className={cls(s.errors['contents'] ? 'border-danger' : '', 'form-control')}
                                            ></textarea>
                                            <div className="text-xs text-start">{s.counts?.contents ? s.counts?.contents : '0'}/1000</div>
                                            {s.errors['contents'] && <div className="form-error">{s.errors['contents']}</div>}
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>

                        <div className="border py-4 px-6 rounded shadow-md bg-white mt-5">
                            <div className="font-bold mb-4">상담로그</div>

                            <table className="border w-full">
                                <tbody>
                                    <tr className="col-table grid grid-cols-6 text-center items-center border-b">
                                        <th className="col-span-1 py-4 h-full bg-gray-100 font-bold">상담자 메모</th>
                                        <td className="col-span-5 p-3">
                                            <textarea
                                                name="memo"
                                                rows={4}
                                                value={s.values?.memo || ''}
                                                placeholder="추가할 상담로그 내용을 입력하세요"
                                                onChange={fn.handleTextAreaChange}
                                                className={cls(s.errors['memo'] ? 'border-danger' : '', 'form-control')}
                                            ></textarea>
                                            <div className="flex gap-2">
                                                <div className="text-xs text-start">{s.counts?.memo ? s.counts?.memo : '0'}/1000</div>
                                                {/* <button className="text-sm inline-flex rounded-md border-2 border-sky-300 p-1" disabled={s.submitting}>
                                                    상담메모추가
                                                </button> */}
                                            </div>
                                        </td>
                                    </tr>
                                    {memo.list?.map((vv, ii) => (
                                        <tr className="col-table grid grid-cols-6 text-center items-center border-b" key={ii}>
                                            <th className="col-span-1 py-4 h-full bg-gray-100 font-bold text-sm">
                                                {vv.create_user}
                                                <div className="text-xs text-slate-400">{vv.create_at}</div>
                                            </th>
                                            <td className="col-span-5 p-3 text-start">{vv.memo}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>

                        <div className="offcanvas-footer grid grid-cols-3 gap-4 !p-0 my-5">
                            <button className="btn-del hidden" type="button" onClick={deleting}>
                                삭제
                            </button>
                            <button className="btn-save col-span-3 hover:bg-blue-600" disabled={s.submitting}>
                                저장
                            </button>
                        </div>
                    </div>
                </div>
            </form>
        </>
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
