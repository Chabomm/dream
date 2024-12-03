import React from 'react';
import api from '@/libs/axios';
import useForm from '../form/useForm';
import { yyyymmdd_hhmmss } from '@/libs/utils';

import { EditForm, EditFormTextarea, EditFormButton, EditFormButtonWrap } from '@/components/UIcomponent/form/EditFormA';
import { AModal, AModalHeader, AModalBody, AModalFooter } from '@/components/UIcomponent/modal/ModalA';

interface ModalProps {
    setExcelModalOpen?: any;
    params?: any;
    url?: any;
    title?: any;
    failList?: any;
}
export default function ExcelModal({ setExcelModalOpen, params, url, title, failList }: ModalProps) {
    const closeModal = () => {
        setExcelModalOpen(false);
    };

    const { s, fn, attrs } = useForm({
        initialValues: {
            download_reason: '',
        },
        onSubmit: async () => {
            await fnEdit();
        },
    });
    const fnEdit = async () => {
        try {
            s.values.url = window.location.href;

            if (typeof params == 'undefined') {
                params = {
                    filters: {},
                };
            }

            s.values.params = params;

            if (typeof failList != 'undefined') {
                s.values.fail_list = failList;
            }

            await api({
                url: url,
                method: 'POST',
                responseType: 'blob',
                data: s.values,
            }).then(response => {
                var fileURL = window.URL.createObjectURL(new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }));
                var fileLink = document.createElement('a');
                fileLink.href = fileURL;
                fileLink.setAttribute('download', yyyymmdd_hhmmss() + '_' + title + '.xlsx');
                document.body.appendChild(fileLink);
                fileLink.click();

                s.setSubmitting(false);
                setExcelModalOpen(false);
            });
        } catch (e: any) {}
    };
    return (
        <AModal onclick={closeModal} width_style={'36rem'}>
            <AModalHeader onclick={closeModal}>엑셀 다운로드</AModalHeader>
            <AModalBody>
                <EditForm onSubmit={fn.handleSubmit}>
                    <div className="p-4 h-full ">
                        <EditFormTextarea
                            name="download_reason"
                            value={s.values?.download_reason || ''}
                            maxLength={50}
                            rows={5}
                            placeholder="다운로드 목적을 입력해 주세요."
                            errors={s.errors}
                            values={s.values}
                            is_mand={true}
                            max_length={100}
                            set_values={s.setValues}
                        />
                        <EditFormButtonWrap>
                            <EditFormButton onclick={closeModal} type={'button'} button_name="취소" />
                            <EditFormButton type={'submit'} button_name="다운로드" submitting={s.submitting} />
                        </EditFormButtonWrap>
                    </div>
                </EditForm>
            </AModalBody>
            <AModalFooter></AModalFooter>
        </AModal>
    );
}
