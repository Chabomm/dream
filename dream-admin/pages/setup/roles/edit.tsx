import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect, useRef } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import { cls, checkNumeric } from '@/libs/utils';
import useForm from '@/components/form/useForm';
import LayoutPopup from '@/components/LayoutPopup';

import { EditForm, EditFormTable, EditFormTH, EditFormTD, EditFormSubmit, EditFormInput, EditFormCheckboxList, EditFormLabel } from '@/components/UIcomponent/form/EditFormA';
import EditFormCallout from '@/components/UIcomponent/form/EditFormCallout';

const SetupRolesEdit: NextPage = (props: any) => {
    const crumbs = ['환경설정', '역할 ' + (props.response.values?.uid > 0 ? '수정' : '등록')];
    const callout = [];
    const title_sub = '관리자를 역할을 등록/수정할 수 있습니다';
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
            const { data } = await api.post(`/be/admin/setup/roles/edit`, s.values);
            if (data.code == 200) {
                if (s.values.mode == 'REG') {
                    alert(data.msg);
                    // router.replace(`/setup/roles/edit?uid=${data.uid}`);
                    window.opener.location.reload();
                } else {
                    alert(data.msg);
                }
            } else {
                alert(data.msg);
            }

            return;
        } catch (e: any) {}
    };

    return (
        <>
            <LayoutPopup title={crumbs[crumbs.length - 1]}>
                <EditFormCallout title={crumbs[crumbs.length - 1]} title_sub={title_sub} callout={callout} />
                <EditForm onSubmit={fn.handleSubmit}>
                    <EditFormTable className="grid-cols-6">
                        <EditFormTH className="col-span-1 mand">관리자 이름</EditFormTH>
                        <EditFormTD className="col-span-5">
                            <EditFormInput type="text" name="name" value={s.values?.name || ''} is_mand={true} onChange={fn.handleChange} errors={s.errors} className="w-full" />
                        </EditFormTD>
                        <EditFormTH className="col-span-1">메뉴 권한 설정</EditFormTH>
                        <EditFormTD className="col-span-5">
                            <div className="grid grid-cols-3 checkbox_filter">
                                {filter?.menus?.depth1?.map((v: any, i: number) => (
                                    <div key={'dpeth1-' + i} className="h-min w-full">
                                        <div className="font-bold mt-5 mb-2">{v.name}</div>
                                        {filter?.menus?.depth2
                                            ?.filter(p => p.parent == v.uid)
                                            .map((vv: any, ii: number) => (
                                                <div className="checkboxs_wrap" key={'dpeth2-' + ii} style={{ height: 'auto' }}>
                                                    <label>
                                                        <input
                                                            id={`menus-${ii}`}
                                                            checked={s.values?.menus.filter(p => p == vv.uid) == checkNumeric(vv.uid) ? true : false}
                                                            onChange={fn.handleCheckboxGroupForInteger}
                                                            type="checkbox"
                                                            value={vv.uid}
                                                            name="menus"
                                                        />
                                                        <span className="ml-3">
                                                            {vv.name} [{vv.uid}]
                                                        </span>
                                                    </label>
                                                </div>
                                            ))}
                                    </div>
                                ))}
                            </div>
                        </EditFormTD>
                    </EditFormTable>
                    <EditFormSubmit button_name={`${s.values?.uid > 0 ? '수정' : '등록'}하기`} submitting={s.submitting}></EditFormSubmit>
                </EditForm>
            </LayoutPopup>
        </>
    );
};
export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {
        uid: ctx.query.uid,
        partner_uid: ctx.query.partner_uid,
        site_id: ctx.query.site_id,
    };
    var response: any = {};
    try {
        const { data } = await api.post(`/be/admin/setup/roles/read`, request);
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

export default SetupRolesEdit;
