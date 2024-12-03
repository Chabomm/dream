import React, { useState, useEffect } from 'react';
import { api } from '@/libs/axios';
import useForm from '@/components/form/useForm';

import { EditForm, EditFormTable, EditFormTH, EditFormTD, EditFormKeyword, EditFormDateRange, EditFormSubmitSearch } from '@/components/UIcomponent/form/EditFormA';
import { ListTable, ListTableHead, ListTableBody, ListTableCaption, Callout } from '@/components/UIcomponent/table/ListTableA';
import { checkNumeric } from '@/libs/utils';
import ListPagenation from '@/components/bbs/ListPagenation';

function BbsBoardList(props: any) {
    const [filter, setFilter] = useState<any>({});
    const [params, setParams] = useState<any>({});
    const [posts, setPosts] = useState<any>([]);

    useEffect(() => {
        if (props) {
            setFilter(props.response.filter);
            setParams(props.response.params);
            s.setValues(props.response.params.filters);
            getPagePost(props.response.params);
        }
    }, [props]);

    const getPagePost = async p => {
        let newPosts = await getPostsData(p);
        setPosts(newPosts.list);
    };

    const getPostsData = async p => {
        try {
            const { data } = await api.post(`/be/manager/bbs/list/${props.response.board.uid}`, p);
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

    const viewPosts = (item: any) => {
        window.open(`/bbs/board/view?uid=${item.uid}`, '게시물 상세', 'width=1120,height=800,location=no,status=no,scrollbars=yes');
    };

    const openEdit = (uid: number) => {
        window.open(`/bbs/board/edit?uid=${uid}&board_uid=${props.response.board.uid}`, '게시물 등록/수정', 'width=1120,height=800,location=no,status=no,scrollbars=yes');
    };

    return (
        <>
            <EditForm onSubmit={fn.handleSubmit}>
                <EditFormTable className="grid-cols-6">
                    <EditFormTH className="col-span-1">등록일 조회</EditFormTH>
                    <EditFormTD className="col-span-2">
                        <EditFormDateRange input_name="create_at" values={s.values?.create_at} errors={s.errors} handleChange={fn.handleChangeDateRange} />
                    </EditFormTD>
                    <EditFormTD className="col-span-3"> </EditFormTD>
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
                <div className="">
                    <button
                        onClick={() => {
                            openEdit(0);
                        }}
                        className="text-sm text-blue-600"
                    >
                        <i className="far fa-plus-square me-2"></i>게시글 등록
                    </button>
                </div>
            </ListTableCaption>

            <ListTable>
                <ListTableHead>
                    <th>고유번호</th>
                    <th style={{ width: '900px' }}>게시물 제목</th>
                    <th>작성자</th>
                    <th>작성일</th>
                </ListTableHead>
                <ListTableBody>
                    {posts?.map((v: any, i: number) => (
                        <tr key={`list-table-${i}`} className="">
                            <td className="text-center">{v.uid}</td>
                            <td className="">
                                <div
                                    onClick={() => {
                                        viewPosts(v);
                                    }}
                                    className="!justify-start text-left truncate col-span-3"
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
                            </td>
                            <td className="text-center">{v.create_name}</td>
                            <td className="text-center">
                                <div dangerouslySetInnerHTML={{ __html: v.create_at }}></div>
                            </td>
                        </tr>
                    ))}
                </ListTableBody>
            </ListTable>

            <ListPagenation props={params} getPagePost={getPagePost} />
        </>
    );
}

export default BbsBoardList;
