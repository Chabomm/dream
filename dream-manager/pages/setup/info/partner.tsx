import type { GetServerSideProps, NextPage } from 'next';
import React, { useEffect, useState } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import Link from 'next/link';

import { EditForm, EditFormTable, EditFormTH, EditFormTD, EditFormSubmit, EditFormInput, EditFormLabel, EditFormTextarea } from '@/components/UIcomponent/form/EditFormA';
import EditFormCallout from '@/components/UIcomponent/form/EditFormCallout';

const SetupInfoPartner: NextPage = (props: any) => {
    const nav_id = 120;
    const crumbs = ['환경설정', '구축정보'];
    const callout = [];
    const title_sub = '로그인 계정의 정보를 변경할 수 있습니다.';
    const router = useRouter();
    const [posts, setPosts] = useState<any>([]);

    useEffect(() => {
        setPosts(props.response);
    }, []);

    return (
        <Layout nav_id={nav_id} crumbs={crumbs} title={crumbs[crumbs.length - 1]} user={props.user}>
            <EditFormCallout title={crumbs[crumbs.length - 1]} title_sub={title_sub} callout={callout} className="" />
            <EditFormTable className="grid-cols-6">
                <EditFormTH className="col-span-1">복지몰 도메인</EditFormTH>
                <EditFormTD className="col-span-5">
                    <EditFormLabel className="">
                        <span className="me-2">https://{posts?.partner_id}.welfaredream.com</span>
                        <Link href={`https://${posts?.partner_id}.welfaredream.com`} target="_blank">
                            <i className="fas fa-external-link-alt ms-1"></i>
                        </Link>
                    </EditFormLabel>
                </EditFormTD>
                <EditFormTH className="col-span-1">회사명</EditFormTH>
                <EditFormTD className="col-span-2">
                    <EditFormLabel className="">{posts.company_name}</EditFormLabel>
                </EditFormTD>
                <EditFormTH className="col-span-1">복지몰명</EditFormTH>
                <EditFormTD className="col-span-2">
                    <EditFormLabel className="">{posts.mall_name}</EditFormLabel>
                </EditFormTD>
                <EditFormTH className="col-span-1">대표자 이름</EditFormTH>
                <EditFormTD className="col-span-2">
                    <EditFormLabel className="">{posts.ceo_name}</EditFormLabel>
                </EditFormTD>
                <EditFormTH className="col-span-1">사업자등록번호</EditFormTH>
                <EditFormTD className="col-span-2">
                    <EditFormLabel className="">{posts.biz_no}</EditFormLabel>
                </EditFormTD>
                <EditFormTH className="col-span-1">회사 주소</EditFormTH>
                <EditFormTD className="col-span-5">
                    <EditFormLabel className="">
                        ({posts.post}){posts.addr}
                        {posts.addr_detail}
                    </EditFormLabel>
                </EditFormTD>
                <EditFormTH className="col-span-1">회사 대표번호</EditFormTH>
                <EditFormTD className="col-span-2">
                    <EditFormLabel className="">{posts.company_hp}</EditFormLabel>
                </EditFormTD>
                <EditFormTH className="col-span-1">고객사 코드</EditFormTH>
                <EditFormTD className="col-span-2">
                    <EditFormLabel className="">{posts.host}</EditFormLabel>
                </EditFormTD>
                <EditFormTH className="col-span-1">담당자명</EditFormTH>
                <EditFormTD className="col-span-2">
                    <EditFormLabel className="">{posts.staff_name}</EditFormLabel>
                </EditFormTD>
                <EditFormTH className="col-span-1">부서 및 직책</EditFormTH>
                <EditFormTD className="col-span-2">
                    <EditFormLabel className="">
                        {posts.staff_dept} {posts.staff_position} {posts.staff_position2}
                    </EditFormLabel>
                </EditFormTD>
                <EditFormTH className="col-span-1">담당자 휴대번호</EditFormTH>
                <EditFormTD className="col-span-2">
                    <EditFormLabel className="">{posts.staff_mobile}</EditFormLabel>
                </EditFormTD>
                <EditFormTH className="col-span-1">담당자 이메일</EditFormTH>
                <EditFormTD className="col-span-2">
                    <EditFormLabel className="">{posts.staff_email}</EditFormLabel>
                </EditFormTD>
            </EditFormTable>
        </Layout>
    );
};
export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {};
    var response: any = {};
    try {
        const { data } = await api.post(`/be/manager/setup/info/partner/read`, request);
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

export default SetupInfoPartner;
