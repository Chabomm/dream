import { api } from '@/libs/axios';
import React, { useState, forwardRef, useImperativeHandle } from 'react';
import { checkNumeric, cls } from '@/libs/utils';
import useForm from '@/components/form/useForm';

interface Iprops {
    callback: (arg: any) => void;
}

const PartnerChoice = forwardRef(({ callback }: Iprops, ref) => {
    const [open, setOpen] = useState<boolean>(false);
    const [show, setShow] = useState<boolean>(false);

    const onToggle = () => {
        setShow(!open);
        setOpen(!open);
    };

    useImperativeHandle(ref, () => ({
        init,
        onToggle,
    }));

    function init(p) {
        // alert('현재 [앱사용자전체]만 이용 가능합니다.');
        s.setValues({ ...s.values, partners: p });
        getDataRead();
        setOpen(true);
    }

    const [partners, setPartners] = useState<any>({});
    const getDataRead = async () => {
        try {
            const { data } = await api.post(`/ums/push/rec_type/partners`, {});
            setPartners(data);
            setShow(true);
        } catch (e: any) {}
    };

    const { s, fn, attrs } = useForm({
        initialValues: {
            partners: [],
        },
        onSubmit: async () => {
            await editing('REG');
        },
    });

    const deleting = () => editing('DEL');

    const editing = async mode => {
        callback(s.values.partners);
    };

    return (
        <>
            {open && (
                <>
                    <form onSubmit={fn.handleSubmit} noValidate className={cls('offcanvas', show ? 'show' : '')}>
                        <div className="offcanvas-header">
                            <div className="">푸쉬 발송 예약 - 고객사 선택</div>
                            <i className="fas fa-times btn-close" onClick={onToggle}></i>
                        </div>
                        <div className="offcanvas-body">
                            {process.env.NODE_ENV == 'development' && (
                                <pre className="">
                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <div className="font-bold mb-3 text-red-500">s.values</div>
                                            {JSON.stringify(s.values, null, 4)}
                                        </div>
                                    </div>
                                </pre>
                            )}
                            <div className="mb-3 text-sm text-gray-500">* 괄호는 현재 기준 active device</div>
                            <div className="grid grid-cols-2 checkbox_filter">
                                {partners.list?.map((v: any, i: number) => (
                                    <div className="checkboxs_wrap" key={i} style={{ height: 'auto' }}>
                                        <label>
                                            <input
                                                id={`state-${i}`}
                                                defaultChecked={s.values.partners.filter(p => p == v.uid) == checkNumeric(v.uid) ? true : false}
                                                onChange={fn.handleCheckboxGroupForInteger}
                                                type="checkbox"
                                                value={v.uid}
                                                name="partners"
                                            />
                                            <span className="ml-3">
                                                {v.mall_name} ({v.count})
                                            </span>
                                        </label>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="offcanvas-footer grid grid-cols-3 gap-4">
                            <button className="btn-del" type="button" onClick={onToggle}>
                                {'<'} 뒤로가기
                            </button>
                            <button className="btn-save col-span-2 hover:bg-blue-600" disabled={s.submitting}>
                                저장
                            </button>
                        </div>
                    </form>
                    <div className="offcanvas-backdrop fade" onClick={onToggle}></div>
                </>
            )}
        </>
    );
});

PartnerChoice.displayName = 'PartnerChoice';
export default PartnerChoice;
