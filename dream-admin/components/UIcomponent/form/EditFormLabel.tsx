import { cls } from '@/libs/utils';

export default function EditFormLabel({ children, className }) {
    return <div className={cls('form-control', className)}>{children}</div>;
}
