import type { GetServerSideProps, NextPage } from 'next';
import React, { useEffect, useRef, useState } from 'react';
import Layout from '@/components/Layout';
import useForm from '@/components/form/useForm';
import Datepicker from 'react-tailwindcss-datepicker';
import { checkNumeric, cls, dateformatYYYYMMDD, getToken } from '@/libs/utils';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import SellerSearch from '@/components/searchBox/sellerSearch';

import dynamic from 'next/dynamic';
const CKEditor = dynamic(() => import('@/components/editor/CKEditor'), { ssr: false });

const B2BGoodsReg: NextPage = (props: any) => {
    const router = useRouter();
    const [posts, setPosts] = useState<any>({});
    const [filter, setFilter] = useState<any>({});

    // dynamic import라서 라우터 이동한 경우 객체가 남아 있어서 initdata 세팅하면 onchange가 발동되어 문제가되는걸 방지
    const [CKEditorInit, setCKEditorInit] = useState<boolean>(true);

    useEffect(() => {
        s.setValues(props.response.values);
        setPosts(props.response);
        setFilter(props.response.filter);
    }, [props]);

    const radioChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value, checked } = e.target;
        s.setValues({ ...s.values, [name]: value });
    };

    const { s, fn, attrs } = useForm({
        initialValues: {},
        onSubmit: async () => {
            await fnAccept('REG');
        },
    });

    const fnAccept = async mode => {
        if (mode == 'REG' && s.values.uid > 0) {
            mode = 'MOD';
        }
        s.values.mode = mode;

        if (s.values.thumb == '' || s.values.thumb == null) {
            alert('메인 이미지를 선택하세요');
            return;
        }
        if (s.values.etc_images.length <= 0) {
            alert('추가 이미지를 선택하세요');
            return;
        }
        if (s.values.option_list.length <= 0) {
            alert('추가항목을 1개 이상 설정하세요.');
            return;
        }
        if (s.values.seller_id == '' || typeof s.values.seller_id == 'undefined' || s.values.seller_id == null) {
            alert('업체명을 검색해주세요');
            return;
        }

        s.values.goods_option_yn = 'N';
        if (s.values.option_value != '') {
            s.values.goods_option_yn = 'Y';
        }

        if (s.values.sale_at != null) {
            s.values.start_date = s.values.sale_at.startDate;
            s.values.end_date = s.values.sale_at.endDate;
        }

        try {
            const { data } = await api.post(`/be/admin/b2b/goods/edit`, s.values);

            s.setSubmitting(false);
            if (data.code == 200) {
                if (mode == 'REG') {
                    alert(data.msg);
                    router.replace(`/b2b/goods/reg?guid=${data.uid}`);
                } else {
                    alert(data.msg);
                    router.reload();
                }
            } else {
                alert(data.msg);
            }

            return;
        } catch (e: any) {}
    };

    // [ S ] 업체명검색
    const [sellerSearchOpen, setSellerSearchOpen] = useState(false);
    const sellerSubmit = () => {
        if (s.values.seller == '' || typeof s.values.seller == 'undefined') {
            alert('검색어를 입력해주세요');
            return;
        }
        setSellerSearchOpen(true);
    };

    const getSellerUid = (uid: number, seller_id: string, seller_name: string, indend_md: string) => {
        const copy = { ...s.values };
        copy.seller_uid = uid;
        copy.seller_id = seller_id;
        copy.seller_name = seller_name;
        copy.indend_md = indend_md;
        s.setValues(copy);
    };
    // [ E ] 업체명검색

    // [ S ] images
    const ThumbInput = useRef<any>();
    const EtcImageInput = useRef<any>();
    const imageUpload = () => {
        ThumbInput.current.click();
    };
    const etcImageUpload = () => {
        EtcImageInput.current.click();
    };

    const fnDel = (param: string, index: number) => {
        const copy = { ...s.values };
        if (param == 'thumb') {
            copy[param] = '';
        } else {
            copy[param].splice(index, 1);
        }
        s.setValues(copy);
    };

    // 추가이미지리스트
    const addImageHandle = async (e: React.ChangeEvent<HTMLInputElement>, options: any) => {
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

            // const input_name = (name + '').replace('-file', '');
            // setValues({ ...values, [input_name]: data.s3_url });

            // const { data } = await api.post(`/be/files/upload`, formData, { headers: { 'Content-Type': 'multipart/form-data' } });
            const { data } = await api.post(`/be/aws/upload`, formData, { headers: { 'Content-Type': 'multipart/form-data' } });

            const copy = { ...s.values };
            const input_name = (name + '').replace('-file', '');
            copy.etc_images.push({ [input_name]: data.s3_url, [input_name + '_fakename']: data.fake_name });

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

    // [ E ] images

    const addOption = (option_title: string, option_type: string, option_yn: string, placeholder: any) => {
        const copy = { ...s.values };
        if (option_title == '' || option_title == undefined) {
            alert('항목명을 입력하세요.');
            const el = document.querySelector("[name='option_title']");
            (el as HTMLElement)?.focus();
            return;
        }
        if (option_type == '' || option_type == undefined) {
            alert('항목타입을 선택하세요.');
            return;
        }

        if (option_type == 'A' || option_type == 'B' || option_type == 'G') {
            if (placeholder == '') {
                alert('설정사항을 입력하세요.');
                const el = document.querySelector("[name='placeholder']");
                (el as HTMLElement)?.focus();
                return;
            }
        }
        // else if (option_type == 'C' || option_type == 'D') {
        //     let placeholder_list: any = [];
        //     let split_word: any = placeholder.split(',');
        //     split_word.map((v: any, i: number) => {
        //         placeholder_list.push(v);
        //     });
        //     placeholder = placeholder_list;
        // }
        copy.option_list?.push({
            uid: 0,
            option_num: copy.option_list.length + 1,
            option_title,
            option_type,
            option_yn,
            placeholder,
        });
        s.values.placeholder = '';
        s.setValues({ ...s.values, option_list: copy.option_list });
    };
    const optionDel = (index: number) => {
        const copy = { ...s.values };
        copy.option_list.splice(index, 1);
        s.setValues(copy);
    };

    const fileUpload = useRef<any>();
    const fileUploadBtn = () => {
        fileUpload.current.click();
    };

    return (
        <Layout user={props.user} title="indendkorea admin console" nav_id={112} crumbs={['기업혜택', 'B2B상품등록']}>
            <div>
                <form onSubmit={fn.handleSubmit} noValidate>
                    <div className="mb-12 bg-white p-5 border rounded">
                        <div className="text-xl font-bold mb-4">업체정보</div>
                        <table className="form-table table table-bordered align-middle w-full border-t-2 border-black">
                            <tbody className="border-t border-black">
                                <tr className="border-b">
                                    <th scope="row" className="table_must">
                                        업체명
                                    </th>
                                    <td colSpan={3} className="">
                                        <div className="flex">
                                            <input
                                                type="text"
                                                name="seller"
                                                value={s.values?.seller || ''}
                                                placeholder="업체명, 업체아이디, 담당자명 검색"
                                                onChange={fn.handleChange}
                                                className="form-control mr-3"
                                                style={{ width: '300px' }}
                                            />
                                            <button className="btn-filter col-span-2" type="button" onClick={() => sellerSubmit()}>
                                                업체 검색
                                            </button>
                                            <div className="ms-3">
                                                <input
                                                    type="text"
                                                    name="seller_id"
                                                    value={s.values?.seller_id || ''}
                                                    placeholder=""
                                                    className="form-control mr-3 !text-red-500"
                                                    style={{ width: 'auto' }}
                                                    disabled
                                                />
                                                <input
                                                    type="text"
                                                    name="seller_name"
                                                    value={s.values?.seller_name || ''}
                                                    placeholder=""
                                                    onChange={fn.handleChange}
                                                    className="form-control mr-3 !text-red-500"
                                                    style={{ width: 'auto' }}
                                                    disabled
                                                />
                                            </div>
                                        </div>
                                    </td>
                                </tr>
                                <tr className="border-b">
                                    <th scope="row" className="">
                                        상품구분
                                    </th>
                                    <td colSpan={3} className="">
                                        <ul className="grid w-full grid-cols-12 gap-3">
                                            <li className="">
                                                <input
                                                    onChange={radioChange}
                                                    type="radio"
                                                    id="service_type_C"
                                                    name="service_type"
                                                    value="C"
                                                    className="hidden peer"
                                                    required
                                                    checked={s.values?.service_type == 'C' ? true : false}
                                                />
                                                <label
                                                    htmlFor="service_type_C"
                                                    className="inline-flex items-center justify-between w-full py-1 px-2 text-center text-gray-600 bg-white border border-gray-500 rounded-lg cursor-pointer peer-checked:bg-gray-500 peer-checked:text-white"
                                                >
                                                    <div className="w-full">고객사 혜택</div>
                                                </label>
                                            </li>
                                            <li>
                                                <input
                                                    type="radio"
                                                    id="service_type_D"
                                                    name="service_type"
                                                    value="D"
                                                    checked={s.values?.service_type == 'D' ? true : false}
                                                    className="hidden peer"
                                                    onChange={radioChange}
                                                />
                                                <label
                                                    htmlFor="service_type_D"
                                                    className="inline-flex items-center justify-between w-full py-1 px-2 text-center text-gray-600 bg-white border border-gray-500 rounded-lg cursor-pointer peer-checked:bg-gray-500 peer-checked:text-white"
                                                >
                                                    <div className="w-full">드림클럽</div>
                                                </label>
                                            </li>
                                        </ul>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <div className="mb-12 bg-white p-5 border rounded">
                        <div className="text-xl font-bold mb-4">상품정보</div>
                        <table className="form-table table table-bordered align-middle w-full border-t-2 border-black">
                            <tbody className="border-t border-black">
                                <tr className="border-b">
                                    <th scope="row" className="table_must">
                                        진열순서
                                    </th>
                                    <td colSpan={3} className="">
                                        <input
                                            type="text"
                                            name="sort"
                                            {...attrs.is_mand}
                                            value={s.values?.sort || ''}
                                            placeholder="숫자만 입력 (숫자가 낮을 수록 먼저 노출됨, 동률인 경우 최신순)"
                                            onChange={fn.handleChange}
                                            className={cls(s.errors['sort'] ? 'border-danger' : '', 'form-control')}
                                        />
                                        {s.errors['sort'] && <div className="form-error">{s.errors['sort']}</div>}
                                    </td>
                                </tr>
                                <tr className="border-b">
                                    <th scope="row" className="table_must">
                                        상품진열
                                    </th>
                                    <td colSpan={3} className="">
                                        <ul className="grid w-full grid-cols-12 gap-3">
                                            <li className="">
                                                <input
                                                    type="radio"
                                                    id="is_display_T"
                                                    name="is_display"
                                                    value="T"
                                                    checked={s.values?.is_display == 'T' ? true : false}
                                                    className="hidden peer"
                                                    onChange={radioChange}
                                                    {...attrs.is_mand}
                                                />
                                                <label
                                                    htmlFor="is_display_T"
                                                    className="inline-flex items-center justify-between w-full py-1 px-2 text-center text-gray-600 bg-white border border-gray-500 rounded-lg cursor-pointer peer-checked:bg-gray-500 peer-checked:text-white"
                                                >
                                                    <div className="w-full">진열</div>
                                                </label>
                                            </li>
                                            <li>
                                                <input
                                                    type="radio"
                                                    id="is_display_F"
                                                    name="is_display"
                                                    value="F"
                                                    checked={s.values?.is_display == 'F' ? true : false}
                                                    className="hidden peer"
                                                    onChange={radioChange}
                                                    {...attrs.is_mand}
                                                />
                                                <label
                                                    htmlFor="is_display_F"
                                                    className="inline-flex items-center justify-between w-full py-1 px-2 text-center text-gray-600 bg-white border border-gray-500 rounded-lg cursor-pointer peer-checked:bg-gray-500 peer-checked:text-white"
                                                >
                                                    <div className="w-full">미진열</div>
                                                </label>
                                            </li>
                                        </ul>
                                    </td>
                                </tr>
                                <tr className="border-b">
                                    <th scope="row" className="">
                                        판매기간
                                    </th>
                                    <td colSpan={3} className="">
                                        <Datepicker
                                            inputName="sale_at"
                                            value={s.values?.sale_at}
                                            i18n={'ko'}
                                            onChange={fn.handleChangeDateRange}
                                            containerClassName="relative w-72 text-gray-700 border border-gray-300 rounded"
                                        />
                                    </td>
                                </tr>
                                <tr className="border-b">
                                    <th scope="row" className="table_must">
                                        카테고리
                                    </th>
                                    <td colSpan={3} className="">
                                        <select
                                            name="category"
                                            value={s.values?.category || ''}
                                            onChange={fn.handleChange}
                                            className={cls(s.errors['category'] ? 'border-danger' : '', 'form-select mr-3')}
                                            style={{ width: 'auto' }}
                                            {...attrs.is_mand}
                                        >
                                            {filter?.category?.map((v: any, i: number) => (
                                                <option key={i} value={v.key}>
                                                    {v.text}
                                                </option>
                                            ))}
                                        </select>
                                    </td>
                                </tr>
                                <tr className="border-b">
                                    <th scope="row" className="table_must">
                                        상품명
                                    </th>
                                    <td colSpan={3} className="">
                                        <input
                                            type="text"
                                            name="title"
                                            value={s.values?.title || ''}
                                            placeholder="상품 제목을 입력해주세요."
                                            onChange={fn.handleChange}
                                            className={cls(s.errors['title'] ? 'border-danger' : '', 'form-control')}
                                            {...attrs.is_mand}
                                        />
                                        {s.errors['title'] && <div className="form-error">{s.errors['title']}</div>}
                                    </td>
                                </tr>
                                <tr className="border-b">
                                    <th scope="row" className="">
                                        서브타이틀
                                    </th>
                                    <td className="">
                                        <input
                                            type="text"
                                            name="sub_title"
                                            value={s.values?.sub_title || ''}
                                            placeholder="상품 서브 제목을 입력해주세요."
                                            onChange={fn.handleChange}
                                            className={cls(s.errors['sub_title'] ? 'border-danger' : '', 'form-control')}
                                        />
                                    </td>
                                    <th scope="row" className="">
                                        키워드
                                    </th>
                                    <td className="">
                                        <input
                                            type="text"
                                            name="keyword"
                                            value={s.values?.keyword || ''}
                                            placeholder="콤마(,)로 구분"
                                            onChange={fn.handleChange}
                                            className={cls(s.errors['keyword'] ? 'border-danger' : '', 'form-control')}
                                        />
                                    </td>
                                </tr>
                                <tr className="border-b">
                                    <th scope="row" className="table_must">
                                        정가
                                    </th>
                                    <td className="">
                                        <input
                                            type="text"
                                            name="str_market_price"
                                            {...attrs.is_mand}
                                            value={s.values?.str_market_price || ''}
                                            placeholder="기존 판매가 입력"
                                            onChange={fn.handleChange}
                                            className={cls(s.errors['str_market_price'] ? 'border-danger' : '', 'form-control')}
                                        />
                                        {s.errors['str_market_price'] && <div className="form-error">{s.errors['str_market_price']}</div>}
                                    </td>
                                    <th scope="row" className="table_must">
                                        판매가
                                    </th>
                                    <td className="">
                                        <input
                                            type="text"
                                            name="str_price"
                                            {...attrs.is_mand}
                                            value={s.values?.str_price || ''}
                                            placeholder="복지드림 판매가 입력"
                                            onChange={fn.handleChange}
                                            className={cls(s.errors['str_price'] ? 'border-danger' : '', 'form-control')}
                                        />
                                        {s.errors['str_price'] && <div className="form-error">{s.errors['str_price']}</div>}
                                    </td>
                                </tr>
                                <tr className="border-b">
                                    <th scope="row" className="table_must">
                                        복지드림 수수료
                                    </th>
                                    <td className="">
                                        <ul className="grid w-full grid-cols-3 gap-3 mb-2">
                                            <li className="">
                                                <input
                                                    type="radio"
                                                    id="commission_type_A"
                                                    name="commission_type"
                                                    value="A"
                                                    checked={s.values?.commission_type == 'A' ? true : false}
                                                    className="hidden peer"
                                                    onChange={radioChange}
                                                    {...attrs.is_mand}
                                                />
                                                <label
                                                    htmlFor="commission_type_A"
                                                    className="inline-flex items-center justify-between w-full py-1 px-2 text-center text-gray-600 bg-white border border-gray-500 rounded-lg cursor-pointer peer-checked:bg-gray-500 peer-checked:text-white"
                                                >
                                                    <div className="w-full">A type.계약금의(%)</div>
                                                </label>
                                            </li>
                                            <li>
                                                <input
                                                    type="radio"
                                                    id="commission_type_B"
                                                    name="commission_type"
                                                    value="B"
                                                    checked={s.values?.commission_type == 'B' ? true : false}
                                                    className="hidden peer"
                                                    onChange={radioChange}
                                                    {...attrs.is_mand}
                                                />
                                                <label
                                                    htmlFor="commission_type_B"
                                                    className="inline-flex items-center justify-between w-full py-1 px-2 text-center text-gray-600 bg-white border border-gray-500 rounded-lg cursor-pointer peer-checked:bg-gray-500 peer-checked:text-white"
                                                >
                                                    <div className="w-full">B type.계약 건당(원)</div>
                                                </label>
                                            </li>
                                        </ul>

                                        <input
                                            type="text"
                                            name="commission"
                                            {...attrs.is_mand}
                                            value={s.values?.commission || ''}
                                            placeholder="숫자 입력"
                                            onChange={fn.handleChange}
                                            className={cls(s.errors['commission'] ? 'border-danger' : '', 'form-control')}
                                        />
                                        {s.errors['commission'] && <div className="form-error">{s.errors['commission']}</div>}
                                    </td>
                                    <th scope="row" className="table_must">
                                        할인율
                                    </th>
                                    <td className="">
                                        <input
                                            type="text"
                                            name="str_sale_percent"
                                            {...attrs.is_mand}
                                            value={s.values?.str_sale_percent || ''}
                                            placeholder="%는 빼고 숫자만 입력"
                                            onChange={fn.handleChange}
                                            className={cls(s.errors['str_sale_percent'] ? 'border-danger' : '', 'form-control')}
                                        />
                                        {s.errors['str_sale_percent'] && <div className="form-error">{s.errors['str_sale_percent']}</div>}
                                    </td>
                                </tr>
                                <tr className="border-b">
                                    <th scope="row" className="table_must">
                                        옵션
                                    </th>
                                    <td colSpan={3} className="">
                                        <input
                                            type="text"
                                            name="option_value"
                                            {...attrs.is_mand}
                                            value={s.values?.option_value || ''}
                                            placeholder="콤마(,)로 구분"
                                            onChange={fn.handleChange}
                                            className={cls(s.errors['option_value'] ? 'border-danger' : '', 'form-control')}
                                        />
                                        {s.errors['option_value'] && <div className="form-error">{s.errors['option_value']}</div>}
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <div className="mb-12 bg-white p-5 border rounded">
                        <div className="text-xl font-bold mb-4">상품 이미지</div>
                        <table className="form-table table table-bordered align-middle w-full border-t-2 border-black">
                            <tbody className="border-t border-black">
                                <tr className="border-b">
                                    <th scope="row" className="table_must">
                                        메인 이미지
                                    </th>
                                    <td colSpan={3} className="">
                                        <div className="btn-group">
                                            <button
                                                type="button"
                                                className="del"
                                                onClick={() => {
                                                    fnDel('thumb', 0);
                                                }}
                                            >
                                                삭제
                                            </button>
                                            <div className="imgLabel" onClick={imageUpload}>
                                                {s.values?.thumb != null && s.values?.thumb != '' && (
                                                    <img
                                                        src={s.values?.thumb}
                                                        id="thumb"
                                                        className="w-full h-full absolute top-0 left-0"
                                                        style={{ zIndex: '1' }}
                                                        alt="메인이미지"
                                                    />
                                                )}

                                                <i className="blind"></i>
                                                <input
                                                    name="thumb-file"
                                                    type="file"
                                                    className={cls(s.errors['thumb'] ? 'border-danger' : '', 'form-control hidden')}
                                                    accept="image/*"
                                                    ref={ThumbInput}
                                                    onChange={e => {
                                                        fn.handleImage(e, '/b2b/goods/thumb/' + dateformatYYYYMMDD() + '/');
                                                    }}
                                                />
                                            </div>
                                        </div>
                                    </td>
                                </tr>
                                <tr className="border-b">
                                    <th scope="row" className="table_must">
                                        추가 이미지
                                    </th>
                                    <td colSpan={3} className="">
                                        <div className="flex">
                                            <div className="btn-group">
                                                <div className="imgLabel" onClick={etcImageUpload}>
                                                    <i className="blind"></i>
                                                    <input
                                                        name="img_url-file"
                                                        type="file"
                                                        className={cls(s.errors['etc_image'] ? 'border-danger' : '', 'form-control hidden')}
                                                        accept="image/*"
                                                        ref={EtcImageInput}
                                                        onChange={e => {
                                                            // fn.handleImage(e, '/b2b/goods/thumb/' + dateformatYYYYMMDD() + '/');
                                                            addImageHandle(e, { upload_path: '/b2b/goods/thumb/' + dateformatYYYYMMDD() + '/' });
                                                        }}
                                                    />
                                                </div>
                                            </div>
                                            <div className="etc_image_contents">
                                                {s.values?.etc_images?.map((v, i) => (
                                                    <div key={i} className="btn-group">
                                                        <button
                                                            type="button"
                                                            className="del"
                                                            onClick={() => {
                                                                fnDel('etc_images', i);
                                                            }}
                                                        >
                                                            삭제
                                                        </button>
                                                        <div className="imgLabel">
                                                            <img
                                                                src={v.img_url}
                                                                id={'etc_image_' + i}
                                                                style={{ zIndex: '1' }}
                                                                className="w-full h-full absolute top-0 left-0"
                                                                alt="추가이미지"
                                                            />
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <div className="mb-12 bg-white p-5 border rounded">
                        <div className="text-xl font-bold mb-4">상품 상세내용</div>
                        <table className="form-table table table-bordered align-middle w-full border-t-2 border-black">
                            <tbody className="border-t border-black">
                                <tr className="border-b">
                                    <th scope="row" className="table_must">
                                        상세내용
                                    </th>
                                    <td colSpan={3} className="">
                                        <CKEditor
                                            initialData={s.values?.contents || ''}
                                            onChange={(event, editor) => {
                                                if (!CKEditorInit) {
                                                    s.setValues({ ...s.values, ['contents']: editor.getData() });
                                                } else {
                                                    setCKEditorInit(false);
                                                }
                                            }}
                                            upload_path={'/b2b/goods/contents/' + dateformatYYYYMMDD()}
                                        />
                                    </td>
                                </tr>
                                <tr className="border-b">
                                    <th scope="row" className="table_must">
                                        복지드림 멤버십 혜택
                                    </th>
                                    <td colSpan={3} className="">
                                        <CKEditor
                                            initialData={s.values?.benefit || ''}
                                            onChange={(event, editor) => {
                                                if (!CKEditorInit) {
                                                    s.setValues({ ...s.values, ['benefit']: editor.getData() });
                                                } else {
                                                    setCKEditorInit(false);
                                                }
                                            }}
                                            upload_path={'/b2b/goods/benefit/' + dateformatYYYYMMDD()}
                                        />
                                    </td>
                                </tr>
                                <tr className="border-b">
                                    <th scope="row" className="table_must">
                                        유의사항
                                    </th>
                                    <td colSpan={3} className="">
                                        <CKEditor
                                            initialData={s.values?.attention || ''}
                                            onChange={(event, editor) => {
                                                if (!CKEditorInit) {
                                                    s.setValues({ ...s.values, ['attention']: editor.getData() });
                                                } else {
                                                    setCKEditorInit(false);
                                                }
                                            }}
                                            upload_path={'/b2b/goods/attention/' + dateformatYYYYMMDD()}
                                        />
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <div className="mb-12 bg-white p-5 border rounded">
                        <div className="text-xl font-bold mb-4">추가항목설정</div>
                        <table className="form-table table table-bordered align-middle w-full border-t-2 border-black">
                            <tbody className="border-t border-black">
                                <tr className="border-b">
                                    <th scope="row" className="table_must">
                                        항목명
                                    </th>
                                    <td colSpan={3} className="">
                                        <input
                                            type="text"
                                            name="option_title"
                                            value={s.values?.option_title || ''}
                                            placeholder="항목명을 입력하세요"
                                            onChange={fn.handleChange}
                                            className={cls(s.errors['option_title'] ? 'border-danger' : '', 'form-control')}
                                        />
                                    </td>
                                </tr>
                                <tr className="border-b">
                                    <th scope="row" className="table_must">
                                        필수여부
                                    </th>
                                    <td colSpan={3} className="">
                                        <ul className="grid w-full grid-cols-12 gap-3">
                                            <li className="">
                                                <input
                                                    onChange={radioChange}
                                                    type="radio"
                                                    id="option_yn_Y"
                                                    name="option_yn"
                                                    value="Y"
                                                    className="hidden peer"
                                                    required
                                                    checked={s.values?.option_yn == 'Y' ? true : false}
                                                />

                                                <label
                                                    htmlFor="option_yn_Y"
                                                    className="inline-flex items-center justify-between w-full py-1 px-2 text-center text-gray-600 bg-white border border-gray-500 rounded-lg cursor-pointer peer-checked:bg-gray-500 peer-checked:text-white"
                                                >
                                                    <div className="w-full">필수</div>
                                                </label>
                                            </li>
                                            <li>
                                                <input
                                                    type="radio"
                                                    id="option_yn_N"
                                                    name="option_yn"
                                                    value="N"
                                                    checked={s.values?.option_yn == 'N' ? true : false}
                                                    className="hidden peer"
                                                    onChange={radioChange}
                                                />
                                                <label
                                                    htmlFor="option_yn_N"
                                                    className="inline-flex items-center justify-between w-full py-1 px-2 text-center text-gray-600 bg-white border border-gray-500 rounded-lg cursor-pointer peer-checked:bg-gray-500 peer-checked:text-white"
                                                >
                                                    <div className="w-full">선택</div>
                                                </label>
                                            </li>
                                        </ul>
                                    </td>
                                </tr>
                                <tr className="border-b">
                                    <th scope="row" className="table_must">
                                        항목타입
                                    </th>
                                    <td colSpan={3} className="">
                                        <ul className="grid w-full grid-cols-12 gap-3">
                                            <li className=" me-2">
                                                <input
                                                    onChange={radioChange}
                                                    type="radio"
                                                    id="option_type_A"
                                                    name="option_type"
                                                    value="A"
                                                    className="hidden peer"
                                                    required
                                                    checked={s.values?.option_type == 'A' ? true : false}
                                                />
                                                <label
                                                    htmlFor="option_type_A"
                                                    className="inline-flex items-center justify-between w-full py-1 px-2 text-center text-gray-600 bg-white border border-gray-500 rounded-lg cursor-pointer peer-checked:bg-gray-500 peer-checked:text-white"
                                                >
                                                    <div className="w-full">한줄 입력폼</div>
                                                </label>
                                            </li>
                                            <li>
                                                <input
                                                    type="radio"
                                                    id="option_type_B"
                                                    name="option_type"
                                                    value="B"
                                                    checked={s.values?.option_type == 'B' ? true : false}
                                                    className="hidden peer"
                                                    onChange={radioChange}
                                                />
                                                <label
                                                    htmlFor="option_type_B"
                                                    className="inline-flex items-center justify-between w-full py-1 px-2 text-center text-gray-600 bg-white border border-gray-500 rounded-lg cursor-pointer peer-checked:bg-gray-500 peer-checked:text-white"
                                                >
                                                    <div className="w-full">문장 입력폼</div>
                                                </label>
                                            </li>
                                            <li>
                                                <input
                                                    type="radio"
                                                    id="option_type_C"
                                                    name="option_type"
                                                    value="C"
                                                    checked={s.values?.option_type == 'C' ? true : false}
                                                    className="hidden peer"
                                                    onChange={radioChange}
                                                />
                                                <label
                                                    htmlFor="option_type_C"
                                                    className="inline-flex items-center justify-between w-full py-1 px-2 text-center text-gray-600 bg-white border border-gray-500 rounded-lg cursor-pointer peer-checked:bg-gray-500 peer-checked:text-white"
                                                >
                                                    <div className="w-full">드롭박스</div>
                                                </label>
                                            </li>
                                            <li>
                                                <input
                                                    type="radio"
                                                    id="option_type_D"
                                                    name="option_type"
                                                    value="D"
                                                    checked={s.values?.option_type == 'D' ? true : false}
                                                    className="hidden peer"
                                                    onChange={radioChange}
                                                />
                                                <label
                                                    htmlFor="option_type_D"
                                                    className="inline-flex items-center justify-between w-full py-1 px-2 text-center text-gray-600 bg-white border border-gray-500 rounded-lg cursor-pointer peer-checked:bg-gray-500 peer-checked:text-white"
                                                >
                                                    <div className="w-full">라디오 버튼</div>
                                                </label>
                                            </li>
                                            <li>
                                                <input
                                                    type="radio"
                                                    id="option_type_E"
                                                    name="option_type"
                                                    value="E"
                                                    checked={s.values?.option_type == 'E' ? true : false}
                                                    className="hidden peer"
                                                    onChange={radioChange}
                                                />
                                                <label
                                                    htmlFor="option_type_E"
                                                    className="inline-flex items-center justify-between w-full py-1 px-2 text-center text-gray-600 bg-white border border-gray-500 rounded-lg cursor-pointer peer-checked:bg-gray-500 peer-checked:text-white"
                                                >
                                                    <div className="w-full">날짜</div>
                                                </label>
                                            </li>
                                            <li>
                                                <input
                                                    type="radio"
                                                    id="option_type_F"
                                                    name="option_type"
                                                    value="F"
                                                    checked={s.values?.option_type == 'F' ? true : false}
                                                    className="hidden peer"
                                                    onChange={radioChange}
                                                />
                                                <label
                                                    htmlFor="option_type_F"
                                                    className="inline-flex items-center justify-between w-full py-1 px-2 text-center text-gray-600 bg-white border border-gray-500 rounded-lg cursor-pointer peer-checked:bg-gray-500 peer-checked:text-white"
                                                >
                                                    <div className="w-full">파일업로드</div>
                                                </label>
                                            </li>
                                            <li>
                                                <input
                                                    type="radio"
                                                    id="option_type_G"
                                                    name="option_type"
                                                    value="G"
                                                    checked={s.values?.option_type == 'G' ? true : false}
                                                    className="hidden peer"
                                                    onChange={radioChange}
                                                />
                                                <label
                                                    htmlFor="option_type_G"
                                                    className="inline-flex items-center justify-between w-full py-1 px-2 text-center text-gray-600 bg-white border border-gray-500 rounded-lg cursor-pointer peer-checked:bg-gray-500 peer-checked:text-white"
                                                >
                                                    <div className="w-full">고객안내형</div>
                                                </label>
                                            </li>
                                        </ul>
                                    </td>
                                </tr>
                                {s.values?.option_type != '' && typeof s.values?.option_type != 'undefined' && (
                                    <tr className="border-b">
                                        <th scope="row" className="table_must">
                                            {s.values?.option_type == 'A'
                                                ? '한줄 입력폼 '
                                                : s.values?.option_type == 'B'
                                                ? '문장 입력폼 '
                                                : s.values?.option_type == 'C'
                                                ? '드롭박스 '
                                                : s.values?.option_type == 'D'
                                                ? '라디오 버튼 '
                                                : s.values?.option_type == 'E'
                                                ? '날짜 '
                                                : s.values?.option_type == 'F'
                                                ? '파일업로드 '
                                                : s.values?.option_type == 'G' && '고객안내형 '}
                                            설정사항
                                        </th>
                                        <td colSpan={3} className="flex items-center">
                                            {s.values?.option_type != '' && s.values?.option_type != 'E' && s.values?.option_type != 'F' && (
                                                <div className="flex-shrink-0 me-3">
                                                    {s.values?.option_type == 'A'
                                                        ? '힌트값'
                                                        : s.values?.option_type == 'B'
                                                        ? '힌트값'
                                                        : s.values?.option_type == 'C'
                                                        ? '드롭박스 항목들'
                                                        : s.values?.option_type == 'D'
                                                        ? '라디오 버튼 항목들'
                                                        : s.values?.option_type == 'G' && '안내문구 '}
                                                </div>
                                            )}
                                            {s.values?.option_type == 'E' ? (
                                                <div className="flex gap-3">
                                                    <div className="flex items-center">
                                                        <input
                                                            id={`option_single`}
                                                            onChange={fn.handleChange}
                                                            checked={s.values?.placeholder == 'single' ? true : false}
                                                            type="radio"
                                                            value={'single'}
                                                            name="placeholder"
                                                            className="w-4 h-4"
                                                        />
                                                        <label htmlFor={`option_single`} className="ml-2 text-sm font-medium">
                                                            단일
                                                        </label>
                                                        <Datepicker
                                                            asSingle={true}
                                                            inputName="option_single"
                                                            value={s.values?.option_single}
                                                            onChange={fn.handleChangeDateRange}
                                                            disabled
                                                            containerClassName="ms-3 relative w-72 text-gray-700 border border-gray-300 rounded"
                                                        />
                                                    </div>
                                                    <div className="flex items-center">
                                                        <input
                                                            id={`placeholder-range`}
                                                            onChange={fn.handleChange}
                                                            checked={s.values?.placeholder == 'range' ? true : false}
                                                            type="radio"
                                                            value={'range'}
                                                            name="placeholder"
                                                            className="w-4 h-4"
                                                        />
                                                        <label htmlFor={`placeholder-range`} className="ml-2 text-sm font-medium">
                                                            기간
                                                        </label>

                                                        <Datepicker
                                                            inputName="option_range"
                                                            value={s.values?.option_range}
                                                            i18n={'ko'}
                                                            onChange={fn.handleChangeDateRange}
                                                            disabled
                                                            containerClassName="ms-3 relative w-72 text-gray-700 border border-gray-300 rounded"
                                                        />
                                                    </div>
                                                </div>
                                            ) : s.values?.option_type == 'F' ? (
                                                <div className="flex items-center gap-3 py-2 px-3">
                                                    <div className="flex items-center">
                                                        <input
                                                            id={`placeholder-1`}
                                                            onChange={fn.handleChange}
                                                            checked={s.values?.placeholder == 'imageFile' ? true : false}
                                                            type="radio"
                                                            value={'imageFile'}
                                                            name="placeholder"
                                                            className="w-4 h-4"
                                                        />
                                                        <label htmlFor={`placeholder-1`} className="ml-2 text-sm font-medium">
                                                            이미지 파일 전용(jpg, png, gif)
                                                        </label>
                                                    </div>
                                                    <div className="flex items-center">
                                                        <input
                                                            id={`placeholder-2`}
                                                            onChange={fn.handleChange}
                                                            checked={s.values?.placeholder == 'allFile' ? true : false}
                                                            type="radio"
                                                            value={'allFile'}
                                                            name="placeholder"
                                                            className="w-4 h-4"
                                                        />
                                                        <label htmlFor={`placeholder-2`} className="ml-2 text-sm font-medium">
                                                            전체 파일 (jpg, png, gif, xls, ppt, doc, pdf, hwp 등)zzz
                                                        </label>
                                                    </div>
                                                </div>
                                            ) : (
                                                <input
                                                    type="text"
                                                    name="placeholder"
                                                    value={s.values?.placeholder || ''}
                                                    placeholder={s.values?.option_type == 'C' || s.values?.option_type == 'D' ? '콤마(,)로 구분해주세요.' : ''}
                                                    onChange={fn.handleChange}
                                                    className={cls(s.errors['placeholder'] ? 'border-danger' : '', 'form-control')}
                                                />
                                            )}
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                        <div className="mt-4">
                            <button
                                className="!w-full btn-filter hover:bg-gray-600 hover:text-white"
                                type="button"
                                onClick={() => addOption(s.values?.option_title, s.values?.option_type, s.values?.option_yn, s.values?.placeholder)}
                            >
                                내용추가
                            </button>
                        </div>
                        {s.values?.option_list?.length > 0 && (
                            <div className="mt-4">
                                <div className="col-table">
                                    <div className="col-table-th grid grid-cols-10 sticky top-16 bg-gray-100">
                                        <div className="">번호</div>
                                        <div className="">항목명</div>
                                        <div className="col-span-6">항목 예시</div>
                                        <div className="">필수 유/무</div>
                                        <div className="">삭제</div>
                                    </div>

                                    {s.values?.option_list?.map((v: any, i: number) => (
                                        <div key={i} className="col-table-td grid grid-cols-10 bg-white transition duration-300 ease-in-out hover:bg-gray-100">
                                            <div className="">{i + 1}</div>
                                            <div className="">{v.option_title}</div>
                                            <div className="col-span-6">
                                                {v.option_type == 'B' ? (
                                                    <textarea className="form-control" name="placeholder_B" onChange={fn.handleChange}></textarea>
                                                ) : v.option_type == 'C' ? (
                                                    <select name="placeholder_C" onChange={fn.handleChange} className="form-select">
                                                        {v.placeholder
                                                            .split(',')
                                                            .filter(v => v != '')
                                                            ?.map((vv, ii) => (
                                                                <option key={ii} value={vv}>
                                                                    {vv}
                                                                </option>
                                                            ))}
                                                    </select>
                                                ) : v.option_type == 'D' ? (
                                                    <ul className="flex w-full gap-3 flex-wrap">
                                                        {v.placeholder
                                                            .split(',')
                                                            .filter(v => v != '')
                                                            ?.map((vv: any, ii: number) => (
                                                                <li key={ii} className="">
                                                                    <input
                                                                        onChange={fn.handleChange}
                                                                        data-index={i}
                                                                        type="radio"
                                                                        id={'option_type_D' + i + ii}
                                                                        name={'option_type_D' + i}
                                                                        value={vv}
                                                                        className="hidden peer"
                                                                        required
                                                                    />
                                                                    <label
                                                                        htmlFor={'option_type_D' + i + ii}
                                                                        className="inline-flex items-center justify-between w-full py-1 px-3 text-center text-gray-600 bg-white border border-gray-500 rounded-lg cursor-pointer peer-checked:bg-gray-500 peer-checked:text-white"
                                                                    >
                                                                        <div className="w-full">{vv}</div>
                                                                    </label>
                                                                </li>
                                                            ))}
                                                    </ul>
                                                ) : v.option_type == 'E' ? (
                                                    v.placeholder == 'single' ? (
                                                        <div className="w-full">
                                                            <Datepicker
                                                                asSingle={true}
                                                                inputName="option_single"
                                                                value={s.values?.option_single}
                                                                onChange={fn.handleChangeDateRange}
                                                                containerClassName="relative w-full text-gray-700 border border-gray-300 rounded"
                                                            />
                                                        </div>
                                                    ) : (
                                                        v.placeholder == 'range' && (
                                                            <div className="w-full">
                                                                <Datepicker
                                                                    inputName="option_range"
                                                                    value={s.values?.option_range}
                                                                    i18n={'ko'}
                                                                    onChange={fn.handleChangeDateRange}
                                                                    containerClassName="relative w-full text-gray-700 border border-gray-300 rounded"
                                                                />
                                                            </div>
                                                        )
                                                    )
                                                ) : v.option_type == 'F' ? (
                                                    <div className="flex align-center w-full">
                                                        <button type="button" className="btn-filter me-3" onClick={fileUploadBtn}>
                                                            <i className="far fa-file"></i> 파일업로드
                                                            <input type="file" ref={fileUpload} name="" className="hidden" />
                                                        </button>
                                                        <span className="text-gray-500 text-sm py-2">
                                                            {v.placeholder == 'imageFile'
                                                                ? '업로드 지원 파일 : jpeg, jpg, svg, png, gif'
                                                                : '업로드 지원 파일 : jpeg, jpg, svg, png, gif, pdf, csv, zip, xlsx, xls, docx, doc, pptx, ppt, hwp'}
                                                        </span>
                                                    </div>
                                                ) : v.option_type == 'G' ? (
                                                    <div className="w-full text-start">
                                                        <div className="p-3 bg-gray-50 rounded break-all">{v.placeholder}</div>
                                                    </div>
                                                ) : (
                                                    <div className="w-full text-start">
                                                        <input type="text" name="form" placeholder={v.placeholder} onChange={fn.handleChange} className="form-control" />
                                                    </div>
                                                )}
                                            </div>
                                            <div className="">{v.option_yn == 'Y' ? '필수' : '선택'}</div>
                                            <div className="" onClick={() => optionDel(i)}>
                                                <button type="button" className="btn-red">
                                                    삭제
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                    <div className="mb-12 bg-white p-5 border rounded">
                        <div className="text-xl font-bold mb-4">추가 상품 진열</div>
                        <table className="form-table table table-bordered align-middle w-full border-t-2 border-black">
                            <tbody className="border-t border-black">
                                <tr className="border-b">
                                    <th scope="row">추가상품 진열하기</th>
                                    <td colSpan={3} className="">
                                        <div className="text-sm text-gray-500 mb-2">당분간 상품코드를 콤마로 나열해주세요. 나중에 업데이트 예정</div>
                                        <input
                                            type="text"
                                            name="other_service"
                                            value={s.values?.other_service || ''}
                                            placeholder="콤마(,)로 구분 최대 6개"
                                            onChange={fn.handleChange}
                                            className={cls(s.errors['other_service'] ? 'border-danger' : '', 'form-control')}
                                        />
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <div className="mb-12 bg-white p-5 border rounded">
                        <div className="text-xl font-bold mb-4">관리자메모</div>
                        <table className="form-table table table-bordered align-middle w-full border-t-2 border-black">
                            <tbody className="border-t border-black">
                                <tr className="border-b">
                                    <th scope="row">관리자메모</th>
                                    <td colSpan={3} className="">
                                        <textarea
                                            name="memo"
                                            rows={4}
                                            placeholder="메모를 입력하세요"
                                            onChange={fn.handleChange}
                                            value={s.values?.memo || ''}
                                            className={cls(s.errors['memo'] ? 'border-danger' : '', 'form-control')}
                                        ></textarea>
                                    </td>
                                </tr>
                                {posts.memo_list?.length > 0 &&
                                    posts.memo_list?.map((v: any, i: number) => (
                                        <tr key={i} className="border-b">
                                            <th scope="row">{v.create_user}</th>
                                            <td colSpan={3} className="">
                                                <div className="w-full text-start whitespace-pre-wrap" dangerouslySetInnerHTML={{ __html: v.memo }}></div>
                                            </td>
                                        </tr>
                                    ))}
                            </tbody>
                        </table>
                    </div>
                    <div className="mt-5 w-full text-center">
                        <button className="mr-3 px-5 bg-blue-500 rounded-md py-2 text-white text-center" disabled={s.submitting}>
                            {checkNumeric(router.query.guid) > 0 ? '수정' : '저장'}
                        </button>
                    </div>

                    {sellerSearchOpen && <SellerSearch setSellerSearchOpen={setSellerSearchOpen} seller={s.values?.seller} sandSellerUid={getSellerUid} />}
                </form>
            </div>
        </Layout>
    );
};
export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {
        uid: checkNumeric(ctx.query.guid),
    };
    var response: any = {};
    try {
        const { data } = await api.post(`/be/admin/b2b/goods/read`, request);
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

export default B2BGoodsReg;
