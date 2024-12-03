import { cls } from '@/libs/utils';

export default function EditFormButtonWrap(props: any) {
    const { children, className } = props;
    return <div className={cls('mt-5 mb-5 flex justify-center gap-3', className)}>{children}</div>;
}
