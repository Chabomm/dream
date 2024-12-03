import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';

const BackendLogList: NextPage = (props: any) => {
    const router = useRouter();
    const [posts, setPosts] = useState(props.response.list);
    const [open, setOpen] = useState<boolean>(false);
    const [folderName, setFolderName] = useState<string>();
    const [fileList, setFileList] = useState<any>();

    const openFileList = async (path: string, folder_name: string) => {
        try {
            setFolderName(folder_name);
            posts.map((v: any, i: number) => {
                if (path == v.path) {
                    v.open = !v.open;
                    setOpen(v.open);
                } else {
                    v.open = false;
                }
            });
            const { data } = await api.post(`/be/admin/setup/log/backend/files`, { folder_name: path });
            setFileList(data);
        } catch (e: any) {}
    };

    const openFile = async (file_name: string) => {
        window.open(
            `/setup/backend/popup?folder_name=${folderName}&file_name=${file_name}`,
            '파일정보',
            'width=1120,height=800,location=no,status=no,scrollbars=yes,left=400%,top=50%'
        );
    };
    return (
        <Layout user={props.user} title="indendkorea admin console" nav_id={99} crumbs={['환경설정', '백앤드로그']}>
            <div className="grid grid-cols-12 transition duration-300 ease-in-out gap-5">
                <div className="col-span-6">
                    <div className="text-3xl my-5">Folder List</div>
                    <div className="border bg-white divide-y">
                        {posts.map((v: any, i: number) => (
                            <div key={i} className="p-2 hover:bg-gray-100 cursor-pointer w-full h-full" onClick={() => openFileList(v.path, v.folder)}>
                                <div className="px-3">
                                    {v.open ? <i className="far fa-folder-open me-2"></i> : <i className="far fa-folder me-2"></i>}
                                    {v.folder}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
                <div className="col-span-6">
                    {open ? (
                        <>
                            <div className="text-3xl my-5">File List</div>
                            <div className="border bg-white divide-y">
                                {fileList?.list?.map((v: any, i: number) => (
                                    <div key={i} className="p-2 hover:bg-gray-100 cursor-pointer w-full h-full" onClick={() => openFile(v.name)}>
                                        <div className="px-3">
                                            <i className="far fa-file me-2"></i>
                                            {v.name}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </>
                    ) : null}
                </div>
            </div>
        </Layout>
    );
};
export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {};
    var response: any = {};
    try {
        const { data } = await api.post(`/be/admin/setup/log/backend/log`);
        response = data;
    } catch (e: any) {
        if (typeof e.redirect !== 'undefined') {
            return { redirect: e.redirect };
        }
    }
    return {
        props: { response },
    };
};

export default BackendLogList;
