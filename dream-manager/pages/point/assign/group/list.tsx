import type { GetServerSideProps, NextPage } from 'next';
import React, { useEffect, useRef, useState } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import useForm from '@/components/form/useForm';
import { cls, left, num2Cur, yyyymmdd_hhmmss } from '@/libs/utils';
import { EditForm, EditFormCard, EditFormCardBody, EditFormTD, EditFormTH, EditFormTable } from '@/components/UIcomponent/form/EditFormA';
import { Callout, ListTable, ListTableBody, ListTableHead } from '@/components/UIcomponent/table/ListTableA';
import Layout from '@/components/Layout';
import PointStatus from '../../status';
import ExcelModal from '@/components/modal/excel';
import BulkExcelModal from '@/components/modal/bulk_excel';

const PointAssignGroupList: NextPage = (props: any) => {
    const nav_id = 58;
    const router = useRouter();
    const crumbs = ['포인트 지급관리', '복지포인트 대량 지급'];
    const title_sub = ' 지급 사유 기준으로 복지포인트 지급 및 회수 내역을 확인하고, 포인트 대량지급을 할 수 있습니다.';
    const callout = [
        '지급 사유 기준으로 복지포인트 지급 및 회수 내역을 확인하고, 포인트 대량지급을 할 수 있습니다.',
        '샘플엑셀파일에는 등록된 임직원의 정보가 자동으로 세팅되어 다운로드됩니다.',
        '샘플엑셀파일에서 임직원을 임의로 추가하거나 수정하지 마세요.',
    ];

    const [posts, setPosts] = useState<any>({});
    const [filter, setFilter] = useState<any>({});
    const [loading, setLoading] = useState<boolean>(false);

    const { s, fn, attrs } = useForm({
        onSubmit: async () => {
            await editing();
        },
    });

    const [bulkExcelModalOpen, setBulkExcelModalOpen] = useState<boolean>(false);
    const [bulkButton, setBulkButton] = useState<boolean>(false);

    const editing = async () => {
        if (posts.length == 0) {
            alert('엑셀파일을 업로드해 주세요');
            return;
        }
        setBulkExcelModalOpen(true);
    };
    const [failList, setFailList] = useState<any>();
    const failListVaild = (data: any) => {
        setFailList(data);
    };

    const [excelModalOpen, setExcelModalOpen] = useState<boolean>(false);
    const fnFailListDownload = async () => {
        setExcelModalOpen(true);
    };

    const fnSampleExcelDown = async () => {
        fnStartUploading();

        try {
            await api({
                url: '/be/manager/point/assign/group/excel/sample/download',
                method: 'POST',
                responseType: 'blob',
            }).then(response => {
                var fileURL = window.URL.createObjectURL(new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }));
                var fileLink = document.createElement('a');
                fileLink.href = fileURL;
                fileLink.setAttribute('download', yyyymmdd_hhmmss() + '_복지포인트지급_대량등록_샘플.xlsx');
                document.body.appendChild(fileLink);
                fileLink.click();
            });
        } catch (e: any) {
            fnEndUploading();
        }

        fnEndUploading();
    };

    const fileInput = useRef<any>();
    const fnExcelUpload = () => {
        fileInput.current.click();
    };

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>, options: any) => {
        if (typeof options.start !== 'undefined') {
            options.start();
        }

        try {
            let file: any = null;
            if (e.target.files !== null) {
                file = e.target.files[0];
            }
            const formData = new FormData();
            formData.append('file_object', file);
            formData.append('upload_path', options.upload_path);
            const { data } = await api.post(`/be/manager/point/assign/group/excel/files/upload`, formData, { headers: { 'Content-Type': 'multipart/form-data' } });

            if (data.code != 200) {
                alert(data.msg);
            }

            for (var i = 0; i < data.upload_excel.length; i++) {
                let d, year, date, month;
                try {
                    if (data.upload_excel[i]['포인트소멸일'] != '' && data.upload_excel[i]['포인트소멸일'] != null) {
                        d = new Date(data.upload_excel[i]['포인트소멸일']);
                        year = d.getFullYear();
                        date = d.getDate().toString().padStart(2, '0');
                        month = (d.getMonth() + 1).toString().padStart(2, '0');
                        data.upload_excel[i]['포인트소멸일'] = `${year}-${month}-${date}`;
                        if (left(data.upload_excel[i]['포인트소멸일'], 3) == 'NaN') {
                            data.upload_excel[i]['포인트소멸일'] = '';
                        }
                    }
                } catch (e) {
                    data.upload_excel[i]['포인트소멸일'] = '';
                }
            }
            setBulkButton(false);
            setPosts(data);
        } catch (e) {
            if (typeof options.start !== 'undefined') {
                options.end();
            }
        }

        if (typeof options.start !== 'undefined') {
            options.end();
        }
    };

    function getVaildTxt(val: any) {
        if (val == '대기') {
            return <div className="text-blue-500">대기</div>;
        } else if (val == '완료' || val == '성공') {
            return <div className="text-green-500">{val}</div>;
        } else {
            return <div className="text-red-500">{val}</div>;
        }
    }

    const fnStartUploading = () => {
        setLoading(true);
    };

    const fnEndUploading = () => {
        setLoading(false);
    };

    return (
        <Layout nav_id={nav_id} crumbs={crumbs} title={crumbs[crumbs.length - 1]} user={props.user}>
            <Callout title={crumbs[crumbs.length - 1]} title_sub={title_sub} callout={callout} />

            <PointStatus point_type={'bokji'} />

            {loading && (
                <div className="fixed w-full h-screen bg-opacity-25 bg-white z-10 flex items-center justify-center">
                    <div className="text-lg bg-white px-5 py-3 border rounded">
                        <i className="fas fa-spinner me-2"></i>파일 업로드 중 ...
                    </div>
                </div>
            )}

            <EditForm onSubmit={fn.handleSubmit}>
                <EditFormCard>
                    <EditFormCardBody>
                        <EditFormTable className="grid-cols-6">
                            <EditFormTH className="col-span-1">샘플 양식 다운로드</EditFormTH>
                            <EditFormTD className="col-span-5">
                                <button type="button" className="text-green-600 border-b border-green-600" onClick={() => fnSampleExcelDown()}>
                                    샘플엑셀파일 다운로드<i className="fas fa-download ms-1"></i>
                                </button>
                            </EditFormTD>
                            <EditFormTH className="col-span-1">엑셀파일 업로드</EditFormTH>
                            <EditFormTD className="col-span-5">
                                <button type="button" className="text-green-600 rounded border border-green-600 px-2 py-1" onClick={() => fnExcelUpload()}>
                                    <i className="far fa-file-excel me-1"></i> 엑셀 업로드<i className="fas fa-upload ms-1"></i>
                                </button>
                                <input
                                    name="excel-file"
                                    type="file"
                                    ref={fileInput}
                                    className={cls('form-control hidden')}
                                    onChange={e => {
                                        handleFileUpload(e, { upload_path: '/dream/excel/', start: fnStartUploading, end: fnEndUploading });
                                    }}
                                />
                            </EditFormTD>
                        </EditFormTable>
                    </EditFormCardBody>
                </EditFormCard>
                {posts?.upload_excel?.length > 0 ? (
                    <EditFormCard>
                        <EditFormCardBody>
                            {failList?.length > 0 && (
                                <div className="mb-4">
                                    <button className="w-full border border-green-600 text-green-600 text-2xl py-2 rounded" type="button" onClick={fnFailListDownload}>
                                        <i className="far fa-file-excel me-2"></i>
                                        <span className="text-red-500">실패항목</span> 다운로드
                                    </button>
                                </div>
                            )}
                            <ListTable>
                                <ListTableHead>
                                    <th>검증</th>
                                    <th>고유번호</th>
                                    <th>아이디</th>
                                    <th>이름</th>
                                    <th>적립금액</th>
                                    <th>포인트소멸일</th>
                                    <th>지급사유</th>
                                    <th>관리자기록용</th>
                                </ListTableHead>

                                <ListTableBody>
                                    {posts?.upload_excel?.map((v: any, i: number) => (
                                        <tr key={i} className="">
                                            <td className="text-center">{getVaildTxt(v.검증)}</td>
                                            <td className="text-center">{v.고유번호}</td>
                                            <td className="text-center">{v.아이디}</td>
                                            <td className="text-center">{v.이름}</td>
                                            <td className="text-center">{num2Cur(v.적립금액)}</td>
                                            <td className="text-center">{v.포인트소멸일}</td>
                                            <td className="text-center">{v.지급사유}</td>
                                            <td className="text-center">{v.관리자기록용}</td>
                                        </tr>
                                    ))}
                                </ListTableBody>
                            </ListTable>
                            {bulkButton}
                            {posts.code == 200 && !bulkButton && (
                                <div className="w-full p-5 text-center">
                                    <button className="button-search" type="button" onClick={editing}>
                                        대량등록 시작하기
                                    </button>
                                </div>
                            )}
                        </EditFormCardBody>
                    </EditFormCard>
                ) : null}
            </EditForm>
            {/* 성공/실패 수 보여주는 팝업 */}
            {bulkExcelModalOpen && (
                <BulkExcelModal
                    setBulkExcelModalOpen={setBulkExcelModalOpen}
                    posts={posts}
                    failListVaild={failListVaild}
                    fnFailListDownload={fnFailListDownload}
                    setData={{ url: '/be/manager/point/assign/group/excel/upload/create', gubun: 'group' }}
                    setBulkButton={setBulkButton}
                />
            )}
            {/* 실패항목 다운로드 */}
            {excelModalOpen && (
                <ExcelModal
                    setExcelModalOpen={setExcelModalOpen}
                    url={'/be/manager/point/assign/group/excel/bulk/fail'}
                    title={'포인트지급_대량등록_실패_항목'}
                    failList={failList}
                />
            )}
        </Layout>
    );
};

export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {};
    var response: any = {};
    return {
        props: { request, response },
    };
};

export default PointAssignGroupList;
