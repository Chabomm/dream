import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import useForm from '@/components/form/useForm';
import LayoutPopup from '@/components/LayoutPopup';

import { EditForm, EditFormTable, EditFormTH, EditFormTD, EditFormSubmit, EditFormInput, EditFormCheckboxList, EditFormLabel } from '@/components/UIcomponent/form/EditFormA';
import EditFormCallout from '@/components/UIcomponent/form/EditFormCallout';

const SetupManagerEdit: NextPage = (props: any) => {
    const crumbs = ['환경설정', '관리자 ' + (props.response.values?.uid > 0 ? '수정' : '등록')];
    const callout = [];
    const title_sub = '관리자를 등록/수정할 수 있습니다';
    const router = useRouter();

    const [posts, setPosts] = useState<any>({});
    const [filter, setFilter] = useState<any>({});

    useEffect(() => {
        if (props) {
            if (props.response.code == 200) {
                setPosts(props.response);
                setFilter(props.response.filter);
                s.setValues(props.response.values);
            } else {
                alert(props.response.msg);
                window.close();
            }
        }
    }, []);

    const { s, fn, attrs } = useForm({
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

            const { data } = await api.post(`/be/admin/setup/admin/edit`, s.values);
            if (data.code == 200) {
                if (s.values.mode == 'REG') {
                    alert(data.msg);
                    router.replace(`/setup/admin/edit?uid=${data.uid}`);
                } else {
                    alert(data.msg);
                    if (mode == 'MOD') {
                        router.replace(`/setup/admin/edit?uid=${data.uid}`);
                    }
                }
            } else {
                alert(data.msg);
            }

            return;
        } catch (e: any) {}
    };

    return (
        <LayoutPopup title={crumbs[crumbs.length - 1]} className="px-3">
            <EditFormCallout title={crumbs[crumbs.length - 1]} title_sub={title_sub} callout={callout} />
            <EditForm onSubmit={fn.handleSubmit}>
                {process.env.NODE_ENV == 'development' && (
                    <pre className="">
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <div className="font-bold mb-3 text-red-500">filter</div>
                                {JSON.stringify(filter, null, 4)}
                            </div>
                            <div>
                                <div className="font-bold mb-3 text-red-500">s.values</div>
                                {JSON.stringify(s.values, null, 4)}
                            </div>
                            <div className="">
                                <div className="font-bold mb-3 text-red-500">posts</div>
                                {JSON.stringify(posts, null, 4)}
                            </div>
                        </div>
                    </pre>
                )}

                <EditFormTable className="grid-cols-6">
                    <EditFormTH className="col-span-1 mand">관리자 아이디</EditFormTH>
                    <EditFormTD className="col-span-2">
                        {s.values?.uid > 0 ? (
                            <EditFormLabel className="">{posts?.user_id}</EditFormLabel>
                        ) : (
                            <EditFormInput
                                type="text"
                                name="user_id"
                                value={s.values?.user_id || ''}
                                is_mand={true}
                                onChange={fn.handleChange}
                                errors={s.errors}
                                className="w-full"
                            />
                        )}
                    </EditFormTD>
                    <EditFormTH className="col-span-1">-</EditFormTH>
                    <EditFormTD className="col-span-2">-</EditFormTD>
                    <EditFormTH className="col-span-1 mand">관리자 이름</EditFormTH>
                    <EditFormTD className="col-span-2">
                        <EditFormInput
                            type="text"
                            name="user_name"
                            value={s.values?.user_name || ''}
                            is_mand={true}
                            onChange={fn.handleChange}
                            errors={s.errors}
                            className="w-full"
                        />
                    </EditFormTD>
                    <EditFormTH className="col-span-1 mand">이메일</EditFormTH>
                    <EditFormTD className="col-span-2">
                        <EditFormInput
                            type="text"
                            name="email"
                            value={s.values?.email || ''}
                            is_mand={true}
                            is_email={true}
                            onChange={fn.handleChange}
                            errors={s.errors}
                            className="w-full"
                        />
                    </EditFormTD>
                    <EditFormTH className="col-span-1">휴대전화</EditFormTH>
                    <EditFormTD className="col-span-2">
                        <EditFormInput type="tel" name="mobile" value={s.values?.mobile || ''} is_mobile={true} onChange={fn.handleChange} errors={s.errors} className="w-full" />
                    </EditFormTD>
                    <EditFormTH className="col-span-1">일반전화</EditFormTH>
                    <EditFormTD className="col-span-2">
                        <EditFormInput type="tel" name="tel" value={s.values?.tel || ''} onChange={fn.handleChange} errors={s.errors} className="w-full" />
                    </EditFormTD>
                    <EditFormTH className="col-span-1">직위</EditFormTH>
                    <EditFormTD className="col-span-2">
                        <EditFormInput type="text" name="position1" value={s.values?.position1 || ''} onChange={fn.handleChange} errors={s.errors} className="w-full" />
                    </EditFormTD>
                    <EditFormTH className="col-span-1">직책</EditFormTH>
                    <EditFormTD className="col-span-2">
                        <EditFormInput type="text" name="position2" value={s.values?.position2 || ''} onChange={fn.handleChange} errors={s.errors} className="w-full" />
                    </EditFormTD>
                    <EditFormTH className="col-span-1">부서</EditFormTH>
                    <EditFormTD className="col-span-2">
                        <EditFormInput type="text" name="depart" value={s.values?.depart || ''} onChange={fn.handleChange} errors={s.errors} className="w-full" />
                    </EditFormTD>
                    <EditFormTH className="col-span-1">역할</EditFormTH>
                    <EditFormTD className="col-span-2">
                        <EditFormCheckboxList
                            input_name="roles"
                            values={s.values?.roles}
                            filter_list={filter?.roles}
                            cols={2}
                            errors={s.errors}
                            handleChange={fn.handleCheckboxGroupForInteger}
                        />
                    </EditFormTD>
                </EditFormTable>
                <EditFormSubmit button_name={`${s.values?.uid > 0 ? '수정' : '등록'}하기`} submitting={s.submitting}></EditFormSubmit>
            </EditForm>
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
        const { data } = await api.post(`/be/admin/setup/admin/read`, request);
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

export default SetupManagerEdit;
