import React, { useEffect, useState } from 'react';
import { api, setContext } from '@/libs/axios';

interface Props {
    setAdminUserOpen?: any;
    sandAdminUser?: any;
}
export default function AdminUserSearch({ setAdminUserOpen, sandAdminUser }: Props) {
    const closeModal = () => {
        setAdminUserOpen(false);
    };

    useEffect(() => {
        getAdminUser();
    }, []);

    const [posts, setPosts] = useState<any>([]);
    const getAdminUser = async () => {
        try {
            const { data } = await api.post(`/be/admin/b2b/seller/admin/list`, {
                page: 1,
                page_size: 0,
                page_view_size: 0,
                page_total: 0,
                page_last: 0,
            });
            setPosts(data);
        } catch (e: any) {}
    };

    const adminUserPick = (uid: number, user_id: string, user_name: string, email: string, tel: string, mobile: string) => {
        sandAdminUser(uid, user_id, user_name, email, tel, mobile);
        closeModal();
    };

    return (
        <div className="fixed z-50 top-0 w-full">
            <div className="w-full mt-10 m-auto max-w-lg">
                <div className="border-0 rounded-lg shadow-lg relative flex flex-col w-full bg-white outline-none focus:outline-none z-50 h-full">
                    <div className="flex justify-between p-5 rounded-t border-b">
                        <div className="text-xl">담당MD 목록</div>
                        <button className="" type="button" onClick={closeModal}>
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="w-6 h-6">
                                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                    <div>
                        {posts.list?.length > 0 ? (
                            <div className="h-full">
                                <div className="h-96 overflow-scroll">
                                    <div className="relative p-4 h-full">
                                        <div className="col-table h-full">
                                            <div className="col-table-th grid grid-cols-5 sticky bg-gray-100">
                                                <div className="col-span-2">아이디</div>
                                                <div className="col-span-2">이름</div>
                                                <div className="">선택</div>
                                            </div>
                                            {posts.list?.map((v: any, i: number) => (
                                                <div key={i} className="col-table-td grid grid-cols-5 bg-white transition duration-300 ease-in-out hover:bg-gray-100">
                                                    <div className="col-span-2 break-all">{v.user_id}</div>
                                                    <div className="col-span-2">{v.user_name}</div>
                                                    <div className="" onClick={() => adminUserPick(v.uid, v.user_id, v.user_name, v.email, v.tel, v.mobile)}>
                                                        <button type="button" className="btn-filter">
                                                            선택
                                                        </button>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="p-6 text-center">고객사 목록이 없습니다.</div>
                        )}
                    </div>
                </div>
            </div>
            <div className="opacity-25 fixed inset-0 z-40 bg-black" onClick={closeModal}></div>
        </div>
    );
}
