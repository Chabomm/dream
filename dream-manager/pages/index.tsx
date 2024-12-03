import Link from 'next/link';
import type { NextPage } from 'next';
import React, { useEffect, useRef, useState } from 'react';
import Layout from '@/components/Layout';
import { api } from '@/libs/axios';
import { checkNumeric, cls, null2Blank, num2Cur } from '@/libs/utils';
import { useRouter } from 'next/router';

import { Chart, registerables, ArcElement } from 'chart.js';
import { Doughnut } from 'react-chartjs-2';
import ChartDataLabels from 'chartjs-plugin-datalabels';

Chart.register(...registerables);

const Home: NextPage = (props: any) => {
    const router = useRouter();
    const [userInfo, setUserInfo] = useState<any>();
    const [point, setPoint] = useState<any>();
    const [member, setMember] = useState<any>();
    const [balance, setBalance] = useState<any>();
    const [assing, setAssing] = useState<any>();
    const [dayPoint, setDayPoint] = useState<any>();

    useEffect(() => {
        getJsonData();
    }, []);
    const getJsonData = async () => {
        try {
            const { data } = await api.post(`/be/manager/home`, {});
            console.log('data', data);
            setUserInfo(data.user_info);
            setPoint(data.point_info);
            setMember(data.member_info);
            setPoint(data.point_info);
            setBalance(data.balance_info);
            setAssing(data.point_assign_info);
            setDayPoint(data.day_point_info);
            return data.point_info;
        } catch (e: any) {}
    };
    const fnPagemove = (pageName: string) => {
        if (pageName == 'balance') {
            router.push('/point/balance/list');
            // } else if (pageName == 'partner') {
            //     router.push('/setup/info/partner');
            // } else if (pageName == 'manager') {
            //     router.push('/setup/info/manager');
        } else if (pageName == 'bokji') {
            router.push('/point/assign/single/list');
        } else if (pageName == 'member') {
            router.push('/member/list');
        } else if (pageName == 'point_used') {
            router.push('/point/used/mall/list');
        } else if (pageName == 'point_list') {
            router.push('/point/assign/list');
        } else if (pageName == 'new_member') {
            window.open(`/member/edit?uid=0`, '회원정보', 'width=1120,height=800,location=no,status=no,scrollbars=yes,left=200%,top=50%');
        }
    };

    // [ S ] chart.js
    const [usedCharge, setUsedCharge] = useState<number>(0);
    const [usedPoint, setUsedPoint] = useState<number>(0);
    // useEffect(() => {
    //     fnChartChargeData();
    //     fnChartPointData();
    // }, []);
    // const fnChartChargeData = async () => {
    //     let newData = await getJsonData();

    //     let used_point = Math.ceil((checkNumeric(newData.used_charge_balance) / checkNumeric(newData.total_charge_balance)) * 100 * Math.pow(10, 0)) / Math.pow(10, 0);
    //     let avail_point = Math.ceil((checkNumeric(newData.avail_charge_balance) / checkNumeric(newData.total_charge_balance)) * 100 * Math.pow(10, 0)) / Math.pow(10, 0);
    //     setUsedCharge(used_point);
    //     let chargeCurrentCtx: any = document.getElementById('chargeCurrent');

    //     let datasets =
    //         used_point == 0
    //             ? [
    //                   {
    //                       label: ['미사용'],
    //                       data: [avail_point],
    //                       backgroundColor: ['#F2F3F6'],
    //                   },
    //               ]
    //             : [
    //                   {
    //                       label: ['사용완료', '미사용'],
    //                       data: [used_point, avail_point],
    //                       backgroundColor: ['#f44a3d', '#F2F3F6'],
    //                   },
    //               ];
    //     let config: any = {
    //         type: 'pie',
    //         data: {
    //             datasets: datasets,
    //         },
    //         plugins: [ChartDataLabels],
    //         options: {
    //             responsive: false, // true : 정적(width="60" height="60"), false : 동적(width="60vw" height="60vh") 사이즈 조정 가능
    //             legend: {
    //                 display: false,
    //             },
    //             animation: {
    //                 animateScale: true, // 중앙에서 바깥쪽으로 차트 배율을 애니메이션 합니다.
    //                 animateRotate: true, //차트가 회전 애니메이션으로 애니메이션 합니다.
    //             },
    //             plugins: {
    //                 legend: {
    //                     display: false,
    //                 },
    //                 tooltip: {
    //                     // 기존 툴팁 사용 안 함
    //                     enabled: false,
    //                 },
    //                 datalabels: {
    //                     color: 'white',
    //                     font: {
    //                         size: '15px',
    //                         weight: 'bold',
    //                     },
    //                     align: 'center',
    //                     formatter: function (value, context) {
    //                         return context.active ? context.dataset.label[context.dataIndex] + '\n' + value + '%' : Math.round(value);
    //                     },
    //                 },
    //             },
    //         },
    //     };

    //     new Chart(chargeCurrentCtx, config);
    // };
    // const fnChartPointData = async () => {
    //     let newData = await getJsonData();

    //     let used_point = Math.ceil((checkNumeric(newData.used_welfare_point) / checkNumeric(newData.saved_welfare_point)) * 100 * Math.pow(10, 0)) / Math.pow(10, 0);
    //     let avail_point = Math.ceil((checkNumeric(newData.avail_welfare_point) / checkNumeric(newData.saved_welfare_point)) * 100 * Math.pow(10, 0)) / Math.pow(10, 0);
    //     setUsedPoint(used_point);
    //     let pointCurrentCtx: any = document.getElementById('pointCurrent');

    //     let datasets =
    //         used_point == 0
    //             ? [
    //                   {
    //                       label: ['미사용'],
    //                       data: [avail_point],
    //                       backgroundColor: ['#F2F3F6'],
    //                   },
    //               ]
    //             : [
    //                   {
    //                       label: ['사용완료', '미사용'],
    //                       data: [used_point, avail_point],
    //                       backgroundColor: ['#f44a3d', '#F2F3F6'],
    //                   },
    //               ];

    //     let config: any = {
    //         type: 'pie',
    //         data: {
    //             datasets: datasets,
    //         },
    //         plugins: [ChartDataLabels],
    //         options: {
    //             responsive: false,
    //             legend: {
    //                 display: false,
    //             },
    //             animation: {
    //                 animateScale: true,
    //                 animateRotate: true,
    //             },
    //             plugins: {
    //                 legend: {
    //                     display: false,
    //                 },
    //                 tooltip: {
    //                     enabled: false,
    //                 },
    //                 datalabels: {
    //                     color: 'white',
    //                     font: {
    //                         size: '15px',
    //                         weight: 'bold',
    //                     },
    //                     align: 'center',
    //                     formatter: function (value, context) {
    //                         return context.active ? context.dataset.label[context.dataIndex] + '\n' + value + '%' : Math.round(value);
    //                     },
    //                 },
    //             },
    //         },
    //     };

    //     new Chart(pointCurrentCtx, config);
    // };
    // [ E ] chart.js

    return (
        <Layout user={props.user} title="indendkorea admin console" nav_id="" crumbs={[]}>
            <main className="dashboard">
                <div className="grid grid-cols-8 gap-5">
                    <div aria-label="임직원정보" className="card-box mb-10 col-span-2">
                        <div className="card-body">
                            <div className="flex items-center gap-3 mb-3">
                                <img src={userInfo?.file_logo ? userInfo?.file_logo : userInfo?.file_mall_logo} alt="logo_img" className="w-36" />
                            </div>
                            <div className="text-xl font-bold justify-between flex items-center">
                                <div>{userInfo?.company_name} </div>
                                {/* <div>
                                    <i className="fas fa-cog cursor-pointer" onClick={() => fnPagemove('partner')}></i>
                                </div> */}
                            </div>
                            <div className="text-xl mt-2">복지몰명 : {userInfo?.mall_name}</div>
                            <div className="mt-2 text-gray-700 flex items-center gap-1 text-xl justify-between">
                                <div>
                                    [{userInfo?.depart}] {userInfo?.name}{' '}
                                </div>
                                {/* <div>
                                    <i className="fas fa-cog cursor-pointer" onClick={() => fnPagemove('manager')}></i>
                                </div> */}
                            </div>
                        </div>
                    </div>
                    <div aria-label="예치금 현황" className="card-box mb-10 col-span-3">
                        <div className="card-header">
                            <div className="title flex gap-3 items-center">
                                <div>예치금 현황</div>
                                <div>
                                    (<span className="text-gray-500 text-base font-normal">총 충전 예치금</span>
                                    <span className="font-bold text-base"> {num2Cur(point?.total_charge_balance)} P</span>)
                                </div>
                            </div>
                            <div className="flex-shrink-0" onClick={() => fnPagemove('balance')}>
                                <div className="text-sm text-gray-500 flex items-center cursor-pointer">
                                    더보기
                                    <i className="fas fa-chevron-right fa-xs ms-2"></i>
                                </div>
                            </div>
                        </div>
                        <div className="card-body">
                            <div className="grid grid-cols-2 text-center divide-x">
                                {[
                                    ['사용 예치금', point?.used_charge_balance, 'text-blue-500'],
                                    ['잔여 예치금', point?.avail_charge_balance, 'text-red-500'],
                                ].map(([title, point, color]) => (
                                    <div key={title} className="">
                                        <div className="text-gray-500">{title}</div>
                                        <div className="font-bold text-xl">
                                            <span className={cls('num2Cur !text-center', color)}>{num2Cur(point)} P</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                    <div aria-label="복지포인트 현황" className="card-box mb-10 col-span-3">
                        <div className="card-header">
                            <div className="title flex gap-3 items-center">
                                <div>복지포인트 현황</div>
                                <div>
                                    (<span className="text-gray-500 text-base font-normal">지급완료 복지포인트</span>
                                    <span className="font-bold text-base"> {num2Cur(point?.saved_welfare_point)} P</span>)
                                </div>
                            </div>
                            <div className="flex-shrink-0" onClick={() => fnPagemove('bokji')}>
                                <div className="text-sm text-gray-500 flex items-center cursor-pointer">
                                    더보기
                                    <i className="fas fa-chevron-right fa-xs ms-2"></i>
                                </div>
                            </div>
                        </div>
                        <div className="card-body">
                            <div className="grid grid-cols-3 text-center divide-x">
                                {[
                                    ['사용완료 복지포인트', point?.used_welfare_point, 'text-blue-500'],
                                    ['미사용 복지포인트', point?.avail_welfare_point, 'text-red-500'],
                                    ['만료된 복지포인트', point?.exp_welfare_point, ''],
                                ].map(([title, point, color]) => (
                                    <div key={title} className="">
                                        <div className="text-gray-500">{title}</div>
                                        <div className="font-bold text-xl">
                                            <span className={cls('num2Cur !text-center', color)}>{num2Cur(point)} P</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
                <div className="grid grid-cols-3 gap-5">
                    <div aria-label="예치금/포인트 사용현황" className="card-box mb-10 col-span-1">
                        <div className="card-header">
                            <div className="title">예치금/포인트 현황</div>
                        </div>
                        <div className="card-body">
                            <div className="flex gap-3 justify-between">
                                <div>
                                    <canvas id="chargeCurrent" width="200" height="200"></canvas>
                                    <div className="text-center">
                                        사용완료
                                        <br />
                                        예치금
                                        <br />
                                        <span className="text-red-500 text-xl font-bold">{usedCharge}%</span>
                                    </div>
                                </div>
                                <div>
                                    <canvas id="pointCurrent" width="200" height="200"></canvas>
                                    <div className="text-center">
                                        사용완료
                                        <br />
                                        복지포인트
                                        <br />
                                        <span className="text-orange-500 text-xl font-bold">{usedPoint}%</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div aria-label="카테고리별 포인트 사용 현황" className="card-box mb-10 col-span-2">
                        <div className="card-header">
                            <div className="title">카테고리별 포인트 사용 현황</div>
                        </div>
                        <div className="card-body"></div>
                    </div>
                </div>
                <div className="grid grid-cols-4 gap-5">
                    <div aria-label="임직원 현황" className="card-box mb-10 col-span-1">
                        <div className="card-header">
                            <div className="title">임직원 현황</div>
                            <div className="flex-shrink-0" onClick={() => fnPagemove('member')}>
                                <div className="text-sm text-gray-500 flex items-center cursor-pointer">
                                    더보기
                                    <i className="fas fa-chevron-right fa-xs ms-2"></i>
                                </div>
                            </div>
                        </div>
                        <div className="card-body">
                            <ul className="flex flex-col gap-4">
                                {[
                                    ['전체 임직원', `${member?.all_cnt} 명`],
                                    ['재직 임직원', `${member?.mem_재직} 명`],
                                    ['휴직 임직원', `${member?.mem_휴직} 명`],
                                    ['퇴직 임직원', `${member?.mem_퇴직} 명`],
                                ].map(([title, count]) => (
                                    <li key={title} className="flex justify-between items-center leading-none">
                                        <div className="text-gray-500">{title}</div>
                                        <div className="font-bold">{count}</div>
                                    </li>
                                ))}
                            </ul>
                        </div>
                        <div className="card-footer" onClick={() => fnPagemove('new_member')}>
                            <div className="text-sm font-bold">신규 임직원 등록하기</div>
                            <div className="text-sm font-bold">
                                <i className="fas fa-chevron-right fa-xs ms-2"></i>
                            </div>
                        </div>
                    </div>
                    <div aria-label="예치금 충전 현황" className="card-box mb-10 col-span-1">
                        <div className="card-header">
                            <div className="title">예치금 충전 현황</div>
                            <div className="flex-shrink-0" onClick={() => fnPagemove('balance')}>
                                <div className="text-sm text-gray-500 flex items-center cursor-pointer">
                                    더보기
                                    <i className="fas fa-chevron-right fa-xs ms-2"></i>
                                </div>
                            </div>
                        </div>
                        <div className="card-body">
                            <ul className="flex flex-col gap-4">
                                {balance?.map((v: any, i: number) => (
                                    <li key={i} className="flex justify-between items-center leading-none">
                                        <div className="text-gray-500">{v.create_at}</div>
                                        <div className="font-bold">{num2Cur(v.save_point)} 원</div>
                                    </li>
                                ))}
                            </ul>
                        </div>
                        <div className="card-footer" onClick={() => fnPagemove('balance')}>
                            <div className="text-sm font-bold">예치금 충전하기</div>
                            <div className="text-sm font-bold">
                                <i className="fas fa-chevron-right fa-xs ms-2"></i>
                            </div>
                        </div>
                    </div>
                    <div aria-label="복지포인트 지급/회수 현황" className="card-box mb-10 col-span-1">
                        <div className="card-header">
                            <div className="title">복지포인트 지급/회수 현황</div>
                            <div className="flex-shrink-0" onClick={() => fnPagemove('point_list')}>
                                <div className="text-sm text-gray-500 flex items-center cursor-pointer">
                                    더보기
                                    <i className="fas fa-chevron-right fa-xs ms-2"></i>
                                </div>
                            </div>
                        </div>
                        <div className="card-body">
                            <ul className="flex flex-col gap-4">
                                {assing?.map((v: any, i: number) => (
                                    <li key={i} className="flex justify-between items-center leading-none">
                                        <div className="text-gray-500">{v.create_at}</div>
                                        <div className={cls('', v.saved_type == '개별회수' ? 'text-red-500' : 'text-blue-500')}>{v.saved_type}</div>
                                        <div className="font-bold">{num2Cur(v.saved_point)} P</div>
                                    </li>
                                ))}
                            </ul>
                        </div>
                        <div className="card-footer" onClick={() => fnPagemove('bokji')}>
                            <div className="text-sm font-bold">복지포인트 지급하기</div>
                            <div className="text-sm font-bold">
                                <i className="fas fa-chevron-right fa-xs ms-2"></i>
                            </div>
                        </div>
                    </div>
                    <div aria-label="일별 복지포인트 사용 현황" className="card-box mb-10 col-span-1">
                        <div className="card-header">
                            <div className="title">일별 복지포인트 사용 현황</div>
                            <div className="flex-shrink-0" onClick={() => fnPagemove('point_used')}>
                                <div className="text-sm text-gray-500 flex items-center cursor-pointer">
                                    더보기
                                    <i className="fas fa-chevron-right fa-xs ms-2"></i>
                                </div>
                            </div>
                        </div>
                        <div className="card-body">
                            <ul className="flex flex-col gap-4">
                                {dayPoint?.map((v: any, i: number) => (
                                    <li key={i} className="flex justify-between items-center leading-none">
                                        <div className="text-gray-500">{v.create_at}</div>
                                        <div className="font-bold">{num2Cur(v.used_point)} P</div>
                                    </li>
                                ))}
                            </ul>
                        </div>
                        <div className="card-footer" onClick={() => fnPagemove('point_used')}>
                            <div className="text-sm font-bold">포인트 사용현황 보러가기</div>
                            <div className="text-sm font-bold">
                                <i className="fas fa-chevron-right fa-xs ms-2"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </Layout>
    );
};

export default Home;
