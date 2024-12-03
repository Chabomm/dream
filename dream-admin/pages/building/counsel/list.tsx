import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import { cls } from '@/libs/utils';
import Layout from '@/components/Layout';
import useForm from '@/components/form/useForm';
import Datepicker from 'react-tailwindcss-datepicker';
import ListPagenation from '@/components/bbs/ListPagenation';
import ButtonSearch from '@/components/UIcomponent/ButtonSearch';

const BuildingCounselList: NextPage = (props: any) => {
    const router = useRouter();
    const [filter, setFilter] = useState<any>({});
    const [params, setParams] = useState<any>({});
    const [posts, setPosts] = useState<any>([]);

    useEffect(() => {
        setFilter(props.response.filter);
        setParams(props.response.params);
        s.setValues(props.response.params.filters);
        getPagePost(props.response.params);
    }, []);

    const getPagePost = async p => {
        let newPosts = await getPostsData(p);
        setPosts(newPosts.list);
    };

    const getPostsData = async p => {
        try {
            const { data } = await api.post(`/be/admin/entry/counsel/list`, p);
            setParams(data.params);
            return data;
        } catch (e: any) {}
    };

    const { s, fn } = useForm({
        onSubmit: async () => {
            await searching();
        },
    });

    const searching = async () => {
        params.filters = s.values;
        let newPosts = await getPostsData(params);
        setPosts(newPosts.list);
    };

    const goEdit = (item: any) => {
        window.open(`/entry/counsel/edit?uid=${item.uid}`, '수기상담 수정', 'width=1120,height=800,location=no,status=no,scrollbars=yes');
    };

    const goCounsel = (item: any) => {
        window.open(`http://localhost:10020/dream/counsel?uid=${item.uid}`, '수기상담 등록', 'width=1120,height=800,location=no,status=no,scrollbars=yes');
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
                    return '상담문의';
                case '200':
                    return '상담중';
                case '300':
                    return '도입보류';
                case '501':
                    return '도입대기';
                case '502':
                    return '도입신청완료';
                default:
                    return value;
            }
        }
        return value;
    };

    return (
        <Layout user={props.user} title="indendkorea admin console" nav_id={88} crumbs={['구축관리', '상담신청']}>
            <form onSubmit={fn.handleSubmit} noValidate className="w-full border py-4 px-6 rounded shadow-md bg-white mt-5 relative">
                <div className="grid grid-cols-4 gap-6">
                    <div className="col-span-1">
                        <div className="col-span-1">
                            <label className="form-label">등록일</label>
                            <Datepicker
                                inputName="create_at"
                                value={s.values?.create_at}
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

                        <ButtonSearch submitting={s.submitting}>
                            <i className="fas fa-search mr-3"></i> 검색
                        </ButtonSearch>
                        <button type="button" className="btn-filter ml-3">
                            <i className="fas fa-stream"></i> 필터
                        </button>
                    </div>
                </div>

                <div className="checkbox_filter">
                    <div className="grid grid-cols-5 gap-6">
                        <div className="col-span-1">
                            <div className="title">진행상태</div>
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
                        수기상담 등록
                    </button>
                </div>
            </div>

            <div className="col-table">
                <div className="col-table-th grid grid-cols-9 sticky top-16 bg-gray-100">
                    <div className="">UID</div>
                    <div className="">진행상태</div>
                    <div className="col-span-2">기업명</div>
                    <div className="">임직원수</div>
                    <div className="">담당자명</div>
                    <div className="">작성일</div>
                    <div className="">수정일</div>
                    <div className="">상세보기</div>
                </div>

                {posts.map((v: any, i: number) => (
                    <div key={i} className="col-table-td grid grid-cols-9 bg-white transition duration-300 ease-in-out hover:bg-gray-100">
                        <div className="">{v.uid}</div>
                        <div className="">{getValueToText('state', v.state)}</div>
                        <div className="col-span-2">{v.company_name}</div>
                        <div className="">{v.staff_count}</div>
                        <div className="">{v.staff_name}</div>
                        <div className="">{v.create_at}</div>
                        <div className="">{v.update_at}</div>
                        <div className="">
                            <button
                                type="button"
                                className="text-blue-500 underline"
                                onClick={() => {
                                    goEdit(v);
                                }}
                            >
                                수정
                            </button>
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
    var request: any = {};
    var response: any = {};
    try {
        const { data } = await api.post(`/be/admin/entry/counsel/init`, request);
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

export default BuildingCounselList;
