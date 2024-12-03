import React, { useEffect, useState } from 'react';
import api from '@/libs/axios';

import { AModal, AModalHeader, AModalBody, AModalFooter } from '@/components/UIcomponent/modal/ModalA';
import { ListTable, ListTableHead, ListTableBody } from '@/components/UIcomponent/table/ListTableA';

interface ModalProps {
    setBulkExcelModalOpen?: any;
    posts?: any;
    failListVaild?: any;
    fnFailListDownload?: any;
    setData?: any;
    setBulkButton?: any;
}
export default function BulkExcelModal({ setBulkExcelModalOpen, posts, failListVaild, fnFailListDownload, setData, setBulkButton }: ModalProps) {
    const closeModal = () => {
        setBulkExcelModalOpen(false);
    };

    const [fail, setFail] = useState<number>(0);
    const [success, setSuccess] = useState<number>(0);
    useEffect(() => {
        fnUploadExcel();
    }, []);

    const [failList, setFailList] = useState<any>([]);
    let fail_data = 0;
    let success_data = 0;
    const fnUploadExcel = async () => {
        for (var i = 0; i < posts.upload_excel.length; i++) {
            try {
                const { data } = await api.post(setData.url, { post: posts.upload_excel[i], fail: fail_data, success: success_data, gubun: setData.gubun });

                posts.upload_excel[i].검증 = data.msg;

                fail_data = data.fail;
                success_data = data.success;

                setFail(data.fail);
                setSuccess(data.success);
                if (posts.upload_excel.length == success_data) {
                    setBulkButton(true);
                }
                if (data.fail >= 1 && data.fail_list.length != 0) {
                    failList.push(data.fail_list);
                }
            } catch (e) {
                console.log(e);
            }
        }
        if (failList.length > 0) {
            alert('오류가 발생한 내역이 있습니다. 결과를 확인해주세요.');
            failListVaild(failList);
        }
    };

    return (
        <AModal width_style={'36rem'}>
            {/* onclick={closeModal}  */}
            <AModalHeader onclick={closeModal}>엑셀 다운로드</AModalHeader>
            <AModalBody className={'!overflow-clip p-5'}>
                <ListTable>
                    <ListTableHead>
                        <th>총 합계</th>
                        <th>성공 수</th>
                        <th>실패 수</th>
                    </ListTableHead>
                    <ListTableBody>
                        <tr className="">
                            <td className="text-center">{posts.upload_excel.length}</td>
                            <td className="text-center text-blue-500">{success}</td>
                            <td className="text-center text-red-500">{fail}</td>
                        </tr>
                    </ListTableBody>
                </ListTable>
                {failList.length > 0 && (
                    <>
                        <div className="mb-2 text-red-500 text-sm mt-3 font-bold">오류가 발생한 내역이 있습니다. 결과를 확인해주세요.</div>
                        <div className="mb-4">
                            <button
                                className="w-full border border-green-600 text-green-600 text-2xl py-2 rounded"
                                type="button"
                                onClick={() => {
                                    fnFailListDownload(), setBulkExcelModalOpen(false);
                                }}
                            >
                                <i className="far fa-file-excel me-2"></i>
                                <span className="text-red-500">실패항목</span> 다운로드
                            </button>
                        </div>
                    </>
                )}
                {posts.upload_excel.length == success && (
                    <div className="m-4">
                        <button className="w-full border border-blue-600 text-blue-600 text-2xl py-2 rounded" type="button" onClick={() => setBulkExcelModalOpen(false)}>
                            <i className="fas fa-redo me-2"></i>
                            성공목록 확인하기
                        </button>
                    </div>
                )}
            </AModalBody>
            <AModalFooter></AModalFooter>
        </AModal>
    );
}
