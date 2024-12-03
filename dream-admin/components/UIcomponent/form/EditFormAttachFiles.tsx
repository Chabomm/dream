import Attrs from '@/components/form/attrs';
import api from '@/libs/axios';
import { cls } from '@/libs/utils';
import { useState } from 'react';
import EditformFileUploading from './EditFormFileUploading';
import ButtonGray from '../ButtonGray';

/*
    last update : 2024-01-02
    필수 : 
*/

export default function EditFormAttachFiles(props: any) {
    const { files_of_values, errors, name, values, set_values, upload_option }: any = props;
    const { attrs } = Attrs();
    const [loading, setLoading] = useState<boolean>(false);

    const fnStartUploading = () => {
        setLoading(true);
    };

    const fnEndUploading = () => {
        setLoading(false);
    };

    const deleteFile = idx => {
        const copy = { ...values };
        let temp_files: any = [];
        for (var i = 0; i < copy.files.length; i++) {
            if (i != idx) {
                temp_files.push(copy.files[i]);
            }
        }
        copy.files = temp_files;
        set_values(copy);
    };

    const downloadFile = async idx => {
        try {
            await api({
                url: `/be/files/attach/download/${files_of_values[idx].attach_uid}`,
                method: 'GET',
                responseType: 'blob',
            }).then(response => {
                var fileURL = window.URL.createObjectURL(new Blob([response.data]));
                var fileLink = document.createElement('a');
                fileLink.href = fileURL;
                fileLink.setAttribute('download', files_of_values[idx].fake_name);
                document.body.appendChild(fileLink);
                fileLink.click();
            });
        } catch (e: any) {}
    };

    const handleFilesAttachUpload = async (e: React.ChangeEvent<HTMLInputElement>, index: number, options: any) => {
        fnStartUploading();
        try {
            let files: any = e.target.files;
            // let copy = { ...s.values };
            for (var i = 0; i < files.length; i++) {
                var file = files[i];

                // 1. 확장자 체크
                var ext = file.name.split('.').pop().toLowerCase();

                if (options.file_type === undefined || options.file_type == '' || options.file_type == 'img') {
                    if (['jpeg', 'jpg', 'svg', 'png', 'gif'].indexOf(ext) == -1) {
                        alert(ext + '파일은 업로드 하실 수 없습니다.');
                        continue;
                    }
                } else if (options.file_type == 'all') {
                    if (['jpeg', 'jpg', 'svg', 'png', 'gif', 'pdf', 'csv', 'zip', 'xlsx', 'xls', 'docx', 'doc', 'pptx', 'ppt', 'hwp'].indexOf(ext) == -1) {
                        alert(ext + '파일은 업로드 하실 수 없습니다.');
                        continue;
                    }
                }

                const formData = new FormData();
                formData.append('file_object', file);
                formData.append('upload_path', options.upload_path);
                formData.append('table_uid', options.table_uid);
                formData.append('table_name', options.table_name);
                const { data } = await api.post(`/be/files/attach/upload`, formData, { headers: { 'Content-Type': 'multipart/form-data' } });

                files_of_values?.push({
                    attach_uid: data.file_uid,
                    table_uid: options.table_uid,
                    table_name: options.table_name,
                    fake_name: data.fake_name,
                    upload_path: data.file_url,
                });
            }

            const copy = { ...values };
            copy.files = files_of_values;
            set_values(copy);

            // 초기값 제거
            // let temp_files: any = [];
            // for (var i = 0; i < copy.files.length; i++) {
            //     if (copy.files[i].uid != -1) {
            //         temp_files.push(copy.files[i]);
            //     }
            // }
            // copy.files = temp_files;

            // s.setValues(copy);
            e.target.value = '';
        } catch (e) {
            console.log(e);
            fnEndUploading();
        }

        fnEndUploading();
    };

    const trigger_file_input = () => {
        (document.getElementById(name) as HTMLElement)?.click();
    };

    return (
        <div className="flex flex-col">
            {loading && <EditformFileUploading />}
            <div className="flex items-center leading-none">
                <ButtonGray onClick={trigger_file_input}>
                    <i className="fas fa-file-upload me-2"></i>파일추가
                </ButtonGray>
            </div>
            <input
                type="file"
                id={name}
                name={name}
                multiple
                className="hidden"
                onChange={e => {
                    handleFilesAttachUpload(e, 0, upload_option);
                }}
            />

            {files_of_values?.map((v, i) => (
                <div className="mt-3">
                    <div className="flex items-center leading-none">
                        <div className="font-semibold text-blue-500 me-3">첨부파일 #{i + 1}</div>
                        <div className="font-semibold text-slate-600 me-3">
                            <div
                                className="cursor-pointer underline"
                                onClick={() => {
                                    downloadFile(i);
                                }}
                            >
                                {v.fake_name}
                            </div>
                        </div>
                        <div
                            className="font-semibold text-red-500 cursor-pointer underline"
                            onClick={() => {
                                deleteFile(i);
                            }}
                        >
                            [삭제]
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );
}
//
