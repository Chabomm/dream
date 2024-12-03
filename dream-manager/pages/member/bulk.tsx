import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect, useRef } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import useForm from '@/components/form/useForm';
import Layout from '@/components/Layout';

import {
    EditForm,
    EditFormTable,
    EditFormTH,
    EditFormTD,
    EditFormKeyword,
    EditFormDateRange,
    EditFormSubmitSearch,
    EditFormCheckboxList,
    EditFormSelect,
} from '@/components/UIcomponent/form/EditFormA';
import { ListTable, ListTableHead, ListTableBody, ListTableCaption, Callout } from '@/components/UIcomponent/table/ListTableA';
import ListPagenation from '@/components/bbs/ListPagenation';
import { cls, left, yyyymmdd_hhmmss } from '@/libs/utils';
import ExcelModal from '@/components/modal/excel';
import BulkExcelModal from '@/components/modal/bulk_excel';

const MemberList: NextPage = (props: any) => {
    const nav_id = 141;
    const crumbs = ['임직원 관리', '임직원 대량등록'];
    const title_sub = '임직원을 대량 등록 할 수 있습니다.';
    const callout = [
        '다운받은 샘플엑셀파일에서 *는 필수항목 입니다.',
        '휴대전화번호는 하이픈(-)을 포함하여 입력해주세요',
        '재직여부는 재직, 휴직, 퇴직 중 한개를 한글로 입력해주세요',
        '성별은 여자, 남자 중 한개를 한글로 입력해주세요',
        '날짜포맷은 yyyy-mm-dd 형태로 입력해주세요',
    ];
    const router = useRouter();
    const [posts, setPosts] = useState<any>({});

    const [bulkExcelModalOpen, setBulkExcelModalOpen] = useState<boolean>(false);

    const start_bulk_save = async () => {
        if (posts.length == 0) {
            alert('엑셀파일을 업로드해 주세요');
            return;
        }
        setBulkExcelModalOpen(true);
    };

    const fileInput = useRef<any>();
    const fnExcelUpload = () => {
        fileInput.current.click();
    };

    const fnSampleExcelDown = async () => {
        fnStartUploading();
        try {
            await api({
                url: '/be/manager/member/excel/sample/download',
                method: 'POST',
                responseType: 'blob',
            }).then(response => {
                var fileURL = window.URL.createObjectURL(new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }));
                var fileLink = document.createElement('a');
                fileLink.href = fileURL;
                fileLink.setAttribute('download', yyyymmdd_hhmmss() + '_임직원_대량등록_샘플.xlsx');
                document.body.appendChild(fileLink);
                fileLink.click();
            });
        } catch (e: any) {
            fnEndUploading();
        }
        fnEndUploading();
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
            const { data } = await api.post(`/be/manager/member/excel/files/upload`, formData, { headers: { 'Content-Type': 'multipart/form-data' } });
            if (data.code != 200) {
                alert(data.msg);
            }

            for (var i = 0; i < data.upload_excel.length; i++) {
                let d, year, date, month;
                try {
                    if (data.upload_excel[i]['생년월일'] != '' && data.upload_excel[i]['생년월일'] != null) {
                        d = new Date(data.upload_excel[i]['생년월일']);
                        year = d.getFullYear();
                        date = d.getDate().toString().padStart(2, '0');
                        month = (d.getMonth() + 1).toString().padStart(2, '0');
                        data.upload_excel[i]['생년월일'] = `${year}-${month}-${date}`;
                        if (left(data.upload_excel[i]['생년월일'], 3) == 'NaN') {
                            data.upload_excel[i]['생년월일'] = '';
                        }
                    }
                } catch (e) {
                    data.upload_excel[i]['생년월일'] = '';
                }

                try {
                    if (data.upload_excel[i]['입사일'] != '' && data.upload_excel[i]['입사일'] != null) {
                        d = new Date(data.upload_excel[i]['입사일']);
                        year = d.getFullYear();
                        date = d.getDate().toString().padStart(2, '0');
                        month = (d.getMonth() + 1).toString().padStart(2, '0');
                        data.upload_excel[i]['입사일'] = `${year}-${month}-${date}`;
                        if (left(data.upload_excel[i]['입사일'], 3) == 'NaN') {
                            data.upload_excel[i]['입사일'] = '';
                        }
                    }
                } catch (e) {
                    data.upload_excel[i]['입사일'] = '';
                }

                try {
                    if (data.upload_excel[i]['기념일'] != '' && data.upload_excel[i]['기념일'] != null) {
                        d = new Date(data.upload_excel[i]['기념일']);
                        year = d.getFullYear();
                        date = d.getDate().toString().padStart(2, '0');
                        month = (d.getMonth() + 1).toString().padStart(2, '0');
                        data.upload_excel[i]['기념일'] = `${year}-${month}-${date}`;
                        if (left(data.upload_excel[i]['기념일'], 3) == 'NaN') {
                            data.upload_excel[i]['기념일'] = '';
                        }
                    }
                } catch (e) {
                    data.upload_excel[i]['기념일'] = '';
                }
            }

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

    const [failList, setFailList] = useState<any>();
    const failListVaild = (data: any) => {
        setFailList(data);
    };

    const [excelModalOpen, setExcelModalOpen] = useState<boolean>(false);
    const fnFailListDownload = async () => {
        setExcelModalOpen(true);
    };

    const [loading, setLoading] = useState<boolean>(false);
    const fnStartUploading = () => {
        setLoading(true);
    };

    const fnEndUploading = () => {
        setLoading(false);
    };

    return (
        <>
            <Layout nav_id={nav_id} crumbs={crumbs} title={crumbs[crumbs.length - 1]} user={props.user}>
                <Callout title={crumbs[crumbs.length - 1]} title_sub={title_sub} callout={callout} />
                {loading && (
                    <div className="fixed w-full h-screen bg-opacity-25 bg-white z-10 flex items-center justify-center">
                        <div className="text-lg bg-white px-5 py-3 border rounded">
                            <i className="fas fa-spinner me-2"></i>파일 업로드 중 ...
                        </div>
                    </div>
                )}
                <EditForm className="mb-10">
                    <EditFormTable className="grid-cols-6">
                        <EditFormTH className="col-span-1">샘플 양식 다운로드</EditFormTH>
                        <EditFormTD className="col-span-5">
                            <div className=" text-green-600 underline cursor-pointer" onClick={() => fnSampleExcelDown()}>
                                샘플엑셀파일 다운로드 <i className="fas fa-file-download ms-2"></i>
                            </div>
                        </EditFormTD>
                        <EditFormTH className="col-span-1">엑셀파일 업로드</EditFormTH>
                        <EditFormTD className="col-span-5">
                            <div className="border py-1 px-3 border-green-600 rounded cursor-pointer" onClick={() => fnExcelUpload()}>
                                <button className="text-green-600" type="button">
                                    엑셀 업로드
                                    <i className="fas fa-file-upload ms-1"></i>
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
                            </div>
                        </EditFormTD>
                    </EditFormTable>
                </EditForm>

                {posts?.upload_excel?.length > 0 ? (
                    <div>
                        {posts.code == 200 && (
                            <div className="mb-4">
                                <button className="w-full border border-blue-500 text-blue-500 py-1 rounded" type="button" onClick={start_bulk_save}>
                                    대량등록 시작하기
                                </button>
                            </div>
                        )}

                        {failList?.length > 0 && (
                            <div className="mb-4">
                                <button className="w-full border border-green-600 text-green-600 text-2xl py-2 rounded" type="button" onClick={fnFailListDownload}>
                                    <i className="far fa-file-excel me-2"></i>
                                    <span className="text-red-500">실패항목</span> 다운로드
                                </button>
                            </div>
                        )}

                        <div>
                            <div className="mb-2 text-red-500 text-sm">엑셀 헤더 (컬럼) / 순서 주의해 주세요 / 별표시(*)는 필수값 입니다.</div>
                            <ListTable>
                                <ListTableHead>
                                    <th>검증</th>
                                    <th>아이디</th>
                                    <th>이름</th>
                                    <th>성별</th>
                                    <th>재직여부</th>
                                    <th>복지몰 로그인</th>
                                    <th>포인트사용</th>
                                    <th>휴대전화</th>
                                    <th>이메일</th>
                                    <th>우편번호</th>
                                    <th>주소</th>
                                    <th>주소상세</th>
                                    <th>생년월일</th>
                                    <th>기념일</th>
                                    <th>사번</th>
                                    <th>부서</th>
                                    <th>직급</th>
                                    <th>직책</th>
                                    <th>입사일</th>
                                </ListTableHead>
                                <ListTableBody>
                                    {posts?.upload_excel?.map((v: any, i: number) => (
                                        <tr key={i} className="">
                                            <td className="text-center">{getVaildTxt(v.검증)}</td>
                                            <td className="text-center">{v.아이디}</td>
                                            <td className="text-center">{v.이름}</td>
                                            <td className="text-center">{v.성별}</td>
                                            <td className="text-center">{v.재직여부}</td>
                                            <td className="text-center">{v.복지몰}</td>
                                            <td className="text-center">{v.포인트사용}</td>
                                            <td className="text-center">{v.휴대전화}</td>
                                            <td className="text-center">{v.이메일}</td>
                                            <td className="text-center">{v.우편번호}</td>
                                            <td className="text-center">{v.주소}</td>
                                            <td className="text-center">{v.주소상세}</td>
                                            <td className="text-center">{v.생년월일}</td>
                                            <td className="text-center">{v.기념일}</td>
                                            <td className="text-center">{v.사번}</td>
                                            <td className="text-center">{v.부서}</td>
                                            <td className="text-center">{v.직급}</td>
                                            <td className="text-center">{v.직책}</td>
                                            <td className="text-center">{v.입사일}</td>
                                        </tr>
                                    ))}
                                </ListTableBody>
                            </ListTable>
                        </div>
                    </div>
                ) : null}
            </Layout>
            {bulkExcelModalOpen && (
                <BulkExcelModal
                    setBulkExcelModalOpen={setBulkExcelModalOpen}
                    posts={posts}
                    failListVaild={failListVaild}
                    fnFailListDownload={fnFailListDownload}
                    setData={{ url: '/be/manager/member/excel/upload/create', gubun: 'member' }}
                />
            )}

            {excelModalOpen && (
                <ExcelModal setExcelModalOpen={setExcelModalOpen} url={'/be/manager/member/excel/bulk/fail'} title={'임직원_대량등록_실패_항목'} failList={failList} />
            )}
        </>
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

export default MemberList;
