// import Layout from 'components/Layout';
// import { NextPage } from 'next';
// import ServiceItemsList from './tmpl/list';

// const B2bGoodsList: NextPage = (props: any) => {
//     const nav_id = 63;
//     const crumbs = ['고객사혜택', '서비스 리스트'];

//     return (
//         <Layout nav_id={nav_id} crumbs={crumbs} title={crumbs[crumbs.length - 1]} user={props.user}>
//             <ServiceItemsList service_type={'C'} user={props.user} />
//         </Layout>
//     );
// };

// export default B2bGoodsList;

import type { GetServerSideProps, NextPage, NextPageContext } from 'next';
import React from 'react';
import Layout from '@/components/Layout';
import api, { setContext } from '@/libs/axios';
import Callout from '@/components/UIcomponent/table/Callout';

import dynamic from 'next/dynamic';
const TmplList = dynamic(() => import('./tmpl/list'), { ssr: false });

const B2bGoodsList: NextPage = (props: any) => {
    const nav_id = 63;
    const crumbs = ['부가 서비스', '서비스 리스트'];
    const title_sub = '';
    const callout = [];

    return (
        <Layout nav_id={nav_id} crumbs={crumbs} title={crumbs[crumbs.length - 1]} user={props.user}>
            <Callout title={crumbs[crumbs.length - 1]} title_sub={title_sub} callout={callout} />
            <TmplList response={props.response} user={props.user} />
        </Layout>
    );
};

export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {};
    var response: any = {};
    try {
        const { data } = await api.post(`/be/manager/b2b/goods/init/`, request);
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

export default B2bGoodsList;
