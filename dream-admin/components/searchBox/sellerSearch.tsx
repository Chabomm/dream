import React, { useEffect, useState } from 'react';
import { api, setContext } from '@/libs/axios';

interface Props {
    setSellerSearchOpen?: any;
    seller?: string;
    sandSellerUid?: any;
}
export default function SellerSearch({ setSellerSearchOpen, seller, sandSellerUid }: Props) {
    const closeModal = () => {
        setSellerSearchOpen(false);
    };

    useEffect(() => {
        getSeller();
    }, []);

    const [posts, setPosts] = useState<any>([]);
    const getSeller = async () => {
        try {
            const { data } = await api.post(`/be/admin/b2b/seller/search/list`, {
                seller,
            });
            setPosts(data);
        } catch (e: any) {}
    };

    const sellerPick = (uid: number, seller_id: string, seller_name: string, indend_md: string) => {
        sandSellerUid(uid, seller_id, seller_name, indend_md);
        closeModal();
    };

    return (
        <div className="fixed z-50 top-0 w-full">
            <div className="w-full mt-10 m-auto max-w-lg">
                <div className="border-0 rounded-lg shadow-lg relative flex flex-col w-full bg-white outline-none focus:outline-none z-50 h-full">
                    <div className="flex justify-between p-5 rounded-t border-b">
                        <div className="text-xl">고객사 목록</div>
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
                                            <div className="col-table-th grid grid-cols-7 sticky bg-gray-100">
                                                <div className="col-span-2">판매자 아이디</div>
                                                <div className="col-span-2">판매자명</div>
                                                <div className="col-span-2">담당자명</div>
                                                <div className="">선택</div>
                                            </div>
                                            {posts.list?.map((v: any, i: number) => (
                                                <div key={i} className="col-table-td grid grid-cols-7 bg-white transition duration-300 ease-in-out hover:bg-gray-100">
                                                    <div className="col-span-2 break-all">{v.seller_id}</div>
                                                    <div className="col-span-2">{v.seller_name}</div>
                                                    <div className="col-span-2">{v.indend_md}</div>
                                                    <div className="" onClick={() => sellerPick(v.uid, v.seller_id, v.seller_name, v.indend_md)}>
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
