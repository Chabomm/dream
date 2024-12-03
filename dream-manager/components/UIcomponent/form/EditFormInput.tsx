import Attrs from '@/components/form/attrs';
import { checkNumeric, cls } from '@/libs/utils';
import { numToKorean } from 'num-to-korean';

/*
    last update : 2024-01-24
    [2024-01-24] is_number 숫자만 입력할 수 있게 하는 attr 추가
    [2024-01-24] is_price 숫자만 입력할 수 있게 + 3자리 마다 콤마
    [2024-01-24] values, set_values 보내면 내부 handle change 돌게함
*/

export default function EditFormInput(props: any) {
    const {
        type,
        name,
        value,
        placeholder,
        onChange,
        className,
        autoComplete,
        errors,
        is_mand,
        is_mobile,
        is_email,
        is_bizno,
        is_number,
        is_price,
        disabled,
        inputClassName,
        values,
        set_values,
    }: any = props;
    const { attrs } = Attrs();

    const customHandleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value, checked } = e.target;
        let trans_value = value;
        if (is_mobile) {
            trans_value = value
                .replace(/[^0-9]/g, '')
                .replace(/(^02|^0505|^1[0-9]{3}|^0[0-9]{2})([0-9]+)?([0-9]{4})$/, '$1-$2-$3')
                .replace('--', '-');
        }

        if (is_bizno) {
            trans_value = value
                .replace(/[^0-9]/g, '')
                .replace(/(\d{3})(\d{2})(\d{5})/, '$1-$2-$3')
                .replace('--', '-');
        }

        if (is_number) {
            trans_value = value.replace(/[^0-9]/g, '');
        }

        if (is_price) {
            trans_value = value.replace(/[^0-9]/g, '');
            trans_value = formatComma(trans_value, 0);
        }

        // console.log(value, numToKorean(checkNumeric(value)));

        // set_values({ ...values, save_point_kor: numToKorean(checkNumeric(value)) });

        // copy.save_point_kor = copy.save_point_kor != '' ? copy.save_point_kor + '원' : '';

        // s.setValues(copy);

        set_values({ ...values, [name]: trans_value });
    };

    // 콤마(,) 제거 ##################################################
    function stripComma(str) {
        var re = /,/g;
        return str.replace(re, '');
    }

    // 숫자 3자리수마다 콤마(,) 찍기 ##################################################
    function formatComma(num, pos) {
        if (!pos) pos = 0; //소숫점 이하 자리수
        var re = /(-?\d+)(\d{3}[,.])/;

        var strNum = stripComma(num.toString());
        var arrNum = strNum.split('.');

        arrNum[0] += '.';

        while (re.test(arrNum[0])) {
            arrNum[0] = arrNum[0].replace(re, '$1,$2');
        }

        if (arrNum.length > 1) {
            if (arrNum[1].length > pos) {
                arrNum[1] = arrNum[1].substr(0, pos);
            }
            return arrNum.join('');
        } else {
            return arrNum[0].split('.')[0];
        }
    }

    return (
        <div className={className}>
            <input
                type={type}
                name={name}
                value={value || ''}
                {...(is_mand && { ...attrs.is_mand })}
                {...(is_mobile && { ...attrs.is_mobile })}
                {...(is_email && { ...attrs.is_email })}
                {...(is_bizno && { ...attrs.is_bizno })}
                placeholder={placeholder}
                onChange={values ? customHandleChange : onChange}
                className={cls(errors[name] ? 'border-danger' : '', 'form-control', inputClassName)}
                autoComplete={autoComplete}
                disabled={disabled}
            />
            <div>{errors[name] && <div className="form-error">{errors[name]}</div>}</div>
        </div>
    );
}
//
