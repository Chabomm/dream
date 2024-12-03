import Attrs from '@/components/form/attrs';
import { cls } from '@/libs/utils';

export default function EditFormInputGroup(props: any) {
    const { type, name, value, placeholder, onChange, className, autoComplete, errors, button_name, button_click, is_mand, is_mobile, is_email, is_bizno }: any = props;
    const { attrs } = Attrs();
    return (
        <div className="">
            <div className="input-group">
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
                    className={cls(className, errors[name] ? 'border-danger' : '', 'form-control !rounded-e-none')}
                    autoComplete={autoComplete}
                    style={{ 'margin-right': '-1px' }}
                />
                <button className="form-control-button !rounded-s-none" onClick={button_click} type="button">
                    {button_name}
                </button>
            </div>
            <div>{errors[name] && <div className="form-error">{errors[name]}</div>}</div>
        </div>
    );
}
//
