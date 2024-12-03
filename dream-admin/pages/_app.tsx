import Head from 'next/head';
import '../styles/globals.css';
import '../styles/form.css';
import '../styles/table.css';
import '../public/font/SUIT/SUIT.css';
import type { AppContext, AppProps } from 'next/app';
import React, { useState, createContext, Dispatch, SetStateAction, useEffect } from 'react';
import { checkNumeric, getAgentDevice, getCookie } from '@/libs/utils';
import jwt_decode from 'jwt-decode';

interface IGlobalContext {
    aside?: boolean;
    setAside?: Dispatch<SetStateAction<boolean>>;
}
export const GlobalContext = createContext<IGlobalContext>({});

function MyApp({ Component, pageProps }: AppProps) {
    const [aside, setAside] = useState(true);
    const value = { aside, setAside };

    useEffect(() => {
        if (typeof pageProps.response !== 'undefined') {
            if (typeof pageProps.response.code !== 'undefined') {
                if (checkNumeric(pageProps.response.code) > 0 && checkNumeric(pageProps.response.code) != 200) {
                    alert(`오류가 발생하였습니다. 문제 지속시 관리자에게 문의하세요.\n[${pageProps.response.code}] ${pageProps.response.msg}`);
                }
            }
        }
    }, [pageProps.response]);

    return (
        <GlobalContext.Provider value={value}>
            <Head>
                <link rel="preload" href="/font/SUIT/SUIT-Bold.woff2" as="font" type="font/woff2" crossOrigin="anonymous" />
                <link rel="preload" href="/font/SUIT/SUIT-ExtraBold.woff2" as="font" type="font/woff2" crossOrigin="anonymous" />
                <link rel="preload" href="/font/SUIT/SUIT-Heavy.woff2" as="font" type="font/woff2" crossOrigin="anonymous" />
                <link rel="preload" href="/font/SUIT/SUIT-Light.woff2" as="font" type="font/woff2" crossOrigin="anonymous" />
                <link rel="preload" href="/font/SUIT/SUIT-Medium.woff2" as="font" type="font/woff2" crossOrigin="anonymous" />
                <link rel="preload" href="/font/SUIT/SUIT-Regular.woff2" as="font" type="font/woff2" crossOrigin="anonymous" />
                <link rel="preload" href="/font/SUIT/SUIT-SemiBold.woff2" as="font" type="font/woff2" crossOrigin="anonymous" />
            </Head>
            <Component {...pageProps} />
        </GlobalContext.Provider>
    );
}

import * as cookie from 'cookie';
MyApp.getInitialProps = async (context: AppContext) => {
    const { ctx, Component } = context;
    let user: any = {};
    let token: string = '';

    // const { pathname, asPath, res }: any = ctx;
    // if (pathname == '/login' || pathname == '/logout' || pathname == '/callback' || pathname == '/404' || pathname == '/500') {
    //     return {};
    // }

    // SSR만 접근 가능하게, 만약 CSR 접근시 바로 리턴
    // if (typeof ctx.req === 'undefined') {
    //     return {};
    // }

    try {
        let header_cookie: string = ctx?.req?.headers.cookie || '';
        const parsedCookies = cookie.parse(header_cookie);
        token = parsedCookies[process.env.NEXT_PUBLIC_TOKENNAME] + '';
        user = jwt_decode(token);
    } catch (e) {
        // console.log(e);
    }

    if (JSON.stringify(user) == '{}') {
        try {
            const token: string = getCookie(`${process.env.NEXT_PUBLIC_TOKENNAME}`) as string;
            user = jwt_decode(token);
        } catch (e) {
            // console.log(e);
        }
    }

    if (JSON.stringify(user) == '{}') {
        const { pathname, asPath, res }: any = ctx;
        if (pathname != '/login' && pathname != '/logout' && pathname != '/callback') {
            try {
                res.writeHead(307, { Location: '/login?redirect=' + asPath });
                res.end();
            } catch (e) {
                // console.log(e);
            }
        }
    }

    let pageProps = {};
    let device = getAgentDevice(ctx);
    if (Component.getInitialProps) {
        pageProps = await Component.getInitialProps(ctx);
    }

    return {
        pageProps: {
            device: device,
            user: user,
        },
    };
};

export default MyApp;
