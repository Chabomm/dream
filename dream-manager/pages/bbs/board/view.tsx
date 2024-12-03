import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect, useRef } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import LayoutPopup from '@/components/LayoutPopup';
import BoardReply from '@/components/bbs/BoardReply';

const BoardView: NextPage = (props: any) => {
    const router = useRouter();
    const [posts, setPosts] = useState<any>({});

    useEffect(() => {
        if (props) {
            if (props.response.code != '200') {
                alert(props.response.msg);
                window.close();
            }
            setPosts(props.response);
        }
    }, [router.asPath]);

    const download_file = async file => {
        try {
            let request = { uid: file.uid };
            await api({
                url: `/be/admin/posts/file/download/${file.uid}`,
                method: 'POST',
                responseType: 'blob',
            }).then(response => {
                var fileURL = window.URL.createObjectURL(new Blob([response.data]));
                var fileLink = document.createElement('a');
                fileLink.href = fileURL;
                fileLink.setAttribute('download', file.fake_name);
                document.body.appendChild(fileLink);
                fileLink.click();
            });
        } catch (e: any) {}
    };

    const routePosts = (uid: number) => {
        if (uid > 0) {
            router.replace(`/bbs/board/view?uid=${uid}`);
        }
    };

    const openEdit = (uid: number) => {
        window.open(`/bbs/board/edit?uid=${uid}&board_uid=${props.response.board_uid}`, '게시물 등록/수정', 'width=1120,height=800,location=no,status=no,scrollbars=yes');
    };
    return (
        <LayoutPopup title={'게시물상세'}>
            <div className="card_area mb-20">
                <section className="site-width pb-24 bbs-contents">
                    <div className="my-10 text-center">
                        <div className="text-2xl font-bold mb-2">{posts.title}</div>
                        <div className="text font-normal text-gray-500">{posts.create_at}</div>
                    </div>

                    <div className="border-y-2 border-second mb-10">
                        {posts?.files?.length > 0 && posts.files[0].uid > 0 && (
                            <table className="form-table table table-bordered align-middle w-full">
                                <tbody className="border-t border-black">
                                    <tr>
                                        <th scope="row">
                                            <span className="">첨부파일</span>
                                        </th>
                                        <td colSpan={3} className="!px-5 !pt-3 !pb-0">
                                            <div className="">
                                                {posts?.files?.map((v, i) => (
                                                    <div
                                                        key={i}
                                                        className="mb-3 cursor-pointer"
                                                        onClick={e => {
                                                            download_file(v);
                                                        }}
                                                    >
                                                        <i className="far fa-save me-2"></i>
                                                        <span className="">{v.fake_name}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        )}

                        <div className="border-t border-black py-10 text-justify px-10 bg-white">
                            <img className="mb-3" src={posts.thumb} />
                            {/* 썸네일보여주기 팀장님이랑 같이 하기로 함 */}
                            {posts.youtube && (
                                <div className="embed-container">
                                    <iframe src={`https://www.youtube.com/embed/${posts.youtube}`} frameBorder="0" allowFullScreen></iframe>
                                </div>
                            )}
                            <div className="ck-content" dangerouslySetInnerHTML={{ __html: posts.contents }}></div>
                        </div>

                        <div className="border-t border-black bg-white px-5 mt-5">
                            <div className="flex justify-between py-2 border-b items-center">
                                <div className="w-20 flex-shrink-0">
                                    <i className="fas fa-chevron-up me-2"></i>이전글
                                </div>
                                <div
                                    onClick={e => {
                                        routePosts(posts?.prev_posts?.uid);
                                    }}
                                    className="flex-grow cursor-pointer truncate"
                                >
                                    {posts?.prev_posts?.title}
                                </div>
                                {props.device == 'desktop' && <div className="text-gray-500">{posts?.prev_posts?.create_at}</div>}
                            </div>

                            <div className="flex justify-between py-2 border-b items-center">
                                <div className="w-20 flex-shrink-0">
                                    <i className="fas fa-chevron-down me-2"></i>다음글
                                </div>
                                <div
                                    onClick={e => {
                                        routePosts(posts?.next_posts?.uid);
                                    }}
                                    className="flex-grow cursor-pointer truncate"
                                >
                                    {posts?.next_posts?.title}
                                </div>
                                {props.device == 'desktop' && <div className="text-gray-500">{posts?.next_posts?.create_at}</div>}
                            </div>
                        </div>
                    </div>
                    {(props.user.role == 'master' || posts.create_user == props.user?.user_id) && (
                        <div className="mt-5 w-full text-center">
                            <button
                                className="mr-3 px-5 bg-blue-500 rounded-md py-2 text-white text-center"
                                onClick={() => {
                                    openEdit(posts.uid);
                                }}
                            >
                                수정
                            </button>
                        </div>
                    )}
                    <BoardReply props={props} />
                </section>
            </div>
        </LayoutPopup>
    );
};
export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {
        uid: ctx.query.uid,
    };
    var response: any = {};
    try {
        const { data } = await api.post(`/be/manager/bbs/read`, request);
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

export default BoardView;
