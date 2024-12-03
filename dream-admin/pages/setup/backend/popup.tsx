import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';

const SetupBackendPopup: NextPage = (props: any) => {
    const router = useRouter();
    const [posts, setPosts] = useState<any>([]);

    useEffect(() => {
        if (props) {
            setPosts(props.response);
        }
    }, [props]);

    const closeTab = () => {
        window.close();
    };
    return (
        <>
            <div className="w-full bg-slate-100 mx-auto py-10">
                <div className="px-9">
                    <div className="border py-4 px-6 rounded shadow-md bg-white mt-5">
                        <div className="font-bold mb-4">파일 정보</div>
                        <div className="w-full whitespace-pre">
                            {props.response.map((v: any, i: number) => (
                                <div key={i} className="" dangerouslySetInnerHTML={{ __html: v }}></div>
                            ))}
                        </div>
                    </div>
                    <div className="w-full text-center mt-5">
                        <button className="px-10 bg-gray-500 rounded-md py-2 text-white text-center" onClick={closeTab}>
                            닫기
                        </button>
                    </div>
                </div>
            </div>
        </>
    );
};
export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {
        file_name: ctx.query.file_name,
        folder_name: ctx.query.folder_name,
    };
    var response: any = {};
    try {
        const { data } = await api.post(`/be/admin/setup/log/backend/read`, request);
        response = data;
    } catch (e: any) {
        if (typeof e.redirect !== 'undefined') {
            return { redirect: e.redirect };
        }
    }
    return {
        props: { request, response },
    };
};

export default SetupBackendPopup;
