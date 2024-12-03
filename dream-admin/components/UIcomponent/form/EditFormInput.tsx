import Attrs from '@/components/form/attrs';
import { cls } from '@/libs/utils';

export default function EditFormInput(props: any) {
    const { type, name, value, placeholder, onChange, className, autoComplete, errors, is_mand, is_mobile, is_email, is_bizno, disabled, inputClassName }: any = props;
    const { attrs } = Attrs();
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
                onChange={onChange}
                className={cls(errors[name] ? 'border-danger' : '', 'form-control', inputClassName)}
                autoComplete={autoComplete}
                disabled={disabled}
            />
            <div>{errors[name] && <div className="form-error">{errors[name]}</div>}</div>
        </div>
    );
}
//
