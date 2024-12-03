import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import { cls, checkNumeric, dateformatYYYYMMDD } from '@/libs/utils';
import useForm from '@/components/form/useForm';
import Datepicker from 'react-tailwindcss-datepicker';

import {
    EditForm,
    EditFormTable,
    EditFormTH,
    EditFormTD,
    EditFormRadioList,
    EditFormSubmit,
    EditFormInput,
    EditFormDate,
    EditFormTextarea,
    EditFormCard,
    EditFormCardHead,
    EditFormCardBody,
} from '@/components/UIcomponent/form/EditFormA';
import EditFormCallout from '@/components/UIcomponent/form/EditFormCallout';
import LayoutPopup from '@/components/LayoutPopup';
import EditFormToggle from '@/components/UIcomponent/form/EditFormToggle';
import ListTable from '@/components/UIcomponent/table/ListTable';
import ListTableHead from '@/components/UIcomponent/table/ListTableHead';
import ListTableBody from '@/components/UIcomponent/table/ListTableBody';
import Status from '@/pages/point/status';

const SingleEdit: NextPage = (props: any) => {
    const router = useRouter();
    const crumbs = ['포인트 지급관리', '식권 포인트 ' + (checkNumeric(router.query.save_type) > 2 ? '회수' : '지급')];
    const callout = [];
    const title_sub = '';

    const [posts, setPosts] = useState<any>({});
    const [filter, setFilter] = useState<any>({});

    useEffect(() => {
        if (props) {
            if (props.response.code == 200) {
                setPosts(props.response);
                setFilter(props.response.filter);
                s.setValues(props.response.values);

                s.setValues(prevState => {
                    return { ...prevState, save_type: props.request.save_type };
                });
            } else {
                alert(props.response.msg);
                window.close();
            }
        }
    }, []);

    const { s, fn, attrs } = useForm({
        initialValues: {},
        onSubmit: async () => {
            await editing();
        },
    });

    const deleting = () => editing();

    const editing = async () => {
        try {
            const params = { ...s.values };

            const { data } = await api.post(`/be/manager/point/assign/sikwon/single/edit`, params);
            s.setSubmitting(false);
            if (data.code == 200) {
                alert(data.msg);
                window.opener.assign_callback(data);
                window.close();
            } else {
                const copy_list = { ...posts };
                alert(data.msg);
                if (data.list !== 'undefined') {
                    copy_list.lack_list = data.list;
                    setPosts(copy_list);
                }
            }
        } catch (e: any) {}
    };

    const handleChangeToggle = (e: React.ChangeEvent<HTMLInputElement>) => {
        const params = {
            target: e.target.name,
            checked: e.target.checked,
        };

        const copy = { ...s.values };
        if (params.checked == true) {
            copy[params.target] = 'true';
        } else {
            copy[params.target] = '';
        }
        s.setValues(copy);
    };

    let save_type_txt = checkNumeric(router.query.save_type) > 2 ? '회수' : '지급';

    const upToPoint = point => {
        var copy = { ...s.values };
        copy.saved_point = checkNumeric(copy.saved_point) + checkNumeric(point);
        s.setValues(copy);
    };

    const removeList = (uid: number) => {
        const copy = { ...s.values };
        let temp: any = [];
        for (var i = 0; i < copy.user_uids.length; i++) {
            if (checkNumeric(copy.user_uids[i]) != uid) {
                temp.push(copy.user_uids[i]);
            }
        }
        copy.user_uids = temp;
        s.setValues(copy);

        const copy_posts = { ...posts };
        let temp_posts: any = [];
        for (var i = 0; i < copy_posts.list.length; i++) {
            if (checkNumeric(copy_posts.list[i].uid) != uid) {
                temp_posts.push(copy_posts.list[i]);
            }
        }
        copy_posts.list = temp_posts;
        setPosts(copy_posts);
    };
    return (
        <LayoutPopup title={crumbs[crumbs.length - 1]} className="px-6 bg-slate-50">
            <EditFormCallout title={crumbs[crumbs.length - 1]} title_sub={title_sub} callout={callout} />

            <Status point_type={'sikwon'} />
            <EditForm onSubmit={fn.handleSubmit}>
                <EditFormCard>
                    <EditFormCardHead className={cls(checkNumeric(router.query.save_type) > 2 ? 'bg-red-400' : 'bg-blue-500')}>
                        <div className="text-lg text-white">포인트 {save_type_txt}</div>
                    </EditFormCardHead>
                    <EditFormCardBody>
                        <EditFormTable className="grid-cols-6">
                            <EditFormTH className="col-span-1">{save_type_txt}사유</EditFormTH>
                            <EditFormTD className="col-span-5">
                                <EditFormInput
                                    type="text"
                                    name="reason"
                                    value={s.values?.reason || ''}
                                    is_mand={true}
                                    onChange={fn.handleChange}
                                    placeholder={`${save_type_txt}사유를 입력해 주세요`}
                                    errors={s.errors}
                                    className=""
                                />
                            </EditFormTD>
                            {checkNumeric(router.query.save_type) < 3 && (
                                <>
                                    <EditFormTH className="col-span-1">포인트 소멸일</EditFormTH>
                                    <EditFormTD className="col-span-5">
                                        <EditFormDate
                                            input_name="expiration_date"
                                            values={s.values?.expiration_date}
                                            is_mand={s.values?.is_exp_date}
                                            is_disabled={s.values?.is_exp_date}
                                            errors={s.errors}
                                            min_date={dateformatYYYYMMDD('YYYY-MM-DD')}
                                            handleChange={fn.handleChangeDate}
                                        />
                                        <div className="ms-2">
                                            <EditFormToggle name={'is_exp_date'} onChange={handleChangeToggle}>
                                                소멸일 없음
                                            </EditFormToggle>
                                        </div>
                                    </EditFormTD>
                                </>
                            )}

                            <EditFormTH className="col-span-1">{save_type_txt} 포인트</EditFormTH>
                            <EditFormTD className="col-span-5">
                                <EditFormInput
                                    type="text"
                                    name="saved_point"
                                    value={s.values?.saved_point || ''}
                                    is_price={true}
                                    onChange={fn.handleChange}
                                    placeholder={'숫자만 입력해 주세요'}
                                    errors={s.errors}
                                    className=""
                                    values={s.values}
                                    set_values={s.setValues}
                                />
                                <div className="ms-2">
                                    <button
                                        type="button"
                                        onClick={() => {
                                            upToPoint(10000);
                                        }}
                                        className="border rounded-md me-2 py-1 px-2"
                                    >
                                        +10,000
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => {
                                            upToPoint(50000);
                                        }}
                                        className="border rounded-md me-2 py-1 px-2"
                                    >
                                        +50,000
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => {
                                            upToPoint(100000);
                                        }}
                                        className="border rounded-md me-2 py-1 px-2"
                                    >
                                        +100,000
                                    </button>
                                </div>
                            </EditFormTD>
                            <EditFormTH className="col-span-1">관리자 메모</EditFormTH>
                            <EditFormTD className="col-span-5">
                                <EditFormTextarea
                                    name="admin_memo"
                                    value={s.values?.admin_memo || ''}
                                    rows={2}
                                    placeholder="관리 특이사항 작성이 가능하며, 작성 내용은 임직원에게 노출되지 않습니다."
                                    errors={s.errors}
                                    values={s.values}
                                    set_values={s.setValues}
                                    max_length={100}
                                />
                            </EditFormTD>
                        </EditFormTable>
                    </EditFormCardBody>
                    <EditFormSubmit
                        button_name={`${posts.list?.length}명 포인트 ${checkNumeric(router.query.save_type) > 2 ? '회수' : '지급'}하기`}
                        submitting={s.submitting}
                    ></EditFormSubmit>
                </EditFormCard>

                <EditFormCard>
                    <EditFormCardHead>
                        <div className="text-lg">
                            <span className="text-xl font-bold me-3">선택된 회원정보 {posts.list?.length}명</span>
                        </div>
                    </EditFormCardHead>
                    <EditFormCardBody>
                        <ListTable>
                            <ListTableHead>
                                <th>제거</th>
                                <th>이름</th>
                                <th>아이디</th>
                                <th>부서</th>
                                <th>직급/직책</th>
                                <th>미사용 포인트</th>
                                <th>포인트 사용상태</th>
                                <th>재직여부</th>
                                <th>검증</th>
                            </ListTableHead>

                            <ListTableBody>
                                {posts.list?.map((v: any, i: number) => (
                                    <tr key={`list-table-${i}`}>
                                        <td className="text-center" onClick={() => removeList(v.uid)}>
                                            <button type="button" className="text-red-500 underline">
                                                제거
                                            </button>
                                        </td>
                                        <td className="text-center">{v.user_name}</td>
                                        <td className="text-center">{v.login_id}</td>
                                        <td className="text-center">{v.depart}</td>
                                        <td className="text-center">
                                            {v.position}
                                            {v.position && v.position2 && '/'}
                                            {v.position2}
                                        </td>
                                        <td className="num2Cur">{checkNumeric(v.spare_point)}원</td>
                                        <td className="text-center">{v.is_point == 'T' ? '가능' : <span className="text-red-500">불가능</span>}</td>
                                        <td className="text-center">{v.serve}</td>
                                        <td className="text-center">{posts.lack_list?.includes(v.uid) ? <span className="text-red-500">포인트부족</span> : ''}</td>
                                    </tr>
                                ))}
                            </ListTableBody>
                        </ListTable>
                    </EditFormCardBody>
                </EditFormCard>
            </EditForm>
        </LayoutPopup>
    );
};

export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);

    let postData: any = {};
    if (ctx.req?.method == 'POST') {
        postData = await new Promise((resolve, reject) => {
            const body: any = [];
            ctx.req?.on('data', (chunk: any) => {
                body.push(chunk);
            });
            ctx.req?.on('end', () => {
                const asString = body.toString();
                const data = JSON.parse('{"' + decodeURI(asString).replace(/"/g, '\\"').replace(/&/g, '","').replace(/=/g, '":"') + '"}');
                resolve(data);
            });
            ctx.req?.on('error', e => {
                resolve(e);
            });
        });

        setContext(ctx);
    } else {
        setContext(ctx);
    }

    var request: any = {
        save_type: ctx.query.save_type,
        user_uids: decodeURIComponent(postData.user_uids),
    };
    var response: any = {};
    try {
        const { data } = await api.post(`/be/manager/point/assign/sikwon/single/read`, request);
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

export default SingleEdit;
