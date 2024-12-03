import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect, useRef } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import { cls, left } from '@/libs/utils';
import useForm from '@/components/form/useForm';
import Datepicker from 'react-tailwindcss-datepicker';
import PartnerChoice from '@/components/ums/PartnerChoice';
import DeviceChoice from '@/components/ums/DeviceChoice';

const UmsPushEdit: NextPage = (props: any) => {
    const router = useRouter();
    const [filter, setFilter] = useState<any>([]);

    useEffect(() => {
        if (props) {
            s.setValues(props.response.values);
            setFilter(props.response.filter);
        }
    }, [props]);

    const { s, fn, attrs } = useForm({
        initialValues: {
            startDate: '',
            endDate: '',
            booking_at_date: {
                startDate: '',
                endDate: '',
            },
        },
        onSubmit: async () => {
            await editing('REG');
        },
    });

    const deleting = () => editing('DEL');

    const editing = async mode => {
        try {
            if (mode == 'REG' && s.values.uid > 0) {
                mode = 'MOD';
            }
            s.values.mode = mode;

            if (typeof s.values.booking_at_date.startDate === 'undefined') {
                alert('발송예약일을 선택해 주세요');
                return;
            } else {
                s.values.booking_at = s.values.booking_at_date.startDate + ' ' + s.values.booking_at_time;
            }

            if (s.values.push_link != '' && left(s.values.push_link, 1) != '/') {
                alert('푸시 연결 링크는 도메인을 제외한 /로 시작해야합니다.');
                return;
            }

            if (s.values.rec_type == 'P' && s.values.partners.length == 0) {
                alert('발송대상 고객사를 선택해 주세요');
                return;
            }

            if (s.values.rec_type == 'S' && s.values.devices.length == 0) {
                alert('발송대상 디바이스를 선택해 주세요');
                return;
            }

            if (s.values.rec_type == 'A') {
                // alert('전체발송은 준비중');
                // return;
            }
            const { data } = await api.post(`/ums/push/booking/edit`, s.values);
            if (data.code == 200) {
                alert(data.msg);
                router.push('/message/push/edit?uid=' + data.uid);
            } else {
                alert(data.msg);
            }
        } catch (e: any) {}
    };

    const fn_rec_type_change = e => {
        const { name, value, checked } = e.target;
        const copy = { ...s.values };
        copy[name] = value;

        if (value == 'A') {
            copy.partners = [];
            copy.devices = [];
        } else if (value == 'P') {
            // openPartnerChoice();
        }

        s.setValues(copy);
    };

    const time_picker = [
        { value: '08:00:00', text: '오전 08시' },
        { value: '09:00:00', text: '오전 09시' },
        { value: '10:00:00', text: '오전 10시' },
        { value: '11:00:00', text: '오전 11시' },
        { value: '12:00:00', text: '오후 12시' },
        { value: '13:00:00', text: '오후 01시' },
        { value: '14:00:00', text: '오후 02시' },
        { value: '15:00:00', text: '오후 03시' },
        { value: '16:00:00', text: '오후 04시' },
        { value: '17:00:00', text: '오후 05시' },
        { value: '18:00:00', text: '오후 06시' },
        { value: '19:00:00', text: '오후 07시' },
        { value: '20:00:00', text: '오후 08시' },
    ];

    const refPartnerChoice = useRef<any>();
    function openPartnerChoice() {
        refPartnerChoice.current.init(s.values.partners);
    }

    const fnPartnerChoiceCallback = partners => {
        const copy = { ...s.values };
        copy.partners = partners;
        s.setValues(copy);
        refPartnerChoice.current.onToggle();
    };

    const refDeviceChoice = useRef<any>();
    function openDeviceChoice() {
        refDeviceChoice.current.init(s.values.devices);
    }

    const fnDeviceChoiceCallback = devices => {
        const copy = { ...s.values };
        copy.devices = devices;
        s.setValues(copy);
        refDeviceChoice.current.onToggle();
    };

    return (
        <>
            <form onSubmit={fn.handleSubmit} noValidate>
                <div className="edit_popup w-full bg-slate-100 mx-auto py-10" style={{ minHeight: '100vh' }}>
                    <div className="px-9">
                        <div className="text-2xl font-semibold">PUSH 발송예약 상세</div>

                        {process.env.NODE_ENV == 'development' && (
                            <pre className="">
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <div className="font-bold mb-3 text-red-500">filter</div>
                                        {JSON.stringify(filter, null, 4)}
                                    </div>
                                    <div>
                                        <div className="font-bold mb-3 text-red-500">s.values</div>
                                        {JSON.stringify(s.values, null, 4)}
                                    </div>
                                </div>
                            </pre>
                        )}

                        <div className="card_area">
                            <div className="grid grid-cols-2 gap-4">
                                <div className="col-span-1">
                                    <label className="form-label">수신대상</label>
                                    <div className="flex items-center gap-4 h-10">
                                        {filter.rec_type?.map((v: any, i: number) => (
                                            <div key={i} className="flex items-center">
                                                <input
                                                    id={`rec_type-e-${i}`}
                                                    checked={s.values.rec_type == v.key ? true : false}
                                                    type="radio"
                                                    value={v.key}
                                                    name="rec_type"
                                                    className="w-4 h-4"
                                                    onChange={fn_rec_type_change}
                                                />
                                                <label htmlFor={`rec_type-e-${i}`} className="ml-2 text-sm font-medium">
                                                    {v.text}
                                                </label>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                                <div className="col-span-1">
                                    <label className="form-label">수신대상</label>
                                    {s.values.rec_type == 'P' && (
                                        <div className="text-red-500 h-10 leading-10 underline cursor-pointer" onClick={openPartnerChoice}>
                                            {s.values.partners.length}개 고객사
                                        </div>
                                    )}
                                    {s.values.rec_type == 'S' && (
                                        <div className="text-red-500 h-10 leading-10 underline cursor-pointer" onClick={openDeviceChoice}>
                                            {s.values.devices.length}개 디바이스
                                        </div>
                                    )}
                                </div>
                                <div className="col-span-1">
                                    <label className="form-label">발송예약일</label>
                                    <Datepicker
                                        containerClassName="relative w-full text-gray-700 border border-gray-300 rounded"
                                        useRange={false}
                                        asSingle={true}
                                        inputName="booking_at_date"
                                        i18n={'ko'}
                                        value={{
                                            startDate: s.values?.booking_at_date.startDate || '',
                                            endDate: s.values?.booking_at_date.endDate || '',
                                        }}
                                        onChange={fn.handleChangeDateRange}
                                    />
                                    {s.errors['booking_at_date'] && <div className="form-error">{s.errors['booking_at_date']}</div>}
                                </div>
                                <div className="col-span-1">
                                    <label className="form-label">발송예약시간</label>
                                    <select
                                        name="booking_at_time"
                                        value={s.values?.booking_at_time || ''}
                                        onChange={fn.handleChange}
                                        className={cls(s.errors['booking_at_time'] ? 'border-danger' : '', 'form-select')}
                                    >
                                        {time_picker?.map((v, i) => (
                                            <option key={i} value={v.value}>
                                                {v.text}
                                            </option>
                                        ))}
                                    </select>
                                    {s.errors['booking_at_time'] && <div className="form-error">{s.errors['booking_at_time']}</div>}
                                </div>

                                <div className="col-span-2">
                                    <label className="form-label">푸시 제목</label>
                                    <input
                                        type="text"
                                        name="push_title"
                                        {...attrs.is_mand}
                                        value={s.values?.push_title || ''}
                                        placeholder=""
                                        onChange={fn.handleChange}
                                        className={cls(s.errors['push_title'] ? 'border-danger' : '', 'form-control')}
                                    />
                                    {s.errors['push_title'] && <div className="form-error">{s.errors['push_title']}</div>}
                                </div>
                                <div className="col-span-2">
                                    <label className="form-label">푸시 내용</label>
                                    <textarea
                                        name="push_msg"
                                        rows={5}
                                        maxLength={128}
                                        {...attrs.is_mand}
                                        value={s.values?.push_msg || ''}
                                        placeholder="한 줄 최대 32자 씩 4줄로 최대 128자"
                                        onChange={fn.handleTextAreaChange}
                                        className={cls(s.errors['push_msg'] ? 'border-danger' : '', 'form-control')}
                                    />
                                    {s.errors['push_msg'] && <div className="form-error">{s.errors['push_msg']}</div>}
                                    <div className="w-full">
                                        <div className="mt-3 border border-red-500 bg-red-200 p-3 text-sm w-full">
                                            <div className="font-bold mb-2">변수 사용방법</div>
                                            <div className="">
                                                <div>
                                                    <code className="code">{'#{복지몰명}'}</code> : 사용자의 partner_id를 기반으로 복지몰명으로 치환됨 (고객사가 혼합된 경우 사용)
                                                </div>
                                                <div>
                                                    <code className="code">{'#{고객사명}'}</code> : 사용자의 partner_id를 기반으로 회사명으로 치환됨 (고객사가 혼합된 경우 사용)
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div className="col-span-2">
                                    <label className="form-label">연결링크URL</label>
                                    <input
                                        type="text"
                                        name="push_link"
                                        value={s.values?.push_link || ''}
                                        placeholder="도메인제외 / 부터 시작"
                                        onChange={fn.handleChange}
                                        className={cls(s.errors['push_link'] ? 'border-danger' : '', 'form-control')}
                                    />
                                    {s.errors['push_link'] && <div className="form-error">{s.errors['push_link']}</div>}
                                    <div className="mt-3 text-gray-400 px-3 text-sm">도메인을 제외한 / 부터 시작해야 합니다.</div>
                                    <div className="mt-3 text-gray-400 px-3 text-sm">일반메인으로 연결시 비워두면 됩니다.</div>
                                </div>
                                <div className="col-span-2">
                                    <label className="form-label">푸시 이미지</label>
                                    <input
                                        name="push_img-file"
                                        type="file"
                                        className={cls(s.errors['push_img'] ? 'border-danger' : '', 'form-control')}
                                        accept="image/*"
                                        onChange={e => {
                                            fn.handleImage(e, '/ums/push/');
                                        }}
                                    />
                                    {s.values.push_img ? <img src={s.values.push_img} className="my-3" alt="img" /> : ''}
                                    <div className="mt-3 text-gray-400 px-3 text-sm">
                                        안드로이드 알림센터에 노출되는 이미지 영역의 최대 사이즈는 800*464 픽셀이며 720*350 이내로 내용이 들어가도록 제작하는것이 좋습니다.
                                    </div>
                                </div>
                            </div>
                            {/* end grid */}
                        </div>
                        {/* card_area */}

                        <div className="offcanvas-footer grid grid-cols-3 gap-4 !p-0 my-5">
                            <button className="btn-del" type="button" onClick={deleting}>
                                삭제
                            </button>
                            <button className="btn-save col-span-2 hover:bg-blue-600" disabled={s.submitting}>
                                저장
                            </button>
                        </div>
                    </div>
                </div>
            </form>
            <PartnerChoice ref={refPartnerChoice} callback={fnPartnerChoiceCallback} />
            <DeviceChoice ref={refDeviceChoice} callback={fnDeviceChoiceCallback} />
        </>
    );
};
export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {
        uid: ctx.query.uid,
    };
    var response: any = {};
    try {
        const { data } = await api.post(`/ums/push/booking/read`, request);
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

export default UmsPushEdit;
