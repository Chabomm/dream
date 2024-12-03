import type { GetServerSideProps, NextPage } from 'next';
import React, { useState, useEffect } from 'react';
import { api, setContext } from '@/libs/axios';
import { useRouter } from 'next/router';
import { checkNumeric, cls, dateformatYYYYMMDD } from '@/libs/utils';
import useForm from '@/components/form/useForm';
import DaumPost from '@/components/DaumPost';
import LayoutPopup from '@/components/LayoutPopup';
import StaffEdit from '@/components/modal/staffEdit';
import { ReactSortable } from 'react-sortablejs';
import LogList from '@/components/modal/logList';
import AdminUserSearch from '@/components/searchBox/AdminUserSearch';

import {
    EditForm,
    EditFormTable,
    EditFormInput,
    EditFormTH,
    EditFormTD,
    EditFormSubmit,
    EditFormRadioList,
    EditFormCard,
    EditFormCardHead,
    EditFormCardBody,
    EditFormAddr,
    EditFormSelect,
    EditFormTextarea,
    EditFormLabel,
} from '@/components/UIcomponent/form/EditFormA';
import { ListTable, ListTableHead, ListTableBody } from '@/components/UIcomponent/table/ListTableA';

import EditFormCallout from '@/components/UIcomponent/form/EditFormCallout';

const MemberEdit: NextPage = (props: any) => {
    const crumbs = ['B2B 판매자'];
    const callout = [];
    const title_sub = '';

    const router = useRouter();
    const [user, setUser] = useState<any>({});
    const [posts, setPosts] = useState<any>({});
    const [filter, setFilter] = useState<any>({});

    const [sort, setSort] = useState<any>([]);
    const [staffSort, setStaffSort] = useState<any>([]);
    const [sortDiff, setSortDiff] = useState<boolean>(false);

    useEffect(() => {
        if (props) {
            setUser(props.user);
            setPosts(props.response);
            s.setValues(props.response.values);
            setStaffSort(props.response.staff_list);
            setFilter(props.response.filter);
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
            if (mode == 'REG' && posts?.uid > 0) {
                mode = 'MOD';
            }
            s.values.mode = mode;

            const { data } = await api.post(`/be/admin/b2b/seller/edit`, s.values);
            if (data.code == 200) {
                if (s.values.mode == 'REG') {
                    alert(data.msg);
                    router.replace(`/b2b/seller/edit?seller_uid=${data.uid}`);
                } else {
                    alert(data.msg);
                    if (s.values.mode == 'MOD') {
                        router.replace(`/b2b/seller/edit?seller_uid=${posts?.uid}`);
                    }
                }
            } else {
                alert(data.msg);
            }

            return;
        } catch (e: any) {}
    };

    // [ S ] 담당자 모달
    const [staffEditOpen, setStaffEditOpen] = useState(false);
    const [stateInfo, setStateInfo] = useState<any>();
    const openStaffEdit = (uid: number, mode: string, seller_uid: number) => {
        setStaffEditOpen(true);
        setStateInfo({
            uid,
            mode,
            seller_uid,
            seller_id: s.values.seller_id,
        });
    };
    // [ E ] 담당자 모달

    // [ S ] 순서변경
    useEffect(() => {
        if (sort.length == 0) {
            staffSort?.map((v: any) => {
                setSort(current => [...current, v.uid]);
            });
        } else {
            var sort_diff = false;
            staffSort?.map((v: any, i: number) => {
                if (v.uid != sort[i]) {
                    sort_diff = true;
                }
            });
            if (sort_diff) {
                setSort([]);
                staffSort?.map((v: any) => {
                    setSort(current => [...current, v.uid]);
                });
                setSortDiff(sort_diff);
            }
        }
    }, [staffSort]);

    const sorting = async () => {
        try {
            const p = {
                mode: 'SORT',
                uid: posts?.uid,
                sort_array: sort,
            };

            const { data } = await api.post(`/be/admin/b2b/seller/edit`, p);
            if (data.code == 200) {
                alert(data.msg);
                router.reload();
            } else {
                alert(data.msg);
            }
        } catch (e: any) {}
    };

    const sortableOptions = {
        animation: 150,
        handle: '.handle',
    };
    // [ E ] 순서변경

    const addMemo = async () => {
        if (s.values.memo == '' || typeof s.values.memo == 'undefined' || s.values.memo == null) {
            alert('메모를 입력해주세요.');
            return;
        }
        try {
            const p = {
                mode: 'MEMO',
                uid: posts?.uid,
                memo: s.values.memo,
            };

            const { data } = await api.post(`/be/admin/b2b/seller/edit`, p);
            if (data.code == 200) {
                alert(data.msg);
                router.reload();
            } else {
                alert(data.msg);
            }
        } catch (e: any) {}
    };

    // [ S ] 수정이력확인 모달
    const editLogList = (table_name: string, table_uid: number) => {
        window.open(`/setup/log/popup?table_name=${table_name}&table_uid=${table_uid}`, '로그리스트', 'width=1120,height=800,location=no,status=no,scrollbars=yes');
    };
    // [ E ] 수정이력확인 모달

    // [ S ] 담당MD변경 모달
    const [adminUserOpen, setAdminUserOpen] = useState(false);
    const openAdminUser = () => {
        setAdminUserOpen(true);
    };

    const getAdminUser = (uid: number, user_id: string, user_name: string, email: string, tel: string, mobile: string) => {
        const copy = { ...s.values };
        copy.indend_md_uid = uid;
        copy.indend_md = user_id;
        copy.indend_md_name = user_name;
        copy.indend_md_email = email;
        copy.indend_md_tel = tel;
        copy.indend_md_mobile = mobile;
        s.setValues(copy);
    };
    // [ E ] 담당MD변경 모달

    // [ S ] 파일 다운로드
    const handleImage = async (e: React.ChangeEvent<HTMLInputElement>, upload_path: string) => {
        const { name, value } = e.target;
        let file: any = null;
        if (e.target.files !== null) {
            file = e.target.files[0];
        }

        const formData = new FormData();
        formData.append('file_object', file);
        formData.append('upload_path', upload_path);

        const { data } = await api.post(`/be/aws/upload`, formData, { headers: { 'Content-Type': 'multipart/form-data' } });
        const input_name = (name + '').replace('-file', '');

        const copy = { ...s.values };
        copy[input_name] = data.s3_url;
        copy[input_name + '_fakename'] = data.fake_name;
        s.setValues(copy);

        e.target.value = '';
    };

    const download_file = async (file_kind: string) => {
        let file_link = '';
        if (file_kind == 'biz_file') {
            file_link = s.values.biz_file;
        } else {
            file_link = s.values.biz_hooper;
        }

        const arr_file_link = file_link.split('/');
        const file_name = arr_file_link[arr_file_link.length - 1];

        try {
            await api({
                url: `/be/aws/download`,
                method: 'POST',
                responseType: 'blob',
                data: {
                    file_url: file_link,
                },
            }).then(async response => {
                var fileURL = window.URL.createObjectURL(new Blob([response.data]));
                var fileLink = document.createElement('a');
                fileLink.href = fileURL;
                fileLink.setAttribute('download', file_name);
                document.body.appendChild(fileLink);
                fileLink.click();

                await api.post(`/be/aws/temp/delete`);
            });
        } catch (e: any) {
            console.log(e);
        }
    };
    // [ E ] 파일 다운로드

    return (
        <>
            <LayoutPopup title={crumbs[crumbs.length - 1]} className="px-6">
                <EditFormCallout title={crumbs[crumbs.length - 1]} title_sub={title_sub} callout={callout} />
                <EditForm onSubmit={fn.handleSubmit}>
                    <EditFormCard>
                        <EditFormCardHead>
                            <div className="text-lg">B2B 판매자 {posts.uid > 0 ? '수정' : '등록'}</div>
                        </EditFormCardHead>
                        <EditFormCardBody>
                            <EditFormTable className="grid-cols-6">
                                <EditFormTH className="col-span-1">판매자아이디</EditFormTH>
                                <EditFormTD className="col-span-5 gap-3">
                                    <EditFormInput
                                        type="text"
                                        name="seller_id"
                                        value={s.values?.seller_id || ''}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        className=""
                                        disabled
                                    />
                                    {posts.uid > 0 && (
                                        <div>
                                            <button
                                                className="px-3 rounded-md py-1 text-sm  text-white text-center bg-orange-500"
                                                type="button"
                                                onClick={() => {
                                                    editLogList('T_B2B_SELLER', posts?.uid);
                                                }}
                                            >
                                                수정이력확인
                                            </button>
                                        </div>
                                    )}
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">담당MD</EditFormTH>
                                <EditFormTD className="col-span-5">
                                    <EditFormInput
                                        type="text"
                                        name="indend_md"
                                        value={s.values?.indend_md || ''}
                                        is_mand={true}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        inputClassName={'!text-red-500 !rounded-none !rounded-s-md !border-r-0'}
                                        disabled
                                    />
                                    <EditFormInput
                                        type="text"
                                        name="indend_md_name"
                                        value={s.values?.indend_md_name || ''}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        inputClassName={'!text-red-500 !rounded-none'}
                                        disabled
                                    />
                                    <button
                                        className="h-8 leading-8 px-3 border rounded-none rounded-r-md border-l-0 shadow-none bg-gray-100"
                                        type="button"
                                        onClick={() => openAdminUser()}
                                    >
                                        담당MD{posts?.uid > 0 ? '변경' : '등록'}
                                    </button>
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">판매자명</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput
                                        type="text"
                                        name="seller_name"
                                        value={s.values?.seller_name || ''}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                        is_mand={true}
                                        className=""
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1">대표자명</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput type="text" name="ceo_name" value={s.values?.ceo_name || ''} onChange={fn.handleChange} errors={s.errors} className="" />
                                </EditFormTD>
                                <EditFormTH className="col-span-1">업태</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput type="text" name="biz_kind" value={s.values?.biz_kind || ''} onChange={fn.handleChange} errors={s.errors} className="" />
                                </EditFormTD>
                                <EditFormTH className="col-span-1">종목</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput type="text" name="biz_item" value={s.values?.biz_item || ''} onChange={fn.handleChange} errors={s.errors} className="" />
                                </EditFormTD>
                                <EditFormTH className="col-span-1">사업자등록번호</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput type="text" name="is_bizno" value={s.values?.is_bizno || ''} onChange={fn.handleChange} errors={s.errors} className="" />
                                </EditFormTD>
                                <EditFormTH className="col-span-1">사업자등록증첨부</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <div>
                                        <input
                                            name="biz_file"
                                            type="file"
                                            className={cls(s.errors['biz_file'] ? 'border-danger' : '', '')}
                                            accept="image/*"
                                            onChange={e => {
                                                handleImage(e, '/b2b/seller/biz_file/' + dateformatYYYYMMDD() + '/');
                                            }}
                                        />
                                        <button
                                            type="button"
                                            className="text-blue-500 underline cursor-pointe text-start"
                                            onClick={e => {
                                                download_file('biz_file');
                                            }}
                                        >
                                            {s.values?.biz_file_fakename != '' && typeof s.values?.biz_file_fakename != 'undefined'
                                                ? s.values?.biz_file_fakename
                                                : s.values?.biz_file}
                                        </button>
                                    </div>
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">사업장 소재지</EditFormTH>
                                <EditFormTD className="col-span-5">
                                    <EditFormAddr
                                        post="post"
                                        addr="addr"
                                        addr_detail="addr_detail"
                                        values={s.values}
                                        is_mand={true}
                                        set_values={s.setValues}
                                        onChange={fn.handleChange}
                                        errors={s.errors}
                                    />
                                </EditFormTD>

                                <EditFormTH className="col-span-1">정산주기</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormRadioList
                                        input_name="account_cycle"
                                        values={s.values?.account_cycle}
                                        filter_list={filter?.account_cycle}
                                        handleChange={fn.handleChange}
                                        errors={s.errors}
                                    />
                                </EditFormTD>
                                <EditFormTH className="col-span-1">세금계산서 메일주소</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <EditFormInput type="text" name="tax_email" value={s.values?.tax_email || ''} onChange={fn.handleChange} errors={s.errors} className="" />
                                </EditFormTD>
                                <EditFormTH className="col-span-1 mand">정산은행</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <div className="flex flex-col">
                                        <div className="flex">
                                            <EditFormSelect
                                                input_name="bank"
                                                value={s.values?.bank}
                                                filter_list={filter?.bank_list}
                                                onChange={fn.handleChange}
                                                className="!w-48"
                                            ></EditFormSelect>
                                            <EditFormInput
                                                type="text"
                                                name="depositor"
                                                value={s.values?.depositor || ''}
                                                onChange={fn.handleChange}
                                                errors={s.errors}
                                                is_mand={true}
                                                placeholder={'예금주'}
                                            />
                                        </div>

                                        <EditFormInput
                                            type="text"
                                            name="account"
                                            value={s.values?.account || ''}
                                            onChange={fn.handleChange}
                                            errors={s.errors}
                                            is_mand={true}
                                            placeholder={'계좌번호를 입력하세요.'}
                                        />
                                    </div>
                                    {s.errors['bank'] ? (
                                        <div className="form-error">{s.errors['bank']}</div>
                                    ) : s.errors['account'] ? (
                                        <div className="form-error">{s.errors['account']}</div>
                                    ) : (
                                        s.errors['depositor'] && <div className="form-error">{s.errors['depositor']}</div>
                                    )}
                                </EditFormTD>
                                <EditFormTH className="col-span-1">통장사본첨부</EditFormTH>
                                <EditFormTD className="col-span-2">
                                    <div>
                                        <input
                                            name="biz_hooper"
                                            type="file"
                                            className={cls(s.errors['biz_hooper'] ? 'border-danger' : '', '')}
                                            accept="image/*"
                                            onChange={e => {
                                                handleImage(e, '/b2b/seller/biz_hooper/' + dateformatYYYYMMDD() + '/');
                                            }}
                                        />
                                        <button
                                            type="button"
                                            className="text-start text-blue-500 underline cursor-pointer"
                                            onClick={e => {
                                                download_file('biz_hooper');
                                            }}
                                        >
                                            {s.values?.biz_hooper_fakename != '' && typeof s.values?.biz_hooper_fakename != 'undefined'
                                                ? s.values?.biz_hooper_fakename
                                                : s.values?.biz_hooper}
                                        </button>
                                    </div>
                                </EditFormTD>
                            </EditFormTable>
                            <EditFormSubmit button_name={`${checkNumeric(router.query.seller_uid) > 0 ? '수정' : '저장'}하기`} submitting={s.submitting}></EditFormSubmit>
                        </EditFormCardBody>
                    </EditFormCard>

                    {posts?.uid > 0 && (
                        <EditFormCard>
                            <EditFormCardHead>
                                <div className="text-lg">
                                    <div>
                                        <span className="text-xl font-bold me-3">관리자메모</span>
                                        <span className="text-red-500 text-base">관리자메모는 [수정하기]와 별개로 바로 저장됩니다.</span>
                                    </div>
                                </div>
                            </EditFormCardHead>
                            <EditFormCardBody>
                                <EditFormTable className="grid-cols-6">
                                    <EditFormTH className="col-span-1">관리자메모</EditFormTH>
                                    <EditFormTD className="col-span-5">
                                        <div className="w-full">
                                            <EditFormTextarea
                                                name="memo"
                                                value={s.values?.memo || ''}
                                                rows={4}
                                                placeholder="메모를 입력하세요"
                                                errors={s.errors}
                                                values={s.values}
                                                set_values={s.setValues}
                                            />
                                            <div className="mt-1 text-sm">
                                                <span className="me-2">
                                                    {user.user_name}({user.user_id})
                                                </span>
                                                <button
                                                    className="btn-search-line px-2 py-1"
                                                    type="button"
                                                    onClick={() => {
                                                        addMemo();
                                                    }}
                                                >
                                                    관리자메모추가
                                                </button>
                                            </div>
                                        </div>
                                    </EditFormTD>
                                </EditFormTable>
                                {posts.memo_list?.length > 0 &&
                                    posts.memo_list?.map((v: any, i: number) => (
                                        <div key={i}>
                                            <EditFormTable className="grid-cols-6 !border-t-0">
                                                <EditFormTH className="col-span-1">{v.create_user}</EditFormTH>
                                                <EditFormTD className="col-span-5">{v.memo}</EditFormTD>
                                            </EditFormTable>
                                        </div>
                                    ))}
                            </EditFormCardBody>
                        </EditFormCard>
                    )}
                    {posts?.uid > 0 && (
                        <EditFormCard>
                            <EditFormCardHead>
                                <div className="text-lg">
                                    <span className="text-xl font-bold me-3">판매자 담당자 정보</span>
                                    <span className="text-red-500 text-base">판매자담당자 정보는 [수정하기]와 별개로 바로 저장됩니다.</span>
                                </div>
                                <button
                                    className="px-3 rounded-md py-1 text-sm  text-white text-center bg-orange-500"
                                    type="button"
                                    onClick={() => {
                                        editLogList('T_B2B_SELLER_STAFF', posts.uid);
                                    }}
                                >
                                    수정이력확인
                                </button>
                            </EditFormCardHead>
                            <EditFormCardBody>
                                <div className="flex justify-between items-center mb-4">
                                    <button
                                        className="btn-search-line px-2 py-1"
                                        type="button"
                                        onClick={() => {
                                            openStaffEdit(0, 'REG', posts?.uid);
                                        }}
                                    >
                                        신규담당자 추가
                                    </button>
                                </div>

                                {sortDiff && (
                                    <div className="py-5">
                                        <button
                                            type="button"
                                            className="btn-funcs"
                                            onClick={() => {
                                                sorting();
                                            }}
                                        >
                                            순서 적용하기
                                        </button>
                                        <div className="text-red-600 font-bold ml-5">순서가 변경되었습니다. 적용하기 버튼을 클릭하여 저장해 주세요</div>
                                    </div>
                                )}
                                <ListTable>
                                    <ListTableHead>
                                        <th>순서</th>
                                        <th>구분</th>
                                        <th>담당자명</th>
                                        <th>일반전화</th>
                                        <th>휴대전화</th>
                                        <th>알림톡수신</th>
                                        <th>이메일</th>
                                        <th>이메일수신</th>
                                        <th>수정/삭제</th>
                                    </ListTableHead>

                                    {/* <ListTableBody> list-table-body */}
                                    <ReactSortable tag="tbody" className="list-table-body" {...sortableOptions} list={staffSort} setList={setStaffSort}>
                                        {staffSort?.map((v: any, i: number) => (
                                            <tr key={`list-table-${i}`} className="">
                                                <td className="handle">
                                                    <div className="flex items-center justify-center border p-3 rounded bg-slate-50">
                                                        <i className="fas fa-sort me-2"></i>
                                                        <div className="font-semibold">{v.sort}</div>
                                                    </div>
                                                </td>
                                                <td className="">{v.roles_txt}</td>
                                                <td className="break-all">{v.name}</td>
                                                <td className="">{v.tel}</td>

                                                <td className="">{v.mobile}</td>
                                                <td className="">{v.alarm_kakao == 'T' ? '수신' : '미수신'}</td>
                                                <td className="">{v.email}</td>
                                                <td className="">{v.alarm_email == 'T' ? '수신' : '미수신'}</td>
                                                <td className="">
                                                    <div className="flex gap-2">
                                                        <button
                                                            className="btn-search-line !p-2"
                                                            type="button"
                                                            onClick={() => {
                                                                openStaffEdit(v.uid, 'MOD', v.seller_uid);
                                                            }}
                                                        >
                                                            수정
                                                        </button>
                                                        <button
                                                            className="btn-red-line !p-2"
                                                            type="button"
                                                            onClick={() => {
                                                                openStaffEdit(v.uid, 'DEL', v.seller_uid);
                                                            }}
                                                        >
                                                            삭제
                                                        </button>
                                                        <button
                                                            className="btn-green-line !p-2"
                                                            type="button"
                                                            onClick={() => {
                                                                openStaffEdit(v.uid, 'COPY', v.seller_uid);
                                                            }}
                                                        >
                                                            복사
                                                        </button>
                                                    </div>
                                                </td>
                                            </tr>
                                        ))}
                                    </ReactSortable>
                                    {/* </ListTableBody> */}
                                </ListTable>
                            </EditFormCardBody>
                        </EditFormCard>
                    )}
                </EditForm>
                {adminUserOpen && <AdminUserSearch setAdminUserOpen={setAdminUserOpen} sandAdminUser={getAdminUser} />}
                {staffEditOpen && <StaffEdit setStaffEditOpen={setStaffEditOpen} stateInfo={stateInfo} />}
            </LayoutPopup>
        </>
    );
};
export const getServerSideProps: GetServerSideProps = async ctx => {
    setContext(ctx);
    var request: any = {
        uid: ctx.query.seller_uid,
    };
    var response: any = {};
    try {
        const { data } = await api.post(`/be/admin/b2b/seller/read`, request);
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
