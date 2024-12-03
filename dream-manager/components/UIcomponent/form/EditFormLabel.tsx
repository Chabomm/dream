import { cls } from '@/libs/utils';

export default function EditFormLabel(props: any) {
    const { children, className, tootip } = props;

    return <div className={cls('form-control', className)}>{children}</div>;
}
