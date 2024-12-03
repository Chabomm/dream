import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import { cls, checkNumeric, dateformatYYYYMMDD } from '@/libs/utils';
import useForm from '@/components/form/useForm';

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
    EditFormCard,
    EditFormCardHead,
    EditFormCardBody,
    EditFormSelect,
    EditFormTextarea,
} from '@/components/UIcomponent/form/EditFormA';
import EditFormCallout from '@/components/UIcomponent/form/EditFormCallout';
import LayoutPopup from '@/components/LayoutPopup';

const CounselEdit: NextPage = (props: any) => {
    const crumbs = ['구축관리', '구축신청 ' + (props.response.values?.uid > 0 ? '수정' : '등록')];
    const callout = [];
    const title_sub = '복지몰 구축 상담신청 등록/수정을 할 수 있습니다';
    const router = useRouter();

    const [memo, setMemo] = useState<any>([]);
    const [posts, setPosts] = useState<any>({});
    const [filter, setFilter] = useState<any>({});
    const [comItemList, setComItemList] = useState<any>([]);

    useEffect(() => {
        if (props) {
            if (props.response.code == 200) {
                setPosts(props.response);
                setFilter(props.response.filter);
                s.setValues(props.response.values);
                setComItemList(props.response.com_item_list);
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

            const { data } = await api.post(`/be/admin/entry/build/edit`, params);
            s.setSubmitting(false);
            if (data.code == 200) {
                alert(data.msg);
                router.reload();
            } else {
                alert(data.msg);
            }
        } catch (e: any) {}
    };

    // 도메인(input) 변경 되면
    const handleBlur = async () => {
        const copy = { ...s.values };
        if (copy.host == '' || s.values?.host != copy.adminid_check_value) {
            copy.adminid_check_value = '';
            copy.is_adminid_checked = false;
            s.setValues(copy);
        }
    };

    const adminIdCheck = async () => {
        try {
            const copy = { ...s.values };

            const item = {
                adminid_input_value: copy.host, // 체크할 값
                adminid_check_value: '', // 이전에 체크한 값
                is_adminid_checked: false, // 이전에 체크 했는지
            };

            copy.adminid_input_value = item.adminid_input_value;
            copy.adminid_check_value = item.adminid_check_value;
            copy.is_adminid_checked = item.is_adminid_checked;

            if (item.adminid_input_value.length < 4 || item.adminid_input_value.length > 20) {
                alert('관리자 아이디는 영문 혹은 숫자 4자~20자리로 해주세요.');
                copy.is_adminid_checked = false;
                return;
            }
            const { data } = await api.post(`/be/admin/entry/build/check`, item);
            copy.is_adminid_checked = data;
            if (data.code == 200) {
                if (data.check_result) {
                    alert('사용가능한 아이디입니다.');
                    copy.adminid_check_value = item.adminid_input_value;
                    s.setValues(copy);
                } else {
                    alert('이미 사용중인 아이디입니다.');
                    copy.adminid_check_value = '';
                    s.setValues(copy);
                }
            } else {
                alert(data.msg);
                return;
            }
        } catch (e: any) {}
    };

    let entry_domain = `http://localhost:13020`;
    if (`${process.env.NODE_ENV}` == 'production') {
        entry_domain = `https://`;
    }
    const goEdit = (item: number) => {
        window.open(`/entry/partner/edit?uid=${item}`, '고객사 상세', 'width=1120,height=800,location=no,status=no,scrollbars=yes');
    };

    // [ S ] 파일 다운로드
    const download_file = async (file_kind: string) => {
        let file_link = '';
        if (file_kind == 'file_biz_no') {
            file_link = posts.file_biz_no;
        } else if (file_kind == 'file_logo') {
            file_link = posts.file_logo;
        } else if (file_kind == 'file_bank') {
            file_link = posts.file_bank;
        } else if (file_kind == 'file_mall_logo') {
            file_link = posts.file_mall_logo;
        }

        const arr_file_link = file_link.split('/');
        const file_name = arr_file_link[arr_file_link.length - 1];

        try {
            await api({
                url: `/be/aws/download`,
                method: 'POST',
                responseType: 'blob',
                data: {
                    file_url: file_link,
                },
            }).then(async response => {
                var fileURL = window.URL.createObjectURL(new Blob([response.data]));
                var fileLink = document.createElement('a');
                fileLink.href = fileURL;
                fileLink.setAttribute('download', file_name);
                document.body.appendChild(fileLink);
                fileLink.click();

                await api.post(`/be/aws/temp/delete`);
            });
        } catch (e: any) {
            console.log(e);
        }
    };
    // [ E ] 파일 다운로드

    return (
        <>
            <LayoutPopup title={crumbs[crumbs.length - 1]} className="px-6 bg-slate-50">
                <EditFormCallout title={crumbs[crumbs.length - 1]} title_sub={title_sub} callout={callout} />

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
                            <div className="text-lg">구축신청정보</div>
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
                                <EditFormTH className="col-span-1 mand">대표자 이름</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput
                                        type="text"
                                        name="ceo_name"
                                        value={s.values?.ceo_name || ''}
                                        is_mand={true}
                                        placeholder={'대표자명을 입력하세요'}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        className=""
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">회사 대표번호</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput
                                        type="text"
                                        name="company_hp"
                                        value={s.values?.company_hp || ''}
                                        is_mand={true}
                                        is_mobile={true}
                                        placeholder={'대표번호를 입력하세요'}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        className=""
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">사업자등록번호</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput
                                        type="text"
                                        name="biz_no"
                                        value={s.values?.biz_no || ''}
                                        is_mand={true}
                                        is_bizno={true}
                                        placeholder={'ex) 000-00-00000'}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        className=""
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">사업자 분류</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormRadioList
                                        input_name="biz_kind"
                                        values={s.values?.biz_kind}
                                        filter_list={[
                                            { key: '100', text: '법인사업자' },
                                            { key: '200', text: '일반(개인)사업자' },
                                            { key: '300', text: '기타' },
                                        ]}
                                        is_mand={true}
                                        errors={s.errors}
                                        handleChange={fn.handleChange}
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">업종</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormSelect
                                        input_name="biz_item"
                                        value={s.values?.biz_item || ''}
                                        is_mand={true}
                                        filter_list={comItemList}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        className="w-full"
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">회사주소</EditFormTH>
                                <EditFormTD className="col-span-5">
                                    <EditFormAddr
                                        post="post"
                                        addr="addr"
                                        addr_detail="addr_detail"
                                        values={s.values}
                                        is_mand={true}
                                        set_values={s.setValues}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                    />
                                </EditFormTD>
                            </EditFormTable>
                        </EditFormCardBody>
                    </EditFormCard>

                    <EditFormCard>
                        <EditFormCardHead>
                            <div className="text-lg">담당자 정보</div>
                        </EditFormCardHead>
                        <EditFormCardBody>
                            <EditFormTable className="grid-cols-6">
                                <EditFormTH className="col-span-1 mand">담당자명</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput
                                        type="text"
                                        name="staff_name"
                                        value={s.values?.staff_name || ''}
                                        is_mand={true}
                                        placeholder={'담당자 이름을 입력하세요'}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        className=""
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1">담당자 부서</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput
                                        type="text"
                                        name="staff_dept"
                                        value={s.values?.staff_dept || ''}
                                        placeholder={'대표자명을 입력하세요'}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        className=""
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1">담당자 직급</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput
                                        type="text"
                                        name="staff_position"
                                        value={s.values?.staff_position || ''}
                                        placeholder={'담당자 직급을 입력하세요'}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        className=""
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1">담당자 직책</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput
                                        type="text"
                                        name="staff_position2"
                                        value={s.values?.staff_position2 || ''}
                                        placeholder={'담당자 직책을 입력하세요'}
                                        onChange={fn.handleChange}
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
                                        placeholder={'ex) 010-1234-1234'}
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
                                        placeholder={'ex) example@naver.com'}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        className=""
                                    />
                                </EditFormTD>
                            </EditFormTable>
                        </EditFormCardBody>
                    </EditFormCard>

                    <EditFormCard>
                        <EditFormCardHead>
                            <div className="text-lg">복지몰 구축정보</div>
                        </EditFormCardHead>
                        <EditFormCardBody>
                            <EditFormTable className="grid-cols-6">
                                <EditFormTH className="col-span-1 mand">복지몰명</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput
                                        type="text"
                                        name="mall_name"
                                        value={s.values?.mall_name || ''}
                                        is_mand={true}
                                        placeholder={'복지몰명을 입력하세요'}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        className=""
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">복지몰 도메인</EditFormTH>
                                <EditFormTD className="col-span-2 !block">
                                    <div className="flex mb-2">
                                        <span className="inline-flex items-center px-3 text-sm text-gray-900 bg-gray-200 border border-r-0 border-gray-300 rounded-l-md">
                                            https://
                                        </span>
                                        <input
                                            type="text"
                                            name="host"
                                            value={s.values?.host || ''}
                                            onChange={fn.handleChange}
                                            // {...attrs.is_mand}
                                            className={cls(s.errors['host'] ? 'border-danger' : '', 'form-control !rounded-none !rounded-x-md')}
                                            placeholder="대표관리자아이디"
                                            onBlur={() => handleBlur()}
                                        />
                                        <span className="inline-flex items-center px-3 text-sm text-gray-900 bg-gray-200 border border-l-0 border-gray-300 rounded-r-md">
                                            .welfaredream.com
                                        </span>
                                    </div>

                                    {s.values?.adminid_check_value ? (
                                        <div className="p-2" style={{ backgroundColor: '#f5f9fc' }}>
                                            <div className="text-red-400">{s.values?.adminid_check_value}.welfaredream.com</div>
                                        </div>
                                    ) : (
                                        <div>
                                            <button
                                                type="button"
                                                onClick={() => {
                                                    adminIdCheck();
                                                }}
                                                className="rounded-md border border-gray-400 text-gray-500 py-2 w-full"
                                            >
                                                중복확인
                                            </button>
                                            <div className="text-sm text-slate-500 p-2" style={{ backgroundColor: '#f5f9fc' }}>
                                                관리자아이디 중복확인을 해주세요
                                            </div>
                                        </div>
                                    )}
                                    <div className="text-red-400 text-sm">
                                        ※ 대표 관리자 아이디가 복지몰 도메인으로 사용되오니 반드시 확인 바랍니다. (Tip.회사 영문명 또는 약자 추천)
                                    </div>
                                </EditFormTD>
                                <EditFormTH className="col-span-1">대표 관리자 아이디</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    {s.values?.adminid_check_value ? (
                                        <>
                                            {s.values?.is_adminid_checked && (
                                                <div className="text-lime-500 text-sm">{s.values?.adminid_check_value}은(는) 사용가능한 아이디입니다.</div>
                                            )}
                                        </>
                                    ) : (
                                        <>{!s.values?.is_adminid_checked && <div className="text-red-400 text-sm">관리자아이디 중복확인을 해주세요</div>}</>
                                    )}
                                </EditFormTD>
                                <EditFormTH className="col-span-1">대표 관리자 비밀번호</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <div className="text-sm text-slate-500">
                                        초기 비밀번호는 <br />
                                        관리자 아이디 + 담당자 휴대번호 뒤 4자리 입니다.
                                    </div>
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">정산 이메일</EditFormTH>
                                <EditFormTD className="col-span-5">
                                    <EditFormInput
                                        type="text"
                                        name="account_email"
                                        value={s.values?.account_email || ''}
                                        is_mand={true}
                                        is_email={true}
                                        placeholder={'ex) tax@domain.com'}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        className=""
                                    />
                                </EditFormTD>
                            </EditFormTable>
                        </EditFormCardBody>
                    </EditFormCard>

                    <EditFormCard>
                        <EditFormCardHead>
                            <div className="text-lg">필수 제출서류</div>
                        </EditFormCardHead>
                        <EditFormCardBody>
                            <EditFormTable className="grid-cols-6">
                                <EditFormTH className="col-span-1 mand">사업자등록증</EditFormTH>
                                <EditFormTD className="col-span-2 !block">
                                    <input
                                        name="file_biz_no-file"
                                        type="file"
                                        className={cls(s.errors['file_biz_no'] ? 'border-danger' : '', 'form-control')}
                                        onChange={e => {
                                            fn.handleFileUpload(e, { upload_path: '/dream/build/', file_type: 'all' });
                                        }}
                                    />
                                    <input {...attrs.is_mand} name="file_biz_no" type="hidden" readOnly />
                                    <div>
                                        <button
                                            type="button"
                                            className="text-blue-500 underline cursor-pointe text-start"
                                            onClick={e => {
                                                download_file('file_biz_no');
                                            }}
                                        >
                                            <span>
                                                <i className="fas fa-file-download me-1"></i>
                                            </span>
                                            {s.values?.file_biz_no_fakename != '' && typeof s.values?.file_biz_no_fakename != 'undefined'
                                                ? s.values?.file_biz_no_fakename
                                                : s.values?.file_biz_no}
                                        </button>
                                    </div>
                                    <div className="form_control_padding_se bg-light p-2 text-sm text-slate-500" style={{ backgroundColor: '#f5f9fc' }}>
                                        {s.values?.file_biz_no_fakename ? (
                                            <div className="text-red-400">업로드 파일명 : {s.values?.file_biz_no_fakename}</div>
                                        ) : (
                                            <div>사업자등록증을 첨부해 주세요</div>
                                        )}
                                        <div className="text-muted">지원파일 : jpg,png,pdf (최대10MB)</div>
                                    </div>
                                    {s.errors['file_biz_no'] && <div className="form-error">{s.errors['file_biz_no']}</div>}
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">회사 로고 파일</EditFormTH>
                                <EditFormTD className="col-span-2 !block">
                                    <input
                                        name="file_logo-file"
                                        type="file"
                                        className={cls(s.errors['file_logo'] ? 'border-danger' : '', 'form-control')}
                                        onChange={e => {
                                            fn.handleFileUpload(e, { upload_path: '/dream/build/', file_type: 'all' });
                                        }}
                                    />
                                    <input {...attrs.is_mand} name="file_logo" type="hidden" readOnly />
                                    <div>
                                        <button
                                            type="button"
                                            className="text-blue-500 underline cursor-pointe text-start"
                                            onClick={e => {
                                                download_file('file_logo');
                                            }}
                                        >
                                            <span>
                                                <i className="fas fa-file-download me-1"></i>
                                            </span>
                                            {s.values?.file_logo_fakename != '' && typeof s.values?.file_logo_fakename != 'undefined'
                                                ? s.values?.file_logo_fakename
                                                : s.values?.file_logo}
                                        </button>
                                    </div>
                                    <div className="form_control_padding_se bg-light p-2 text-sm text-slate-500" style={{ backgroundColor: '#f5f9fc' }}>
                                        {s.values?.file_logo_fakename ? (
                                            <div className="text-red-400">업로드 파일명 : {s.values?.file_logo_fakename}</div>
                                        ) : (
                                            <div>회사 로고 파일을 첨부해 주세요</div>
                                        )}
                                        <div className="text-muted">이미지 가이드 : 380px x 60px (가로 x 세로), 투명 배경, png (최대 10MB)</div>
                                    </div>
                                    {s.errors['file_logo'] && <div className="form-error">{s.errors['file_logo']}</div>}
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">통장사본</EditFormTH>
                                <EditFormTD className="col-span-2 !block">
                                    <input
                                        name="file_bank-file"
                                        type="file"
                                        className={cls(s.errors['file_bank'] ? 'border-danger' : '', 'form-control')}
                                        onChange={e => {
                                            fn.handleFileUpload(e, { upload_path: '/dream/build/', file_type: 'all' });
                                        }}
                                    />
                                    <input {...attrs.is_mand} name="file_bank" type="hidden" readOnly />
                                    <div>
                                        <button
                                            type="button"
                                            className="text-blue-500 underline cursor-pointe text-start"
                                            onClick={e => {
                                                download_file('file_bank');
                                            }}
                                        >
                                            <span>
                                                <i className="fas fa-file-download me-1"></i>
                                            </span>
                                            {s.values?.file_bank_fakename != '' && typeof s.values?.file_bank_fakename != 'undefined'
                                                ? s.values?.file_bank_fakename
                                                : s.values?.file_bank}
                                        </button>
                                    </div>
                                    <div className="form_control_padding_se bg-light p-2 text-sm text-slate-500" style={{ backgroundColor: '#f5f9fc' }}>
                                        {s.values?.file_bank_fakename ? (
                                            <div className="text-red-400">업로드 파일명 : {s.values?.file_bank_fakename}</div>
                                        ) : (
                                            <div>통장사본을 첨부해 주세요</div>
                                        )}
                                        <div className="text-muted">지원파일 : jpg,png,pdf (최대10MB)</div>
                                    </div>
                                    {s.errors['file_bank'] && <div className="form-error">{s.errors['file_bank']}</div>}
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">복지몰 로고 파일</EditFormTH>
                                <EditFormTD className="col-span-2 !block">
                                    <input
                                        name="file_mall_logo-file"
                                        type="file"
                                        className={cls(s.errors['file_mall_logo'] ? 'border-danger' : '', 'form-control')}
                                        onChange={e => {
                                            fn.handleFileUpload(e, { upload_path: '/dream/build/', file_type: 'all' });
                                        }}
                                    />
                                    <input {...attrs.is_mand} name="file_mall_logo" type="hidden" readOnly />
                                    <div>
                                        <button
                                            type="button"
                                            className="text-blue-500 underline cursor-pointe text-start"
                                            onClick={e => {
                                                download_file('file_mall_logo');
                                            }}
                                        >
                                            <span>
                                                <i className="fas fa-file-download me-1"></i>
                                            </span>
                                            {s.values?.file_mall_logo_fakename != '' && typeof s.values?.file_mall_logo_fakename != 'undefined'
                                                ? s.values?.file_mall_logo_fakename
                                                : s.values?.file_mall_logo}
                                        </button>
                                    </div>
                                    <div className="form_control_padding_se bg-light p-2 text-sm text-slate-500" style={{ backgroundColor: '#f5f9fc' }}>
                                        {s.values?.file_mall_logo_fakename ? (
                                            <div className="text-red-400">업로드 파일명 : {s.values?.file_mall_logo_fakename}</div>
                                        ) : (
                                            <div>복지몰 로고 파일을 첨부해 주세요</div>
                                        )}
                                        <div className="text-muted">이미지 가이드 : 245*102px, 투명 배경, png (최대 10MB)</div>
                                    </div>
                                    {s.errors['file_mall_logo'] && <div className="form-error">{s.errors['file_mall_logo']}</div>}
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
                    </EditFormCard>
                    {posts?.state == '200' ? (
                        <div className="flex-grow-1 text-center">
                            <div className="text-red-500">구축이 완료된 고객사는 고객사 상세정보에서 수정가능 합니다.</div>
                            <div
                                className="mt-2 cursor-pointer"
                                onClick={() => {
                                    goEdit(posts?.partner_uid);
                                }}
                            >
                                바로가기
                            </div>
                        </div>
                    ) : (
                        <EditFormSubmit button_name={`${s.values?.uid > 0 ? '수정' : '등록'}하기`} submitting={s.submitting}></EditFormSubmit>
                    )}
                </EditForm>
            </LayoutPopup>
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
        const { data } = await api.post(`/be/admin/entry/build/read`, request);
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
