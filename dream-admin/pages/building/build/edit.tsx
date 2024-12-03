import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import { cls, checkNumeric } from '@/libs/utils';
import useForm from '@/components/form/useForm';
import Datepicker from 'react-tailwindcss-datepicker';
import DaumPost from '@/components/DaumPost';

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

            // return;
            const { data } = await api.post(`/be/admin/building/counsel/edit`, params);
            s.setSubmitting(false);
            if (data.code == 200) {
                alert(data.msg);
            } else {
                alert(data.msg);
            }
        } catch (e: any) {}
    };

    // [ S ] daumpost
    const [daumModal, setDaumModal] = useState(false);
    // 주소 모달에서 선택 후
    const handleCompleteFormSet = (data: any) => {
        s.values.post = data.zonecode;
        s.values.addr = data.roadAddress;
        const el = document.querySelector("input[name='addr_detail']");
        (el as HTMLElement)?.focus();
    };
    // [ E ] daumpost

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
                            <div className="font-bold mb-4">구축신청정보</div>

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
                                        <th className="col-span-1 p-3 bg-gray-100 font-bold">대표자 이름</th>
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
                                    </tr>
                                    <tr className="col-table grid grid-cols-6 items-center border-b">
                                        <th className="col-span-1 p-3 bg-gray-100 font-bold">회사 대표번호</th>
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
                                        <th className="col-span-1 p-3 bg-gray-100 font-bold">사업자등록번호</th>
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
                                    </tr>
                                    <tr className="col-table grid grid-cols-6 items-center border-b">
                                        <th className="col-span-1 p-3 bg-gray-100 font-bold">사업자 분류</th>
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
                                        <th className="col-span-1 p-3 bg-gray-100 font-bold">업종</th>
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

                                    {/* <div className="col-span-1">
                                        <label className="must form-label">회사주소</label>
                                        <div className="flex ">
                                            <button
                                                className="inline-flex items-center px-3 text-sm text-gray-900 bg-gray-200 border border-r-0 border-gray-300 rounded-l-md dark:bg-gray-600 dark:text-gray-400 dark:border-gray-600 r"
                                                type="button"
                                                onClick={() => {
                                                    setDaumModal(true);
                                                }}
                                            >
                                                <i className="fas fa-search"></i>
                                            </button>
                                            <input name="post" type="hidden" value={s.values?.post || ''} onChange={fn.handleChange} readOnly />
                                            <input
                                                type="text"
                                                name="addr"
                                                value={s.values?.addr || ''}
                                                onChange={fn.handleChange}
                                                onClick={() => {
                                                    setDaumModal(true);
                                                }}
                                                {...attrs.is_mand}
                                                className={cls(s.errors['addr'] ? 'border-danger' : '', 'form-control !rounded-none !rounded-r-md cursor-pointer')}
                                                placeholder="지번,도로명,건물명으로 검색"
                                                readOnly
                                            />
                                        </div>
                                        {s.errors['addr'] && <div className="form-error">{s.errors['addr']}</div>}
                                    </div>

                                    <div className="col-span-1 ">
                                        <label className="must form-label">상세주소</label>
                                        <input
                                            type="text"
                                            name="addr_detail"
                                            {...attrs.is_mand}
                                            value={s.values?.addr_detail || ''}
                                            placeholder="상세위치 입력 (예:○○빌딩 2층)"
                                            onChange={fn.handleChange}
                                            className={cls(s.errors['addr_detail'] ? 'border-danger' : '', 'form-control')}
                                        />
                                        {s.errors['addr_detail'] && <div className="form-error">{s.errors['addr_detail']}</div>}
                                    </div> */}

                                    <tr className="col-table grid grid-cols-6 items-center border-b">
                                        <th className="col-span-1 p-3 bg-gray-100 font-bold">회사주소</th>
                                        <td className="col-span-2 px-3">
                                            <div className="flex">
                                                <button
                                                    className="inline-flex items-center px-3 text-sm text-gray-900 bg-gray-200 border border-r-0 border-gray-300 rounded-l-md dark:bg-gray-600 dark:text-gray-400 dark:border-gray-600 r"
                                                    type="button"
                                                    onClick={() => {
                                                        setDaumModal(true);
                                                    }}
                                                >
                                                    <i className="fas fa-search"></i>
                                                </button>
                                                <input name="post" type="hidden" value={s.values?.post || ''} onChange={fn.handleChange} readOnly />
                                                <input
                                                    type="text"
                                                    name="addr"
                                                    value={s.values?.addr || ''}
                                                    onChange={fn.handleChange}
                                                    onClick={() => {
                                                        setDaumModal(true);
                                                    }}
                                                    {...attrs.is_mand}
                                                    className={cls(s.errors['addr'] ? 'border-danger' : '', 'form-control !rounded-none !rounded-r-md cursor-pointer')}
                                                    placeholder="지번,도로명,건물명으로 검색"
                                                    readOnly
                                                />
                                            </div>
                                        </td>
                                        <th className="col-span-1 p-3 bg-gray-100 font-bold">상세주소</th>
                                        <td className="col-span-2 px-3">
                                            <input
                                                type="text"
                                                name="addr_detail"
                                                {...attrs.is_mand}
                                                value={s.values?.addr_detail || ''}
                                                placeholder="상세위치 입력 (예:○○빌딩 2층)"
                                                onChange={fn.handleChange}
                                                className={cls(s.errors['addr_detail'] ? 'border-danger' : '', 'form-control')}
                                            />
                                            {s.errors['addr_detail'] && <div className="form-error">{s.errors['addr_detail']}</div>}
                                        </td>
                                    </tr>
                                    <tr className="col-table grid grid-cols-6 items-center border-b">
                                        <th className="col-span-1 py-4 bg-gray-100 font-bold">담당자명</th>
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
                                        <th className="col-span-1 py-4 bg-gray-100 font-bold">직급/직책</th>
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
                                </tbody>
                            </table>
                        </div>

                        <div className="border py-4 px-6 rounded shadow-md bg-white mt-5">
                            <div className="font-bold mb-4">복지몰 구축정보</div>

                            <table className="border w-full">
                                <tbody>
                                    <tr className="col-table grid grid-cols-6 items-center border-b">
                                        <th className="col-span-1 py-4 bg-gray-100 font-bold">복지몰 명</th>
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
                                        <th className="col-span-1 py-4 bg-gray-100 font-bold">복지몰 도메인</th>
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
                                    <tr className="col-table grid grid-cols-6 items-center border-b">
                                        <th className="col-span-1 p-3 bg-gray-100 font-bold">대표 관리자 아이디</th>
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
                                        <th className="col-span-1 p-3 bg-gray-100 font-bold">대표 관리자 비밀번호</th>
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
                                    </tr>
                                </tbody>
                            </table>
                        </div>

                        <div className="border py-4 px-6 rounded shadow-md bg-white mt-5">
                            <div className="font-bold mb-4">필수 제출서류</div>

                            <table className="border w-full">
                                <tbody>
                                    <tr className="col-table grid grid-cols-6 items-center border-b">
                                        <th className="col-span-1 py-4 bg-gray-100 font-bold">사업자등록증</th>
                                        <td className="col-span-2 px-3">
                                            <input
                                                name="file_biz_no-file"
                                                type="file"
                                                className={cls(s.errors['file_biz_no'] ? 'border-danger' : '', 'form-control')}
                                                onChange={e => {
                                                    fn.handleFileUpload(e, { upload_path: '/dream/build/', file_type: 'all' });
                                                }}
                                            />
                                            <input {...attrs.is_mand} name="file_biz_no" type="hidden" readOnly />
                                            <div className="form_control_padding_se bg-light p-2 text-sm text-slate-500" style={{ backgroundColor: '#f5f9fc' }}>
                                                {s.values.file_biz_no_fakename ? (
                                                    <div className="text-red-400">업로드 파일명 : {s.values.file_biz_no_fakename}</div>
                                                ) : (
                                                    <div>사업자등록증을 첨부해 주세요</div>
                                                )}
                                                <div className="text-muted">지원파일 : jpg,png,pdf (최대10MB)</div>
                                            </div>
                                            {s.errors['file_biz_no'] && <div className="form-error">{s.errors['file_biz_no']}</div>}
                                        </td>
                                        <th className="col-span-1 py-4 bg-gray-100 font-bold">회사 로고 파일</th>
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
                                    <tr className="col-table grid grid-cols-6 items-center border-b">
                                        <th className="col-span-1 p-3 bg-gray-100 font-bold">통장사본</th>
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
                                        <th className="col-span-1 p-3 bg-gray-100 font-bold">정산 이메일</th>
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
                                    </tr>
                                </tbody>
                            </table>
                        </div>

                        <div className="border py-4 px-6 rounded shadow-md bg-white mt-5">
                            <div className="font-bold mb-4">드림클럽 신청/승인 조건</div>

                            <table className="border w-full">
                                <tbody>
                                    <tr className="col-table grid grid-cols-6 items-center border-b">
                                        <th className="col-span-1 py-4 bg-gray-100 font-bold">사업자등록증</th>
                                        <td className="col-span-2 px-3">
                                            <input
                                                name="file_biz_no-file"
                                                type="file"
                                                className={cls(s.errors['file_biz_no'] ? 'border-danger' : '', 'form-control')}
                                                onChange={e => {
                                                    fn.handleFileUpload(e, { upload_path: '/dream/build/', file_type: 'all' });
                                                }}
                                            />
                                            <input {...attrs.is_mand} name="file_biz_no" type="hidden" readOnly />
                                            <div className="form_control_padding_se bg-light p-2 text-sm text-slate-500" style={{ backgroundColor: '#f5f9fc' }}>
                                                {s.values.file_biz_no_fakename ? (
                                                    <div className="text-red-400">업로드 파일명 : {s.values.file_biz_no_fakename}</div>
                                                ) : (
                                                    <div>사업자등록증을 첨부해 주세요</div>
                                                )}
                                                <div className="text-muted">지원파일 : jpg,png,pdf (최대10MB)</div>
                                            </div>
                                            {s.errors['file_biz_no'] && <div className="form-error">{s.errors['file_biz_no']}</div>}
                                        </td>
                                        <th className="col-span-1 py-4 bg-gray-100 font-bold">회사 로고 파일</th>
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
                                    <tr className="col-table grid grid-cols-6 items-center border-b">
                                        <th className="col-span-1 p-3 bg-gray-100 font-bold">통장사본</th>
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
                                        <th className="col-span-1 p-3 bg-gray-100 font-bold">정산 이메일</th>
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
                {daumModal && <DaumPost daumModal={daumModal} setDaumModal={setDaumModal} handleCompleteFormSet={handleCompleteFormSet} />}
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
        const { data } = await api.post(`/be/admin/building/counsel/read`, request);
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
