import React, { useState, useEffect, useRef } from 'react';
import { cls } from '@/libs/utils';

export default function OverlayText(props: any) {
    const [open, setOpen] = useState(false);
    const onToggle = () => setOpen(!open);

    const ref = useRef(null);

    const { dire, view_text, push_title, push_msg, push_img } = props.item;

    const [direction, setDirection] = useState<any>();
    useEffect(() => {
        if (dire == 'left') {
            setDirection({
                wrap_absolute: 'left-0',
                squre_absolute: 'border-r',
                wrap_style: {
                    transform: 'translate(calc(-100% - 1rem), -50%)',
                },
                squre_style: {
                    top: 'calc(50% - 1.25rem)',
                    right: '-0.5rem',
                },
            });
        } else if (dire == 'right') {
            setDirection({
                wrap_absolute: 'right-0',
                squre_absolute: 'right-5 border-l',
            });
        } else if (dire == 'middle') {
            setDirection({
                wrap_absolute: 'inset-x-1/2',
                squre_absolute: 'right-1/2',
            });
        }
    }, [props]);

    // const [text, setText] = useState(title + '이(가) 없습니다');
    // useEffect(() => {
    //     if (typeof message === 'object') {
    //         var complate_message = '';
    //         message.forEach(function (v: any, i: number, a: any) {
    //             if (v !== '') {
    //                 complate_message = complate_message + v + '\n';
    //             }
    //         });
    //         if (complate_message == '') {
    //             setText(title + '이(가) 없습니다');
    //         } else {
    //             setText(complate_message);
    //         }
    //     }
    // }, [message]);

    const mouseOver = (e: any) => {
        setOpen(true);
    };
    const onMouseLeave = (e: any) => {
        setOpen(false);
    };

    return (
        <>
            <div className="relative" onMouseOver={mouseOver} onMouseLeave={onMouseLeave}>
                <div ref={ref} className="underline text-blue-300 cursor-pointer">
                    {view_text}
                </div>
                {open && (
                    <div style={direction?.wrap_style} className={cls(direction?.wrap_absolute, 'w-96 absolute text-left z-10')}>
                        <div
                            style={direction?.squre_style}
                            className={cls(direction?.squre_absolute, 'absolute z-20 h-4 w-4 rotate-45 mt-0.5 ml-[1.2rem]  border-t border-gray-300 bg-white')}
                        ></div>
                        <div className="mt-2.5 shadow-sm border border-gray-300 px-1 py-0.5 bg-white rounded-lg">
                            <table className="border-collapse border border-slate-400 w-full">
                                <tbody>
                                    <tr>
                                        <th className="border border-slate-200 bg-gray-100 w-24">제목</th>
                                        <td className="border border-slate-200 p-2">{push_title}</td>
                                    </tr>
                                    <tr>
                                        <th className="border border-slate-200 bg-gray-100 w-24">내용</th>
                                        <td className="border border-slate-200 p-2">
                                            <div className="whitespace-pre-wrap">{push_msg}</div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <th className="border border-slate-200 bg-gray-100 w-24">이미지</th>
                                        <td className="border border-slate-200 p-2">
                                            <img src={push_img} className="w-full" />
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}
            </div>
        </>
    );
}
