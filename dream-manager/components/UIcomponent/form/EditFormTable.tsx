import { cls } from '@/libs/utils';

export default function EditFormTable({ children, className }) {
    return <div className={cls('edit-form grid border-s border-t border-t-black', className)}>{children}</div>;
}
