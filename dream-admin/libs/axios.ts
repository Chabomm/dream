// https://gist.github.com/moogii/f4b3c35b22ca1b20fdcbc0fa770069ca
import { GetServerSidePropsContext } from 'next';
import { getServerCookieToken, getToken, getUserIP, left } from './utils';
import axios, { AxiosError } from 'axios';
import Router from 'next/router';

export const api = axios.create({
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true,
});

const isServer = () => {
    return typeof window === 'undefined';
};

let context = <GetServerSidePropsContext>{};
export const setContext = (_context: GetServerSidePropsContext) => {
    context = _context;
};

api.interceptors.request.use(config => {
    /** config에는 위의 axiosInstance 객체를 이용하여 request를 보냈을떄의 모든 설정값들이 들어있다.
     * [활용]
     * 1. api요청의 경우 token이 필요한 경우가 있는데, 필요에 따른 토큰 정보들을 여기서 처리할 경우
     * 토큰에 대한 정보를 여러곳에서 처리하지 않아도 된다.
     * 2. 요청 method에 따른 외부로 드러내지 않고 처리하고 싶은 부분에 대한 작업이 가능
     */

    if (left(config.url, 5) == '/ums/') {
        if (isServer()) {
            config.baseURL = `${process.env.NEXT_PUBLIC_UMS}`;
            config.headers['x-user-ip'] = `${getUserIP(context)}`;
            config.headers['Authorization'] = `Bearer ${getToken(context)}`;
        } else {
            config.baseURL = ``;
            config.headers['Authorization'] = `Bearer ${getToken(null)}`;
        }
    } else {
        if (isServer()) {
            config.baseURL = `${process.env.NEXT_PUBLIC_BACKEND}`;
            config.headers['x-user-ip'] = `${getUserIP(context)}`;
            config.headers['Authorization'] = `Bearer ${getToken(context)}`;
        } else {
            config.baseURL = ``;
            config.headers['Authorization'] = `Bearer ${getToken(null)}`;
        }
    }
    return config;
});

api.interceptors.response.use(
    response => {
        /** 요청을 보낸 뒤에 response(응답)이 오는 경우에 여기서 먼저 확인이 가능하다.
         * [활용]
         * 1. status-code가 정상적이어도 내용상의 이유로 에러처리가 필요한 경우
         * 2. 민감정보 또는 데이터에 대한 가공 작업
         */
        // console.log('interceptors response', response);

        if (isServer() && !response?.config?.url?.includes('be/client_error')) {
            context.res?.setHeader('set-cookie', `${process.env.NEXT_PUBLIC_TOKENNAME}=${getServerCookieToken(response)}; path=/;`);
        }
        return response;
    },
    (error: AxiosError) => {
        /** response응답 후에 status-code가 4xx, 5xx 처럼 에러를 나타내는 경우 해당 루트를 수행한다. */
        if (process.env.NODE_ENV == 'production') {
            return sendErrorLog(error);
        } else {
            return;
        }
    }
);

const sendErrorLog = async (oError: any) => {
    api.post(`/be/client_error`, {
        error_page: context.resolvedUrl,
        code: oError.code,
        headers: oError.config?.headers,
        status: oError.response?.status,
        status_text: oError.response?.statusText,
        axios_url: `${oError.config?.baseURL}${oError.config?.url}`,
        request_data: JSON.parse(oError.response?.config.data),
        response_data: oError.response?.data,
    });

    // client side
    if (!isServer() && !Router.asPath.includes('/login')) {
        // backend에서 토큰 재생성 하지만, 재생성 도중 backend 500에러인 경우
        // 서버와 nextjs간 토큰 씽크가 안맞을 때가 있음 그럴때 다시 로그인 하도록 처리.
        if (oError.response.status == 401) {
            Router.push(`/login?redirect=${encodeURIComponent(Router.asPath)}&status=${oError.response.status}`);
        }
        // Router.push('/500');
    }

    // server side
    if (isServer()) {
        oError.redirect = {
            permanent: false,
            destination: '/500',
        };
        if (oError.response.status == 401) {
            oError.redirect = {
                permanent: false,
                destination: `/login?redirect=${encodeURIComponent(context.resolvedUrl)}&status=${oError.response.status}`,
            };
        }
    }

    return Promise.reject(oError);
};

export default api;
