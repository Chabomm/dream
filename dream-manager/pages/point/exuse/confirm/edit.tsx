import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import { cls, checkNumeric } from '@/libs/utils';
import useForm from '@/components/form/useForm';
import ConfirmStateEdit from '@/components/modal/confirmStateEdit';

import {
    EditForm,
    EditFormTable,
    EditFormTH,
    EditFormTD,
    EditFormSubmit,
    EditFormInput,
    EditFormLabel,
    EditFormCard,
    EditFormCardHead,
    EditFormCardBody,
    EditFormTextarea,
    EditFormRadioList,
} from '@/components/UIcomponent/form/EditFormA';
import EditFormCallout from '@/components/UIcomponent/form/EditFormCallout';
import LayoutPopup from '@/components/LayoutPopup';

const ConfirmEdit: NextPage = (props: any) => {
    const crumbs = ['소명신청 관리', '소명승인 ' + (props.response.values?.uid > 0 ? '수정' : '등록')];
    const callout = [];
    const title_sub = '복지카드 사용 건 중 소명신청한 내역 확인 및 수정';
    const router = useRouter();

    const [memo, setMemo] = useState<any>([]);
    const [posts, setPosts] = useState<any>({});

    useEffect(() => {
        if (props) {
            if (props.response.code == 200) {
                setPosts(props.response);
                s.setValues(props.response.values);
                setMemo(props.response.memo_list);
            } else {
                alert(props.response.msg);
                window.close();
            }
        }
    }, []);

    const { s, fn, attrs } = useForm({
        onSubmit: async () => {
            await editing();
        },
    });

    const editing = async () => {
        if (posts?.state == '소명승인완료' && s.values.state != '소명승인완료') {
            alert('소명승인완료된 건은 수정은 불가 합니다.');
            return;
        } else if (s.values.state == '결제취소') {
            alert('결제취소 상태로 변경은 불가합니다.(자동변경됩니다)');
            return;
        } else if (posts?.state == '결제취소') {
            alert('결제취소 상태는 변경이 불가합니다.');
            return;
        } else {
            openConfirmEdit();
        }
    };

    // [ S ] 상태변경 모달
    const [confirmEditOpen, setConfirmEditOpen] = useState(false);
    const openConfirmEdit = () => {
        setConfirmEditOpen(true);
    };
    // [ E ] 상태변경 모달

    // [ S ] 파일 다운로드
    const download_file = async (file_kind: string) => {
        let file_link = '';
        if (file_kind == 'attch_file') {
            file_link = posts.attch_file;
        } else {
            file_link = posts.biz_hooper;
        }

        const arr_file_link = file_link.split('/');
        const file_name = arr_file_link[arr_file_link.length - 1];

        try {
            await api({
                url: `/be/aws/download`,
                method: 'POST',
                responseType: 'blob',
                data: {
                    file_url: file_link,
                },
            }).then(async response => {
                var fileURL = window.URL.createObjectURL(new Blob([response.data]));
                var fileLink = document.createElement('a');
                fileLink.href = fileURL;
                fileLink.setAttribute('download', file_name);
                document.body.appendChild(fileLink);
                fileLink.click();

                await api.post(`/be/aws/temp/delete`);
            });
        } catch (e: any) {
            console.log(e);
        }
    };
    // [ E ] 파일 다운로드

    return (
        <>
            <LayoutPopup title={crumbs[crumbs.length - 1]} className="px-6 bg-slate-50">
                <EditFormCallout title={crumbs[crumbs.length - 1]} title_sub={title_sub} callout={callout} />

                <EditForm onSubmit={fn.handleSubmit}>
                    <EditFormCard>
                        <EditFormCardHead>
                            <div className="text-lg">소명신청 상세</div>
                        </EditFormCardHead>
                        <EditFormCardBody>
                            <EditFormTable className="grid-cols-6">
                                <EditFormTH className="col-span-1">상태변경</EditFormTH>
                                <EditFormTD className="col-span-5">
                                    <EditFormRadioList
                                        input_name="state"
                                        values={s.values?.state}
                                        filter_list={[
                                            { key: '소명신청', text: '소명신청' },
                                            { key: '소명승인완료', text: '소명승인완료' },
                                            { key: '미승인', text: '미승인' },
                                            { key: '재차감설정', text: '재차감설정' },
                                            { key: '결제취소', text: '결제취소' },
                                        ]}
                                        is_mand={true}
                                        errors={s.errors}
                                        handleChange={fn.handleChange}
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1">포인트종류</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormLabel className="">{posts?.point_type}</EditFormLabel>
                                </EditFormTD>
                                <EditFormTH className="col-span-1">복지항목</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormLabel className="">{posts?.welfare_type}</EditFormLabel>
                                </EditFormTD>
                                <EditFormTH className="col-span-1">가맹점명</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormLabel className="">{posts?.biz_item}</EditFormLabel>
                                </EditFormTD>
                                <EditFormTH className="col-span-1">소명내용</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormLabel className="">{posts?.exuse_detail}</EditFormLabel>
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">신청금액</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput
                                        type="text"
                                        name="exuse_amount"
                                        value={s.values?.exuse_amount || ''}
                                        is_mand={true}
                                        placeholder={'신청금액을 입력하세요'}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        className=""
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1">증빙자료</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    {/* <div>
                                        <button
                                            type="button"
                                            className="text-blue-500 underline cursor-pointe text-start"
                                            onClick={e => {
                                                download_file('attch_file');
                                            }}
                                        >
                                            <span>
                                                <i className="fas fa-file-download me-1"></i>
                                            </span>
                                            {posts?.attch_file_fakename != '' && typeof posts?.attch_file_fakename != 'undefined' ? posts?.attch_file_fakename : posts?.attch_file}
                                        </button>
                                    </div> */}
                                    <div>
                                        <button
                                            type="button"
                                            className="text-blue-500 underline cursor-pointe text-start"
                                            onClick={e => {
                                                download_file('attch_file');
                                            }}
                                        >
                                            {posts?.attch_file != '' && posts?.attch_file != null ? (
                                                <span>
                                                    <i className="fas fa-file-download me-1"></i>
                                                    {posts?.attch_file}
                                                </span>
                                            ) : (
                                                <></>
                                            )}
                                        </button>
                                    </div>
                                </EditFormTD>
                            </EditFormTable>
                        </EditFormCardBody>
                    </EditFormCard>
                    <EditFormCard>
                        <EditFormCardHead>
                            <div className="text-lg">상담로그</div>
                        </EditFormCardHead>
                        <EditFormCardBody>
                            <EditFormTable className="grid-cols-6">
                                <EditFormTH className="col-span-1">상담자 메모</EditFormTH>
                                <EditFormTD className="col-span-5">
                                    <EditFormTextarea
                                        name="memo"
                                        value={s.values?.memo || ''}
                                        rows={4}
                                        placeholder="추가할 상담로그 내용을 입력하세요"
                                        errors={s.errors}
                                        values={s.values}
                                        set_values={s.setValues}
                                        max_length={1000}
                                    />
                                </EditFormTD>
                            </EditFormTable>
                            {memo.list?.map((vv, ii) => (
                                <tr className="col-table grid grid-cols-6 text-center items-center border-b border-x" key={ii}>
                                    <th className="col-span-1 py-4 h-full bg-gray-100 font-bold text-sm">
                                        {vv.create_user}
                                        <div className="text-xs text-slate-400">{vv.create_at}</div>
                                    </th>
                                    <td className="col-span-5 p-3 text-start">{vv.memo}</td>
                                </tr>
                            ))}
                        </EditFormCardBody>
                    </EditFormCard>

                    <EditFormSubmit button_name={`${s.values?.uid > 0 ? '수정' : '등록'}하기`} submitting={s.submitting}></EditFormSubmit>
                </EditForm>
                {confirmEditOpen && <ConfirmStateEdit setConfirmEditOpen={setConfirmEditOpen} params={s.values} posts={posts} />}
            </LayoutPopup>
        </>
    );
};
export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {
        uid: checkNumeric(ctx.query.uid),
    };
    var response: any = {};
    try {
        const { data } = await api.post(`/be/manager/point/exuse/confirm/read`, request);
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

export default ConfirmEdit;
