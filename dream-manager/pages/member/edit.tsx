import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import useForm from '@/components/form/useForm';
import LayoutPopup from '@/components/LayoutPopup';
import {
    EditForm,
    EditFormTable,
    EditFormTH,
    EditFormTD,
    EditFormRadioList,
    EditFormSubmit,
    EditFormInput,
    EditFormLabel,
    EditFormAddr,
    EditFormInputGroup,
    EditFormDate,
    EditFormCheckboxList,
} from '@/components/UIcomponent/form/EditFormA';
import EditFormCallout from '@/components/UIcomponent/form/EditFormCallout';

const MemberEdit: NextPage = (props: any) => {
    const nav_id = 56;
    const crumbs = ['임직원 관리', '임직원 ' + (props.response.values?.uid > 0 ? '수정' : '등록')];
    const callout = [];
    const title_sub = '임직원을 등록/수정할 수 있습니다';
    const router = useRouter();

    const [posts, setPosts] = useState<any>({});
    const [filter, setFilter] = useState<any>({});

    useEffect(() => {
        if (props) {
            if (props.response.code == 200) {
                setPosts(props.response);
                setFilter(props.response.filter);
                s.setValues(props.response.values);
            } else {
                alert(props.response.msg);
                // window.close();
            }
        }
    }, []);

    const { s, fn, attrs } = useForm({
        onSubmit: async () => {
            await editing('REG');
        },
    });

    const deleting = () => editing('DEL');

    const editing = async mode => {
        try {
            const params = { ...s.values };

            if (mode == 'REG' && params.uid > 0) {
                mode = 'MOD';
            }

            if (!params.is_memberid_checked && params.uid == 0) {
                alert('아이디 중복검사를 수행해 주세요');
                const el = document.querySelector("input[name='login_id']");
                (el as HTMLElement)?.focus();
                return;
            }

            if (params.birth == undefined || params.birth == '') {
                alert('생년월일을 입력해주세요');
                const el = document.querySelector("input[name='birth']");
                (el as HTMLElement)?.focus();
                return;
            }

            params.mode = mode;
            params.board_uid = 1;
            params.user_id = params.prefix + params.login_id;

            if (params.anniversary?.startDate != undefined) {
                params.anniversary = params.anniversary.startDate;
            }
            if (params.join_com?.startDate != undefined) {
                params.join_com = params.join_com?.startDate;
            }

            const { data } = await api.post(`/be/manager/member/edit`, params);
            s.setSubmitting(false);
            if (data.code == 200) {
                alert(data.msg);
            } else {
                alert(data.msg);
            }
        } catch (e: any) {}
    };

    // 도메인(input) 변경 되면
    const handleBlur = async () => {
        const copy = { ...s.values };
        if (copy.login_id == '' || s.values.login_id != copy.memberid_check_value) {
            copy.memberid_check_value = '';
            copy.is_memberid_checked = false;
            s.setValues(copy);
        }
    };

    // 아이디 중복체크
    const memberIdCheck = async () => {
        try {
            const copy = { ...s.values };

            const item = {
                memberid_input_value: copy.login_id, // 체크할 값
                memberid_check_value: '', // 이전에 체크한 값
                is_memberid_checked: false, // 이전에 체크 했는지
                prefix: copy.prefix,
            };

            copy.memberid_input_value = item.memberid_input_value;
            copy.memberid_check_value = item.memberid_check_value;
            copy.is_memberid_checked = item.is_memberid_checked;

            if (item.memberid_input_value.length < 4 || item.memberid_input_value.length > 20) {
                alert('관리자 아이디는 영문 혹은 숫자 4자~20자리로 해주세요.');
                copy.is_memberid_checked = false;
                return;
            }
            const { data } = await api.post(`/be/manager/member/check`, item);
            if (data.code == 200) {
                alert('사용가능한 아이디입니다.');
                copy.memberid_check_value = item.memberid_input_value;
                copy.is_memberid_checked = true;
                s.setValues(copy);
            } else {
                alert('이미 사용중인 아이디입니다.');
                copy.memberid_check_value = '';
                copy.is_memberid_checked = false;
                s.setValues(copy);
            }
        } catch (e: any) {}
    };

    return (
        <LayoutPopup title={crumbs[crumbs.length - 1]} className="px-3">
            <EditFormCallout title={crumbs[crumbs.length - 1]} title_sub={title_sub} callout={callout} />

            <EditForm onSubmit={fn.handleSubmit}>
                <EditFormTable className="grid-cols-6">
                    <EditFormTH className="col-span-1 mand">아이디</EditFormTH>
                    <EditFormTD className="col-span-2">
                        {s.values?.uid > 0 ? (
                            <EditFormLabel className="">{posts?.login_id}</EditFormLabel>
                        ) : (
                            <div className="flex flex-col">
                                <EditFormInputGroup
                                    type="text"
                                    name="login_id"
                                    value={s.values?.login_id || ''}
                                    is_mand={true}
                                    onChange={fn.handleChange}
                                    errors={s.errors}
                                    className=""
                                    autoComplete="new-password"
                                    button_name="중복체크"
                                    button_click={memberIdCheck}
                                />
                                <div>{s.values?.memberid_check_value == '' && <div className="text-sm text-red-500 pt-2">아이디 중복확인을 해주세요</div>}</div>
                                <div className="pt-2 text-xs text-gray-500">4~20자리 이내, 띄어쓰기 없이 영문 소문자 또는 숫자만 가능</div>
                            </div>
                        )}
                    </EditFormTD>
                    <EditFormTH className="col-span-1 mand">이름</EditFormTH>
                    <EditFormTD className="col-span-2">
                        <EditFormInput
                            type="text"
                            name="user_name"
                            value={s.values?.user_name || ''}
                            is_mand={true}
                            autoComplete="new-password"
                            onChange={fn.handleChange}
                            errors={s.errors}
                            className=""
                        />
                    </EditFormTD>
                    <EditFormTH className="col-span-1 mand">성별</EditFormTH>
                    <EditFormTD className="col-span-2">
                        <EditFormRadioList
                            input_name="gender"
                            values={s.values?.gender}
                            filter_list={[
                                { key: '남자', text: '남자' },
                                { key: '여자', text: '여자' },
                            ]}
                            is_mand={true}
                            errors={s.errors}
                            handleChange={fn.handleChange}
                        />
                    </EditFormTD>
                    <EditFormTH className="col-span-1 mand">재직여부</EditFormTH>
                    <EditFormTD className="col-span-2">
                        <EditFormRadioList
                            input_name="serve"
                            values={s.values?.serve}
                            filter_list={[
                                { key: '재직', text: '재직' },
                                { key: '휴직', text: '휴직' },
                                { key: '퇴직', text: '퇴직' },
                            ]}
                            is_mand={true}
                            errors={s.errors}
                            handleChange={fn.handleChange}
                        />
                    </EditFormTD>
                    <EditFormTH className="col-span-1 mand">복지몰 로그인</EditFormTH>
                    <EditFormTD className="col-span-2">
                        <EditFormRadioList
                            input_name="is_login"
                            values={s.values?.is_login}
                            filter_list={[
                                { key: 'T', text: '가능' },
                                { key: 'F', text: '불가능' },
                            ]}
                            is_mand={true}
                            errors={s.errors}
                            handleChange={fn.handleChange}
                        />
                    </EditFormTD>
                    <EditFormTH className="col-span-1 mand">포인트사용</EditFormTH>
                    <EditFormTD className="col-span-2">
                        <EditFormRadioList
                            input_name="is_point"
                            values={s.values?.is_point}
                            filter_list={[
                                { key: 'T', text: '가능' },
                                { key: 'F', text: '불가능' },
                            ]}
                            is_mand={true}
                            errors={s.errors}
                            handleChange={fn.handleChange}
                        />
                    </EditFormTD>
                    <EditFormTH className="col-span-1 mand">휴대전화</EditFormTH>
                    <EditFormTD className="col-span-2">
                        <EditFormInput
                            type="text"
                            name="mobile"
                            value={s.values?.mobile || ''}
                            is_mand={true}
                            is_mobile={true}
                            placeholder="ex) 010-1234-1234"
                            autoComplete="new-password"
                            onChange={fn.handleChange}
                            errors={s.errors}
                            className=""
                        />
                    </EditFormTD>
                    <EditFormTH className="col-span-1 mand">이메일</EditFormTH>
                    <EditFormTD className="col-span-2">
                        <EditFormInput
                            type="text"
                            name="email"
                            value={s.values?.email || ''}
                            is_mand={true}
                            is_email={true}
                            placeholder="ex) example@naver.com"
                            autoComplete="new-password"
                            onChange={fn.handleChange}
                            errors={s.errors}
                            className=""
                        />
                    </EditFormTD>
                    <EditFormTH className="col-span-1">주소</EditFormTH>
                    <EditFormTD className="col-span-2">
                        <EditFormAddr post="post" addr="addr" addr_detail="addr_detail" values={s.values} set_values={s.setValues} onChange={fn.handleChange} errors={s.errors} />
                    </EditFormTD>

                    <EditFormTH className="col-span-1 mand">생년월일</EditFormTH>
                    <EditFormTD className="col-span-2">
                        <EditFormDate input_name="birth" values={s.values?.birth} is_mand={true} errors={s.errors} handleChange={fn.handleChangeDate} />
                    </EditFormTD>

                    <EditFormTH className="col-span-1">기념일</EditFormTH>
                    <EditFormTD className="col-span-2">
                        <EditFormDate input_name="anniversary" values={s.values?.anniversary} errors={s.errors} handleChange={fn.handleChangeDate} />
                    </EditFormTD>

                    <EditFormTH className="col-span-1">사번</EditFormTH>
                    <EditFormTD className="col-span-2">
                        <EditFormInput
                            type="text"
                            name="emp_no"
                            value={s.values?.emp_no || ''}
                            placeholder="사번을 입력하세요"
                            autoComplete="new-password"
                            onChange={fn.handleChange}
                            errors={s.errors}
                            className=""
                        />
                    </EditFormTD>
                    <EditFormTH className="col-span-1">부서</EditFormTH>
                    <EditFormTD className="col-span-2">
                        <EditFormInput
                            type="text"
                            name="depart"
                            value={s.values?.depart || ''}
                            placeholder="부서를 입력하세요"
                            autoComplete="new-password"
                            onChange={fn.handleChange}
                            errors={s.errors}
                            className=""
                        />
                    </EditFormTD>
                    <EditFormTH className="col-span-1">직급</EditFormTH>
                    <EditFormTD className="col-span-2">
                        <EditFormInput
                            type="text"
                            name="position"
                            value={s.values?.position || ''}
                            placeholder="직급을 입력하세요"
                            autoComplete="new-password"
                            onChange={fn.handleChange}
                            errors={s.errors}
                            className=""
                        />
                    </EditFormTD>
                    <EditFormTH className="col-span-1">직책</EditFormTH>
                    <EditFormTD className="col-span-2">
                        <EditFormInput
                            type="text"
                            name="position2"
                            value={s.values?.position2 || ''}
                            placeholder="직책을 입력하세요"
                            autoComplete="new-password"
                            onChange={fn.handleChange}
                            errors={s.errors}
                            className=""
                        />
                    </EditFormTD>

                    <EditFormTH className="col-span-1">입사일</EditFormTH>
                    <EditFormTD className="col-span-2">
                        <EditFormDate input_name="join_com" values={s.values?.join_com} errors={s.errors} handleChange={fn.handleChangeDate} />
                    </EditFormTD>
                </EditFormTable>
                <EditFormSubmit button_name={`${s.values?.uid > 0 ? '수정' : '등록'}하기`} submitting={s.submitting}></EditFormSubmit>
            </EditForm>
        </LayoutPopup>
    );
};
export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {
        uid: ctx.query.uid,
    };
    var response: any = {};
    try {
        const { data } = await api.post(`/be/manager/member/read`, request);
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
