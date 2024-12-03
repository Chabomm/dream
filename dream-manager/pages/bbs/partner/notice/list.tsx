import type { GetServerSideProps, NextPage, NextPageContext } from 'next';
import React from 'react';
import Layout from '@/components/Layout';
import api, { setContext } from '@/libs/axios';
import Callout from '@/components/UIcomponent/table/Callout';

import dynamic from 'next/dynamic';
const BoardPostList = dynamic(() => import('../../board/list'), { ssr: false });

const BoardPartnerNotice: NextPage = (props: any) => {
    const nav_id = 69;
    const crumbs = ['사내복지관리', '사내 공지사항'];
    const title_sub = '공지사항을 관리할 수 있습니다.';
    const callout = [];

    return (
        <Layout nav_id={nav_id} crumbs={crumbs} title={crumbs[crumbs.length - 1]} user={props.user}>
            <Callout title={crumbs[crumbs.length - 1]} title_sub={title_sub} callout={callout} />
            <BoardPostList response={props.response} />
        </Layout>
    );
};

export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {
        board_uid: 2,
    };
    var response: any = {};
    try {
        const { data } = await api.post(`/be/manager/bbs/init/${request.board_uid}`, request);
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

export default BoardPartnerNotice;
