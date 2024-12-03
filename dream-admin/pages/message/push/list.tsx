import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import { cls } from '@/libs/utils';
import Layout from '@/components/Layout';
import useForm from '@/components/form/useForm';
import Datepicker from 'react-tailwindcss-datepicker';
import ListPagenation from '@/components/bbs/ListPagenation';

const UmsPushList: NextPage = (props: any) => {
    const router = useRouter();
    const [params, setParams] = useState(props.request);
    const [posts, setPosts] = useState(props.response.list);

    useEffect(() => {
        if (sessionStorage.getItem(router.asPath) || '{}' !== '{}') {
            setParams(JSON.parse(sessionStorage.getItem(router.asPath) || '{}').params);
            setPosts(JSON.parse(sessionStorage.getItem(router.asPath) || '{}').data);
            return () => {
                const scroll = parseInt(JSON.parse(sessionStorage.getItem(router.asPath) || '{}').scroll_y, 10);
                window.scrollTo(0, scroll);
                sessionStorage.removeItem(router.asPath);
            };
        }
    }, [posts, router.asPath]);

    const getPagePost = async p => {
        let newPosts = await getPostsData(p);
        setPosts(newPosts.list);
        setParams(newPosts.params);
    };

    const getPostsData = async p => {
        try {
            const { data } = await api.post(`/push/booking/list`, p);
            return data;
        } catch (e: any) {}
    };

    const { s, fn } = useForm({
        initialValues: {
            skeyword: '',
            skeyword_type: '',
            rec_type: [],
            state: [],
            create_at: {
                startDate: null,
                endDate: null,
            },
        },
        onSubmit: async () => {
            await searching();
        },
    });

    const [filter, setFilter] = useState<any>({});

    useEffect(() => {
        getFilterContidion();
    }, []);

    const getFilterContidion = async () => {
        try {
            const { data } = await api.post(`/ums/push/booking/filter`);
            setFilter(data);

            const copy = { ...s.values };
            copy.rec_type = data.rec_type.map(row => row.checked && row.key);
            copy.state = data.state.map(row => row.checked && row.key);
            s.setValues(copy);
        } catch (e: any) {}
    };

    const searching = async () => {
        params.filters = s.values;
        let newPosts = await getPostsData(params);
        setPosts(newPosts.list);
    };

    const getValueToText = (name, value) => {
        if (name == 'rec_type') {
            switch (value) {
                case 'A':
                    return '앱사용자전체';
                case 'P':
                    return '고객사';
                case 'S':
                    return '개별';
                default:
                    return value;
            }
        } else if (name == 'state') {
            switch (value) {
                case '100':
                    return '대기';
                case '200':
                    return '발송완료';
                case '300':
                    return '발송취소';
                default:
                    return value;
            }
        }
        return value;
    };

    const goEdit = (item: any) => {
        window.open(`/message/push/edit?uid=${item.uid}`, 'PUSH 발송예약 상세', 'width=1120,height=800,location=no,status=no,scrollbars=yes');
    };

    const goSended = (item: any) => {
        window.open(`/message/push/sended?uid=${item.uid}`, 'PUSH 발송예약 상세', 'width=1120,height=800,location=no,status=no,scrollbars=yes');
    };

    return (
        <Layout user={props.user} title="indendkorea admin console" nav_id={85} crumbs={['UMS관리', 'PUSH 발송예약']}>
            <form onSubmit={fn.handleSubmit} noValidate className="w-full border py-4 px-6 rounded shadow-md bg-white mt-5 relative">
                <div className="grid grid-cols-4 gap-6">
                    <div className="col-span-1">
                        <div className="col-span-1">
                            <label className="form-label">등록일</label>
                            <Datepicker
                                inputName="create_at"
                                value={s.values.create_at}
                                i18n={'ko'}
                                onChange={fn.handleChangeDateRange}
                                containerClassName="relative w-full text-gray-700 border border-gray-300 rounded"
                            />
                        </div>
                    </div>
                    <div className="col-span-1">
                        <div className="col-span-1">
                            <label className="form-label">발송일</label>
                            <Datepicker
                                inputName="send_at"
                                value={s.values.send_at}
                                i18n={'ko'}
                                onChange={fn.handleChangeDateRange}
                                containerClassName="relative w-full text-gray-700 border border-gray-300 rounded"
                            />
                        </div>
                    </div>
                    <div className="col-span-4">
                        <select
                            name="skeyword_type"
                            value={s.values?.skeyword_type || ''}
                            onChange={fn.handleChange}
                            className={cls(s.errors['skeyword_type'] ? 'border-danger' : '', 'form-select mr-3')}
                            style={{ width: 'auto' }}
                        >
                            <option value="">전체</option>
                            {filter.skeyword_type?.map((v: any, i: number) => (
                                <option key={i} value={v.key}>
                                    {v.text}
                                </option>
                            ))}
                        </select>
                        <input
                            type="text"
                            name="skeyword"
                            value={s.values?.skeyword || ''}
                            placeholder=""
                            onChange={fn.handleChange}
                            className={cls(s.errors['skeyword'] ? 'border-danger' : '', 'form-control mr-3')}
                            style={{ width: 'auto' }}
                        />
                        <button className="btn-search col-span-2" disabled={s.submitting}>
                            <i className="fas fa-search mr-3" style={{ color: '#ffffff' }}></i> 검색
                        </button>
                        <button type="button" className="btn-filter ml-3">
                            <i className="fas fa-stream"></i> 필터
                        </button>
                    </div>
                </div>

                <div className="checkbox_filter">
                    <div className="grid grid-cols-5 gap-6">
                        <div className="col-span-1">
                            <div className="title">수신대상</div>
                            <div className="checkboxs_wrap h-24 overflow-y-auto">
                                {filter.rec_type?.map((v: any, i: number) => (
                                    <label key={i}>
                                        <input
                                            id={`rec_type-${i}`}
                                            onChange={fn.handleCheckboxGroup}
                                            type="checkbox"
                                            value={v.key}
                                            checked={s.values.rec_type.includes(v.key)}
                                            name="rec_type"
                                        />
                                        <span className="font-bold">{v.text}</span>
                                    </label>
                                ))}
                            </div>
                        </div>
                        <div className="col-span-1">
                            <div className="title">발송상태</div>
                            <div className="checkboxs_wrap h-24 overflow-y-auto">
                                {filter.state?.map((v: any, i: number) => (
                                    <label key={i}>
                                        <input
                                            id={`state-${i}`}
                                            onChange={fn.handleCheckboxGroup}
                                            type="checkbox"
                                            value={v.key}
                                            checked={s.values.state.includes(v.key)}
                                            name="state"
                                        />
                                        <span className="font-bold">{v.text}</span>
                                    </label>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </form>

            <div className="border-t py-3 grid grid-cols-2 h-16 items-center">
                <div className="text-left">
                    총 {params.page_total} 개 중 {params.page_size}개
                </div>
                <div className="text-right">
                    <button
                        type="button"
                        className="btn-funcs"
                        onClick={() => {
                            goEdit({ uid: 0 });
                        }}
                    >
                        PUSH 발송예약 등록
                    </button>
                </div>
            </div>

            <div className="col-table">
                <div className="col-table-th grid grid-cols-11 sticky top-16 bg-gray-100">
                    <div className="">uid</div>
                    <div className="">발송예약일</div>
                    <div className="">발송일</div>
                    <div className="col-span-3">푸시 내용</div>
                    <div className="">수신대상</div>
                    <div className="">발송상태</div>
                    <div className="">발송카운트</div>
                    <div className="">발송내역</div>
                </div>

                {posts.map((v: any, i: number) => (
                    <div key={i} className="col-table-td grid grid-cols-11 bg-white transition duration-300 ease-in-out hover:bg-gray-100">
                        <div className="">{v.uid}</div>
                        <div className="">{v.booking_at}</div>
                        <div className="">
                            {v.start_send_at} ~ {v.end_send_at}
                        </div>

                        <div className="col-span-3 flex-col">
                            <div className="font-bold truncate w-full">
                                {v.push_title}
                                {v.push_img != '' && <i className="far fa-image ms-1"></i>}
                            </div>
                            <div className="text-start h-24 overflow-hidden whitespace-pre">{v.push_msg}</div>
                        </div>
                        <div className="">{getValueToText('rec_type', v.rec_type)}</div>
                        <div className="">{getValueToText('state', v.state)}</div>
                        <div className="">
                            {v.success_count}/{v.send_count}
                        </div>
                        <div className="">
                            <button
                                type="button"
                                className="text-blue-500 underline"
                                onClick={() => {
                                    goSended(v);
                                }}
                            >
                                발송(예정)내역보기
                            </button>
                        </div>
                        <div className="">
                            {v.state == '100' && (
                                <button
                                    type="button"
                                    className="text-blue-500 underline"
                                    onClick={() => {
                                        goEdit(v);
                                    }}
                                >
                                    예약수정
                                </button>
                            )}
                        </div>
                    </div>
                ))}
            </div>
            <ListPagenation props={params} getPagePost={getPagePost} />
        </Layout>
    );
};
export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {
        page: 1,
        page_size: 0,
        page_view_size: 0,
        page_total: 0,
        page_last: 0,
    };
    var response: any = {};
    try {
        const { data } = await api.post(`/be/admin/ums/push/booking/list`, request);
        response = data;
        request = response.params;
    } catch (e: any) {
        if (typeof e.redirect !== 'undefined') {
            return { redirect: e.redirect };
        }
    }
    return {
        props: { request, response },
    };
};

export default UmsPushList;
