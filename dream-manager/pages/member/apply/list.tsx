import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect, useRef } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import Empty from '@/components/Empty';

const MemberApplyList: NextPage = (props: any) => {
    const nav_id = 79;
    const crumbs = ['임직원 관리', '가입신청 내역'];
    const router = useRouter();

    return (
        <Layout nav_id={nav_id} crumbs={crumbs} title={crumbs[crumbs.length - 1]} user={props.user}>
            <Empty title={crumbs[crumbs.length - 1]}></Empty>
        </Layout>
    );
};
export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {};
    var response: any = {};

    return {
        props: { request, response },
    };
};

export default MemberApplyList;
