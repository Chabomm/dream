import Attrs from '@/components/form/attrs';
import { cls } from '@/libs/utils';

/*
    last update : 2024-01-11
    [2024-01-11] errors, is_mand 추가
*/

export default function EditFormRadioList(props: any) {
    const { filter_list, input_name, handleChange, values, is_mand, errors } = props;
    const { attrs } = Attrs();
    return (
        <div className="flex-col">
            <div className="flex items-center">
                {filter_list?.map((v: any, i: number) => (
                    <div key={i} className="flex items-center mr-4 hover:text-blue-700 hover:font-bold h-8">
                        <input
                            id={`${input_name}-${i}`}
                            onChange={handleChange}
                            {...(is_mand && { ...attrs.is_mand })}
                            checked={values == v.key ? true : false}
                            type="radio"
                            value={v.key || ''}
                            name={input_name}
                            className={cls(errors[input_name] ? 'border-danger' : '', 'w-4 h-4')}
                        />
                        <label htmlFor={`${input_name}-${i}`} className="ps-2 text-sm font-medium">
                            {v.text}
                        </label>
                    </div>
                ))}
            </div>
            <div>{errors[input_name] && <div className="form-error">{errors[input_name]}</div>}</div>
        </div>
    );
}
//
