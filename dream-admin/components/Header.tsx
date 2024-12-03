import Link from 'next/link';
import React, { useState, useEffect, useContext } from 'react';
import { useRouter } from 'next/router';
import { GlobalContext } from '@/pages/_app';
import { cls } from '@/libs/utils';

export default function Header(props: any) {
    const router = useRouter();
    const { aside, setAside } = useContext(GlobalContext);

    const toggleAside = () => {
        setAside && setAside(!aside);
    };

    const { navi_list, nav_id } = props;
    const [traces, setTraces] = useState([]);

    var trace: any[] = [];

    useEffect(() => {
        if (router.isReady) {
            if (sessionStorage.getItem('trace') || '{}' !== '{}') {
                trace = JSON.parse(sessionStorage.getItem('trace') || '[]');
            }
            var oTrace: any = {};
            navi_list.map((v: any) => {
                v.children.map((vv: any) => {
                    if (vv.id == nav_id) {
                        oTrace.name = v.name + ' > ' + vv.name;
                        oTrace.to = vv.to;
                        oTrace.id = vv.id;
                    }
                });
            });

            if (JSON.stringify(oTrace) !== '{}') {
                trace.unshift(oTrace);
            }

            const result = trace.reduce((acc, v) => {
                return acc.find((x: any) => x.name === v.name) ? acc : [...acc, v];
            }, []);

            sessionStorage.setItem('trace', JSON.stringify(result));
            setTraces(result);
        }
    }, [navi_list]);

    const delTrace = (i: number) => {
        if (sessionStorage.getItem('trace') || '{}' !== '{}') {
            trace = JSON.parse(sessionStorage.getItem('trace') || '[]');
        }
        trace.splice(i, 1);
        sessionStorage.setItem('trace', JSON.stringify(trace));
        setTraces && setTraces(trace && []);
    };

    return (
        <nav className="bg-white border-b border-gray-200 w-full h-16 fixed flex items-center justify-between px-5 z-10">
            <div className="flex items-center justify-start">
                <button
                    onClick={toggleAside}
                    className="mr-3 text-gray-600 hover:text-gray-900 cursor-pointer p-2 hover:bg-gray-100 focus:bg-gray-100 focus:ring-2 focus:ring-gray-100 rounded"
                >
                    <svg className={cls('w-6 h-6', aside ? 'hidden' : '')} fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                        <path
                            fillRule="evenodd"
                            d="M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h6a1 1 0 110 2H4a1 1 0 01-1-1zM3 15a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z"
                            clipRule="evenodd"
                        ></path>
                    </svg>

                    <svg className={cls('w-6 h-6', aside ? '' : 'hidden')} fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                        <path
                            fillRule="evenodd"
                            d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                            clipRule="evenodd"
                        ></path>
                    </svg>
                </button>
                <div className="pl-4 border-gray-200 w-full py-2 overflow-x-auto flex">
                    {traces?.map((v: any, i: number) => (
                        <span key={i} id="badge-dismiss-default" className="flex-shrink-0 flex items-center px-2 py-1 mr-2 text-sm font-medium text-blue-800 bg-blue-100 rounded">
                            <Link href={v.to}>{v.name}</Link>
                            <button
                                onClick={() => {
                                    delTrace(i);
                                }}
                                type="button"
                                className="flex items-center p-0.5 ml-2 text-sm text-blue-400 bg-transparent rounded-sm hover:bg-blue-200 hover:text-blue-900"
                            >
                                <i className="fas fa-times"></i>
                            </button>
                        </span>
                    ))}
                </div>
            </div>
            <div className="flex items-center">
                <button id="toggleSidebarMobileSearch" type="button" className="lg:hidden text-gray-500 hover:text-gray-900 hover:bg-gray-100 p-2 rounded-lg">
                    <span className="sr-only">Search</span>
                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                        <path
                            fillRule="evenodd"
                            d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
                            clipRule="evenodd"
                        ></path>
                    </svg>
                </button>
            </div>
        </nav>
    );
}
