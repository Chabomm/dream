import React, { useState, forwardRef, useImperativeHandle, useRef } from 'react';
import { cls, getToken } from '@/libs/utils';
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
        alert('현재 [앱사용자전체]만 이용 가능합니다.');
        // s.setValues({ ...s.values, partners: p });
        // getDataRead();
        // setOpen(true);
    }

    const [partners, setPartners] = useState<any>({});
    const getDataRead = async () => {
        // axios.defaults.headers.common['Authorization'] = `Bearer ${getToken(null)}`;
        // const res = await axios.post(`/be/admin/ums/push/rec_type/partners`, {});
        // const result = res.data;
        // setPartners(result);
        setShow(true);
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
                            <div className="">푸쉬 발송 예약 - 디바이스 선택</div>
                            <i className="fas fa-times btn-close" onClick={onToggle}></i>
                        </div>
                        <div className="offcanvas-body">
                            <div className="grid grid-cols-2 checkbox_filter">
                                {partners.list?.map((v: any, i: number) => (
                                    <div className="checkboxs_wrap" key={i} style={{ height: 'auto' }}>
                                        <label>
                                            <input
                                                id={`state-${i}`}
                                                defaultChecked={s.values.partners.filter(p => p == v.uid) == v.uid ? true : false}
                                                onChange={fn.handleCheckboxGroup}
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
