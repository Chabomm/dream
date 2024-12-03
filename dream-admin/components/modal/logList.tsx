import React, { useEffect, useState } from 'react';
import api from '@/libs/axios';
import { useRouter } from 'next/router';
import ListPagenation from '../bbs/ListPagenation';

import { ListTable, ListTableHead, ListTableBody } from '@/components/UIcomponent/table/ListTableA';

import { AModal, AModalHeader, AModalBody, AModalFooter } from '@/components/UIcomponent/modal/ModalA';

interface ModalProps {
    setLogListOpen?: any;
    logListInfo?: any;
}
export default function LogList({ setLogListOpen, logListInfo }: ModalProps) {
    const router = useRouter();
    const [params, setParams] = useState<any>({});
    const [posts, setPosts] = useState<any>([]);

    useEffect(() => {
        setParams(logListInfo);
        getPostsData(logListInfo);
    }, []);

    const getPagePost = async p => {
        await getPostsData(p);
    };

    const getPostsData = async (p: any) => {
        try {
            const { data } = await api.post(`/be/admin/setup/log/list`, p);
            setParams((param: any) => {
                param.page = data.page;
                param.page_size = data.page_size;
                param.page_view_size = data.page_view_size;
                param.page_total = data.page_total;
                param.page_last = data.page_last;
                param.table_name = data.table_name;
                param.table_uid = data.table_uid;
                return param;
            });
            setPosts(data);
        } catch (e: any) {}
    };

    const closeModal = () => {
        setLogListOpen(false);
    };

    return (
        <AModal onclick={closeModal} width={'800px'}>
            <AModalHeader onclick={closeModal}>수정이력확인</AModalHeader>
            <AModalBody>
                <ListTable className="px-3">
                    <ListTableHead className="!top-0">
                        <th>내용</th>
                        <th>전</th>
                        <th>후</th>
                        <th>등록자</th>
                    </ListTableHead>
                    <ListTableBody>
                        {posts.list?.map((v: any, i: number) => (
                            <tr key={`list-table-${i}`}>
                                <td className="">{v.column_name}</td>
                                <td className="!justify-start">{v.cl_before}</td>
                                <td className="break-all ">{v.cl_after}</td>
                                <td className="break-all ">{v.create_user}</td>
                            </tr>
                        ))}
                    </ListTableBody>
                </ListTable>
            </AModalBody>
            <AModalFooter>
                <ListPagenation props={params} getPagePost={getPagePost} />
            </AModalFooter>
        </AModal>
    );
}
