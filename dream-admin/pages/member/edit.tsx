import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import { cls } from '@/libs/utils';
import useForm from '@/components/form/useForm';
import DaumPost from '@/components/DaumPost';
import LayoutPopup from '@/components/LayoutPopup';
import Datepicker from 'react-tailwindcss-datepicker';

const MemberEdit: NextPage = (props: any) => {
    const router = useRouter();
    useEffect(() => {
        if (props) {
            s.setValues(props.response);
        }
    }, [props]);

    const { s, fn, attrs } = useForm({
        initialValues: {},
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
            s.values.birth = s.values.birth?.startDate;
            s.values.anniversary = s.values.anniversary?.startDate;
            s.values.join_com = s.values.join_com?.startDate;

            if (s.values.birth + '' == 'null' && typeof s.values.birth?.startDate == 'undefined') {
                alert('생일을 선택해주세요.');
                const el = document.querySelector("input[name='birth']");
                (el as HTMLElement)?.focus();
                return;
            }
            const { data } = await api.post(`/be/admin/member/edit`, s.values);

            if (data.code == 200) {
                if (s.values.mode == 'REG') {
                    alert(data.msg);
                    router.replace(`/member/edit?uid=${s.values.uid}`);
                } else {
                    alert(data.msg);
                    if (mode == 'MOD') {
                        router.replace(`/member/edit?uid=${data.uid}`);
                    }
                }
            } else {
                alert(data.msg);
            }

            return;
        } catch (e: any) {}
    };

    const changeLog = () => {
        alert('changeLog');
    };
    const pwReset = () => {
        alert('pwReset');
    };

    // [ S ] daumpost
    const [daumModal, setDaumModal] = useState(false);
    // 주소 모달에서 선택 후
    const handleCompleteFormSet = (data: any) => {
        s.values.post = data.zonecode;
        s.values.addr = data.roadAddress;
        const el = document.querySelector("input[name='addr_detail']");
        (el as HTMLElement)?.focus();
    };
    // [ E ] daumpost

    const radioChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value, checked } = e.target;
        s.setValues({ ...s.values, [name]: value });
    };

    return (
        <>
            <LayoutPopup title={''}>
                <div className="w-full bg-slate-100 mx-auto py-10">
                    <form onSubmit={fn.handleSubmit} noValidate>
                        <div className="px-9">
                            <div className="flex justify-between">
                                <div className="text-2xl font-semibold">회원 {s.values.uid > 0 ? '수정' : '등록'}</div>
                            </div>
                            <div className="border py-4 px-6 rounded shadow-md bg-white mt-5">
                                <div className="card_area">
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="col-span-1">
                                            {/* 이름 */}
                                            <label className="form-label">아이디</label>
                                            <input
                                                type="text"
                                                name="user_id"
                                                {...attrs.is_mand}
                                                value={s.values?.user_id || ''}
                                                placeholder=""
                                                onChange={fn.handleChange}
                                                readOnly={s.values.uid > 0 && true}
                                                className={cls(s.errors['user_id'] ? 'border-danger' : '', 'form-control')}
                                            />
                                            {s.errors['user_id'] && <div className="form-error">{s.errors['user_id']}</div>}
                                        </div>
                                        <div className="col-span-1">
                                            {/* 회원상태 */}
                                            <label className="form-label">회원상태</label>
                                            <ul className="grid w-56 grid-cols-4">
                                                <li>
                                                    <input
                                                        onChange={radioChange}
                                                        type="radio"
                                                        id="state_200"
                                                        name="state"
                                                        value="200"
                                                        className="hidden peer"
                                                        required
                                                        defaultChecked={s.values.state == '200' ? true : false}
                                                    />
                                                    <label
                                                        htmlFor="state_200"
                                                        className="inline-flex items-center justify-between w-full p-1 text-center text-gray-600 bg-white border border-r-0 border-gray-500 rounded-l-lg cursor-pointer peer-checked:bg-gray-500 peer-checked:text-white"
                                                    >
                                                        <div className="w-full">대기</div>
                                                    </label>
                                                </li>
                                                <li>
                                                    <input
                                                        type="radio"
                                                        id="state_100"
                                                        name="state"
                                                        value="100"
                                                        className="hidden peer"
                                                        required
                                                        defaultChecked={s.values.state == '100' ? true : false}
                                                        onChange={radioChange}
                                                    />
                                                    <label
                                                        htmlFor="state_100"
                                                        className="inline-flex items-center justify-between w-full p-1 text-center text-gray-600 bg-white border border-r-0 border-gray-500 cursor-pointer peer-checked:bg-gray-500 peer-checked:text-white"
                                                    >
                                                        <div className="w-full">정상</div>
                                                    </label>
                                                </li>
                                                <li>
                                                    <input
                                                        type="radio"
                                                        id="state_900"
                                                        name="state"
                                                        value="900"
                                                        defaultChecked={s.values.state == '900' ? true : false}
                                                        className="hidden peer"
                                                        onChange={radioChange}
                                                    />
                                                    <label
                                                        htmlFor="state_900"
                                                        className="inline-flex items-center justify-between w-full p-1 text-center text-gray-600 bg-white border border-gray-500 rounded-r-lg cursor-pointer peer-checked:bg-gray-500 peer-checked:text-white"
                                                    >
                                                        <div className="w-full">탈퇴</div>
                                                    </label>
                                                </li>
                                            </ul>
                                        </div>
                                        <div className="col-span-2">
                                            {/* 임시비밀번호 */}
                                            <label className="form-label">임시비밀번호</label>
                                            <div className="flex gap-3 items-center">
                                                <div className="text-gray-600">
                                                    임시 비밀번호는 <span className="text-red-500">아이디+휴대전화뒤4자리</span>로 초기화 되며, 인증 후 이용가능합니다.
                                                </div>
                                                <button
                                                    type="button"
                                                    className="p-1 px-2 text-center text-cyan-600 bg-white border border-cyan-500 rounded cursor-pointer hover:bg-cyan-500 hover:text-white"
                                                    onClick={() => changeLog()}
                                                >
                                                    변경이력
                                                </button>
                                                <button
                                                    type="button"
                                                    className="p-1 px-2 text-center text-red-600 bg-white border border-red-500 rounded cursor-pointer hover:bg-red-500 hover:text-white"
                                                    onClick={() => pwReset()}
                                                >
                                                    비밀번호초기화
                                                </button>
                                            </div>
                                        </div>
                                        <div className="col-span-1">
                                            {/* 이름 */}
                                            <label className="form-label">이름</label>
                                            <input
                                                type="text"
                                                name="user_name"
                                                {...attrs.is_mand}
                                                value={s.values?.user_name || ''}
                                                placeholder=""
                                                onChange={fn.handleChange}
                                                className={cls(s.errors['user_name'] ? 'border-danger' : '', 'form-control')}
                                            />
                                            {s.errors['user_name'] && <div className="form-error">{s.errors['user_name']}</div>}
                                        </div>
                                        <div className="col-span-1">
                                            {/* 성별 */}
                                            <label className="form-label">성별</label>
                                            <ul className="grid w-56 grid-cols-4">
                                                <li>
                                                    <input
                                                        type="radio"
                                                        id="gender_M"
                                                        name="gender"
                                                        value="남자"
                                                        className="hidden peer"
                                                        required
                                                        defaultChecked={s.values.gender == '남자' ? true : false}
                                                        onChange={radioChange}
                                                    />
                                                    <label
                                                        htmlFor="gender_M"
                                                        className="inline-flex items-center justify-between w-full p-1 text-center text-gray-600 bg-white border border-r-0 border-gray-500 rounded-l-lg cursor-pointer peer-checked:bg-gray-500 peer-checked:text-white"
                                                    >
                                                        <div className="w-full">남자</div>
                                                    </label>
                                                </li>
                                                <li>
                                                    <input
                                                        type="radio"
                                                        id="gender_W"
                                                        name="gender"
                                                        value="여자"
                                                        defaultChecked={s.values.gender == '여자' ? true : false}
                                                        className="hidden peer"
                                                        onChange={radioChange}
                                                    />
                                                    <label
                                                        htmlFor="gender_W"
                                                        className="inline-flex items-center justify-between w-full p-1 text-center text-gray-600 bg-white border border-gray-500 rounded-r-lg cursor-pointer peer-checked:bg-gray-500 peer-checked:text-white"
                                                    >
                                                        <div className="w-full">여자</div>
                                                    </label>
                                                </li>
                                            </ul>
                                        </div>
                                        <div className="col-span-1">
                                            {/* 복지몰 로그인 */}
                                            <label className="form-label">복지몰 로그인</label>
                                            <ul className="grid w-56 grid-cols-4">
                                                <li>
                                                    <input
                                                        type="radio"
                                                        id="is_login_T"
                                                        name="is_login"
                                                        value="T"
                                                        className="hidden peer"
                                                        required
                                                        defaultChecked={s.values.is_login == 'T' ? true : false}
                                                        onChange={radioChange}
                                                    />
                                                    <label
                                                        htmlFor="is_login_T"
                                                        className="inline-flex items-center justify-between w-full p-1 text-center text-gray-600 bg-white border border-r-0 border-gray-500 rounded-l-lg cursor-pointer peer-checked:bg-gray-500 peer-checked:text-white"
                                                    >
                                                        <div className="w-full">가능</div>
                                                    </label>
                                                </li>
                                                <li>
                                                    <input
                                                        type="radio"
                                                        id="is_login_F"
                                                        name="is_login"
                                                        value="F"
                                                        defaultChecked={s.values.is_login == 'F' ? true : false}
                                                        className="hidden peer"
                                                        onChange={radioChange}
                                                    />
                                                    <label
                                                        htmlFor="is_login_F"
                                                        className="inline-flex items-center justify-between w-full p-1 text-center text-gray-600 bg-white border border-gray-500 rounded-r-lg cursor-pointer peer-checked:bg-gray-500 peer-checked:text-white"
                                                    >
                                                        <div className="w-full">불가능</div>
                                                    </label>
                                                </li>
                                            </ul>
                                        </div>
                                        <div className="col-span-1">
                                            {/* 포인트사용 */}
                                            <label className="form-label">포인트사용</label>
                                            <ul className="grid w-56 grid-cols-4">
                                                <li>
                                                    <input
                                                        type="radio"
                                                        id="is_point_T"
                                                        name="is_point"
                                                        value="T"
                                                        className="hidden peer"
                                                        required
                                                        defaultChecked={s.values.is_point == 'T' ? true : false}
                                                        onChange={radioChange}
                                                    />
                                                    <label
                                                        htmlFor="is_point_T"
                                                        className="inline-flex items-center justify-between w-full p-1 text-center text-gray-600 bg-white border border-r-0 border-gray-500 rounded-l-lg cursor-pointer peer-checked:bg-gray-500 peer-checked:text-white"
                                                    >
                                                        <div className="w-full">가능</div>
                                                    </label>
                                                </li>
                                                <li>
                                                    <input
                                                        type="radio"
                                                        id="is_point_F"
                                                        name="is_point"
                                                        value="F"
                                                        defaultChecked={s.values.is_point == 'F' ? true : false}
                                                        className="hidden peer"
                                                        onChange={radioChange}
                                                    />
                                                    <label
                                                        htmlFor="is_point_F"
                                                        className="inline-flex items-center justify-between w-full p-1 text-center text-gray-600 bg-white border border-gray-500 rounded-r-lg cursor-pointer peer-checked:bg-gray-500 peer-checked:text-white"
                                                    >
                                                        <div className="w-full">불가능</div>
                                                    </label>
                                                </li>
                                            </ul>
                                        </div>
                                        <div className="col-span-1">
                                            {/* 휴대전화 */}
                                            <label className="form-label">휴대전화</label>
                                            <input
                                                type="text"
                                                name="mobile"
                                                {...attrs.is_mand}
                                                value={s.values?.mobile || ''}
                                                placeholder=""
                                                onChange={fn.handleChange}
                                                className={cls(s.errors['mobile'] ? 'border-danger' : '', 'form-control')}
                                            />
                                            {s.errors['mobile'] && <div className="form-error">{s.errors['mobile']}</div>}
                                        </div>
                                        <div className="col-span-1">
                                            {/* 이메일 */}
                                            <label className="form-label">이메일</label>
                                            <input
                                                type="text"
                                                name="email"
                                                {...attrs.is_mand}
                                                value={s.values?.email || ''}
                                                placeholder=""
                                                onChange={fn.handleChange}
                                                className={cls(s.errors['email'] ? 'border-danger' : '', 'form-control')}
                                            />
                                            {s.errors['email'] && <div className="form-error">{s.errors['email']}</div>}
                                        </div>
                                        <div className="col-span-2">
                                            {/* 주소 */}
                                            <label className="form-label">주소</label>
                                            <div className="grid grid-cols-12 gap-4">
                                                <div className="col-span-2">
                                                    <button
                                                        className="btn-del border border-gray-800 rounded-md h-full w-full"
                                                        type="button"
                                                        onClick={() => {
                                                            setDaumModal(true);
                                                        }}
                                                    >
                                                        주소검색
                                                    </button>
                                                </div>
                                                <div className="col-span-3">
                                                    <input
                                                        name="post"
                                                        value={s.values?.post || ''}
                                                        onChange={fn.handleChange}
                                                        type="text"
                                                        className={cls(s.errors['post'] ? 'border-danger' : '', 'form-control')}
                                                        placeholder="우편번호"
                                                        readOnly
                                                    />
                                                </div>
                                                <div className="col-span-7">
                                                    <input
                                                        name="addr"
                                                        value={s.values?.addr || ''}
                                                        onChange={fn.handleChange}
                                                        type="text"
                                                        id="addr"
                                                        className={cls(s.errors['addr'] ? 'border-danger' : '', 'form-control')}
                                                        placeholder=""
                                                        readOnly
                                                    />
                                                    {s.errors['addr'] && <div className="form-error">{s.errors['addr']}</div>}
                                                </div>
                                                <div className="col-span-7">
                                                    <input
                                                        name="addr_detail"
                                                        value={s.values?.addr_detail || ''}
                                                        onChange={fn.handleChange}
                                                        type="text"
                                                        id="addr_detail"
                                                        className={cls(s.errors['addr'] ? 'border-danger' : '', 'form-control')}
                                                        placeholder="상세위치 입력 (예:○○빌딩 2층)"
                                                    />
                                                    {s.errors['addr_detail'] && <div className="form-error">{s.errors['addr_detail']}</div>}
                                                </div>
                                            </div>
                                        </div>
                                        <div className="col-span-1">
                                            {/* 생년월일 */}
                                            <label className="form-label">생년월일</label>

                                            <Datepicker
                                                containerClassName="relative w-full text-gray-700 border border-gray-300 rounded"
                                                useRange={false}
                                                asSingle={true}
                                                inputName="birth"
                                                i18n={'ko'}
                                                value={{
                                                    startDate: s.values?.birth?.startDate || s.values?.birth,
                                                    endDate: s.values?.birth?.endDate || s.values?.birth,
                                                }}
                                                {...attrs.is_mand}
                                                onChange={fn.handleChangeDateRange}
                                            />
                                            {s.errors['birth'] && <div className="form-error">{s.errors['birth']}</div>}
                                        </div>
                                        <div className="col-span-1">
                                            {/* 기념일 */}
                                            <label className="form-label">기념일</label>

                                            <Datepicker
                                                containerClassName="relative w-full text-gray-700 border border-gray-300 rounded"
                                                useRange={false}
                                                asSingle={true}
                                                inputName="anniversary"
                                                i18n={'ko'}
                                                value={{
                                                    startDate: s.values?.anniversary?.startDate || s.values?.anniversary,
                                                    endDate: s.values?.anniversary?.endDate || s.values?.anniversary,
                                                }}
                                                onChange={fn.handleChangeDateRange}
                                            />
                                        </div>
                                        <div className="col-span-1">
                                            {/* 재직여부 */}
                                            <label className="form-label">재직여부</label>
                                            <ul className="grid w-56 grid-cols-4">
                                                <li>
                                                    <input
                                                        type="radio"
                                                        id="serve_W"
                                                        name="serve"
                                                        value="재직"
                                                        className="hidden peer"
                                                        required
                                                        defaultChecked={s.values.serve == '재직' ? true : false}
                                                        onChange={radioChange}
                                                    />
                                                    <label
                                                        htmlFor="serve_W"
                                                        className="inline-flex items-center justify-between w-full p-1 text-center text-gray-600 bg-white border border-r-0 border-gray-500 rounded-l-lg cursor-pointer peer-checked:bg-gray-500 peer-checked:text-white"
                                                    >
                                                        <div className="w-full">재직</div>
                                                    </label>
                                                </li>
                                                <li>
                                                    <input
                                                        type="radio"
                                                        id="serve_H"
                                                        name="serve"
                                                        value="휴직"
                                                        className="hidden peer"
                                                        required
                                                        defaultChecked={s.values.serve == '휴직' ? true : false}
                                                        onChange={radioChange}
                                                    />
                                                    <label
                                                        htmlFor="serve_H"
                                                        className="inline-flex items-center justify-between w-full p-1 text-center text-gray-600 bg-white border border-r-0 border-gray-500 cursor-pointer peer-checked:bg-gray-500 peer-checked:text-white"
                                                    >
                                                        <div className="w-full">휴직</div>
                                                    </label>
                                                </li>
                                                <li>
                                                    <input
                                                        type="radio"
                                                        id="serve_R"
                                                        name="serve"
                                                        value="퇴직"
                                                        defaultChecked={s.values.serve == '퇴직' ? true : false}
                                                        className="hidden peer"
                                                        onChange={radioChange}
                                                    />
                                                    <label
                                                        htmlFor="serve_R"
                                                        className="inline-flex items-center justify-between w-full p-1 text-center text-gray-600 bg-white border border-gray-500 rounded-r-lg cursor-pointer peer-checked:bg-gray-500 peer-checked:text-white"
                                                    >
                                                        <div className="w-full">퇴직</div>
                                                    </label>
                                                </li>
                                            </ul>
                                        </div>
                                        <div className="col-span-1">
                                            {/* 사번 */}
                                            <label className="form-label">사번</label>
                                            <input
                                                type="text"
                                                name="emp_no"
                                                value={s.values?.emp_no || ''}
                                                placeholder=""
                                                onChange={fn.handleChange}
                                                className={cls(s.errors['emp_no'] ? 'border-danger' : '', 'form-control')}
                                            />
                                        </div>
                                        <div className="col-span-1">
                                            {/* 부서 */}
                                            <label className="form-label">부서</label>
                                            <input
                                                type="text"
                                                name="depart"
                                                value={s.values?.depart || ''}
                                                placeholder=""
                                                onChange={fn.handleChange}
                                                className={cls(s.errors['depart'] ? 'border-danger' : '', 'form-control')}
                                            />
                                        </div>
                                        <div className="col-span-1">
                                            {/* 입사일 */}
                                            <label className="form-label">입사일</label>
                                            <Datepicker
                                                containerClassName="relative w-full text-gray-700 border border-gray-300 rounded"
                                                useRange={false}
                                                asSingle={true}
                                                inputName="join_com"
                                                i18n={'ko'}
                                                value={{
                                                    startDate: s.values?.join_com?.startDate || s.values?.join_com,
                                                    endDate: s.values?.join_com?.endDate || s.values?.join_com,
                                                }}
                                                onChange={fn.handleChangeDateRange}
                                            />
                                        </div>
                                        <div className="col-span-1">
                                            {/* 직급 */}
                                            <label className="form-label">직급</label>
                                            <input
                                                type="text"
                                                name="position"
                                                value={s.values?.position || ''}
                                                placeholder=""
                                                onChange={fn.handleChange}
                                                className={cls(s.errors['position'] ? 'border-danger' : '', 'form-control')}
                                            />
                                        </div>
                                        <div className="col-span-1">
                                            {/* 직책 */}
                                            <label className="form-label">직책</label>
                                            <input
                                                type="text"
                                                name="position2"
                                                value={s.values?.position2 || ''}
                                                placeholder=""
                                                onChange={fn.handleChange}
                                                className={cls(s.errors['position2'] ? 'border-danger' : '', 'form-control')}
                                            />
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="mt-5 w-full text-center">
                                <button className="mr-3 px-5 bg-blue-500 rounded-md py-2 text-white text-center" disabled={s.submitting}>
                                    저장
                                </button>
                            </div>
                        </div>

                        {daumModal && <DaumPost daumModal={daumModal} setDaumModal={setDaumModal} handleCompleteFormSet={handleCompleteFormSet} />}
                    </form>
                </div>
            </LayoutPopup>
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
        const { data } = await api.post(`/be/admin/member/read`, request);
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

export default MemberEdit;
