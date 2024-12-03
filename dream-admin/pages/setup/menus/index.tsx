import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import { ReactSortable } from 'react-sortablejs';

const SetupMenus: NextPage = (props: any) => {
    const router = useRouter();
    const [posts, setPosts] = useState<any>([]);
    const [sort, setSort] = useState<any>([]);
    const [sortDiff, setSortDiff] = useState<boolean>(false);

    useEffect(() => {
        if (JSON.stringify(props) !== '{}') {
            setPosts(props.response);
        }
    }, [props]);

    useEffect(() => {
        if (sort.length == 0) {
            posts.map((v: any) => {
                setSort(current => [...current, v.uid]);
            });
        } else {
            var sort_diff = false;
            posts.map((v: any, i: number) => {
                if (v.uid != sort[i]) {
                    sort_diff = true;
                }
            });
            if (sort_diff) {
                setSort([]);
                posts.map((v: any) => {
                    setSort(current => [...current, v.uid]);
                });
                setSortDiff(sort_diff);
            }
        }
    }, [posts]);

    // 대/소메뉴 등록 수정
    const openAdminMenuEdit = (uid: number) => {
        window.open(`/setup/menus/parent_edit?uid=${uid}&depth=1&parent=0`, '대메뉴 정보', 'width=1120,height=800,location=no,status=no,scrollbars=yes,left=200%,top=50%');
    };
    // 소메뉴 list
    const openAdminMenuDepth2 = (uid: number) => {
        window.open(`/setup/menus/child_edit?uid=${uid}`, '소메뉴 정보', 'width=1120,height=800,location=no,status=no,scrollbars=yes,left=200%,top=50%');
    };

    const sortableOptions = {
        animation: 150,
        handle: '.handle',
    };

    const sorting = async v => {
        try {
            const p = {
                mode: 'SORT',
                // depth: 1,
                parent: 0,
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
        <Layout user={props.user} title="indendkorea admin console" nav_id={92} crumbs={['환경설정', '메뉴관리']}>
            {sortDiff && (
                <div className="py-5">
                    <button
                        type="button"
                        className="btn-funcs"
                        onClick={() => {
                            sorting(posts);
                        }}
                    >
                        대메뉴 순서 적용하기
                    </button>
                    <div className="text-red-600 font-bold ml-5">순서가 변경되었습니다. 적용하기 버튼을 클릭하여 저장해 주세요</div>
                </div>
            )}
            <div className="border-t py-3 grid grid-cols-2 h-16 items-center mb-2">
                <div className="text-left">총 {posts?.length} 개</div>
                <div className="text-right">
                    <button
                        type="button"
                        className="btn-funcs"
                        onClick={() => {
                            openAdminMenuEdit(0);
                        }}
                    >
                        <i className="fas fa-pen me-2"></i> 등록
                    </button>
                </div>
            </div>

            <div className="col-table">
                <div className="col-table-th grid grid-cols-6 sticky top-16 bg-gray-100">
                    {/* col-span-2 */}
                    <div className="">순서</div>
                    <div className="">대메뉴수정</div>
                    <div className="">번호</div>
                    <div className="">icon</div>
                    <div className="">대분류</div>
                    <div className="">상세보기</div>
                </div>

                <ReactSortable {...sortableOptions} list={posts} setList={setPosts} dragClass="sortableDrag">
                    {posts?.map((v: any, i: number) => (
                        <div key={i} className="col-table-td grid grid-cols-6 bg-white transition duration-300 ease-in-out hover:bg-gray-100">
                            <div className="handle flex-col cursor-pointer">
                                <div className="flex items-center justify-center border p-3 rounded bg-slate-50">
                                    <i className="fas fa-sort me-2"></i>
                                    <div className="font-semibold">{v.sort}</div>
                                </div>
                            </div>
                            <div className="filtered">
                                <button
                                    type="button"
                                    className="text-blue-500 underline"
                                    onClick={() => {
                                        openAdminMenuEdit(v.uid);
                                    }}
                                >
                                    수정
                                </button>
                            </div>
                            <div className="">{v.uid}</div>
                            <div className="">
                                <i className={`${v.icon}`}></i>
                            </div>
                            <div className="">{v.name}</div>
                            <div className="">
                                <button
                                    type="button"
                                    className="text-blue-500 underline"
                                    onClick={() => {
                                        openAdminMenuDepth2(v.uid);
                                    }}
                                >
                                    소메뉴 상세
                                </button>
                            </div>
                        </div>
                    ))}
                </ReactSortable>
            </div>
        </Layout>
    );
};
export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {};
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

export default SetupMenus;
