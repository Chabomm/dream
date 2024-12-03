import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import { checkNumeric } from '@/libs/utils';
import { ReactSortable } from 'react-sortablejs';
import LayoutPopup from '@/components/LayoutPopup';

const SetupChildEdit: NextPage = (props: any) => {
    const router = useRouter();
    const [sortDiff, setSortDiff] = useState<boolean>(false);
    const [sort, setSort] = useState<any>([]);
    const [posts, setPosts] = useState<any>(props.response);

    useEffect(() => {
        if (sort.length == 0) {
            posts?.map((v: any) => {
                setSort(current => [...current, v.uid]);
            });
        } else {
            var sort_diff = false;
            posts?.map((v: any, i: number) => {
                if (v.uid != sort[i]) {
                    sort_diff = true;
                }
            });
            if (sort_diff) {
                setSort([]);
                posts?.map((v: any) => {
                    setSort(current => [...current, v.uid]);
                });
                setSortDiff(sort_diff);
            }
        }
    }, [posts]);

    const openAdminMenuEdit = (uid: number, depth?: number, parent?: number) => {
        window.open(
            `/setup/menus/parent_edit?uid=${uid}&depth=${depth}&parent=${parent}`,
            '메뉴 정보',
            'width=1120,height=800,location=no,status=no,scrollbars=yes,left=200%,top=50%'
        );
    };

    const GoAdminMenuEdit = (uid: number, depth?: number, parent?: number) => {
        router.push(`/setup/menus/parent_edit?uid=${uid}&depth=${depth}&parent=${parent}`);
    };

    const sortableOptions = {
        animation: 150,
        handle: '.handle',
    };

    const sorting = async () => {
        try {
            const p = {
                mode: 'SORT',
                parent: router.query.uid,
                sort_array: sort,
            };

            const { data } = await api.post(`/be/admin/setup/menus/edit`, p);
            if (data.code == 200) {
                alert(data.msg);
                router.reload();
            } else {
                alert(data.msg);
            }
        } catch (e: any) {}
    };

    return (
        <LayoutPopup title={''}>
            <div className="w-full bg-slate-100 mx-auto py-10">
                <div className="px-9">
                    <div className="flex justify-between">
                        <div className="text-2xl font-semibold">소메뉴 {posts.uid > 0 ? '수정' : '등록'}</div>
                    </div>
                    <div className="border py-4 px-6 rounded shadow-md bg-white mt-5">
                        <div className="card_area">
                            {sortDiff && (
                                <div className="py-5">
                                    <button
                                        type="button"
                                        className="btn-funcs"
                                        onClick={() => {
                                            sorting();
                                        }}
                                    >
                                        소메뉴 순서 적용하기
                                    </button>
                                    <div className="text-red-600 font-bold ml-5">순서가 변경되었습니다. 적용하기 버튼을 클릭하여 저장해 주세요</div>
                                </div>
                            )}
                            <div className="text-right my-5">
                                <button
                                    type="button"
                                    className="btn-funcs"
                                    onClick={() => {
                                        GoAdminMenuEdit(0, 2, checkNumeric(router.query.uid));
                                    }}
                                >
                                    <i className="fas fa-pen me-2"></i> 등록
                                </button>
                            </div>
                            <div className="col-table">
                                <div className="col-table-th grid grid-cols-7 top-16 bg-gray-100">
                                    <div className="">순서</div>
                                    <div className="">uid</div>
                                    <div className="">소메뉴명</div>
                                    <div className="col-span-3">링크</div>
                                    <div className="">수정하기</div>
                                </div>
                                <ReactSortable {...sortableOptions} list={posts} setList={setPosts} dragClass="sortableDrag">
                                    {posts?.map((v: any, i: number) => (
                                        <div key={i} className="col-table-td grid grid-cols-7 bg-white transition duration-300 ease-in-out hover:bg-gray-100">
                                            <div className="handle flex-col cursor-pointer">
                                                <div className="flex items-center justify-center border p-3 rounded bg-slate-50">
                                                    <i className="fas fa-sort me-2"></i>
                                                    <div className="font-semibold">{v.sort}</div>
                                                </div>
                                            </div>
                                            <div className="">{v.uid}</div>
                                            <div className="">{v.name}</div>
                                            <div className="col-span-3">{v.to}</div>
                                            <div className="">
                                                <button
                                                    type="button"
                                                    className="text-blue-500 underline"
                                                    onClick={() => {
                                                        GoAdminMenuEdit(v.uid, 2, checkNumeric(router.query.uid));
                                                    }}
                                                >
                                                    수정하기
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </ReactSortable>
                            </div>
                        </div>
                        {/* card_area */}
                    </div>
                </div>
            </div>
        </LayoutPopup>
    );
};
export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {
        parent: ctx.query.uid,
    };
    var response: any = {};
    try {
        const { data } = await api.post(`/be/admin/setup/menus`, request);
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

export default SetupChildEdit;
