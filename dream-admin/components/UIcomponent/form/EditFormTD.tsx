import { cls } from '@/libs/utils';

export default function EditFormTD({ children, className }) {
    return <div className={cls('edit-form-td border-e border-b', className)}>{children}</div>;
}
