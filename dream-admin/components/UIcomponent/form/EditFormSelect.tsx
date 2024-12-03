import Attrs from '@/components/form/attrs';
import { cls } from '@/libs/utils';

/*
    last update : 2024-01-11
    [2024-01-11] errors, is_mand 추가
*/

export default function EditFormSelect(props: any) {
    const { input_name, value, filter_list, onChange, className, disabled, errors, is_mand }: any = props;
    const { attrs } = Attrs();
    return (
        <div className="flex-col">
            <select name={input_name} value={value || ''} onChange={onChange} {...(is_mand && { ...attrs.is_mand })} className={cls('form-select', className)} disabled={disabled}>
                <option value="">전체</option>
                {filter_list?.map((v, i) => (
                    <option key={i} value={v.key}>
                        {v.text}
                    </option>
                ))}
            </select>
            <div>{errors && errors[input_name] && <div className="form-error">{errors[input_name]}</div>}</div>
        </div>
    );
}
//
