import Attrs from '@/components/form/attrs';
import { checkNumeric, cls } from '@/libs/utils';
import { useState } from 'react';

/*
    last update : 2024-01-04
    필수 : name, rows, value, values, set_values, errors
    선택 : max_length, placeholder, className, is_mand
    [2024-01-04] handlechange를 안에서 할거라서 values와 setValues 필요
    [2024-01-04] 글자수 세기 할거면 max_length 보내면 됨
*/

export default function EditFormTextarea(props: any) {
    const { name, rows, value, values, set_values, errors, max_length, placeholder, className, is_mand }: any = props;
    const { attrs } = Attrs();

    const [counts, setCounts] = useState<any>(0);

    const handleChangeTextarea = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        const count = e.target.value.length;
        let trans_value = value;
        if (checkNumeric(max_length) > 0 && max_length <= counts) {
            alert('최대 ' + max_length + '글자 까지 입력 가능합니다.');
        } else {
            set_values({ ...values, [name]: trans_value });
            if (checkNumeric(max_length) > 0) {
                setCounts(count);
            }
        }
    };

    return (
        <div className={cls('w-full', className)}>
            <textarea
                name={name}
                {...(is_mand && { ...attrs.is_mand })}
                rows={rows}
                placeholder={placeholder}
                onChange={handleChangeTextarea}
                value={value || ''}
                className={cls(errors[name] ? 'border-danger' : '', 'form-control')}
            ></textarea>
            {max_length && (
                <div className="text-xs text-start">
                    {counts ? counts : '0'}/{max_length}
                </div>
            )}
            <div>{errors[name] && <div className="form-error">{errors[name]}</div>}</div>
        </div>
    );
}
//
