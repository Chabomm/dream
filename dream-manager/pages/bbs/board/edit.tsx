import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect, useRef } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import { cls, checkNumeric, dateformatYYYYMMDD, dateformatYYYYMM } from '@/libs/utils';
import BoardReply from '@/components/bbs/BoardReply';
import useForm from '@/components/form/useForm';
import LayoutPopup from '@/components/LayoutPopup';

import dynamic from 'next/dynamic';
const CKEditor = dynamic(() => import('@/components/editor/CKEditor'), { ssr: false });

import { EditForm, EditFormTable, EditFormTH, EditFormTD, EditFormSubmit, EditFormInput, EditFormAttachFiles } from '@/components/UIcomponent/form/EditFormA';
import EditFormCallout from '@/components/UIcomponent/form/EditFormCallout';

const BoardEdit: NextPage = (props: any) => {
    const router = useRouter();
    const crumbs = ['게시물 관리', '게시물 ' + (props.response.values?.uid > 0 ? '수정' : '등록')];
    const callout = [];
    const title_sub = '게시물을 등록/수정할 수 있습니다';

    const [filter, setFilter] = useState<any>([]);
    const [reply, setReply] = useState<any>([]);
    const [board, setBoard] = useState<any>({});

    useEffect(() => {
        if (props) {
            if (props.response.code == 200) {
                s.setValues(props.response.values);
                setFilter(props.response.filter);
                setReply(props.response.reply);
                setBoard(props.response.board);
            } else {
                alert(props.response.msg);
                window.close();
            }
        }
    }, []);

    const { s, fn, attrs } = useForm({
        onSubmit: async () => {
            await editing('REG');
        },
    });

    const deleting = () => editing('DEL');

    const editing = async mode => {
        try {
            const params = { ...s.values };
            return;
            if (mode == 'REG' && params.uid > 0) {
                mode = 'MOD';
            }
            params.mode = mode;

            if (typeof params.board_uid == 'undefined' || params.board_uid + '' == 'null') {
                params.board_uid = checkNumeric(router.query.board_uid);
            }

            if (mode == 'DEL' && !confirm('게시물 삭제시 휴지통으로 이동되며, 게시물은 노출되지 않습니다. 계속 하시겠습니까 ?')) {
                return;
            }
            const { data } = await api.post(`/be/manager/bbs/edit`, params);
            s.setSubmitting(false);
            if (data.code == 200) {
                alert(data.msg);
                router.push('/bbs/board/edit?uid=' + data.uid);
            } else {
                alert(data.msg);
            }
        } catch (e: any) {}
    };

    return (
        <LayoutPopup title={crumbs[crumbs.length - 1]} className="px-3">
            <EditFormCallout title={crumbs[crumbs.length - 1]} title_sub={title_sub} callout={callout} />

            {/* <div>
                <div className="font-bold mb-3 text-red-500">s.values</div>
                {JSON.stringify(s.values, null, 4)}
            </div> */}

            <EditForm onSubmit={fn.handleSubmit}>
                <EditFormTable className="grid-cols-6">
                    <EditFormTH className="col-span-1">제목</EditFormTH>
                    <EditFormTD className="col-span-5">
                        <EditFormInput type="text" name="title" value={s.values?.title || ''} onChange={fn.handleChange} errors={s.errors} is_mand={true} className="w-full" />
                    </EditFormTD>
                    <EditFormTH className="col-span-1">첨부파일</EditFormTH>
                    <EditFormTD className="col-span-5">
                        <EditFormAttachFiles
                            files_of_values={s.values?.files}
                            name="files"
                            errors={s.errors}
                            values={s.values}
                            set_values={s.setValues}
                            upload_option={{ table_uid: s.values?.uid, table_name: 'T_BOARD_POSTS', upload_path: `/board/${dateformatYYYYMM()}/`, file_type: 'all' }}
                        />
                    </EditFormTD>
                    <EditFormTH className="col-span-1">내용</EditFormTH>
                    <EditFormTD className="col-span-5">
                        <CKEditor
                            initialData={s.values?.contents || ''}
                            onChange={(event, editor) => {
                                s.setValues({ ...s.values, ['contents']: editor.getData() });
                            }}
                            upload_path={'/board/editor/' + dateformatYYYYMMDD()}
                        />
                    </EditFormTD>
                </EditFormTable>
                <EditFormSubmit button_name={`${s.values?.uid > 0 ? '수정' : '등록'}하기`} submitting={s.submitting}></EditFormSubmit>
            </EditForm>
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

export default BoardEdit;
