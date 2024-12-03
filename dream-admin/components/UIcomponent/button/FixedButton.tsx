import { cls } from '@/libs/utils';

export default function FixedButton(props: any) {
    const { children, className, onclick, submitting, type, colspan } = props;

    return (
        <button
            className={cls(
                `col-span-${colspan}`,
                `w-full leading-none border border-blue-500 text-blue-500 rounded text-[0.9rem] h-8 flex items-center justify-center`,
                className,
                type == 'submit' ? 'bg-blue-500 hover:bg-blue-600 text-white' : ''
            )}
            type={type}
            onClick={onclick}
            disabled={type != 'button' && submitting}
        >
            {children}
        </button>
    );
}
