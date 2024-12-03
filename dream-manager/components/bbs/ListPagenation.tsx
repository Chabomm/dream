import { cls } from '@/libs/utils';
import React, { useState } from 'react';

export default function ListPagenation({ props, getPagePost }: any) {
    const class_prev = 'cursor-pointer relative inline-flex items-center px-2 py-2 text-zinc-400 bg-neutral-100 focus:z-20 focus:outline-offset-0';

    const class_next = 'cursor-pointer relative inline-flex items-center px-2 py-2 text-zinc-400 bg-neutral-100 focus:z-20 focus:outline-offset-0';

    const class_page = 'cursor-pointer relative items-center px-4 py-2 font-semibold text-gray-900 hover:bg-gray-50 focus:z-20 focus:outline-offset-0';

    const class_page_on =
        'cursor-pointer relative z-10 inline-flex items-center bg-second px-4 py-2 font-bold text-white focus:z-20 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600';

    const class_divider = 'relative inline-flex items-center px-4 py-2 text-sm font-semibold text-gray-700 focus:outline-offset-0';
    const page_count = [...Array(props.page_last)];

    // [ S ] count_page
    let startPage: any;
    let endPage: any;
    let count_page: any = [{ num: 1, active: 'active' }];
    if (props.page_last <= 10) {
        startPage = 1;
        endPage = page_count.length;

        let show_page: any = [];
        for (let i = startPage; i <= endPage; i++) {
            let setPage: any = {};
            if (i == props.page) {
                setPage.active = 'active';
            } else {
                setPage.active = 'No';
            }
            setPage.num = i;
            show_page.push(setPage);
        }
        count_page = show_page;
    } else {
        if (props.page - 4 <= 1) {
            startPage = 1;
        } else {
            startPage = props.page - 4;
        }

        if (props.page + 5 >= props.page_last) {
            endPage = props.page_last;
        } else {
            if (props.page <= 5) {
                endPage = 10;
            } else {
                endPage = props.page + 5;
            }
        }

        let show_page: any = [];
        for (let i = startPage; i <= endPage; i++) {
            let setPage: any = {};
            if (i == props.page) {
                setPage.active = 'active';
            } else {
                setPage.active = 'No';
            }
            setPage.num = i;
            show_page.push(setPage);
        }
        count_page = show_page;
    }

    // [ E ] count_page

    const change_page = page => {
        if (page > 0 && page <= props.page_last) {
            props.page = page;
            getPagePost(props);
        }
    };

    return (
        <div className="py-3">
            <div className="flex flex-1 items-center justify-center pt-10">
                <div className="gap-3 isolate inline-flex -space-x-px ">
                    <div
                        className={class_prev}
                        onClick={() => {
                            change_page(1);
                        }}
                    >
                        <span className="">맨처음</span>
                    </div>
                    <div
                        className={class_prev}
                        onClick={() => {
                            change_page(props.page - 1);
                        }}
                    >
                        <span className="sr-only">Previous</span>
                        <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                            <path
                                fillRule="evenodd"
                                d="M12.79 5.23a.75.75 0 01-.02 1.06L8.832 10l3.938 3.71a.75.75 0 11-1.04 1.08l-4.5-4.25a.75.75 0 010-1.08l4.5-4.25a.75.75 0 011.06.02z"
                                clipRule="evenodd"
                            />
                        </svg>
                    </div>
                    {count_page.map((v: any, i: number) => (
                        <div
                            key={i}
                            className={cls(v.active == 'active' ? class_page_on : class_page)}
                            onClick={() => {
                                change_page(v.num);
                            }}
                        >
                            {v.num}
                        </div>
                    ))}

                    <div
                        className={class_next}
                        onClick={() => {
                            change_page(props.page + 1);
                        }}
                    >
                        <span className="sr-only">Next</span>
                        <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                            <path
                                fillRule="evenodd"
                                d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z"
                                clipRule="evenodd"
                            />
                        </svg>
                    </div>
                    <div
                        className={class_prev}
                        onClick={() => {
                            change_page(props.page_last);
                        }}
                    >
                        <span className="">맨끝</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
