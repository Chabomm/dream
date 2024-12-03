import { checkNumeric, cls } from '@/libs/utils';
import React, { useEffect, useState } from 'react';
import { AModal, AModalHeader, AModalBody, AModalFooter } from '@/components/UIcomponent/modal/ModalA';
import useForm from '@/components/form/useForm';
import { EditForm, EditFormTable, EditFormTH, EditFormTD, EditFormSubmit, EditFormInput, EditFormCheckboxList, EditFormLabel } from '@/components/UIcomponent/form/EditFormA';
import EditFormCallout from '@/components/UIcomponent/form/EditFormCallout';
import { numToKorean } from 'num-to-korean';

export default function PointBalanceFin(props: any) {
    const { className, open, setOpen, balanceInfo, reload_page } = props;

    useEffect(() => {
        const num2Curs: any = document.querySelectorAll('.num2Cur') || undefined;
        num2Curs.forEach(function (v) {
            v.innerText = v.innerText.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
        });
    }, [balanceInfo]);

    const callout = [
        '예치금충전은 무통장입금으로 진행 가능합니다.',
        '입금자명은 반드시 실제 입금하는 입금자명으로 입력해주세요',
        '포인트 충전과 관련한 내용은 하단 입금금액/포인트 충전 내역에서 확인 가능합니다.',
        '입금 확인은 입금 후 1~2분내 확인 가능합니다.',
    ];

    const closeModal = () => {
        setOpen(false);
    };
    const { s, fn } = useForm({
        initialValues: {},
        onSubmit: () => {
            editing('REG');
        },
    });

    const deleting = () => editing('DEL');

    const editing = async mode => {
        reload_page();
        setOpen(false);
    };

    // const number = numToKorean(12354678);
    // console.log('number', number);

    const getSavePointTxt = () => {
        return (
            <div>
                <span className="num2Cur won">{balanceInfo?.save_point}</span> <span>{numToKorean(checkNumeric(balanceInfo?.save_point))}</span>
            </div>
        );
    };

    return (
        <div className={cls(className)}>
            <div className={cls(open ? '' : 'hidden')}>
                <AModal width_style={'800px'}>
                    <AModalBody className="px-4">
                        <EditFormCallout title={'예치금 충전 신청완료'} title_sub={''} callout={callout} />

                        <div className="text-center text-lg font-bold">아래 입금계좌정보로 입금후 1~2분내 확인 가능합니다.</div>
                        <div className="text-center text-lg font-bold mb-5">입금은행과 입금자명 불일치시 확인이 지연될 수 있습니다.</div>

                        <EditForm onSubmit={fn.handleSubmit}>
                            <EditFormTable className="grid-cols-6">
                                <EditFormTH className="col-span-1">입금계좌정보</EditFormTH>
                                <EditFormTD className="col-span-5">
                                    <EditFormLabel className="">기업은행 472-058316-04-039</EditFormLabel>
                                </EditFormTD>
                                <EditFormTH className="col-span-1">충전금액</EditFormTH>
                                <EditFormTD className="col-span-5">
                                    <EditFormLabel className="!text-left">
                                        {/* {getSavePointTxt} */}
                                        <span className="won">{numToKorean(checkNumeric(balanceInfo?.save_point))}</span>(
                                        <span className="num2Cur won">{balanceInfo?.save_point}</span>)
                                    </EditFormLabel>
                                </EditFormTD>
                                <EditFormTH className="col-span-1">입금은행</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormLabel className="">{balanceInfo?.input_bank}</EditFormLabel>
                                </EditFormTD>
                                <EditFormTH className="col-span-1">입금자명</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormLabel className="">{balanceInfo?.input_name}</EditFormLabel>
                                </EditFormTD>
                                <EditFormTH className="col-span-1">관리자 메모</EditFormTH>
                                <EditFormTD className="col-span-5">
                                    <EditFormLabel className="">{balanceInfo?.reason}</EditFormLabel>
                                </EditFormTD>
                            </EditFormTable>
                            <EditFormSubmit button_name={`확인 및 닫기`} submitting={s.submitting}></EditFormSubmit>
                        </EditForm>
                    </AModalBody>
                </AModal>
            </div>
        </div>
    );
}
