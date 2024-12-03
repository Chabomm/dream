import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import { cls, checkNumeric } from '@/libs/utils';
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
    EditFormCheckboxList,
} from '@/components/UIcomponent/form/EditFormA';
import EditFormCallout from '@/components/UIcomponent/form/EditFormCallout';
import LayoutPopup from '@/components/LayoutPopup';
import Link from 'next/link';
import ListTable from '@/components/UIcomponent/table/ListTable';
import ListTableHead from '@/components/UIcomponent/table/ListTableHead';
import ManagerEdit from '@/components/modal/managerEdit';
import ListTableBody from '@/components/UIcomponent/table/ListTableBody';

const BuildingPartnerEdit: NextPage = (props: any) => {
    const crumbs = ['구축관리', '고객사 ' + (props.response.values?.uid > 0 ? '수정' : '등록')];
    const callout = [];
    const title_sub = '복지몰 고객사 등록/수정을 할 수 있습니다';
    const router = useRouter();

    const [posts, setPosts] = useState<any>({});
    const [filter, setFilter] = useState<any>({});
    const [comItemList, setComItemList] = useState<any>([]);
    const [managerSort, setManagerSort] = useState<any>([]);

    useEffect(() => {
        if (props) {
            if (props.response.code == 200) {
                setPosts(props.response);
                setFilter(props.response.filter);
                s.setValues(props.response.values);
                setComItemList(props.response.com_item_list);
                setManagerSort(props.response.list);
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

            const { data } = await api.post(`/be/admin/entry/partner/edit`, s.values);
            s.setSubmitting(false);
            if (data.code == 200) {
                alert(data.msg);
            } else {
                alert(data.msg);
            }
        } catch (e: any) {}
    };

    const goBuild = (uid: number) => {
        window.open(`/entry/build/edit?uid=${uid}`, '구축상세', 'width=1120,height=800,location=no,status=no,scrollbars=yes');
    };

    const goCounsel = (uid: number) => {
        window.open(`/entry/counsel/edit?uid=${uid}`, '상담상세', 'width=1120,height=800,location=no,status=no,scrollbars=yes');
    };

    // [ S ] 담당자 모달
    const [managerEditOpen, setManagerEditOpen] = useState(false);
    const [stateInfo, setStateInfo] = useState<any>();
    const openManagerEdit = (uid: number, mode: string, partner_uid: number) => {
        setManagerEditOpen(true);
        setStateInfo({
            uid,
            mode,
            partner_uid,
            partner_id: posts.partner_id,
            prefix: posts.prefix,
        });
    };
    // [ E ] 담당자 모달

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

                <pre className="mb-5">
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <div className="font-bold mb-3 text-red-500">filter</div>
                            {JSON.stringify(filter, null, 4)}
                        </div>
                        <div>
                            <div className="font-bold mb-3 text-red-500">s.values</div>
                            {JSON.stringify(s.values, null, 4)}
                        </div>
                    </div>
                </pre>
                <EditForm onSubmit={fn.handleSubmit}>
                    <EditFormCard>
                        <EditFormCardHead>
                            <div className="text-lg">복지몰 정보</div>
                        </EditFormCardHead>
                        <EditFormCardBody>
                            <EditFormTable className="grid-cols-6">
                                <EditFormTH className="col-span-1">이력보기</EditFormTH>
                                <EditFormTD className="col-span-5">
                                    <div className="bg-blue-600 text-white border rounded-md px-2 py-1 me-2">
                                        <button type="button">수정이력보기</button>
                                    </div>
                                    <div className="bg-blue-600 text-white border rounded-md px-2 py-1 me-2">
                                        <button type="button" onClick={() => goCounsel(posts?.counsel_uid)}>
                                            상담내용보기
                                        </button>
                                    </div>
                                    <div className="bg-blue-600 text-white border rounded-md px-2 py-1">
                                        <button type="button" onClick={() => goBuild(posts?.build_uid)}>
                                            구축내용보기
                                        </button>
                                    </div>
                                </EditFormTD>
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
                                <EditFormTH className="col-span-1">prefix</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormLabel className="">{posts?.prefix}</EditFormLabel>
                                </EditFormTD>
                                <EditFormTH className="col-span-1">복지몰 도메인</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormLabel className="">
                                        <span className="me-2">https://{posts?.partner_id}.welfaredream.com</span>
                                        <Link href={`https://${posts?.partner_id}.welfaredream.com`} target="_blank">
                                            <i className="fas fa-external-link-alt ms-1"></i>
                                        </Link>
                                    </EditFormLabel>
                                </EditFormTD>
                                <EditFormTH className="col-span-1">HOST</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormLabel className="">{posts?.partner_id}</EditFormLabel>
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">고객사명</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput
                                        type="text"
                                        name="company_name"
                                        value={s.values?.company_name || ''}
                                        is_mand={true}
                                        placeholder={'고객사명을 입력하세요'}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        className=""
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1">등록일</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormLabel className="">{posts?.create_at}</EditFormLabel>
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">복지몰상태</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormRadioList
                                        input_name="state"
                                        values={s.values?.state}
                                        filter_list={filter.state}
                                        is_mand={true}
                                        errors={s.errors}
                                        handleChange={fn.handleChange}
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">SponsorID</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput
                                        type="text"
                                        name="sponsor"
                                        value={s.values?.sponsor || ''}
                                        is_mand={true}
                                        placeholder={'Sponsor를 입력하세요'}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        className=""
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">회원가입유형</EditFormTH>
                                <EditFormTD className="col-span-5">
                                    <EditFormRadioList
                                        input_name="partner_type"
                                        values={s.values?.partner_type}
                                        filter_list={[
                                            { key: '100', text: '개방형' },
                                            { key: '200', text: '직접회원가입' },
                                            { key: '201', text: '직접회원가입 승인제도' },
                                            { key: '300', text: '관리자가 회원등록' },
                                            { key: '400', text: '자동로그인' },
                                        ]}
                                        is_mand={true}
                                        errors={s.errors}
                                        handleChange={fn.handleChange}
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">회원유형</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormRadioList
                                        input_name="mem_type"
                                        values={s.values?.mem_type}
                                        filter_list={[
                                            { key: '임직원', text: '임직원' },
                                            { key: '회원', text: '회원' },
                                        ]}
                                        is_mand={true}
                                        errors={s.errors}
                                        handleChange={fn.handleChange}
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">몰유형</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormRadioList
                                        input_name="mall_type"
                                        values={s.values?.mall_type}
                                        filter_list={[
                                            { key: '임직원몰', text: '임직원몰' },
                                            { key: '멤버십몰', text: '멤버십몰' },
                                            { key: '협회몰', text: '협회몰' },
                                        ]}
                                        is_mand={true}
                                        errors={s.errors}
                                        handleChange={fn.handleChange}
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">복지포인트</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormRadioList
                                        input_name="is_welfare"
                                        values={s.values?.is_welfare}
                                        filter_list={[
                                            { key: 'T', text: '사용중' },
                                            { key: 'F', text: '미사용' },
                                        ]}
                                        is_mand={true}
                                        errors={s.errors}
                                        handleChange={fn.handleChange}
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">드림포인트</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormRadioList
                                        input_name="is_dream"
                                        values={s.values?.is_dream}
                                        filter_list={[
                                            { key: 'T', text: '사용중' },
                                            { key: 'F', text: '미사용' },
                                        ]}
                                        is_mand={true}
                                        errors={s.errors}
                                        handleChange={fn.handleChange}
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1">역할</EditFormTH>
                                <EditFormTD className="col-span-5 flex-col">
                                    <div className="mb-3 font-bold text-red-500 self-start">
                                        고객사에게 배정할 메뉴는
                                        {"'"}구축관리{"'"} {' > '} {"'"}고객사 메뉴역할{"'"}
                                        에서 등록/수정 가능합니다.
                                    </div>
                                    <EditFormCheckboxList
                                        input_name="roles"
                                        values={s.values?.roles}
                                        filter_list={filter?.roles}
                                        cols={2}
                                        errors={s.errors}
                                        handleChange={fn.handleCheckboxGroupForInteger}
                                    />
                                </EditFormTD>
                            </EditFormTable>
                        </EditFormCardBody>
                    </EditFormCard>

                    <EditFormCard>
                        <EditFormCardHead>
                            <div className="text-lg">복지몰 계약 정보</div>
                        </EditFormCardHead>
                        <EditFormCardBody>
                            <EditFormTable className="grid-cols-6">
                                <EditFormTH className="col-span-1">이력보기</EditFormTH>
                                <EditFormTD className="col-span-5">
                                    <div className="bg-blue-600 text-white border rounded-md px-2 py-1">
                                        <button>수정이력보기</button>
                                    </div>
                                </EditFormTD>
                                <EditFormTH className="col-span-1">고객사코드</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormLabel className="">{posts?.partner_code}</EditFormLabel>
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">기업명</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput
                                        type="text"
                                        name="company_name"
                                        value={s.values?.company_name || ''}
                                        is_mand={true}
                                        placeholder={'기업명을 입력하세요'}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        className=""
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">대표자 성함</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput
                                        type="text"
                                        name="ceo_name"
                                        value={s.values?.ceo_name || ''}
                                        is_mand={true}
                                        placeholder={'대표자 성함을 입력하세요'}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        className=""
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">일반전화(대표번호)</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput
                                        type="text"
                                        name="company_hp"
                                        value={s.values?.company_hp || ''}
                                        is_mand={true}
                                        is_mobile={true}
                                        placeholder={'일반전화(대표번호)를 입력하세요'}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        className=""
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">담당자 이름</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput
                                        type="text"
                                        name="staff_name"
                                        value={s.values?.staff_name || ''}
                                        is_mand={true}
                                        placeholder={'이름을 입력하세요'}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        className=""
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">담당자 부서</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput
                                        type="text"
                                        name="staff_depart"
                                        value={s.values?.staff_depart || ''}
                                        is_mand={true}
                                        placeholder={'부서를 입력하세요'}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        className=""
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">담당자 직급</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput
                                        type="text"
                                        name="staff_position"
                                        value={s.values?.staff_position || ''}
                                        is_mand={true}
                                        placeholder={'직급을 입력하세요'}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        className=""
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">담당자 직책</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput
                                        type="text"
                                        name="staff_position2"
                                        value={s.values?.staff_position2 || ''}
                                        is_mand={true}
                                        placeholder={'직책을 입력하세요'}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        className=""
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">담당자 이메일</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput
                                        type="text"
                                        name="staff_email"
                                        value={s.values?.staff_email || ''}
                                        is_mand={true}
                                        is_email={true}
                                        placeholder={'ex) example@indend.co.kr'}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        className=""
                                    />
                                </EditFormTD>

                                <EditFormTH className="col-span-1 mand">담당자 휴대전화</EditFormTH>
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
                                <EditFormTH className="col-span-1 mand">정산 이메일</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput
                                        type="text"
                                        name="account_email"
                                        value={s.values?.account_email || ''}
                                        is_mand={true}
                                        is_email={true}
                                        placeholder={'ex) tax@indend.co.kr'}
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
                                            {s.values?.file_biz_no != '' && s.values?.file_biz_no != null ? (
                                                <span>
                                                    <i className="fas fa-file-download me-1"></i>
                                                    {s.values?.file_biz_no}
                                                </span>
                                            ) : (
                                                <></>
                                            )}
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
                                            {s.values?.file_bank != '' && s.values?.file_bank != null ? (
                                                <span>
                                                    <i className="fas fa-file-download me-1"></i>
                                                    {s.values?.file_bank}
                                                </span>
                                            ) : (
                                                <span></span>
                                            )}
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
                                            {s.values?.file_logo != '' && s.values?.file_logo != null ? (
                                                <span>
                                                    <i className="fas fa-file-download me-1"></i>
                                                    {s.values?.file_logo}
                                                </span>
                                            ) : (
                                                <span></span>
                                            )}
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
                                            {s.values?.file_mall_logo != '' && s.values?.file_mall_logo != null ? (
                                                <span>
                                                    <i className="fas fa-file-download me-1"></i>
                                                    {s.values?.file_mall_logo}
                                                </span>
                                            ) : (
                                                <span></span>
                                            )}
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
                            <div className="text-lg">담당자 정보</div>
                        </EditFormCardHead>
                        <EditFormCardBody>
                            <EditFormTable className="grid-cols-6">
                                <EditFormTH className="col-span-1">고객사관리자</EditFormTH>
                                <EditFormTD className="col-span-5">
                                    <EditFormLabel className="">
                                        <span className="me-2">https://{posts?.partner_id}.welfaredream.com/opmanager</span>
                                        <Link href={`https://${posts?.partner_id}.welfaredream.com/opmanager`} target="_blank">
                                            <i className="fas fa-external-link-alt ms-1"></i>
                                        </Link>
                                    </EditFormLabel>
                                </EditFormTD>
                                <EditFormTH className="col-span-1">아이디</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormLabel className="">{posts?.partner_id}</EditFormLabel>
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">비밀번호</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput
                                        type="text"
                                        name="staff_email"
                                        value={s.values?.staff_email || ''}
                                        is_mand={true}
                                        is_email={true}
                                        placeholder={'ex) example@indend.co.kr'}
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
                            <div className="flex">
                                <div className="text-lg">용어정보</div>
                                {s.values?.mall_type == '' ? (
                                    <div className="text-red-500 font-bold me-3">몰유형을 선택해주세요</div>
                                ) : (
                                    <div>
                                        {posts?.word_partner_id == null ? (
                                            <div className="text-red-500 font-bold">
                                                <span className="text-blue-600 mx-3">{s.values?.mall_type}</span>
                                                기본용어 사용중
                                            </div>
                                        ) : (
                                            <div className="text-red-500 font-bold mx-4">커스텀 용어 사용중</div>
                                        )}
                                    </div>
                                )}
                            </div>
                        </EditFormCardHead>
                        <EditFormCardBody>
                            <EditFormTable className="grid-cols-6">
                                <EditFormTH className="col-span-1">몰명칭</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput
                                        type="text"
                                        name="mall_tltle"
                                        value={s.values?.mall_tltle || ''}
                                        placeholder={posts?.mall_tltle}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        className=""
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1">회원명칭</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput
                                        type="text"
                                        name="member_name"
                                        value={s.values?.member_name || ''}
                                        placeholder={posts?.member_name}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        className=""
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1">복지포인트명</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput
                                        type="text"
                                        name="point_name"
                                        value={s.values?.point_name || ''}
                                        placeholder={posts?.point_name}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        className=""
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1">공지사항명</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput
                                        type="text"
                                        name="notice"
                                        value={s.values?.notice || ''}
                                        placeholder={posts?.notice}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        className=""
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1">인트로문구</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput
                                        type="text"
                                        name="intro"
                                        value={s.values?.intro || ''}
                                        placeholder={posts?.intro}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        className=""
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1">사원증명</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput
                                        type="text"
                                        name="employee_card"
                                        value={s.values?.employee_card || ''}
                                        placeholder={posts?.employee_card}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        className=""
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1">혜택명</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput
                                        type="text"
                                        name="benefit"
                                        value={s.values?.benefit || ''}
                                        placeholder={posts?.benefit}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        className=""
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1">b2b_goods</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput
                                        type="text"
                                        name="b2b_goods"
                                        value={s.values?.b2b_goods || ''}
                                        placeholder={posts?.b2b_goods}
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
                            <div className="flex">
                                <div className="text-lg">드림포인트 정보</div>
                            </div>
                        </EditFormCardHead>
                        <EditFormCardBody>
                            <EditFormTable className="grid-cols-6">
                                <EditFormTH className="col-span-1 mand">포인트 금액</EditFormTH>
                                <EditFormTD className="col-span-2 !block">
                                    <EditFormInput
                                        type="text"
                                        name="give_point"
                                        value={s.values?.give_point || ''}
                                        placeholder={'지급할 포인트 금액'}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        className=""
                                    />
                                    <div className="text-zinc-400 text-xs mt-2">지급할 포인트 금액 (숫자만 입력)</div>
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">포인트 유효일</EditFormTH>
                                <EditFormTD className="col-span-2 !block">
                                    <EditFormInput
                                        type="text"
                                        name="exp_date"
                                        value={s.values?.exp_date || ''}
                                        placeholder={'지급일로 부터 며칠인지 기입'}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        className=""
                                    />
                                    <div className="text-zinc-400 text-xs mt-2">지급일로 부터 며칠동안 사용가능한지 (숫자만 입력)</div>
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">언제까지 지급할건지</EditFormTH>
                                <EditFormTD className="col-span-2 !block">
                                    <EditFormInput
                                        type="text"
                                        name="end_date"
                                        value={s.values?.end_date || ''}
                                        placeholder={'YYYY-MM-DD'}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        className=""
                                    />
                                    <div className="text-zinc-400 text-xs mt-2">신규인원 등록일 기준 언제까지 드림포인트를 지급될건지 날짜로 기입 (ex) 2023-09-11</div>
                                </EditFormTD>
                                <EditFormTH className="col-span-1">관리자 메모</EditFormTH>
                                <EditFormTD className="col-span-2 !block">
                                    <EditFormInput
                                        type="text"
                                        name="memo"
                                        value={s.values?.memo || ''}
                                        placeholder={'특이사항이 있다면 입력'}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        className=""
                                    />
                                    <div className="text-zinc-400 text-xs mt-2">특이사항이 있다면 입력</div>
                                </EditFormTD>
                            </EditFormTable>
                            <EditFormSubmit button_name={`${s.values?.uid > 0 ? '수정' : '등록'}하기`} submitting={s.submitting}></EditFormSubmit>
                        </EditFormCardBody>
                    </EditFormCard>

                    {posts?.uid > 0 && (
                        <EditFormCard>
                            <EditFormCardHead>
                                <div className="text-lg">
                                    <span className="text-xl font-bold me-3">고객사 관리자 정보</span>
                                    <span className="text-red-500 text-base">고객사 관리자 정보는 [수정하기]와 별개로 바로 저장됩니다.</span>
                                </div>
                            </EditFormCardHead>
                            <EditFormCardBody>
                                <div className="flex justify-between items-center mb-4">
                                    <button
                                        className="btn-search-line px-2 py-1"
                                        type="button"
                                        onClick={() => {
                                            openManagerEdit(0, 'REG', posts?.uid);
                                        }}
                                    >
                                        신규담당자 추가
                                    </button>
                                </div>

                                <ListTable>
                                    <ListTableHead>
                                        <th>번호</th>
                                        <th>역할</th>
                                        <th>아이디</th>
                                        <th>담당자명</th>
                                        <th>일반전화</th>
                                        <th>휴대전화</th>
                                        <th>이메일</th>
                                        <th>수정/삭제</th>
                                    </ListTableHead>

                                    <ListTableBody>
                                        {managerSort?.map((v: any, i: number) => (
                                            <tr key={`list-table-${i}`} className="">
                                                <td className="text-center">{v.uid}</td>
                                                <td className="text-center">
                                                    {v.role == 'master' ? <div className="font-bold text-red-500">{v.role}</div> : <div>{v.roles_txt}</div>}
                                                </td>
                                                <td className="text-center">{v.login_id}</td>
                                                <td className="text-centerbreak-all">{v.name}</td>
                                                <td className="text-center">{v.tel}</td>
                                                <td className="text-center">{v.mobile}</td>
                                                <td className="text-center">{v.email}</td>
                                                <td className="text-center">
                                                    <button
                                                        className="btn-search-line !h-8 !p-0 !px-3 mr-5"
                                                        type="button"
                                                        onClick={() => {
                                                            openManagerEdit(v.uid, 'MOD', v.partner_uid);
                                                        }}
                                                    >
                                                        수정
                                                    </button>
                                                    <button
                                                        className="btn-red-line !h-8 !p-0 !px-3"
                                                        type="button"
                                                        onClick={() => {
                                                            openManagerEdit(v.uid, 'DEL', v.partner_uid);
                                                        }}
                                                    >
                                                        삭제
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                    </ListTableBody>
                                </ListTable>
                            </EditFormCardBody>
                        </EditFormCard>
                    )}
                </EditForm>
                {managerEditOpen && <ManagerEdit setManagerEditOpen={setManagerEditOpen} stateInfo={stateInfo} />}
            </LayoutPopup>
        </>
    );
};
export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {
        uid: ctx.query.uid,
    };
    var response: any = {};
    try {
        const { data } = await api.post(`/be/admin/entry/partner/read`, request);
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

export default BuildingPartnerEdit;
