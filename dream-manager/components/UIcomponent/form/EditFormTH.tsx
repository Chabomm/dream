import { cls } from '@/libs/utils';

export default function EditFormTH({ children, className }) {
    return (
        <div className={cls('edit-form-th relative flex items-center font-semibold border-e border-b', className)}>
            <span>{children}</span>
        </div>
    );
}
