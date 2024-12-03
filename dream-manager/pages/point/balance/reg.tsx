import { checkNumeric, cls } from '@/libs/utils';
import { api, setContext } from '@/libs/axios';
import React, { useEffect, useState } from 'react';
import { AModal, AModalHeader, AModalBody, AModalFooter } from '@/components/UIcomponent/modal/ModalA';
import useForm from '@/components/form/useForm';
import { EditForm, EditFormTable, EditFormTH, EditFormTD, EditFormSubmit, EditFormInput, EditFormCheckboxList, EditFormLabel } from '@/components/UIcomponent/form/EditFormA';
import EditFormCallout from '@/components/UIcomponent/form/EditFormCallout';
import { numToKorean } from 'num-to-korean';

export default function PointBalanceReg(props: any) {
    const { className, callback, getDataValue } = props;
    const [open, setOpen] = useState<any>(false);
    const callout = [
        '예치금충전은 무통장입금으로 진행 가능합니다.',
        '입금자명은 반드시 실제 입금하는 입금자명으로 입력해주세요',
        '포인트 충전과 관련한 내용은 하단 입금금액/포인트 충전 내역에서 확인 가능합니다.',
        '입금 확인은 입금 후 1~2분내 확인 가능합니다.',
    ];

    const closeModal = () => {
        s.setValues({
            save_point: 0,
            save_point_kor: '',
            input_bank: '기업은행',
            input_name: '주식회사 인디앤드코리아',
            reason: '',
        });

        setOpen(false);
    };

    const sendDataValue = (data: any) => {
        getDataValue(data);
    };

    const { s, fn } = useForm({
        initialValues: {
            save_point: 0,
            save_point_kor: '',
            input_bank: '기업은행',
            input_name: '주식회사 인디앤드코리아',
            reason: '',
        },
        onSubmit: () => {
            editing('REG');
        },
    });

    const [savePointKor, setSavePointKor] = useState<Boolean>(false);
    useEffect(() => {
        const copy = s.values;
        copy.save_point_kor = numToKorean(checkNumeric(s.values.save_point));
        copy.save_point_kor = copy.save_point_kor != '' ? copy.save_point_kor + '원' : '';
        s.setValues(copy);
        if (copy.save_point_kor != '') {
            setSavePointKor(true);
            return;
        }
        setSavePointKor(false);
    }, [s.values.save_point]);

    const upToPoint = point => {
        var copy = { ...s.values };
        copy.save_point = checkNumeric(copy.save_point) + checkNumeric(point);
        copy.save_point_kor = numToKorean(checkNumeric(copy.save_point));
        copy.save_point_kor = copy.save_point_kor != '' ? copy.save_point_kor + '원' : '';
        s.setValues(copy);
    };

    const deleting = () => editing('DEL');

    const editing = async mode => {
        try {
            const params = { ...s.values };

            const { data } = await api.post(`/be/manager/point/balance/edit`, params);
            s.setSubmitting(false);
            if (data.code == 200) {
                alert(data.msg);
                callback();
                setOpen(false);
                sendDataValue(data);
            } else {
                alert(data.msg);
            }
        } catch (e: any) {}
    };

    return (
        <div className={cls(className)}>
            <button
                onClick={() => {
                    setOpen(!open);
                }}
                className="text-sm text-blue-600 me-2"
            >
                <i className="far fa-plus-square me-2"></i>예치금 충전
            </button>

            <div className={cls(open ? '' : 'hidden')}>
                <AModal onclick={closeModal} width_style={'800px'}>
                    <AModalBody className="px-4">
                        <EditFormCallout title={'예치금 충전'} title_sub={''} callout={callout} />
                        <EditForm onSubmit={fn.handleSubmit}>
                            <EditFormTable className="grid-cols-6">
                                <EditFormTH className="col-span-1">입금계좌정보</EditFormTH>
                                <EditFormTD className="col-span-5">
                                    <EditFormLabel className="">충전하기 후 계좌번호가 노출됩니다.</EditFormLabel>
                                </EditFormTD>
                                <EditFormTH className="col-span-1">충전금액</EditFormTH>
                                <EditFormTD className="col-span-5 flex-col !items-start">
                                    <div className="flex items-center">
                                        <EditFormInput
                                            type="text"
                                            name="save_point"
                                            is_mand={true}
                                            is_price={true}
                                            value={s.values?.save_point || ''}
                                            errors={s.errors}
                                            className=""
                                            values={s.values}
                                            set_values={s.setValues}
                                        />
                                        <div className="ms-3">
                                            <button
                                                type="button"
                                                onClick={() => {
                                                    upToPoint(100000);
                                                }}
                                                className="border rounded-md me-2 py-1 px-2"
                                            >
                                                +100,000
                                            </button>
                                            <button
                                                type="button"
                                                onClick={() => {
                                                    upToPoint(500000);
                                                }}
                                                className="border rounded-md me-2 py-1 px-2"
                                            >
                                                +500,000
                                            </button>
                                            <button
                                                type="button"
                                                onClick={() => {
                                                    upToPoint(1000000);
                                                }}
                                                className="border rounded-md me-2 py-1 px-2"
                                            >
                                                +1,000,000
                                            </button>
                                        </div>
                                    </div>
                                    {savePointKor ? <EditFormLabel className="mt-3">{s.values.save_point_kor}</EditFormLabel> : null}
                                </EditFormTD>
                                <EditFormTH className="col-span-1">입금은행</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput
                                        type="text"
                                        name="input_bank"
                                        is_mand={true}
                                        value={s.values?.input_bank || ''}
                                        errors={s.errors}
                                        className=""
                                        values={s.values}
                                        set_values={s.setValues}
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1">입금자명</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput
                                        type="text"
                                        name="input_name"
                                        is_mand={true}
                                        value={s.values?.input_name || ''}
                                        errors={s.errors}
                                        className=""
                                        values={s.values}
                                        set_values={s.setValues}
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1">관리자 메모</EditFormTH>
                                <EditFormTD className="col-span-5">
                                    <EditFormInput
                                        type="text"
                                        name="reason"
                                        value={s.values?.reason || ''}
                                        errors={s.errors}
                                        className="w-full"
                                        values={s.values}
                                        set_values={s.setValues}
                                    />
                                </EditFormTD>
                            </EditFormTable>
                            <EditFormSubmit button_name={`충전하기`} submitting={s.submitting}></EditFormSubmit>
                        </EditForm>
                    </AModalBody>
                </AModal>
            </div>
        </div>
    );
}
