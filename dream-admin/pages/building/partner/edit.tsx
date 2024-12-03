import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import { cls, checkNumeric } from '@/libs/utils';
import useForm from '@/components/form/useForm';
import LayoutPopup from '@/components/LayoutPopup';

const BuildingPartnerEdit: NextPage = (props: any) => {
    const router = useRouter();

    useEffect(() => {
        if (props) {
            s.setValues(props.response);
        }
    }, [props]);

    const { s, fn, attrs } = useForm({
        initialValues: {},
        onSubmit: async () => {
            await editing('REG');
        },
    });

    const deleting = () => editing('DEL');

    const editing = async mode => {
        try {
            if (mode == 'REG' && s.values.uid > 0) {
                mode = 'MOD';
            }
            s.values.mode = mode;
            const { data } = await api.post(`/be/admin/setup/roles/edit`, s.values);
            if (data.code == 200) {
                if (s.values.mode == 'REG') {
                    alert(data.msg);
                    router.replace(`/setup/roles/edit?uid=${s.values.uid}`);
                } else {
                    alert(data.msg);
                    if (mode == 'MOD') {
                        router.replace(`/setup/roles/edit?uid=${data.uid}`);
                    }
                }
            } else {
                alert(data.msg);
            }

            return;
        } catch (e: any) {}
    };

    return (
        <LayoutPopup title={'고객사 상세'}>
            <div className="card_area mb-20">
                <section className="site-width pb-24 bbs-contents">
                    <div className="mb-10 px-10">
                        <div className="my-10 text-center">
                            <div className="text-2xl font-bold mb-2">고객사 상세</div>
                            <div className="text font-normal text-gray-500">{s.values.create_at}</div>
                        </div>
                        <table className="form-table table table-bordered align-middle w-full border-y-2 border-second">
                            <tbody className="border-t border-black">
                                <tr className="border-b">
                                    <th scope="row">
                                        <span className="">uid</span>
                                    </th>
                                    <td className="">
                                        <div className="">{s.values.uid}</div>
                                    </td>
                                    <th scope="row">
                                        <span className="">타입</span>
                                    </th>
                                    <td className="">
                                        <div className="">
                                            {s.values.partner_type == 100
                                                ? '개방형'
                                                : s.values.partner_type == 200
                                                ? '직접회원가입'
                                                : s.values.partner_type == 201
                                                ? '직접회원가입 승인제도'
                                                : s.values.partner_type == 300
                                                ? '관리자가 회원등록'
                                                : s.values.partner_type == 400 && '자동로그인'}
                                        </div>
                                    </td>
                                </tr>

                                <tr className="border-b">
                                    <th scope="row">
                                        <span className="">고객사 ID</span>
                                    </th>
                                    <td colSpan={3} className="">
                                        <div className="">{s.values.partner_id}</div>
                                    </td>
                                </tr>

                                <tr className="border-b">
                                    <th scope="row">
                                        <span className="">복지몰명</span>
                                    </th>
                                    <td className="">
                                        <div className="">{s.values.mall_name}</div>
                                    </td>
                                    <th scope="row">
                                        <span className="">고객사 회사명</span>
                                    </th>
                                    <td className="">
                                        <div className="">{s.values.company_name}</div>
                                    </td>
                                </tr>
                                <tr className="border-b">
                                    <th scope="row">
                                        <span className="">스폰서</span>
                                    </th>
                                    <td className="">
                                        <div className="">{s.values.sponsor}</div>
                                    </td>
                                    <th scope="row">
                                        <span className="">고객사 코드</span>
                                    </th>
                                    <td className="">
                                        <div className="">{s.values.partner_code}</div>
                                    </td>
                                </tr>
                                <tr className="border-b">
                                    <th scope="row">
                                        <span className="">아이디프리픽스</span>
                                    </th>
                                    <td className="">
                                        <div className="">{s.values.prefix}</div>
                                    </td>
                                    <th scope="row">
                                        <span className="">로고 이미지</span>
                                    </th>
                                    <td className="">
                                        <div className="">{s.values.logo}</div>
                                    </td>
                                </tr>
                                <tr className="border-b">
                                    <th scope="row">
                                        <span className="">
                                            복지포인트
                                            <br />
                                            사용여부
                                        </span>
                                    </th>
                                    <td className="">
                                        <div className="">{s.values.is_welfare}</div>
                                    </td>
                                    <th scope="row">
                                        <span className="">
                                            드림포인트
                                            <br />
                                            사용여부
                                        </span>
                                    </th>
                                    <td className="">
                                        <div className="">{s.values.is_dream}</div>
                                    </td>
                                </tr>
                                <tr className="border-b">
                                    <th scope="row">
                                        <span className="">상태</span>
                                    </th>
                                    <td className="">
                                        <div className="">
                                            {s.values.state == 100
                                                ? '대기'
                                                : s.values.state == 200
                                                ? '운영중'
                                                : s.values.state == 300
                                                ? '일시중지'
                                                : s.values.state == 400 && '폐쇄'}
                                        </div>
                                    </td>
                                    <th scope="row">
                                        <span className="">회원유형</span>
                                    </th>
                                    <td className="">
                                        <div className="">{s.values.mem_type}</div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    {s.values.manager_list?.length > 0 ? (
                        <div className="mb-10 px-10">
                            <div className="my-10 text-center">
                                <div className="text-2xl font-bold mb-2">고객사 담당자 리스트</div>
                            </div>
                            <div className="col-table">
                                <div className="col-table-th grid grid-cols-7 sticky top-16 bg-gray-100">
                                    <div className="">UID</div>
                                    <div className="">관리자 ID</div>
                                    <div className="">이름</div>
                                    <div className="">부서</div>
                                    <div className="">역할</div>
                                    <div className="">상태</div>
                                    <div className="">날짜</div>
                                </div>

                                {s.values.manager_list?.map((v: any, i: number) => (
                                    <div key={i} className="col-table-td grid grid-cols-7 bg-white transition duration-300 ease-in-out hover:bg-gray-100">
                                        <div className="">{v.uid}</div>
                                        <div className="">{v.login_id}</div>
                                        <div className="">{v.name}</div>
                                        <div className="">{v.depart}</div>
                                        <div className="">{v.roles}</div>
                                        <div className="">{v.state}</div>
                                        <div className="">{v.create_at}</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ) : null}
                </section>
            </div>
        </LayoutPopup>
    );
};
export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {
        uid: ctx.query.uid,
    };
    var response: any = {};
    try {
        const { data } = await api.post(`/be/admin/building/partner/read`, request);
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

export default BuildingPartnerEdit;
