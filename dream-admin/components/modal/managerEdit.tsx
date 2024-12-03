import React, { useEffect, useState } from 'react';
import useForm from '../form/useForm';
import { checkNumeric, cls } from '@/libs/utils';
import api from '@/libs/axios';
import { useRouter } from 'next/router';
import { EditFormLabel } from '@/components/UIcomponent/form/EditFormA';
import EditFormToggle from '../UIcomponent/form/EditFormToggle';

import { EditForm, EditFormTable, EditFormTH, EditFormTD, EditFormSubmit, EditFormInput, EditFormCheckboxList } from '@/components/UIcomponent/form/EditFormA';

import { AModal, AModalHeader, AModalBody, AModalFooter } from '@/components/UIcomponent/modal/ModalA';

interface ModalProps {
    setManagerEditOpen?: any;
    stateInfo?: any;
}
export default function ManagerEdit({ setManagerEditOpen, stateInfo }: ModalProps) {
    const router = useRouter();
    const [params, setParams] = useState<any>({});
    const [posts, setPosts] = useState<any>({});
    const [filter, setFilter] = useState<any>({});

    useEffect(() => {
        setParams(stateInfo);
        getData();
    }, []);

    const getData = async () => {
        const { data } = await api.post(`/be/admin/entry/manager/read`, stateInfo);
        setPosts(data);
        s.setValues(data.values);
        setFilter(data.filter);
    };

    const { s, fn } = useForm({
        initialValues: {},
        onSubmit: () => {
            editing();
        },
    });

    const closeModal = () => {
        setManagerEditOpen(false);
    };

    const editing = async () => {
        if (s.values.roles.length <= 0) {
            alert('역할을 하나 이상 선택하세요.');
            return;
        }
        try {
            s.values.mode = params.mode;
            s.values.partner_id = params.partner_id;
            s.values.partner_uid = params.partner_uid;
            s.values.prefix = params.prefix;

            const { data } = await api.post(`/be/admin/entry/manager/edit`, s.values);
            if (data.code == 200) {
                alert(data.msg);
                setManagerEditOpen(false);
                router.reload();
                // router.replace(`/entry/partner/edit?uid=${s.values.partner_uid}`);
            } else {
                alert(data.msg);
            }
            return;
        } catch (e: any) {}
    };

    const pw_reset = async () => {
        try {
            let confirm_msg = '비밀번호 초기화는 비밀번호와 아이디가 동일하게 됩니다. 계속하시겠습니까? ';
            if (!confirm(confirm_msg)) {
                return;
            }
            const { data } = await api.post(`/be/admin/entry/manager/pw/reset`, { uid: posts.uid });
            if (data.code == 200) {
                alert(data.msg);
                setManagerEditOpen(false);
                window.opener.edit_callback();
                router.replace(`/entry/partner/edit?uid=${s.values.partner_uid}`);
            } else {
                alert(data.msg);
            }
            return;
        } catch (e: any) {}
    };

    const handleChangeToggle = (e: React.ChangeEvent<HTMLInputElement>) => {
        const params = {
            target: e.target.name,
            checked: e.target.checked,
        };

        const copy = { ...s.values };
        if (params.checked == true) {
            copy[params.target] = 'master';
        } else {
            copy[params.target] = '';
        }
        s.setValues(copy);
    };

    return (
        <AModal onclick={closeModal} width={'1000px'}>
            <AModalHeader onclick={closeModal}>
                담당자 {params.mode == 'REG' ? '추가' : params.mode == 'MOD' ? '수정' : params.mode == 'DEL' ? '삭제' : params.mode == 'COPY' && '복사'}
            </AModalHeader>
            <AModalBody>
                <EditForm onSubmit={fn.handleSubmit}>
                    <EditFormTable className="grid-cols-6 mx-4">
                        <EditFormTH className="col-span-1 mand">로그인아이디</EditFormTH>
                        <EditFormTD className="col-span-2">
                            {(params.mode == 'REG' || params.mode == 'COPY') && (
                                <EditFormInput
                                    type="text"
                                    name="login_id"
                                    value={s.values?.login_id || ''}
                                    onChange={fn.handleChange}
                                    errors={s.errors}
                                    is_mand={true}
                                    is_email={true}
                                    className=""
                                    placeholder="이메일 형태만 가능합니다."
                                />
                            )}
                            {(params.mode == 'MOD' || params.mode == 'DEL') && <EditFormLabel className="">{posts?.login_id}</EditFormLabel>}
                        </EditFormTD>
                        <EditFormTH className="col-span-1">로그인비밀번호</EditFormTH>
                        <EditFormTD className="col-span-2 flex-col">
                            {(params.mode == 'MOD' || params.mode == 'DEL') && (
                                <button type="button" className="btn-filter mb-3" onClick={pw_reset}>
                                    비밀번호초기화
                                </button>
                            )}
                            <div className="!leading-4">초기 비밀번호는 아이디로 적용됩니다. 인증 후 비밀번호 변경이 가능합니다.</div>
                        </EditFormTD>
                        <EditFormTH className="col-span-1">담당자명</EditFormTH>
                        <EditFormTD className="col-span-2">
                            <EditFormInput type="text" name="name" value={s.values?.name || ''} onChange={fn.handleChange} errors={s.errors} is_mand={true} className="" />
                        </EditFormTD>
                        <EditFormTH className="col-span-1">이메일</EditFormTH>
                        <EditFormTD className="col-span-2">
                            {(params.mode == 'REG' || params.mode == 'COPY') && (
                                <EditFormInput
                                    type="text"
                                    name="login_id"
                                    value={s.values?.login_id || ''}
                                    onChange={fn.handleChange}
                                    errors={s.errors}
                                    is_mand={true}
                                    is_email={true}
                                    className=""
                                    placeholder="이메일 형태만 가능합니다."
                                />
                            )}
                            {params.mode == 'MOD' && (
                                <EditFormInput
                                    type="text"
                                    name="email"
                                    value={s.values?.email || ''}
                                    onChange={fn.handleChange}
                                    errors={s.errors}
                                    is_mand={true}
                                    is_email={true}
                                    className=""
                                    placeholder="이메일 형태만 가능합니다."
                                />
                            )}
                            {params.mode == 'DEL' && <EditFormLabel className="">{posts?.email}</EditFormLabel>}
                        </EditFormTD>
                        <EditFormTH className="col-span-1">휴대전화</EditFormTH>
                        <EditFormTD className="col-span-2">
                            <EditFormInput
                                type="text"
                                name="mobile"
                                value={s.values?.mobile || ''}
                                onChange={fn.handleChange}
                                errors={s.errors}
                                is_mand={true}
                                is_mobile={true}
                                className=""
                            />
                        </EditFormTD>
                        <EditFormTH className="col-span-1">일반전화</EditFormTH>
                        <EditFormTD className="col-span-2">
                            <EditFormInput type="text" name="tel" value={s.values?.tel || ''} onChange={fn.handleChange} errors={s.errors} className="" />
                        </EditFormTD>
                        <EditFormTH className="col-span-1">직급</EditFormTH>
                        <EditFormTD className="col-span-2">
                            <EditFormInput type="text" name="position1" value={s.values?.position1 || ''} onChange={fn.handleChange} errors={s.errors} className="" />
                        </EditFormTD>
                        <EditFormTH className="col-span-1">직책</EditFormTH>
                        <EditFormTD className="col-span-2">
                            <EditFormInput type="text" name="position2" value={s.values?.position2 || ''} onChange={fn.handleChange} errors={s.errors} className="" />
                        </EditFormTD>
                        <EditFormTH className="col-span-1">부서</EditFormTH>
                        <EditFormTD className="col-span-2">
                            <EditFormInput type="text" name="depart" value={s.values?.depart || ''} onChange={fn.handleChange} errors={s.errors} className="" />
                        </EditFormTD>
                        <EditFormTH className="col-span-1">마스터권한</EditFormTH>
                        <EditFormTD className="col-span-2">
                            {/* <EditFormInput type="text" name="role" value="mster" onChange={fn.handleChange} errors={s.errors} className="" /> */}
                            <EditFormToggle name={'role'} onChange={handleChangeToggle} checked={s.values.role == 'master' ? true : false}>
                                마스터권한
                            </EditFormToggle>
                        </EditFormTD>
                        <EditFormTH className="col-span-1">역할</EditFormTH>
                        <EditFormTD className="col-span-5">
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
                    <EditFormSubmit
                        button_name={params.mode == 'REG' ? '저장' : params.mode == 'MOD' ? '수정' : params.mode == 'DEL' ? '삭제' : '복사'}
                        submitting={s.submitting}
                    ></EditFormSubmit>
                </EditForm>
            </AModalBody>
        </AModal>
    );
}
