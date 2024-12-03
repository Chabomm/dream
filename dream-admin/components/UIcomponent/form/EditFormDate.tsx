import { cls } from '@/libs/utils';
import { useEffect } from 'react';
import Datepicker from 'react-tailwindcss-datepicker';

/*
    단일 날짜 선택
    last update : 2024-01-11
    필수 : input_name, values, handleChange, className, errors
    [2024-01-11] 기본 init value startdate, enddate로 세팅되게 함 
*/

export default function EditFormDate(props: any) {
    const { input_name, values, handleChange, className, is_mand, errors } = props;
    useEffect(() => {
        if (is_mand) {
            (document.getElementById(input_name) as HTMLElement)?.setAttribute('is_mand', 'true');
        }
    }, []);

    return (
        <>
            <Datepicker
                inputClassName={cls('h-8 py-2 px-3 text-09 bg-transparent')}
                containerClassName={cls('relative text-gray-700 border border-gray-300 rounded', errors[input_name] ? 'border-danger' : '', className)}
                inputName={input_name}
                inputId={input_name}
                value={{
                    startDate: values || '',
                    endDate: values || '',
                }}
                useRange={false}
                asSingle={true}
                i18n={'ko'}
                onChange={handleChange}
            />
            <div>{errors[input_name] && <div className="form-error">{errors[input_name]}</div>}</div>
        </>
    );
}
//
