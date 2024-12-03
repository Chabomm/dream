import { checkNumeric, cls } from '@/libs/utils';
import React, { useContext, useState, useEffect, useRef, useCallback } from 'react';
// import { DropEvent, FileRejection, useDropzone } from 'react-dropzone';

interface props {
    s: any;
    fn: any;
    attrs: any;
    param?: any;
    gubun?: any;
}
export default function EditorPlugin({ s, fn, attrs, param, gubun }: props) {
    // input 값 변경 될 때
    const handleContentsInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>, index: number) => {
        const { name, value } = e.target;
        let copy = { ...s.values };
        copy[param][index][name] = value;

        s.setValues(copy);
    };

    // radio 값 변경 될 때
    const handleContentsRadioChange = (e: React.ChangeEvent<HTMLInputElement>, index: number) => {
        const { name, value, checked } = e.target;
        let copy = { ...s.values };

        let r_name = name.replace('-' + gubun + '-' + index, '');
        copy[param][index][r_name] = value;
        s.setValues(copy);
    };

    // img 값 변경 될 때
    const handleContentsImage = async (e: React.ChangeEvent<HTMLInputElement>, index: number) => {
        const { name, value } = e.target;
        let files: any = e.target.files;

        let copy = { ...s.values };
        for (var i = 0; i < files.length; i++) {
            var f = files[i];
            f.index = index; // 사용안되는index 를 f.insec

            if (i == 0) {
                copy[param][index][name] = f;
            } else {
                let c = {
                    btype: 'img',
                    gubun,
                    image_url: '',
                    link: '',
                    html: '',
                    link_target: '',
                    files: f,
                    uid: 0,
                };
                copy[param].splice(i, 0, c);
            }
            s.setValues(copy);
            index = index + 1;
        }
        e.target.value = '';
    };

    const fnDel = (index: number) => {
        const copy = { ...s.values };
        copy[param].splice(index, 1);
        s.setValues(copy);
    };

    return (
        <>
            {s.values[param]?.map((v: any, i: number) => (
                <div key={i} className="relative mb-4">
                    <button type="button" className="absolute right-4 top-1" onClick={() => fnDel(i)}>
                        <i className="fas fa-times text-gray-500 text-lg hover:text-red-600"></i>
                    </button>
                    {v.btype == 'img' ? (
                        <div className="grid grid-cols-2 gap-4 border p-3 rounded">
                            <div className="col-span-1">
                                <label className="form-label">링크</label>
                                <input
                                    type="text"
                                    name="link"
                                    value={s.values[param][i]?.link || ''}
                                    placeholder="링크 주소를 입력해주세요"
                                    onChange={(e: any) => {
                                        handleContentsInputChange(e, i);
                                    }}
                                    className={cls('form-control')}
                                />
                            </div>
                            <div className="col-span-1">
                                <label className="form-label">링크타겟</label>
                                <div className="flex items-center gap-4 p-2">
                                    <div className="flex items-center">
                                        <input
                                            id={`link_target-${gubun}-${i}_self`}
                                            checked={s.values[param][i]?.link_target == '_self' ? true : false}
                                            type="radio"
                                            value={`_self`}
                                            name={`link_target-${gubun}-${i}`}
                                            className="w-4 h-4"
                                            onChange={(e: any) => {
                                                handleContentsRadioChange(e, i);
                                            }}
                                        />
                                        <label htmlFor={`link_target-${gubun}-${i}_self`} className="ml-2 font-medium">
                                            현재창에서 이동
                                        </label>
                                    </div>
                                    <div className="flex items-center">
                                        <input
                                            id={`link_target-${gubun}-${i}_blank`}
                                            checked={s.values[param][i]?.link_target == '_blank' ? true : false}
                                            type="radio"
                                            value={`_blank`}
                                            name={`link_target-${gubun}-${i}`}
                                            className="w-4 h-4"
                                            onChange={(e: any) => {
                                                handleContentsRadioChange(e, i);
                                            }}
                                        />
                                        <label htmlFor={`link_target-${gubun}-${i}_blank`} className="ml-2 font-medium">
                                            새창에서 이동
                                        </label>
                                    </div>
                                </div>
                            </div>
                            <div className="col-span-2">
                                <label className="form-label">이미지</label>
                                <label>
                                    <div className="bg-gray-100 text-gray-500 p-5 border-4 border-dashed !w-full text-center cursor-pointer">
                                        클릭하여 이미지를 선택해주세요
                                        <input
                                            name="files"
                                            type="file"
                                            className="hidden"
                                            accept="image/*"
                                            multiple
                                            onChange={e => {
                                                handleContentsImage(e, i);
                                            }}
                                        />
                                    </div>
                                </label>
                            </div>

                            {JSON.stringify(v.files) == '{}' ? (
                                <div className="col-span-2">
                                    <img src={v.image_url} />
                                </div>
                            ) : (
                                <div className="col-span-2">
                                    <img src={window.URL.createObjectURL(v.files)} className="w-full" alt="" />
                                </div>
                            )}
                        </div>
                    ) : v.btype == 'html' ? (
                        <div className="w-full">
                            <textarea
                                name="html"
                                rows={5}
                                value={s.values[param][i]?.html || ''}
                                placeholder="html code로 입력해주세요"
                                onChange={(e: any) => {
                                    handleContentsInputChange(e, i);
                                }}
                                className={cls(s.errors['param'] ? 'border-danger' : '', 'form-control')}
                            />
                        </div>
                    ) : null}
                </div>
            ))}
        </>
    );
}
