import React, { useState, useEffect } from 'react';
import { api } from '@/libs/axios';
import { useRouter } from 'next/router';
import ListPagenation from '@/components/bbs/ListPagenation';
import { checkNumeric, cls } from '@/libs/utils';
import useForm from '@/components/form/useForm';
import Datepicker from 'react-tailwindcss-datepicker';

import {
    EditForm,
    EditFormTable,
    EditFormTH,
    EditFormTD,
    EditFormKeyword,
    EditFormDateRange,
    EditFormSubmitSearch,
    EditFormCheckboxList,
    EditFormRadioList,
} from '@/components/UIcomponent/form/EditFormA';
import { ListTable, ListTableHead, ListTableBody, ListTableCaption, Callout } from '@/components/UIcomponent/table/ListTableA';

function B2bOrderTmplList(props: any) {
    const router = useRouter();
    const [filter, setFilter] = useState<any>({});
    const [params, setParams] = useState<any>({});
    const [posts, setPosts] = useState<any>([]);

    useEffect(() => {
        if (sessionStorage.getItem(router.asPath) || '{}' !== '{}') {
            setFilter(JSON.parse(sessionStorage.getItem(router.asPath) || '{}').filter);
            setParams(JSON.parse(sessionStorage.getItem(router.asPath) || '{}').params);
            s.setValues(JSON.parse(sessionStorage.getItem(router.asPath) || '{}').params.filters);
            setPosts(JSON.parse(sessionStorage.getItem(router.asPath) || '{}').posts);
            const scroll = checkNumeric(JSON.parse(sessionStorage.getItem(router.asPath) || '{}').scroll_y);
            let intervalRef = setInterval(() => {
                const page_contents: any = document.querySelector('#page_contents');
                page_contents.scrollTo(0, scroll);
                sessionStorage.removeItem(router.asPath);
                clearInterval(intervalRef);
            }, 200);
        } else {
            setFilter(props.response.filter);
            setParams(props.response.params);
            s.setValues(props.response.params.filters);
            getPagePost(props.response.params);
        }
    }, [router.asPath]);

    const getPagePost = async p => {
        let newPosts = await getPostsData(p);
        setPosts(newPosts.list);
    };

    const getPostsData = async p => {
        try {
            const { data } = await api.post(`/be/manager/b2b/order/list`, p);
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

    const openServiceRead = (uid: number) => {
        const page_contents: any = document.querySelector('#page_contents');
        sessionStorage.setItem(
            router.asPath,
            JSON.stringify({
                filter: filter,
                params: params,
                posts: posts,
                scroll_x: `${page_contents.scrollLeft || 0}`,
                scroll_y: `${page_contents.scrollTop || 0}`,
            })
        );
        router.push(`/b2b/order/popup/detail?uid=${uid}`);
    };

    return (
        <>
            <EditForm onSubmit={fn.handleSubmit}>
                <EditFormTable className="grid-cols-6">
                    <EditFormTH className="col-span-1">등록일</EditFormTH>
                    <EditFormTD className="col-span-5">
                        <EditFormDateRange input_name="create_at" values={s.values?.create_at} errors={s.errors} handleChange={fn.handleChangeDateRange} />
                    </EditFormTD>

                    <EditFormTH className="col-span-1">카테고리</EditFormTH>
                    <EditFormTD className="col-span-5">
                        <EditFormRadioList input_name="category" values={s.values?.category} filter_list={filter.category} errors={s.errors} handleChange={fn.handleChange} />
                    </EditFormTD>

                    <EditFormTH className="col-span-1">처리상태</EditFormTH>
                    <EditFormTD className="col-span-5">
                        <EditFormRadioList input_name="state" values={s.values?.state} filter_list={filter.state} errors={s.errors} handleChange={fn.handleChange} />
                    </EditFormTD>

                    <EditFormTH className="col-span-1">검색어</EditFormTH>
                    <EditFormTD className="col-span-5">
                        <EditFormKeyword
                            skeyword_values={s.values?.skeyword}
                            skeyword_type_values={s.values?.skeyword_type}
                            skeyword_type_filter={filter.skeyword_type}
                            handleChange={fn.handleChange}
                            errors={s.errors}
                        ></EditFormKeyword>
                    </EditFormTD>
                </EditFormTable>
                <EditFormSubmitSearch button_name="조회하기" submitting={s.submitting}></EditFormSubmitSearch>
            </EditForm>

            <ListTableCaption>
                <div className="">
                    검색 결과 : 총 {params?.page_total}개 중 {posts?.length}개
                </div>
                <div className=""></div>
            </ListTableCaption>

            <ListTable>
                <ListTableHead>
                    <th>번호</th>
                    <th>카테고리</th>
                    <th style={{ width: '500px' }}>서비스명</th>
                    <th>작성자</th>
                    <th>직급/직책</th>
                    <th>등록일</th>
                    <th>처리상태</th>
                    <th>상세보기</th>
                </ListTableHead>
                <ListTableBody>
                    {posts?.map((v: any, i: number) => (
                        <tr key={`list-table-${i}`} className="">
                            <td className="text-center">{v.uid}</td>
                            <td className="text-center">{v.category}</td>
                            <td className="">{v.title}</td>
                            <td className="text-center">{v.apply_name}</td>
                            <td className="text-center">{v.apply_position}</td>
                            <td className="text-center">{v.create_at}</td>
                            <td className="text-center">{v.state}</td>
                            <td className="text-center">
                                <button type="button" className="btn-filter" onClick={() => openServiceRead(v.uid)}>
                                    상세보기
                                </button>
                            </td>
                        </tr>
                    ))}
                </ListTableBody>
            </ListTable>
            <ListPagenation props={params} getPagePost={getPagePost} />
        </>
    );
}

export default B2bOrderTmplList;
