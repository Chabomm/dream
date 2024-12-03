import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';

const UmsTmplPreview: NextPage = (props: any) => {
    const router = useRouter();
    const [preview, setPreview] = useState<any>([]);

    useEffect(() => {
        if (props) {
            setPreview(props.response.preview);
        }
    }, [props]);

    return (
        <>
            <div dangerouslySetInnerHTML={{ __html: preview }}></div>
        </>
    );
};
export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {
        uid: ctx.query.uid,
        layout_uid: ctx.query.layout_uid,
    };
    var response: any = {};
    try {
        const { data } = await api.post(`/ums/tmpl/preview`, request);
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

export default UmsTmplPreview;
