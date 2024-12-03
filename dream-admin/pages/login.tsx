// import type { NextPage, NextPageContext } from 'next';
// import React from 'react';
// import { useRouter } from 'next/router';

// import dynamic from 'next/dynamic';
// const LottieLogin = dynamic(() => import('@/components/resource/lottie/Login'), { ssr: false });

// import SvgLeftTop from '@/components/resource/svg/lefttop';
// import SvgRightBottom from '@/components/resource/svg/rightbottom';
// import { checkNumeric } from '@/libs/utils';

import type { NextPage } from 'next';
import React from 'react';
import { useRouter } from 'next/router';

import LottieLogin from '@/components/resource/lottie/Login';
import SvgLeftTop from '@/components/resource/svg/lefttop';
import SvgRightBottom from '@/components/resource/svg/rightbottom';
import { checkNumeric } from '@/libs/utils';

const Lgoin: NextPage = (props: any) => {
    const router = useRouter();
    let { redirect, status } = router.query;

    if (status && typeof window !== 'undefined') {
        if (checkNumeric(status) == 401) {
            alert('로그인 정보를 찾을 수 없습니다. 다시 로그인해 주세요');
        } else {
            alert('알 수 없는 오류가 발생하였습니다. 다시 로그인해도 문제 지속시 개발자에게 문의해주세요 (' + status + ')');
        }
    }

    const signin_azure = () => {
        // 24.05.04 강제 관리자 로그인 by.namgu
        location.href = '/callback?sub=XTDhoX5%2F3ubMzgIUcHgv%2FkT9OS4HdWS4LwmCglb1zGCeQu1BwxEroD1QSvzOHV2seWBha0qm9rdbjr8AMJ2LqT8P3CkJdM1fqObllqFAp9B3HOnaeTZr%2FXwgy8EhdABE';
    };

    return (
        <>
            <div className="h-screen overflow-hidden flex items-center justify-center" style={{ background: '#edf2f7' }}>
                <div className="bg-white relative lg:py-20">
                    <div className="flex flex-col items-center justify-between xl:px-5 lg:flex-row">
                        <div className="flex flex-col items-center w-full pt-5 px-5 pb-20 lg:px-10 lg:pt-20 lg:flex-row">
                            <div className="w-full bg-cover relative max-w-md lg:max-w-2xl lg:w-7/12">
                                <div className="flex flex-col items-center justify-center w-full h-full relative lg:pr-10">
                                    <LottieLogin />
                                </div>
                            </div>
                            <div className="w-full mt-20 mr-0 mb-0 ml-0 relative z-10 max-w-2xl lg:mt-0 lg:w-5/12">
                                <div className="flex flex-col items-start justify-start p-5 lg:p-10 bg-white shadow-2xl rounded-xl relative z-10">
                                    <p className="w-full text-4xl font-medium text-center leading-snug font-serif">Sign up for an account</p>

                                    <div className="w-full mt-6 mr-0 mb-0 ml-0 relative space-y-8 cursor-pointer" onClick={signin_azure}>
                                        <img src="https://indend-resource.s3.ap-northeast-1.amazonaws.com/logos/microsoft_logo.svg" alt="mslogo" />
                                    </div>
                                </div>
                                <SvgLeftTop className="absolute top-0 left-0 z-0 w-32 h-32 -mt-12 -ml-12 text-yellow-300 fill-current" />
                                <SvgRightBottom className="absolute bottom-0 right-0 z-0 w-32 h-32 -mb-12 -mr-12 text-indigo-500 fill-current" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
};

export default Lgoin;
