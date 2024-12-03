import { cls } from '@/libs/utils';

export default function EditFormCard(props: any) {
    const { children, className } = props;
    return <div className={cls('border rounded-md bg-white mb-5', className)}>{children}</div>;
}
