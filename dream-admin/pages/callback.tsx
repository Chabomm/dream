import type { GetServerSideProps, NextPage } from 'next';
import React, { useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';

const AzureCallBack: NextPage = (props: any) => {
    const router = useRouter();
    const redirect_url: string = router.query.redirect_url !== undefined ? router.query.redirect_url + '' : '';

    useEffect(() => {
        if (props.response?.code == 200) {
            localStorage.setItem('admin_menus', JSON.stringify(props.response.admin_menus));
            router.replace('/');
        } else {
            // alert('fail');
            // router.replace('/fail');
        }
    }, [props]);

    return <></>;
};

export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {
        sub: ctx.query.sub,
    };
    var response: any = {};
    try {
        const { data } = await api.post(`/be/admin/pullgy`, request);
        response = data;
    } catch (e: any) {
        console.log(e);
        if (typeof e.redirect !== 'undefined') {
            return { redirect: e.redirect };
        }
    }
    return {
        props: { request, response },
    };
};

export default AzureCallBack;
