import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import LayoutPopup from '@/components/LayoutPopup';
import { cls, getToken, num2Cur } from '@/libs/utils';
import Layout from '@/components/Layout';

const ServiceApplyDetail: NextPage = (props: any) => {
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

    // const openServiceItem = (guid: number) => {
    //     router.push(`/b2b/goods/popup/detail?uid=${guid}`);
    // };

    const detail_info = async (service_uid: number) => {
        try {
            const { data } = await api.post(`/be/manager/b2b/order/detail`, {
                service_uid: service_uid,
                partner_uid: props.user.partner_uid,
                user_uid: props.user.user_uid,
            });
            return data;
        } catch (e) {}
    };

    const openServiceItem = async (guid: number) => {
        let newPosts = await detail_info(guid);

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
        newInput.setAttribute('value', newPosts.company_name);
        newForm.appendChild(newInput);

        var newInput = document.createElement('input');
        newInput.setAttribute('type', 'hidden');
        newInput.setAttribute('name', 'depart');
        newInput.setAttribute('value', newPosts.manager.depart);
        newForm.appendChild(newInput);

        var newInput = document.createElement('input');
        newInput.setAttribute('type', 'hidden');
        newInput.setAttribute('name', 'position1');
        newInput.setAttribute('value', newPosts.manager.position1);
        newForm.appendChild(newInput);

        var newInput = document.createElement('input');
        newInput.setAttribute('type', 'hidden');
        newInput.setAttribute('name', 'mobile');
        newInput.setAttribute('value', newPosts.manager.mobile);
        newForm.appendChild(newInput);

        var newInput = document.createElement('input');
        newInput.setAttribute('type', 'hidden');
        newInput.setAttribute('name', 'email');
        newInput.setAttribute('value', newPosts.manager.email);
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
            }).then(async response => {
                var fileURL = window.URL.createObjectURL(new Blob([response.data]));
                var fileLink = document.createElement('a');
                fileLink.href = fileURL;
                fileLink.setAttribute('download', file.file_name);
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
        <Layout user={props.user} title="indendkorea admin console" nav_id={props.response.service_type == 'C' ? 64 : 119} crumbs={['신청상세']}>
            <div className="mt-10 border rounded-md bg-white">
                <div className="border-b p-4 flex gap-4 justify-between">
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
                </div>
                <div className="p-5">
                    <table className="form-table table table-bordered align-middle w-full border-t-2 border-black">
                        <tbody className="border-t border-black">
                            <tr className="border-b">
                                <th scope="row">서비스명</th>
                                <td className="" colSpan={3}>
                                    {posts.title}
                                </td>
                            </tr>
                            <tr className="border-b">
                                <th scope="row">카테고리</th>
                                <td className="" colSpan={3}>
                                    {posts.category}
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            <div className="mt-4 border rounded-md bg-white">
                <div className="border-b p-4 flex gap-4 justify-between">
                    <div className="text-lg">신청 기업 정보</div>
                </div>
                <div className="p-5">
                    <table className="form-table table table-bordered align-middle w-full border-t-2 border-black">
                        <tbody className="border-t border-black">
                            <tr className="border-b">
                                <th scope="row">회사명</th>
                                <td className="" colSpan={3}>
                                    {posts.apply_company}
                                </td>
                            </tr>
                            <tr className="border-b">
                                <th scope="row">담당자명</th>
                                <td className="" colSpan={3}>
                                    {posts.apply_name}
                                </td>
                            </tr>
                            <tr className="border-b">
                                <th scope="row">부서</th>
                                <td className="">{posts.apply_depart}</td>
                                <th scope="row">직책</th>
                                <td className="">{posts.apply_position}</td>
                            </tr>
                            <tr className="border-b">
                                <th scope="row">연락처</th>
                                <td className="">{posts.apply_phone}</td>
                                <th scope="row">이메일</th>
                                <td className="">{posts.apply_email}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            {posts.info_list?.length > 0 && (
                <div className="mt-5 border rounded-md bg-white">
                    <div className="border-b p-4 flex gap-4 justify-between">
                        <div className="text-lg">신청 정보 작성</div>
                    </div>
                    <div className="p-5">
                        <table className="form-table table table-bordered align-middle w-full border-t-2 border-black">
                            <tbody className="border-t border-black">
                                {posts.info_list?.map((v: any, i: number) => (
                                    <tr key={i} className="border-b">
                                        <th scope="row" className={cls(`${v.option_yn == 'Y'} !w-[20%]`)}>
                                            {v.option_title}
                                        </th>
                                        <td className="" colSpan={3}>
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
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </Layout>
    );
};
export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {
        uid: ctx.query.uid,
    };
    var response: any = {};
    try {
        const { data } = await api.post(`/be/manager/b2b/order/read`, request);
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

export default ServiceApplyDetail;
