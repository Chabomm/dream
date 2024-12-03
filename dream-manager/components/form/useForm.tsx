import { api, setContext } from '@/libs/axios';
import React, { useEffect, useState } from 'react';
import validate from '@/components/form/validate';
import { checkNumeric } from '@/libs/utils';

interface Props {
    initialValues?: any;
    onSubmit?: any;
    onCounts?: any;
}

function useForm({ initialValues, onSubmit, onCounts }: Props) {
    const [values, setValues] = useState(initialValues);
    const [errors, setErrors] = useState({});
    const [submitting, setSubmitting] = useState(false);
    const [counts, setCounts] = useState(onCounts);

    useEffect(() => {
        if (submitting) {
            waitingForfetch();
        }
    }, [errors]);

    async function waitingForfetch() {
        if (Object.keys(errors).length === 0) {
            await onSubmit();
        }
        setSubmitting(false);
    }

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>, options: any) => {
        if (typeof options.start !== 'undefined') {
            options.start();
        }

        try {
            const { name } = e.target;
            let file: any = null;
            if (e.target.files !== null) {
                file = e.target.files[0];
            }

            // 1. 확장자 체크
            var ext = file.name.split('.').pop().toLowerCase();

            if (options.file_type === undefined || options.file_type == '' || options.file_type == 'img') {
                if (['jpeg', 'jpg', 'svg', 'png', 'gif'].indexOf(ext) == -1) {
                    alert(ext + '파일은 업로드 하실 수 없습니다.');
                    e.target.value = '';
                    return false;
                }
            } else if (options.file_type == 'all') {
                if (['jpeg', 'jpg', 'svg', 'png', 'gif', 'pdf', 'csv', 'zip', 'xlsx', 'xls', 'docx', 'doc', 'pptx', 'ppt', 'hwp'].indexOf(ext) == -1) {
                    alert(ext + '파일은 업로드 하실 수 없습니다.');
                    e.target.value = '';
                    return false;
                }
            }

            const formData = new FormData();
            formData.append('file_object', file);
            formData.append('upload_path', options.upload_path);

            const res = await api.post(`/be/files/upload`, formData, { headers: { 'Content-Type': 'multipart/form-data' } });
            const result = res.data;
            const input_name = (name + '').replace('-file', '');

            const copy = { ...values };
            copy[input_name] = result.file_url;
            copy[input_name + '_fakename'] = result.fake_name;
            setValues(copy);

            e.target.value = '';
        } catch (e) {
            if (typeof options.start !== 'undefined') {
                options.end();
            }
        }

        if (typeof options.start !== 'undefined') {
            options.end();
        }
    };

    const handleBoardFileUpload = async (e: React.ChangeEvent<HTMLInputElement>, index: number, options: any) => {
        if (typeof options.start !== 'undefined') {
            options.start();
        }

        try {
            let files: any = e.target.files;
            let copy = { ...s.values };
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
                const res = await api.post(`/be/files/upload`, formData, { headers: { 'Content-Type': 'multipart/form-data' } });
                const result = res.data;

                if (i == 0) {
                    if (copy.files[index].uid == -1) {
                        copy.files[index].uid = 0;
                    }
                    copy.files[index].fake_name = result.fake_name;
                    copy.files[index].file_url = result.file_url;
                } else {
                    copy.files.push({
                        uid: 0,
                        board_uid: 0,
                        posts_uid: 0,
                        fake_name: result.fake_name,
                        file_url: result.file_url,
                    });
                }
            }

            // 초기값 제거
            let temp_files: any = [];
            for (var i = 0; i < copy.files.length; i++) {
                if (copy.files[i].uid != -1) {
                    temp_files.push(copy.files[i]);
                }
            }
            copy.files = temp_files;

            s.setValues(copy);
            e.target.value = '';
        } catch (e) {
            if (typeof options.start !== 'undefined') {
                options.end();
            }
        }

        if (typeof options.start !== 'undefined') {
            options.end();
        }
    };

    const handleSubmit = async (e: React.FormEvent<HTMLElement>) => {
        setSubmitting(true);
        e.preventDefault();
        await new Promise(r => setTimeout(r, 500));
        setErrors(validate(values));
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value, checked } = e.target;
        const count = e.target.value.length;
        let trans_value = value;
        if (e.target.getAttribute('is_mobile')) {
            trans_value = value
                .replace(/[^0-9]/g, '')
                .replace(/(^02|^0505|^1[0-9]{3}|^0[0-9]{2})([0-9]+)?([0-9]{4})$/, '$1-$2-$3')
                .replace('--', '-');
        }

        if (e.target.getAttribute('is_bizno')) {
            trans_value = value
                .replace(/[^0-9]/g, '')
                .replace(/(\d{3})(\d{2})(\d{5})/, '$1-$2-$3')
                .replace('--', '-');
        }
        setValues({ ...values, [name]: trans_value });
        setCounts({ ...counts, [name]: count });
    };

    const handleTextAreaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        const count = e.target.value.length;
        setValues({ ...values, [name]: value });
        setCounts({ ...counts, [name]: count });
    };

    const handleImage = async (e: React.ChangeEvent<HTMLInputElement>, upload_path: string) => {
        const { name, value } = e.target;
        let file: any = null;
        if (e.target.files !== null) {
            file = e.target.files[0];
        }

        const formData = new FormData();
        formData.append('file_object', file);
        formData.append('upload_path', upload_path);

        const res = await api.post(`/be/aws/upload`, formData, { headers: { 'Content-Type': 'multipart/form-data' } });
        const result = res.data;
        const input_name = (name + '').replace('-file', '');
        setValues({ ...values, [input_name]: result.s3_url });

        e.target.value = '';
    };

    const handleChangeDateRange = async (newValue: any, element: HTMLInputElement) => {
        var name = element.getAttribute('name') + '';
        setValues({ ...values, [name]: newValue });
    };

    const handleChangeDate = async (newValue: any, element: HTMLInputElement) => {
        var name = element.getAttribute('name') + '';
        setValues({ ...values, [name]: newValue.startDate });
    };

    const handleChangeEditor = ref => {
        // console.log('ref.current', ref.current?.props.name, ref.name, ref);
        const name = ref.name;
        const data = ref.current?.getInstance().getHTML();
        setValues({ ...values, [name]: data });
    };

    const handleUploadImageEditor = async (blob, callback) => {
        const formData = new FormData();
        formData.append('file_object', blob);
        formData.append('upload_path', '/editor/' + dateformat());
        const getData = api.post(`/be/aws/upload`, formData, { headers: { 'Content-Type': 'multipart/form-data' } });
        const result = (await getData).data;
        callback(result.s3_url, 'w-full');
    };

    const handleCheckboxGroup = e => {
        var name = e.target.getAttribute('name') + '';
        if (e.target.checked) {
            setValues({ ...values, [name]: [...values[name], e.target.value] });
        } else {
            setValues({ ...values, [name]: s.values[name].filter(key => key !== e.target.value) });
        }
    };

    const handleCheckboxGroupForInteger = e => {
        var name = e.target.getAttribute('name') + '';
        if (e.target.checked) {
            setValues({ ...values, [name]: [...values[name], checkNumeric(e.target.value)] });
        } else {
            setValues({ ...values, [name]: s.values[name].filter(key => checkNumeric(key) !== checkNumeric(e.target.value)) });
        }
    };

    const fn: any = {};
    fn.handleChange = handleChange;
    fn.handleImage = handleImage;
    fn.handleSubmit = handleSubmit;
    fn.handleChangeEditor = handleChangeEditor;
    fn.handleUploadImageEditor = handleUploadImageEditor;
    fn.handleChangeDateRange = handleChangeDateRange;
    fn.handleChangeDate = handleChangeDate;
    fn.handleTextAreaChange = handleTextAreaChange;
    fn.handleCheckboxGroup = handleCheckboxGroup;
    fn.handleCheckboxGroupForInteger = handleCheckboxGroupForInteger;
    fn.handleFileUpload = handleFileUpload;
    fn.handleBoardFileUpload = handleBoardFileUpload;

    const s: any = {};
    s.values = values;
    s.setValues = setValues;
    s.errors = errors;
    s.setErrors = setErrors;
    s.submitting = submitting;
    s.setSubmitting = setSubmitting;
    s.counts = counts;
    s.setCounts = setCounts;

    const attrs: any = {};
    attrs.is_mand = { is_mand: 'true' };
    attrs.is_mobile = { is_mobile: 'true' };
    attrs.is_email = { is_email: 'true' };
    attrs.is_bizno = { is_bizno: 'true' };

    const dateformat = () => {
        let date, month, year;
        date = new Date().getDate();
        month = new Date().getMonth() + 1;
        year = new Date().getFullYear();
        date = date.toString().padStart(2, '0');
        month = month.toString().padStart(2, '0');
        return `${year}${month}${date}`;
    };

    return { s, fn, attrs };
}

export default useForm;
