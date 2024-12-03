import { cls } from '@/libs/utils';
import { useEffect } from 'react';
import Datepicker from 'react-tailwindcss-datepicker';

/*
    날짜 범위 선택
    last update : 2024-01-03
    필수 : input_name, values, handleChange, className, errors
*/

export default function EditFormDateRange(props: any) {
    const { input_name, values, handleChange, className, is_mand, errors } = props;
    useEffect(() => {
        if (is_mand) {
            (document.getElementById(input_name) as HTMLElement)?.setAttribute('is_mand', 'true');
        }
    }, []);
    return (
        <>
            <Datepicker
                inputClassName={cls('h-8 py-2 px-3 w-72 text-09 bg-transparent')}
                containerClassName={cls('relative text-gray-700 border border-gray-300 rounded', errors[input_name] ? 'border-danger' : '', className)}
                inputName={input_name}
                value={values}
                i18n={'ko'}
                onChange={handleChange}
            />
            <div>{errors[input_name] && <div className="form-error">{errors[input_name]}</div>}</div>
        </>
    );
}
//
