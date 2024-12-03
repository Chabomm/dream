import React, { useState, useEffect } from 'react';
import { checkNumeric } from '@/libs/utils';
import { api } from '@/libs/axios';
import { useRouter } from 'next/router';

export default function BoardReply({ props }) {
    const router = useRouter();
    const [posts, setPosts] = useState<any>({});

    useEffect(() => {
        if (props) {
            setPosts(props.response);
        }
    }, []);

    const [newReply, setNewReply] = useState<string>('');
    const [submitting, setSubmitting] = useState<boolean>(false);

    const handleNewReply = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const { value } = e.target;
        setNewReply(value);
    };

    const addNewReply = async (uid_for_del: number) => {
        setSubmitting(true);
        let params: any = {};
        params.uid = checkNumeric(uid_for_del);
        params.posts_uid = checkNumeric(posts.uid);
        params.board_uid = checkNumeric(posts.board.uid);
        params.reply = newReply;

        let confirm_msg = '댓글(답변)을 등록합니다. 계속 하시겠습니까?';
        if (checkNumeric(uid_for_del) > 0) {
            params.mode = 'DEL';
            confirm_msg = '댓글(답변)을 삭제하시겠습니까?';
        } else {
            params.mode = 'REG';
            if (typeof params.reply === 'undefined' || params.reply == '') {
                alert('댓글(답변) 내용을 입력해 주세요');
                setSubmitting(false);
                return;
            }
        }

        if (!confirm(confirm_msg)) {
            setSubmitting(false);
            return;
        }

        try {
            const { data } = await api.post(`/be/admin/posts/reply/edit`, params);
            if (data.code == 200) {
                alert(data.msg);
                setNewReply('');
                router.reload();
            } else {
                alert(data.msg);
            }
        } catch (e: any) {
            setSubmitting(false);
        }
        setSubmitting(false);
    };
    return (
        <>
            {posts?.board?.is_comment == 'T' && (
                <>
                    <table className="form-table table table-bordered align-middle w-full border-b">
                        <tbody className="border-t-2 border-black">
                            <tr>
                                <th scope="row">
                                    <span className="">답글내용</span>
                                </th>
                                <td colSpan={3}>
                                    <div className="flex justify-stretch items-stretch">
                                        <textarea
                                            rows={5}
                                            placeholder="답글 내용을 입력해주세요."
                                            className="flex-grow border p-3 rounded-0 rounded-l focus:shadow-none focus:outline-none focus:border-black"
                                            onChange={handleNewReply}
                                            value={newReply}
                                        ></textarea>
                                        <button
                                            disabled={submitting}
                                            type="button"
                                            onClick={() => {
                                                addNewReply(0);
                                            }}
                                            className="bg-teal-500 px-5 text-sm text-white rounded-r hover:bg-teal-800 shrink-0"
                                        >
                                            답글추가
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>

                    <div className="border-t border-b border-black bg-zinc-50">
                        {posts?.replys?.map((v, i) => (
                            <div key={i} className="px-10 border-b py-5">
                                <div className="flex items-end justify-between mb-3">
                                    <div className="font-bold">
                                        {v.user_name}({v.user_id})
                                    </div>
                                    <div className="text-gray-700">{v.create_at}</div>
                                </div>
                                <div className="relative">
                                    <div className="whitespace-pre">{v.reply}</div>
                                    <div
                                        onClick={() => {
                                            addNewReply(v.uid);
                                        }}
                                        className="absolute right-0 bottom-0 text-red-500 cursor-pointer"
                                    >
                                        <i className="fas fa-trash-alt me-2"></i> 삭제
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </>
            )}
        </>
    );
}
