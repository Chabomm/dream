import { cls } from '@/libs/utils';

export default function FixedButtonWrap(props: any) {
    const { children, className, cols } = props;
    return (
        <div className={cls(`fixed left-0 bottom-0 w-full flex gap-4 bg-white h-14 items-center px-3 border-t`, className)}>
            <div className={`w-full grid grid-cols-${cols} gap-3`}>{children}</div>
        </div>
    );
}
