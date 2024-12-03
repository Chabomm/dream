import React, { useEffect, useState } from 'react';
import { api, setContext } from '@/libs/axios';

interface Props {
    setPartnerSearchOpen?: any;
    partnerName?: string;
    sandPartnerUid?: any;
}
export default function PartnerSearch({ setPartnerSearchOpen, partnerName, sandPartnerUid }: Props) {
    const closeModal = () => {
        setPartnerSearchOpen(false);
    };

    useEffect(() => {
        getPartner();
    }, []);

    const [posts, setPosts] = useState<any>([]);
    const getPartner = async () => {
        try {
            const { data } = await api.post(`/be/admin/member/partner/list`, {
                page: 1,
                page_size: 0,
                page_view_size: 0,
                page_total: 0,
                page_last: 0,
                partner_name: partnerName,
            });
            setPosts(data);
        } catch (e: any) {}
    };

    const partnerPick = (uid: number, partner_id: string, company_name: string, mall_name: string) => {
        sandPartnerUid(uid, partner_id, company_name, mall_name);
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
                                                <div className="col-span-2">고객사 아이디</div>
                                                <div className="col-span-2">고객사명</div>
                                                <div className="col-span-2">복지몰명</div>
                                                <div className="">선택</div>
                                            </div>
                                            {posts.list?.map((v: any, i: number) => (
                                                <div key={i} className="col-table-td grid grid-cols-7 bg-white transition duration-300 ease-in-out hover:bg-gray-100">
                                                    <div className="col-span-2 break-all">{v.partner_id}</div>
                                                    <div className="col-span-2">{v.company_name}</div>
                                                    <div className="col-span-2">{v.mall_name}</div>
                                                    <div className="" onClick={() => partnerPick(v.uid, v.partner_id, v.company_name, v.mall_name)}>
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
