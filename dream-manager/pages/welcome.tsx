import { useRouter } from 'next/router';
import React, { useState, useEffect } from 'react';
import { GetServerSideProps, NextPage, NextPageContext } from 'next';

import LayoutPopup from '@/components/LayoutPopup';
import useForm from '@/components/form/useForm';
import { api, setContext } from '@/libs/axios';
import { cls } from '@/libs/utils';
import ButtonEditing from '@/components/UIcomponent/ButtonEditing';

import {
    EditForm,
    EditFormTable,
    EditFormTH,
    EditFormTD,
    EditFormRadioList,
    EditFormSubmit,
    EditFormInput,
    EditFormLabel,
    EditFormAddr,
    EditFormCard,
    EditFormCardHead,
    EditFormCardBody,
    EditFormSelect,
    EditFormTextarea,
} from '@/components/UIcomponent/form/EditFormA';
import EditFormCallout from '@/components/UIcomponent/form/EditFormCallout';

const Welcome: NextPage = (props: any) => {
    const crumbs = ['비밀번호 재설정'];
    const callout = ['비밀번호를 재설정 후 이용 가능합니다.', '기타 정보는 홈 > 환경설정 > 정보수정 에서 수정가능합니다.'];
    const title_sub = '';
    const router = useRouter();

    const [posts, setPosts] = useState<any>({});

    useEffect(() => {
        if (JSON.stringify(props) !== '{}') {
            s.setValues(props.response.values);
            setPosts(props.response);
        }
    }, [props]);

    const { s, fn, attrs } = useForm({
        onSubmit: async () => {
            await editing();
        },
    });

    const editing = async () => {
        try {
            const params = { ...s.values };

            // const regex = /^(?=.*[a-zA-Z])(?=.*[0-9])(?=.*[!@#$%^&*?._]).{6,20}$/;
            // var regex = /^(?=.*[a-zA-Z])(?=.*[!\.@#$%^~*+=-])(?=.*[0-9]).{10,20}$/;
            // var regex = /^(?=.*[a-zA-Z])(?=.*\d)(?=.*[$@$!%*#?&\\.])[A-Za-z\d$@$!%*#?&\\.]{8,20}$/;

            // if (params.login_pw !== '') {
            //     if (!regex.test(params.login_pw)) {
            //         alert('비밀번호는 영문, 숫자 조합 6자 이상, 20자 이하여야 합니다.');
            //         return;
            //     }
            // }

            // 임시 비번 새 비번 같으면
            if (params.login_pw != params.login_pw2) {
                alert('새 비밀번호와 새 비밀번호 확인 값이 일치하지 않습니다.');
                return;
            }

            const res = await api.post(`/be/manager/setup/info/edit`, params);
            const result = res.data;

            if (result.code == 200) {
                alert(result.msg);
                router.replace(`/`);
            } else {
                alert(result.msg);
            }
        } catch (e: any) {}
    };

    return (
        <LayoutPopup title={crumbs[crumbs.length - 1]} className="px-6 bg-slate-100">
            <EditFormCallout title={crumbs[crumbs.length - 1]} title_sub={title_sub} callout={callout} className="w-2/3 mx-auto" />

            <EditForm onSubmit={fn.handleSubmit}>
                <EditFormCard className="w-2/3 mx-auto">
                    <EditFormCardBody>
                        <EditFormTable className="grid-cols-6">
                            <EditFormTH className="col-span-1">새 비밀번호</EditFormTH>
                            <EditFormTD className="col-span-2">
                                <EditFormInput
                                    type="password"
                                    name="login_pw"
                                    autoComplete="new-password"
                                    value={s.values?.login_pw || ''}
                                    is_mand={true}
                                    placeholder={'새 비밀번호를 입력해주세요'}
                                    onChange={fn.handleChange}
                                    errors={s.errors}
                                    className=""
                                />
                            </EditFormTD>
                            <EditFormTH className="col-span-1">새 비밀번호 확인</EditFormTH>
                            <EditFormTD className="col-span-2">
                                <EditFormInput
                                    type="password"
                                    name="login_pw2"
                                    autoComplete="new-password"
                                    value={s.values?.login_pw2 || ''}
                                    is_mand={true}
                                    placeholder={'새 비밀번호를 다시 입력해주세요'}
                                    onChange={fn.handleChange}
                                    errors={s.errors}
                                    className=""
                                />
                            </EditFormTD>
                            <EditFormTH className="col-span-1">관리자 ID</EditFormTH>
                            <EditFormTD className="col-span-2">
                                <EditFormLabel className="">{posts?.login_id}</EditFormLabel>
                            </EditFormTD>
                            <EditFormTH className="col-span-1">이름</EditFormTH>
                            <EditFormTD className="col-span-2">
                                <EditFormLabel className="">{posts?.name}</EditFormLabel>
                            </EditFormTD>
                            <EditFormTH className="col-span-1">부서</EditFormTH>
                            <EditFormTD className="col-span-2">
                                <EditFormLabel className="">{posts?.depart}</EditFormLabel>
                            </EditFormTD>
                            <EditFormTH className="col-span-1">이메일</EditFormTH>
                            <EditFormTD className="col-span-2">
                                <EditFormLabel className="">{posts?.email}</EditFormLabel>
                            </EditFormTD>
                            <EditFormTH className="col-span-1">내선번호</EditFormTH>
                            <EditFormTD className="col-span-2">
                                <EditFormLabel className="">{posts?.tel}</EditFormLabel>
                            </EditFormTD>
                            <EditFormTH className="col-span-1">핸드폰번호</EditFormTH>
                            <EditFormTD className="col-span-2">
                                <EditFormLabel className="">{posts?.mobile}</EditFormLabel>
                            </EditFormTD>
                        </EditFormTable>
                    </EditFormCardBody>
                </EditFormCard>
                <EditFormSubmit button_name={'수정하기'} submitting={s.submitting}></EditFormSubmit>
            </EditForm>
        </LayoutPopup>
    );
};

export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {};
    var response: any = {};
    try {
        const { data } = await api.post(`/be/manager/welcome/read`, request);
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

export default Welcome;
