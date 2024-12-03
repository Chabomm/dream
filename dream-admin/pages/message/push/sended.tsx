import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { cls, checkNumeric } from '@/libs/utils';
import OverlayText from '@/components/UIcomponent/OverlayText';

const UmsPushSendedt: NextPage = (props: any) => {
    const [posts, setPosts] = useState([]);
    const [testers, setTesters] = useState([]);
    const [modal, setModal] = useState(false);
    const [pushMsgUid, setPushMsgUid] = useState(0);
    const [modalData, setModalData] = useState({
        result: {},
        tester: {
            tester_name: '',
            device_os: '',
            user_id: '',
            partner_id: '',
        },
    });

    useEffect(() => {
        if (props) {
            setPosts(props.response.list);
            setTesters(props.response.list_tester);
            setPushMsgUid(props.response.list[0].uid);
        }
    }, [props]);

    const send_push_tester = async (tester_uid: number) => {
        try {
            if (checkNumeric(tester_uid) == 0) {
                alert('tester_uid is empty');
                return;
            }

            if (checkNumeric(pushMsgUid) == 0) {
                alert('push_msg_uid is empty');
                return;
            }

            const tester_param = {
                tester_uid: tester_uid,
                push_msg_uid: pushMsgUid,
            };
            const { data } = await api.post(`/ums/push/send/tester`, tester_param);
            if (data.code == 200) {
                setModal(true);
                setModalData(data);
            } else {
                alert(data.msg);
            }
        } catch (e: any) {}
    };

    const closeModal = () => {
        setModal(false);
    };

    const getResultParse = msg => {
        let return_msg = msg;
        try {
            var obj = JSON.parse(msg);
            return_msg = obj.msg + '';

            if (obj.code == '1' && obj.result != '1') {
                return_msg = '<span class="text-red-500 me-1">(실패)</span>' + return_msg;
            }
        } catch (e) {}
        return return_msg;
    };

    return (
        <>
            <div className="edit_popup w-full bg-slate-100 mx-auto py-10" style={{ minHeight: '100vh' }}>
                <div className="px-9">
                    <div className="text-2xl font-semibold">푸쉬 발송(예약) 내역</div>

                    <div className="card_area">
                        <div className="">
                            <div className="font-bold mb-5">테스터</div>

                            <div className="col-table">
                                <div className="col-table-th grid grid-cols-6 sticky bg-gray-100" style={{ top: '-1rem' }}>
                                    <div className="col-span-1">테스터명</div>
                                    <div className="col-span-1">플랫폼</div>
                                    <div className="col-span-1">복지몰</div>
                                    <div className="col-span-2">아이디</div>
                                    <div className="col-span-1">테스트전송</div>
                                </div>

                                {testers?.map((v: any, i: number) => (
                                    <div key={i} className="col-table-td grid grid-cols-6 bg-white transition duration-300 ease-in-out hover:bg-gray-100">
                                        <div className="col-span-1">{v.tester_name}</div>
                                        <div className="col-span-1">{v.device_os}</div>
                                        <div className="col-span-1">{v.partner_id}</div>
                                        <div className="col-span-2">{v.user_id}</div>
                                        <div className="col-span-1">
                                            <button
                                                type="button"
                                                className="btn-funcs"
                                                onClick={() => {
                                                    send_push_tester(v.uid);
                                                }}
                                            >
                                                전송
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="border-t py-3 grid grid-cols-2 h-16 items-center">
                            <div className="text-left">총 {posts?.length} 개</div>
                            <div className="text-right"></div>
                        </div>
                        <div className="col-table">
                            <div className="col-table-th grid grid-cols-7 sticky bg-gray-100" style={{ top: '-1rem' }}>
                                <div className="col-span-1">플랫폼</div>
                                <div className="col-span-1">복지몰</div>
                                <div className="col-span-2">아이디</div>
                                <div className="col-span-1">메시지 내용</div>
                                <div className="col-span-2">결과</div>
                            </div>

                            {posts?.map((v: any, i: number) => (
                                <div key={i} className="col-table-td grid grid-cols-7 bg-white transition duration-300 ease-in-out hover:bg-gray-100">
                                    <div className="col-span-1">{v.device_os}</div>
                                    <div className="col-span-1 truncate">{v.partner_id}</div>
                                    <div className="col-span-2 truncate">{v.user_id}</div>
                                    <div className="col-span-1">
                                        <OverlayText
                                            item={{
                                                dire: 'left',
                                                view_text: '[내용보기]',
                                                push_title: v.push_title,
                                                push_msg: v.push_msg,
                                                push_img: v.push_img,
                                            }}
                                        />
                                    </div>
                                    <div className="col-span-2">
                                        <div dangerouslySetInnerHTML={{ __html: getResultParse(v.push_result) }}></div>
                                    </div>
                                </div>
                            ))}
                        </div>
                        {/* <ListPagenation props={params} getPagePost={getPagePost} /> */}
                    </div>
                    {/* card_area */}
                </div>
            </div>

            <div className={cls(modal ? '' : 'hidden', 'fixed left-0 top-0 flex h-full w-full items-center justify-center bg-black bg-opacity-50 py-10 z-10')}>
                <div className="max-h-full w-full max-w-xl overflow-y-auto sm:rounded-2xl bg-white">
                    <div className="w-full">
                        <div className="m-8 my-20 max-w-[400px] mx-auto">
                            <div className="mb-8">
                                <h1 className="mb-4 text-3xl font-extrabold">전송결과</h1>

                                {/* {process.env.NODE_ENV == 'development' && (
                                    <pre className="">
                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <div className="font-bold mb-3 text-red-500">modalData</div>
                                                {JSON.stringify(modalData, null, 4)}
                                            </div>
                                        </div>
                                    </pre>
                                )} */}

                                <pre className="mb-5">
                                    <div className="font-bold mb-3 text-red-500">전송결과</div>
                                    {JSON.stringify(modalData?.result, null, 4)}
                                </pre>

                                <div className="grid grid-cols-2 gap-4">
                                    <div className="col-span-1">
                                        <label className="form-label">테스터명</label>
                                        <div className="form-control">{modalData.tester.tester_name}</div>
                                    </div>
                                    <div className="col-span-1">
                                        <label className="form-label">디바이스</label>
                                        <div className="form-control">{modalData.tester.device_os}</div>
                                    </div>
                                    <div className="col-span-1">
                                        <label className="form-label">아이디</label>
                                        <div className="form-control">{modalData.tester.user_id}</div>
                                    </div>
                                    <div className="col-span-1">
                                        <label className="form-label">복지몰</label>
                                        <div className="form-control">{modalData.tester.partner_id}</div>
                                    </div>
                                </div>
                            </div>
                            <div className="space-y-4">
                                {/* <button className="p-3 bg-black rounded-full text-white w-full font-semibold">Allow notifications</button> */}
                                <button className="p-3 bg-white border rounded-full w-full font-semibold" onClick={closeModal}>
                                    Close
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
};
export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {
        booking_uid: ctx.query.uid,
        page: 1,
        page_size: 0,
        page_view_size: 0,
        page_total: 0,
        page_last: 0,
    };
    var response: any = {};
    try {
        const { data } = await api.post(`/ums/push/booking/send/list`, request);
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

export default UmsPushSendedt;
