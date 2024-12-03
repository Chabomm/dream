import { checkNumeric, cls } from '@/libs/utils';
import { api, setContext } from '@/libs/axios';
import React, { useEffect, useState } from 'react';

import { EditFormCard, EditFormCardHead } from '@/components/UIcomponent/form/EditFormA';

export default function PointStatus({ point_type }) {
    const [posts, setPosts] = useState<any>({});
    let point_type_txt = point_type == 'bokji' ? '복지포인트' : '식권포인트';

    useEffect(() => {
        getDataRead();
    }, []);

    useEffect(() => {
        if (posts) {
            const num2Curs: any = document.querySelectorAll('.num2Cur') || undefined;
            num2Curs.forEach(function (v) {
                v.innerText = v.innerText.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
            });
        }
    }, [posts]);

    const getDataRead = async () => {
        try {
            const { data } = await api.post(`/be/manager/point/status/read`, { point_type: point_type });
            setPosts(data);
        } catch (e: any) {}
    };

    return (
        <>
            <EditFormCard>
                <EditFormCardHead>
                    <div className="text-lg">기업 예치금 및 {point_type_txt} 충전현황</div>
                </EditFormCardHead>
                <div className="grid grid-cols-2 gap-10 p-5 text-center">
                    <div className="border rounded-md text-lg">
                        <div className="border-b bg-orange-300 rounded-t-md py-2 text-white ">
                            <div className="mb-1 ">총 충전 예치금</div>
                            <div className="">
                                <span className="num2Cur !text-center">{checkNumeric(posts?.total_charge_balance)}</span> 원
                            </div>
                        </div>
                        <div className="grid grid-cols-2 py-5">
                            <div className="border-r">
                                <div>사용 예치금</div>
                                <div className="">
                                    <span className="text-blue-500 num2Cur !text-center">{checkNumeric(posts?.used_charge_balance)}</span> 원
                                </div>
                            </div>
                            <div>
                                <div>잔여 예치금</div>
                                <div className="">
                                    <span className="text-red-500 num2Cur !text-center">{checkNumeric(posts?.avail_charge_balance)}</span> 원
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="border rounded-md text-lg">
                        <div className={cls('border-b rounded-t-md py-2 text-white', point_type == 'bokji' ? 'bg-blue-400' : 'bg-teal-500')}>
                            <div className="mb-1">지급완료 {point_type_txt}</div>
                            <div className="">
                                <span className="num2Cur !text-center">{checkNumeric(posts?.saved_welfare_point)}</span> 원
                            </div>
                        </div>
                        <div className={cls('grid py-5', point_type == 'bokji' ? 'grid-cols-3' : 'grid-cols-2')}>
                            <div className="border-r">
                                <div>사용완료 {point_type_txt}</div>
                                <div className="">
                                    <span className="text-blue-500 num2Cur !text-center">{checkNumeric(posts?.used_welfare_point)}</span> 원
                                </div>
                            </div>
                            <div className="border-r">
                                <div>미사용 {point_type_txt}</div>
                                <div>
                                    <span className="text-red-500 num2Cur !text-center">{checkNumeric(posts?.avail_welfare_point)}</span> 원
                                </div>
                            </div>
                            {point_type == 'bokji' && (
                                <div>
                                    <div>만료된 {point_type_txt}</div>
                                    <div>
                                        <span className="num2Cur !text-center">{checkNumeric(posts?.exp_welfare_point)}</span> 원
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </EditFormCard>
        </>
    );
}
