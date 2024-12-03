import { cls } from '@/libs/utils';

export default function EditFormCardHead(props: any) {
    const { children, className } = props;
    return <div className={cls('border-b p-4 flex gap-4 justify-between', className)}>{children}</div>;
}
