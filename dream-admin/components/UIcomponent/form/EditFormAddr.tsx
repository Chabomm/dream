import DaumPost from '@/components/DaumPost';
import Attrs from '@/components/form/attrs';
import { cls } from '@/libs/utils';
import { useState } from 'react';

/*
    주소검색 
    last update : 2024-01-03
    필수 : post, addr, addr_detail, values, set_values, onChange, errors
    [2024-01-03] post, addr, addr_detail에 각각 input의 name(state의 변수명)을 보내줘야함
    [2024-01-03] is_mand 처리 
*/

export default function EditFormAddr(props: any) {
    const { post, addr, addr_detail, values, set_values, is_mand, onChange, errors } = props;
    const { attrs } = Attrs();

    const [daumModal, setDaumModal] = useState(false);

    // 주소 모달에서 선택 후
    const handleCompleteFormSet = (data: any) => {
        const copy = { ...values };
        copy[post] = data.zonecode;
        copy[addr] = data.roadAddress;
        set_values(copy);
        const el = document.querySelector("input[name='" + addr_detail + "']");
        (el as HTMLElement)?.focus();
    };

    return (
        <div className="">
            {daumModal && <DaumPost daumModal={daumModal} setDaumModal={setDaumModal} handleCompleteFormSet={handleCompleteFormSet} />}

            <div className="input-group mb-3">
                <button
                    className="form-control-button !rounded-e-none"
                    type="button"
                    onClick={() => {
                        setDaumModal(true);
                    }}
                >
                    주소검색
                </button>
                <input name={post} value={typeof values !== 'undefined' ? values[post] : ''} type="text" className="hidden" readOnly />
                <input
                    name={addr}
                    value={typeof values !== 'undefined' ? values[addr] : ''}
                    onClick={() => {
                        setDaumModal(true);
                    }}
                    type="text"
                    {...(is_mand && { ...attrs.is_mand })}
                    className={cls('!rounded-s-none ', errors[addr] ? 'border-danger' : '', 'form-control')}
                    placeholder="주소를 검색해 주세요"
                    readOnly
                    style={{ marginLeft: '-1px' }}
                />
            </div>

            <div className="w-full">
                <input
                    name={addr_detail}
                    value={typeof values !== 'undefined' ? values[addr_detail] : ''}
                    onChange={onChange}
                    {...(is_mand && { ...attrs.is_mand })}
                    type="text"
                    className={cls(errors[addr_detail] ? 'border-danger' : '', 'form-control')}
                    placeholder="상세위치 입력 (예:○○빌딩 2층)"
                />
            </div>

            <div>{errors[addr] || errors[addr_detail] ? <div className="form-error">{errors[addr] || errors[addr_detail]}</div> : <></>}</div>
        </div>
    );
}
