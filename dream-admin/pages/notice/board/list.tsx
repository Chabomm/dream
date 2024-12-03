import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import Datepicker from 'react-tailwindcss-datepicker';
import { cls } from '@/libs/utils';

import useForm from '@/components/form/useForm';
import ListPagenation from '@/components/bbs/ListPagenation';
import PartnerSearch from '@/components/searchBox/PartnerSearch';

function IntranetBoardPostList(props: any) {
    const [filter, setFilter] = useState<any>({});
    const [params, setParams] = useState<any>({});
    const [posts, setPosts] = useState<any>([]);
    const [board, setBoard] = useState<any>({});

    useEffect(() => {
        getNoticePosts({ uid: props.board_uid });
    }, []);

    const getNoticePosts = async p => {
        try {
            const { data } = await api.post(`/be/admin/posts/intranet`, p);
            setBoard(data.board);
            setFilter(data.filter);
            setParams(data.params);
            getPagePost(data.params);
        } catch (e: any) {}
    };

    const getPagePost = async p => {
        let newPosts = await getPostsData(p);
        setPosts(newPosts.list);
    };

    const getPostsData = async p => {
        try {
            const { data } = await api.post(`/be/admin/posts/list`, p);
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
        let board_uid = params.filters.board_uid;
        params.filters = s.values;
        params.filters.board_uid = board_uid;

        let newPosts = await getPostsData(params);
        setPosts(newPosts.list);
    };

    const goEdit = (item: any) => {
        window.open(`/board/posts/edit?uid=${item.uid}&board_uid=${board.uid}`, '게시물 등록/수정', 'width=1120,height=800,location=no,status=no,scrollbars=yes');
    };

    const viewPosts = (item: any) => {
        window.open(`/board/posts/view?uid=${item.uid}`, '게시물 상세', 'width=1120,height=800,location=no,status=no,scrollbars=yes');
    };

    // [ S ] 고객사검색
    const [partnerSearchOpen, setPartnerSearchOpen] = useState(false);
    const partnerSubmit = () => {
        if (s.values?.partner_name == '') {
            alert('검색어를 입력해주세요');
            return;
        }
        setPartnerSearchOpen(true);
    };

    const getPartnerUid = (uid: number, partner_id: string, company_name: string, mall_name: string) => {
        const copy = { ...s.values };
        copy.partner_uid = uid;
        copy.partner_id = partner_id;
        copy.company_name = company_name;
        copy.mall_name = mall_name;
        s.setValues(copy);
    };
    // [ E ] 고객사검색

    return (
        <>
            <form onSubmit={fn.handleSubmit} noValidate className="w-full border py-4 px-6 rounded shadow-md bg-white mt-5">
                <div className="grid grid-cols-4 gap-6">
                    <div className="col-span-1">
                        <label className="form-label">등록일 조회</label>
                        <Datepicker
                            containerClassName="relative w-full text-gray-700 border border-gray-300 rounded"
                            inputName="create_at"
                            value={s.values.create_at}
                            i18n={'ko'}
                            onChange={fn.handleChangeDateRange}
                            primaryColor={'blue'}
                        />
                    </div>
                    {board.site_id == 'manager' && (
                        <div className="col-span-4">
                            <label className="form-label">고객사</label>
                            <div className="flex">
                                <input
                                    type="text"
                                    name="partner_name"
                                    value={s.values?.partner_name || ''}
                                    placeholder="고객사 아이디, 고객사명 또는 복지몰명"
                                    onChange={fn.handleChange}
                                    className="form-control mr-3"
                                    style={{ width: '300px' }}
                                />
                                <button className="btn-filter col-span-2" type="button" onClick={() => partnerSubmit()}>
                                    고객사 검색
                                </button>
                                <div className="ms-3">
                                    <input
                                        type="text"
                                        name="partner_id"
                                        value={s.values?.partner_id || ''}
                                        placeholder=""
                                        className="form-control mr-3 !text-red-500"
                                        style={{ width: 'auto' }}
                                        disabled
                                    />
                                    <input
                                        type="text"
                                        name="mall_name"
                                        value={s.values?.mall_name || ''}
                                        placeholder=""
                                        onChange={fn.handleChange}
                                        className="form-control mr-3 !text-red-500"
                                        style={{ width: 'auto' }}
                                        disabled
                                    />
                                </div>
                            </div>
                        </div>
                    )}
                    <div className="col-span-3">
                        <label className="form-label">키워드 조회</label>
                        <div className="flex">
                            <select
                                name="skeyword_type"
                                value={s.values?.skeyword_type || ''}
                                onChange={fn.handleChange}
                                className={cls(s.errors['skeyword_type'] ? 'border-danger' : '', 'form-select mr-3')}
                                style={{ width: 'auto' }}
                            >
                                <option value="">전체</option>
                                {filter.skeyword_type?.map((v, i) => (
                                    <option key={i} value={v.key}>
                                        {v.value}
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
                        </div>
                    </div>
                </div>
            </form>

            <div className="border-t py-3 grid grid-cols-2 h-16 items-center">
                <div className="text-left">
                    총 {params.page_total} 개 중 {params.page_size}개
                </div>
                <div className="text-right">
                    {board?.poss_insert && props.board_uid == 3 && (
                        <button
                            type="button"
                            className="btn-funcs"
                            onClick={() => {
                                goEdit({ uid: 0 });
                            }}
                        >
                            <i className="fas fa-pen me-2"></i> 게시물 등록하기
                        </button>
                    )}
                </div>
            </div>

            <div className="col-table">
                <div className="col-table-th grid grid-cols-8 sticky top-16 bg-gray-100">
                    <div className="">번호</div>
                    {board.site_id == 'manager' && <div className="">고객사</div>}
                    <div className={cls(board.site_id == 'manager' ? 'col-span-3' : 'col-span-4')}>게시물 제목</div>
                    <div className="">작성자</div>
                    <div className="">작성일</div>
                    <div className="">상세보기</div>
                </div>

                {posts?.map((v: any, i: number) => (
                    <div key={i} className="col-table-td grid grid-cols-8 bg-white transition duration-300 ease-in-out hover:bg-gray-100">
                        <div className="">{v.uid}</div>

                        {board.site_id == 'manager' && <div className="">{v.company_name}</div>}

                        <div
                            onClick={() => {
                                viewPosts(v);
                            }}
                            className={cls('!justify-start text-left truncate', board.site_id == 'manager' ? 'col-span-3' : 'col-span-4')}
                        >
                            {v.thumb == '' || v.thumb == null ? '' : <i className="far fa-image mr-3 text-blue-400"></i>}
                            <span className="cursor-pointer">
                                <span className="">{v.title}</span>
                                {v.reply_count > 0 && (
                                    <span className="text-green-600 ms-3">
                                        <i className="far fa-comment-dots"></i> {v.reply_count}
                                    </span>
                                )}
                                {v.file_count > 0 && (
                                    <span className="text-blue-600 ms-3">
                                        <i className="fas fa-save"></i> {v.file_count}
                                    </span>
                                )}
                            </span>
                        </div>
                        <div className="">{v.create_name}</div>
                        <div className="">
                            <div dangerouslySetInnerHTML={{ __html: v.create_at }}></div>
                        </div>
                        <div className="">
                            {(v.create_user == props.user?.user_id || board?.poss_insert) && props.board_uid == 3 && (
                                <>
                                    <button
                                        type="button"
                                        className="text-blue-500 underline"
                                        onClick={() => {
                                            goEdit(v);
                                        }}
                                    >
                                        수정
                                    </button>
                                    <span className="mx-2">|</span>
                                </>
                            )}
                            <button
                                type="button"
                                className="text-blue-500 underline"
                                onClick={() => {
                                    viewPosts(v);
                                }}
                            >
                                게시물보기
                            </button>
                        </div>
                    </div>
                ))}
            </div>
            <ListPagenation props={params} getPagePost={getPagePost} />
            {partnerSearchOpen && <PartnerSearch setPartnerSearchOpen={setPartnerSearchOpen} partnerName={s.values?.partner_name} sandPartnerUid={getPartnerUid} />}
        </>
    );
}

export default IntranetBoardPostList;
