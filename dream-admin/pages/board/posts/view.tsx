import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import LayoutPopup from '@/components/LayoutPopup';
import BoardReply from '@/components/bbs/BoardReply';

const BoardPostView: NextPage = (props: any) => {
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
            router.replace(`/board/posts/view?uid=${uid}`);
        }
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

                        {posts.person && (
                            <table className="form-table table table-bordered align-middle w-full">
                                <tbody className="border-t border-black">
                                    <tr>
                                        <th scope="row">
                                            <span className="">개인정보</span>
                                        </th>
                                        <td colSpan={3} className="!px-5 !pt-3 !pb-0">
                                            <div className="flex items-center mb-3">
                                                <div className="shrink-0 w-20 font-bold text-end">이 름</div>
                                                <div className="flex-grow ps-5">{posts?.person?.name}</div>
                                            </div>
                                            <div className="flex items-center mb-3">
                                                <div className="shrink-0 w-20 font-bold text-end">휴대전화</div>
                                                <div className="flex-grow ps-5">{posts?.person?.mobile}</div>
                                            </div>
                                            <div className="flex items-center mb-3">
                                                <div className="shrink-0 w-20 font-bold text-end">이메일</div>
                                                <div className="flex-grow ps-5">{posts?.person?.email}</div>
                                            </div>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        )}

                        <div className="border-t border-black py-10 text-justify px-10 bg-white">
                            {posts.youtube && (
                                <div className="embed-container">
                                    <iframe src={`https://www.youtube.com/embed/${posts.youtube}`} frameBorder="0" allowFullScreen></iframe>
                                </div>
                            )}
                            {posts.thumb != '' && typeof posts.thumb != 'undefined' && posts.thumb != null && <img src={posts.thumb} className="my-3" alt="area_thumb" />}

                            <div className="normal-text whitespace-pre-wrap" dangerouslySetInnerHTML={{ __html: posts.contents }}></div>
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
        const { data } = await api.post(`/be/admin/posts/read`, request);
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

export default BoardPostView;
