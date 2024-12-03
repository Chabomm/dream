import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import LayoutPopup from '@/components/LayoutPopup';
import { cls, getToken } from '@/libs/utils';

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
    FixedButtonWrap,
    FixedButton,
} from '@/components/UIcomponent/form/EditFormA';
import EditFormCallout from '@/components/UIcomponent/form/EditFormCallout';

const B2BOrderDetail: NextPage = (props: any) => {
    const crumbs = ['신청 서비스 정보'];
    const callout = [];
    const title_sub = '';

    const router = useRouter();
    const [posts, setPosts] = useState<any>({});

    useEffect(() => {
        if (props) {
            if (props.response.code != '200') {
                alert(props.response.msg);
                window.close();
            }
            setPosts(props.response.posts);
        }
    }, [router.asPath]);

    const openServiceItem = (guid: number) => {
        let b2b_center_domain = `http://localhost:13000`;
        if (`${process.env.NODE_ENV}` == 'production') {
            b2b_center_domain = `https://`;
        }

        var newForm = document.createElement('form');
        newForm.setAttribute('method', 'POST');

        var newInput = document.createElement('input');
        newInput.setAttribute('type', 'hidden');
        newInput.setAttribute('name', 'token');
        newInput.setAttribute('value', getToken(undefined));
        newForm.appendChild(newInput);

        var newInput = document.createElement('input');
        newInput.setAttribute('type', 'hidden');
        newInput.setAttribute('name', 'guid');
        newInput.setAttribute('value', guid + '');
        newForm.appendChild(newInput);

        var newInput = document.createElement('input');
        newInput.setAttribute('type', 'hidden');
        newInput.setAttribute('name', 'company_name');
        newInput.setAttribute('value', '인디앤드코리아');
        newForm.appendChild(newInput);

        var newInput = document.createElement('input');
        newInput.setAttribute('type', 'hidden');
        newInput.setAttribute('name', 'depart');
        newInput.setAttribute('value', '');
        newForm.appendChild(newInput);

        var newInput = document.createElement('input');
        newInput.setAttribute('type', 'hidden');
        newInput.setAttribute('name', 'position1');
        newInput.setAttribute('value', '');
        newForm.appendChild(newInput);

        var newInput = document.createElement('input');
        newInput.setAttribute('type', 'hidden');
        newInput.setAttribute('name', 'mobile');
        newInput.setAttribute('value', '');
        newForm.appendChild(newInput);

        var newInput = document.createElement('input');
        newInput.setAttribute('type', 'hidden');
        newInput.setAttribute('name', 'email');
        newInput.setAttribute('value', '');
        newForm.appendChild(newInput);

        document.body.appendChild(newForm);

        var objPopup = window.open('', 'b2b_goods_view', 'width=1120,height=800, scrollbars=no, toolbar=no, status=no, resizable=no'); //창띄우기 명령에서 그 경로는 빈칸으로 한다.
        newForm.target = 'b2b_goods_view'; // 타겟 : 위의 창띄우기의 창이름과 같아야 한다.
        newForm.action = b2b_center_domain + `/inbound/goods?guid=${guid}`; // 액션경로
        if (objPopup == null) alert('차단된 팝업창을 허용해 주세요'); // 팝업이 뜨는지 확인
        else {
            newForm.submit();
            objPopup.focus(); //새로 띄워준 창에 포커스를 맞춰준다.
        }
    };

    // [ S ] 파일 다운로드
    const download_file = async (file: any) => {
        try {
            await api({
                url: `/be/aws/download`,
                method: 'POST',
                responseType: 'blob',
                data: {
                    file_url: file.apply_value,
                },
            }).then(response => {
                var fileURL = window.URL.createObjectURL(new Blob([response.data]));
                var fileLink = document.createElement('a');
                fileLink.href = fileURL;
                fileLink.setAttribute('download', file.file_name);
                document.body.appendChild(fileLink);
                fileLink.click();
            });
        } catch (e: any) {
            console.log(e);
        }
    };
    // [ E ] 파일 다운로드
    return (
        <LayoutPopup title={crumbs[crumbs.length - 1]} className="px-6">
            <EditFormCallout title={crumbs[crumbs.length - 1]} title_sub={title_sub} callout={callout} />
            <EditFormCard>
                <EditFormCardHead>
                    <div className="text-lg">신청 서비스 정보</div>
                    <div className="">
                        <button
                            className="border border-blue-500 rounded py-1 px-2 text-blue-500 hover:bg-blue-500 hover:text-white"
                            type="button"
                            onClick={() => {
                                openServiceItem(posts.guid);
                            }}
                        >
                            서비스 상세정보
                        </button>
                    </div>
                </EditFormCardHead>
                <EditFormCardBody>
                    <EditFormTable className="grid-cols-6">
                        <EditFormTH className="col-span-1">서비스명</EditFormTH>
                        <EditFormTD className="col-span-5">
                            <EditFormLabel className="">{posts?.title}</EditFormLabel>
                        </EditFormTD>
                        <EditFormTH className="col-span-1">처리상태</EditFormTH>
                        <EditFormTD className="col-span-2">
                            <EditFormLabel className="">{posts?.state}</EditFormLabel>
                        </EditFormTD>
                        <EditFormTH className="col-span-1">신청일</EditFormTH>
                        <EditFormTD className="col-span-2">
                            <EditFormLabel className="">{posts?.create_at}</EditFormLabel>
                        </EditFormTD>
                        <EditFormTH className="col-span-1">카테고리</EditFormTH>
                        <EditFormTD className="col-span-5">
                            <EditFormLabel className="">{posts?.category}</EditFormLabel>
                        </EditFormTD>
                    </EditFormTable>
                </EditFormCardBody>
            </EditFormCard>
            <EditFormCard>
                <EditFormCardHead>
                    <div className="text-lg">신청 기업 정보</div>
                </EditFormCardHead>
                <EditFormCardBody>
                    <EditFormTable className="grid-cols-6">
                        <EditFormTH className="col-span-1">회사명</EditFormTH>
                        <EditFormTD className="col-span-5">
                            <EditFormLabel className="">{posts?.apply_company}</EditFormLabel>
                        </EditFormTD>
                        <EditFormTH className="col-span-1">담당자명</EditFormTH>
                        <EditFormTD className="col-span-5">
                            <EditFormLabel className="">{posts?.apply_name}</EditFormLabel>
                        </EditFormTD>
                        <EditFormTH className="col-span-1">부서</EditFormTH>
                        <EditFormTD className="col-span-2">
                            <EditFormLabel className="">{posts?.apply_depart}</EditFormLabel>
                        </EditFormTD>
                        <EditFormTH className="col-span-1">직책</EditFormTH>
                        <EditFormTD className="col-span-2">
                            <EditFormLabel className="">{posts?.apply_position}</EditFormLabel>
                        </EditFormTD>
                        <EditFormTH className="col-span-1">연락처</EditFormTH>
                        <EditFormTD className="col-span-2">
                            <EditFormLabel className="">{posts?.apply_phone}</EditFormLabel>
                        </EditFormTD>
                        <EditFormTH className="col-span-1">이메일</EditFormTH>
                        <EditFormTD className="col-span-2">
                            <EditFormLabel className="">{posts?.apply_email}</EditFormLabel>
                        </EditFormTD>
                    </EditFormTable>
                </EditFormCardBody>
            </EditFormCard>
            {posts.info_list?.length > 0 && (
                <EditFormCard>
                    <EditFormCardHead>
                        <div className="text-lg">신청정보 작성</div>
                    </EditFormCardHead>
                    <EditFormCardBody>
                        <div className="border-t border-black">
                            {posts.info_list?.map((v: any, i: number) => (
                                <EditFormTable key={i} className="grid-cols-6 !border-t-0">
                                    <EditFormTH className={cls(`${v.option_yn == 'Y' && 'mand'} col-span-1`)}>{v.option_title}</EditFormTH>
                                    <EditFormTD className="col-span-5">
                                        {v.option_type == 'F' ? (
                                            <button
                                                type="button"
                                                className="text-blue-500 underline cursor-pointer"
                                                onClick={e => {
                                                    download_file(v);
                                                }}
                                            >
                                                파일 첨부 확인 ({v.file_name})
                                            </button>
                                        ) : v.option_type == 'G' ? (
                                            <div className="w-full text-start">{v.placeholder}</div>
                                        ) : (
                                            <div className="w-full text-start whitespace-pre-wrap" dangerouslySetInnerHTML={{ __html: v.apply_value }}></div>
                                        )}
                                    </EditFormTD>
                                </EditFormTable>
                            ))}
                        </div>
                    </EditFormCardBody>
                </EditFormCard>
            )}
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
        const { data } = await api.post(`/be/admin/b2b/order/read`, request);
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

export default B2BOrderDetail;
