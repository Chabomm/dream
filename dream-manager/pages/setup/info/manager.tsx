import type { GetServerSideProps, NextPage } from 'next';
import React, { useEffect, useState } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import useForm from '@/components/form/useForm';
import Layout from '@/components/Layout';

import { EditForm, EditFormTable, EditFormTH, EditFormTD, EditFormSubmit, EditFormInput, EditFormLabel, EditFormTextarea } from '@/components/UIcomponent/form/EditFormA';
import EditFormCallout from '@/components/UIcomponent/form/EditFormCallout';

const SetupInfoManager: NextPage = (props: any) => {
    const nav_id = 110;
    const crumbs = ['환경설정', '계정관리'];
    const callout = [];
    const title_sub = '로그인 계정의 정보를 변경할 수 있습니다.';
    const router = useRouter();

    const [posts, setPosts] = useState<any>({});

    useEffect(() => {
        if (JSON.stringify(props) !== '{}') {
            setPosts(props.response);
            s.setValues(props.response.values);
        }
    }, [props]);

    const { s, fn, attrs } = useForm({
        initialValues: {},
        onSubmit: async () => {
            await editing();
        },
    });

    const editing = async () => {
        try {
            s.values.login_id = posts.login_id;

            const { data } = await api.post(`/be/manager/setup/info/edit`, s.values);
            if (data.code == 200) {
                alert(data.msg);
                router.replace(`/setup/info/manager`);
            } else {
                alert(data.msg);
            }
            return;
        } catch (e: any) {}
    };

    return (
        <Layout nav_id={nav_id} crumbs={crumbs} title={crumbs[crumbs.length - 1]} user={props.user} className="w-2/3">
            <EditFormCallout title={crumbs[crumbs.length - 1]} title_sub={title_sub} callout={callout} />
            <div className=" w-2/3"></div>
            <EditForm onSubmit={fn.handleSubmit}>
                <EditFormTable className="grid-cols-6">
                    <EditFormTH className="col-span-1">아이디</EditFormTH>
                    <EditFormTD className="col-span-2">
                        <EditFormLabel className="">{posts.login_id}</EditFormLabel>
                    </EditFormTD>
                    <EditFormTH className="col-span-1">비밀번호</EditFormTH>
                    <EditFormTD className="col-span-2">
                        <div className="flex gap-2 items-center">
                            <EditFormInput
                                type="password"
                                name="login_pw"
                                value={s.values?.login_pw || ''}
                                onChange={fn.handleChange}
                                errors={s.errors}
                                className="w-full flex-grow"
                            />
                        </div>
                    </EditFormTD>
                    <EditFormTH className="col-span-1">이름</EditFormTH>
                    <EditFormTD className="col-span-2">
                        <EditFormLabel className="">{posts.name}</EditFormLabel>
                    </EditFormTD>
                    <EditFormTH className="col-span-1">부서</EditFormTH>
                    <EditFormTD className="col-span-2">
                        <EditFormLabel className="">{posts.depart}</EditFormLabel>
                    </EditFormTD>
                    <EditFormTH className="col-span-1">직급/직책</EditFormTH>
                    <EditFormTD className="col-span-2">
                        <EditFormLabel className="">
                            {posts.position1} {posts.position2}
                        </EditFormLabel>
                    </EditFormTD>
                    <EditFormTH className="col-span-1">이메일</EditFormTH>
                    <EditFormTD className="col-span-2">
                        <EditFormLabel className="">{posts.email}</EditFormLabel>
                    </EditFormTD>
                    <EditFormTH className="col-span-1">일반전화번호</EditFormTH>
                    <EditFormTD className="col-span-2">
                        <EditFormInput type="text" name="tel" value={s.values?.tel || ''} onChange={fn.handleChange} errors={s.errors} className="w-full" />
                    </EditFormTD>
                    <EditFormTH className="col-span-1">핸드폰번호</EditFormTH>
                    <EditFormTD className="col-span-2">
                        <EditFormInput type="text" name="mobile" value={s.values?.mobile || ''} is_mobile={true} onChange={fn.handleChange} errors={s.errors} className="w-full" />
                    </EditFormTD>
                </EditFormTable>
                <EditFormSubmit button_name={`${s.values?.uid > 0 ? '수정' : '등록'}하기`} submitting={s.submitting}></EditFormSubmit>
            </EditForm>
        </Layout>
    );
};
export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {};
    var response: any = {};
    try {
        const { data } = await api.post(`/be/manager/setup/info/read`, request);
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

export default SetupInfoManager;
