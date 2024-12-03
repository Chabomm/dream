import React, { useEffect, useState } from 'react';
import api from '@/libs/axios';
import { useRouter } from 'next/router';

import { AModal, AModalHeader, AModalBody, AModalFooter } from '@/components/UIcomponent/modal/ModalA';
import { EditForm, EditFormInput, EditFormSubmit } from '../UIcomponent/form/EditFormA';
import EditFormToggle from '@/components/UIcomponent/form/EditFormToggle';
import useForm from '../form/useForm';

export default function ConfirmStateEdit({ setConfirmEditOpen, params, posts }: any) {
    const router = useRouter();

    useEffect(() => {
        if (posts?.state == params?.state) {
            editing('EDIT');
        }
    }, []);

    const { s, fn } = useForm({
        initialValues: {},
        onSubmit: () => {
            editing('REG');
        },
    });

    const editing = async mode => {
        try {
            const { data } = await api.post(`/be/manager/point/exuse/confirm/edit`, params);
            s.setSubmitting(false);
            if (data.code == 200) {
                alert(data.msg);
                router.reload();
            } else {
                alert(data.msg);
            }
        } catch (e: any) {}
    };

    const closeModal = () => {
        setConfirmEditOpen(false);
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

    if (posts?.state != params?.state) {
        return (
            <AModal onclick={closeModal} width_style={'800px'}>
                <AModalHeader onclick={closeModal}>선택항목 {params.state} 처리</AModalHeader>
                <AModalBody>
                    <EditForm onSubmit={fn.handleSubmit}>
                        <div className="px-6 border-b text-center">
                            <div className="py-3">
                                <div className="font-bold mb-3">선택한 항목을 {params.state}처리 하시겠습니까?</div>

                                {params.state == '소명신청' && (
                                    <div className="pt-4">
                                        ‘완료’를 누르면 신청자가 최초 소명신청한 상태도 돌아갑니다. 소명신청 상태로 전환되면 해당 건을 다시 ‘미승인(반려)’ 처리 할 수 있습니다.
                                    </div>
                                )}
                            </div>

                            <div className="border-t-2 border-blue-700 py-3 text-start">
                                <div>※ 소명신청자에게 처리 결과 메일 전송 을 원할 경우 하단의 ‘처리결과 메일전송’에 체크해주세요.</div>
                                <div className="my-3">
                                    ※ ‘처리결과 메일전송’ 클릭 시 선택 건 별로 처리결과가 개별 전송되며, 전송된 메일의 보내는 사람 정보에 해당 처리를 진행한 담당자의 정보가
                                    반영됩니다. (이름/이메일 주소)
                                </div>

                                <div className="ms-2">
                                    <EditFormToggle name={'mall_name'} onChange={handleChangeToggle}>
                                        처리결과 메일전송
                                    </EditFormToggle>
                                </div>
                            </div>
                            {params.state == '미승인(반려)' && (
                                <div className="border-t-2 border-blue-700 py-3 text-start">
                                    <div>※ 미승인(반려)처리된 이후 신청자가 해당 건을 다시 소명신청 할 수 있도록 설정하시려면 하단의 ‘재차감 설정’에 체크해주세요.</div>
                                    <div className="my-3">
                                        ※ 지금 ‘재차감 설정’에 체크하지 않아도 <span className="font-bold">소명승인 → 검색조건_처리상태 → 미승인(반려)</span> 선택 후 조회된
                                        검색결과 페이지에서 재차감 설정이 가능합니다.
                                    </div>
                                    <div className="text-blue-500 text-center">재차감 설정</div>
                                </div>
                            )}
                        </div>
                        <div className="w-full text-center">
                            <EditFormSubmit button_name={'처리하기'} submitting={s.submitting}></EditFormSubmit>
                        </div>
                    </EditForm>
                </AModalBody>
            </AModal>
        );
    }
}
