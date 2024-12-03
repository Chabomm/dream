import { cls } from '@/libs/utils';
import { useEffect } from 'react';

export default function AModal(props: any) {
    const { children, onclick, width_style } = props;
    return (
        <div className="fixed z-50 top-0 left-0 w-full h-full">
            <div className="relative top-50 left-0 w-full h-full">
                <div
                    className={cls(`absolute border-0 rounded-lg shadow-lg bg-white z-50 overflow-hidden max-h-full flex flex-col outline-none focus:outline-none`)}
                    style={{ top: '10%', left: '50%', transform: 'translate(-50%,-10%)', width: width_style }}
                >
                    {children}
                </div>
            </div>
            <div className="opacity-25 fixed inset-0 z-40 bg-black" onClick={onclick}></div>
        </div>
    );
}
