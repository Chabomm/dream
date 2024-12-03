import { cls } from '@/libs/utils';

export default function EditFormCardBody(props: any) {
    const { children, className } = props;
    return <div className={cls('p-5', className)}>{children}</div>;
}
