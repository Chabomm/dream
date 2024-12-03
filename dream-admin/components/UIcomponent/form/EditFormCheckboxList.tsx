import { cls, checkNumeric } from '@/libs/utils';
import Attrs from '@/components/form/attrs';

/*
    체크박스 리스트
    last update : 2024-01-03
    필수 : filter_list, input_name, handleChange, values, cols
    [2024-01-02] handleChange는 두 가지 종류를 가짐
                fn.handleCheckboxGroup : values 배열에 문자를 가지는 경우
                fn.handleCheckboxGroupForInteger : values 배열에 숫자를 가지는 경우
    [2024-01-02] cols는 몇 칸으로 나눌지 판별
    [2024-01-03] is_mand 체크 가능하도록 함
*/

export default function EditFormCheckboxList(props: any) {
    const { filter_list, input_name, handleChange, values, cols, errors, is_mand } = props;
    const { attrs } = Attrs();

    const fn_checked = (key: any) => {
        if (handleChange.name == 'handleCheckboxGroup') {
            return values.includes(key);
        } else if (handleChange.name == 'handleCheckboxGroupForInteger') {
            return values?.filter(p => p == key) == checkNumeric(key) ? true : false;
        }
    };

    return (
        <div className="w-full flex-col">
            <div className={`grid grid-cols-${cols} checkbox_filter !m-0 !p-0 !border-t-0 w-full`}>
                {filter_list?.map((v: any, i: number) => (
                    <div className="checkboxs_wrap col-span-1 flex items-center mr-4 hover:text-blue-700 hover:font-bold h-8" key={`${input_name}-${i}`} style={{ height: 'auto' }}>
                        <label className="">
                            <input
                                id={`${input_name}-${i}`}
                                onChange={handleChange}
                                type="checkbox"
                                {...(is_mand && { ...attrs.is_mand })}
                                value={v.key}
                                checked={fn_checked(v.key)}
                                name={`${input_name}`}
                                className="w-4 h-4"
                            />
                            <span className="">{v.text}</span>
                        </label>
                    </div>
                ))}
            </div>
            <div>{errors[input_name] && <div className="form-error">{errors[input_name]}</div>}</div>
        </div>
    );
}
//
