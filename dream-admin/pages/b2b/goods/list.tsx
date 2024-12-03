import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import { checkNumeric, cls, getToken } from '@/libs/utils';
import Layout from '@/components/Layout';
import useForm from '@/components/form/useForm';
import ListPagenation from '@/components/bbs/ListPagenation';
import Datepicker from 'react-tailwindcss-datepicker';
import SellerSearch from '@/components/searchBox/sellerSearch';

import {
    EditForm,
    EditFormTable,
    EditFormTH,
    EditFormTD,
    EditFormKeyword,
    EditFormDateRange,
    EditFormSubmitSearch,
    EditFormRadioList,
    EditFormSelect,
    EditFormCheckboxList,
} from '@/components/UIcomponent/form/EditFormA';

import { ListTable, ListTableHead, ListTableBody, ListTableCaption, Callout } from '@/components/UIcomponent/table/ListTableA';
import ButtonSearch from '@/components/UIcomponent/ButtonSearch';

const B2BGoodsList: NextPage = (props: any) => {
    const nav_id = 113;
    const crumbs = ['기업혜택', 'B2B상품리스트'];
    const title_sub = 'B2B 상품 리스트를 확인/수정할 수 있습니다.';
    const callout = [];

    const router = useRouter();
    const [filter, setFilter] = useState<any>({});
    const [params, setParams] = useState<any>({});
    const [posts, setPosts] = useState<any>([]);

    useEffect(() => {
        if (sessionStorage.getItem(router.asPath) || '{}' !== '{}') {
            setParams(JSON.parse(sessionStorage.getItem(router.asPath) || '{}').params);
            setPosts(JSON.parse(sessionStorage.getItem(router.asPath) || '{}').data);
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
            const { data } = await api.post(`/be/admin/b2b/goods/list`, p);
            setParams(data.params);
            return data;
        } catch (e: any) {}
    };

    const { s, fn } = useForm({
        initialValues: {},
        onSubmit: async () => {
            await searching();
        },
    });

    const searching = async () => {
        params.filters = s.values;
        let newPosts = await getPostsData(params);
        setPosts(newPosts.list);
    };

    const openB2BGoodsEdit = (uid: number) => {
        router.replace(`/b2b/goods/reg?guid=${uid}`);
    };

    // [ S ] 업체명검색
    const [sellerSearchOpen, setSellerSearchOpen] = useState(false);
    const sellerSubmit = () => {
        if (s.values?.seller == '') {
            alert('검색어를 입력해주세요');
            return;
        }
        setSellerSearchOpen(true);
    };

    const getSellerUid = (uid: number, seller_id: string, seller_name: string, indend_md: string) => {
        const copy = { ...s.values };
        copy.seller_uid = uid;
        copy.seller_id = seller_id;
        copy.seller_name = seller_name;
        copy.indend_md = indend_md;
        s.setValues(copy);
    };
    // [ E ] 업체명검색

    // [ S ] 서비스명 클릭 시 오픈
    const openServiceItem = async (guid: number) => {
        let b2b_center_domain = `http://localhost:13000`;
        if (`${process.env.NODE_ENV}` == 'production') {
            b2b_center_domain = `https://`;
        }

        var newForm = document.createElement('form');
        newForm.setAttribute('method', 'POST');

        var newInput = document.createElement('input');
        newInput.setAttribute('type', 'hidden');
        newInput.setAttribute('name', 'token');
        newInput.setAttribute('value', getToken(undefined));
        newForm.appendChild(newInput);

        var newInput = document.createElement('input');
        newInput.setAttribute('type', 'hidden');
        newInput.setAttribute('name', 'guid');
        newInput.setAttribute('value', guid + '');
        newForm.appendChild(newInput);

        var newInput = document.createElement('input');
        newInput.setAttribute('type', 'hidden');
        newInput.setAttribute('name', 'company_name');
        newInput.setAttribute('value', '인디앤드코리아');
        newForm.appendChild(newInput);

        var newInput = document.createElement('input');
        newInput.setAttribute('type', 'hidden');
        newInput.setAttribute('name', 'depart');
        newInput.setAttribute('value', '');
        newForm.appendChild(newInput);

        var newInput = document.createElement('input');
        newInput.setAttribute('type', 'hidden');
        newInput.setAttribute('name', 'position1');
        newInput.setAttribute('value', '');
        newForm.appendChild(newInput);

        var newInput = document.createElement('input');
        newInput.setAttribute('type', 'hidden');
        newInput.setAttribute('name', 'mobile');
        newInput.setAttribute('value', '');
        newForm.appendChild(newInput);

        var newInput = document.createElement('input');
        newInput.setAttribute('type', 'hidden');
        newInput.setAttribute('name', 'email');
        newInput.setAttribute('value', '');
        newForm.appendChild(newInput);

        document.body.appendChild(newForm);

        var objPopup = window.open('', 'b2b_goods_view', 'width=1120,height=800, scrollbars=no, toolbar=no, status=no, resizable=no'); //창띄우기 명령에서 그 경로는 빈칸으로 한다.
        newForm.target = 'b2b_goods_view'; // 타겟 : 위의 창띄우기의 창이름과 같아야 한다.
        newForm.action = b2b_center_domain + `/inbound/goods?guid=${guid}`; // 액션경로
        if (objPopup == null) alert('차단된 팝업창을 허용해 주세요'); // 팝업이 뜨는지 확인
        else {
            newForm.submit();
            objPopup.focus(); //새로 띄워준 창에 포커스를 맞춰준다.
        }
    };
    // [ E ] 서비스명 클릭 시 오픈

    return (
        <>
            <Layout nav_id={nav_id} crumbs={crumbs} title={crumbs[crumbs.length - 1]} user={props.user}>
                <Callout title={crumbs[crumbs.length - 1]} title_sub={title_sub} callout={callout} />
                <EditForm onSubmit={fn.handleSubmit}>
                    <EditFormTable className="grid-cols-6">
                        <EditFormTH className="col-span-1">최근등록일</EditFormTH>
                        <EditFormTD className="col-span-2">
                            <EditFormDateRange input_name="create_at" values={s.values?.create_at} handleChange={fn.handleChangeDateRange} errors={s.errors} />
                        </EditFormTD>
                        <EditFormTH className="col-span-1">카테고리</EditFormTH>
                        <EditFormTD className="col-span-2">
                            <EditFormSelect
                                className={'!w-56'}
                                input_name="category"
                                value={s.values?.category}
                                filter_list={filter?.category}
                                onChange={fn.handleChange}
                            ></EditFormSelect>
                        </EditFormTD>
                        <EditFormTH className="col-span-1">처리상태</EditFormTH>
                        <EditFormTD className="col-span-5">
                            <EditFormRadioList
                                input_name="is_display"
                                values={s.values?.is_display}
                                filter_list={filter.is_display}
                                handleChange={fn.handleChange}
                                errors={s.errors}
                            />
                        </EditFormTD>
                        <EditFormTH className="col-span-1">업체명</EditFormTH>
                        <EditFormTD className="col-span-5">
                            <div className="flex items-center">
                                <input
                                    type="text"
                                    name="seller"
                                    value={s.values?.seller || ''}
                                    placeholder="업체명, 업체아이디, 담당자명 검색"
                                    onChange={fn.handleChange}
                                    className="form-control mr-3"
                                    style={{ width: '300px' }}
                                />
                                <button className="btn-filter col-span-2" type="button" onClick={() => sellerSubmit()}>
                                    업체 검색
                                </button>
                                <div className="ms-3">
                                    <input
                                        type="text"
                                        name="seller_id"
                                        value={s.values?.seller_id || ''}
                                        placeholder=""
                                        className="form-control mr-3 !text-red-500"
                                        style={{ width: 'auto' }}
                                        disabled
                                    />
                                    <input
                                        type="text"
                                        name="seller_name"
                                        value={s.values?.seller_name || ''}
                                        placeholder=""
                                        onChange={fn.handleChange}
                                        className="form-control mr-3 !text-red-500"
                                        style={{ width: 'auto' }}
                                        disabled
                                    />
                                </div>
                            </div>
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
                        <th>순서</th>
                        <th>공급업체명</th>
                        <th>카테고리</th>
                        <th>상품구분</th>
                        <th>상품명</th>
                        <th>최초등록일</th>
                        <th>마지막수정일</th>
                        <th>상태</th>
                        <th>수정</th>
                    </ListTableHead>
                    <ListTableBody>
                        {posts?.map((v: any, i: number) => (
                            <tr key={`list-table-${i}`} className="">
                                <td className="">{v.uid}</td>
                                <td className="">{v.sort}</td>
                                <td className="">{v.seller_name}</td>
                                <td className="">{v.category}</td>
                                <td className="">{v.service_type == 'C' ? '고객사혜택' : '드림클럽'}</td>
                                <td className="text-blue-500 underline cursor-pointer" onClick={() => openServiceItem(v.uid)}>
                                    {v.title}
                                </td>
                                <td className="">{v.create_at}</td>
                                <td className="">{v.update_at}</td>
                                <td className="">{v.is_display == 'T' ? '진열' : '미진열'}</td>
                                <td className="">
                                    <button type="button" className="btn-save" onClick={() => openB2BGoodsEdit(v.uid)}>
                                        수정
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </ListTableBody>
                </ListTable>
                <ListPagenation props={params} getPagePost={getPagePost} />
            </Layout>
            {sellerSearchOpen && <SellerSearch setSellerSearchOpen={setSellerSearchOpen} seller={s.values?.seller} sandSellerUid={getSellerUid} />}
        </>
    );
};
export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {};
    var response: any = {};
    try {
        const { data } = await api.post(`/be/admin/b2b/goods/init`, request);
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

export default B2BGoodsList;
