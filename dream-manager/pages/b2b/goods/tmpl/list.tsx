import React, { useState, useEffect } from 'react';
import { api } from '@/libs/axios';
import { useRouter } from 'next/router';
import ListPagenation from '@/components/bbs/ListPagenation';
import { cls, getToken } from '@/libs/utils';
import useForm from '@/components/form/useForm';

function B2bGoodsTmplList(props: any) {
    const [filter, setFilter] = useState<any>({});
    const [params, setParams] = useState<any>({});
    const [posts, setPosts] = useState<any>([]);

    useEffect(() => {
        if (props) {
            setFilter(props.response.filter);
            setParams(props.response.params);
            s.setValues(props.response.params.filters);
            getPagePost(props.response.params);
        }
    }, [props]);

    const getPagePost = async p => {
        let newPosts = await getPostsData(p);
        setPosts(newPosts.list);
    };

    const getPostsData = async p => {
        try {
            const { data } = await api.post(`/be/manager/b2b/goods/list`, p);
            setParams(data.params);
            return data;
        } catch (e: any) {}
    };

    const { s, fn } = useForm({
        onSubmit: async () => {
            await searching();
        },
    });

    const searching = async () => {
        params.filters = s.values;
        let newPosts = await getPostsData(params);
        setPosts(newPosts.list);
    };

    const [cateValue, setCateValue] = useState<any>('');
    const openList = async (value: string) => {
        setCateValue(value);
        params.filters.category = value;
        let newPosts = await getPostsData(params);
        setPosts(newPosts.list);
    };

    const detail_info = async (service_uid: number) => {
        try {
            const { data } = await api.post(`/be/manager/b2b/order/detail`, {
                service_uid: service_uid,
                partner_uid: props.user.partner_uid,
                user_uid: props.user.user_uid,
            });
            return data;
        } catch (e) {}
    };

    const openDetail = async (guid: number) => {
        let newPosts = await detail_info(guid);

        let b2b_center_domain = `http://localhost:13000`;
        if (`${process.env.NODE_ENV}` == 'production') {
            b2b_center_domain = `https://`;
        }

        var newForm = document.createElement('form');
        newForm.setAttribute('method', 'POST');

        var newInput = document.createElement('input');
        newInput.setAttribute('type', 'hidden');
        newInput.setAttribute('name', 'token');
        newInput.setAttribute('value', getToken(undefined));
        newForm.appendChild(newInput);

        var newInput = document.createElement('input');
        newInput.setAttribute('type', 'hidden');
        newInput.setAttribute('name', 'guid');
        newInput.setAttribute('value', guid + '');
        newForm.appendChild(newInput);

        var newInput = document.createElement('input');
        newInput.setAttribute('type', 'hidden');
        newInput.setAttribute('name', 'company_name');
        newInput.setAttribute('value', newPosts.company_name);
        newForm.appendChild(newInput);

        var newInput = document.createElement('input');
        newInput.setAttribute('type', 'hidden');
        newInput.setAttribute('name', 'depart');
        newInput.setAttribute('value', newPosts.manager.depart);
        newForm.appendChild(newInput);

        var newInput = document.createElement('input');
        newInput.setAttribute('type', 'hidden');
        newInput.setAttribute('name', 'position1');
        newInput.setAttribute('value', newPosts.manager.position1);
        newForm.appendChild(newInput);

        var newInput = document.createElement('input');
        newInput.setAttribute('type', 'hidden');
        newInput.setAttribute('name', 'mobile');
        newInput.setAttribute('value', newPosts.manager.mobile);
        newForm.appendChild(newInput);

        var newInput = document.createElement('input');
        newInput.setAttribute('type', 'hidden');
        newInput.setAttribute('name', 'email');
        newInput.setAttribute('value', newPosts.manager.email);
        newForm.appendChild(newInput);

        document.body.appendChild(newForm);

        var objPopup = window.open('', 'b2b_goods_view', 'width=1120,height=800, scrollbars=no, toolbar=no, status=no, resizable=no'); //창띄우기 명령에서 그 경로는 빈칸으로 한다.
        newForm.target = 'b2b_goods_view'; // 타겟 : 위의 창띄우기의 창이름과 같아야 한다.
        newForm.action = b2b_center_domain + `/inbound/goods?guid=${guid}`; // 액션경로
        if (objPopup == null) alert('차단된 팝업창을 허용해 주세요'); // 팝업이 뜨는지 확인
        else {
            newForm.submit();
            objPopup.focus(); //새로 띄워준 창에 포커스를 맞춰준다.
        }
    };

    return (
        <>
            <div className="" style={{ maxWidth: '1270px' }}>
                <div className="py-5 flex gap-4">
                    {filter.category?.map((v: any, i: number) => (
                        <div
                            key={i}
                            className={cls(
                                `border rounded-full py-2 px-4 leading-none cursor-pointer text-sm font-semibold ${
                                    cateValue == v.key ? 'bg-blue-500 text-white ' : 'bg-white text-slate-700'
                                }`
                            )}
                            onClick={() => openList(v.key)}
                        >
                            {v.text}
                        </div>
                    ))}
                </div>
                {posts?.length > 0 ? (
                    <div className="py-5">
                        <div className="grid grid-cols-4 gap-7">
                            {posts.map((v: any, i: number) => (
                                <div key={i} className="border rounded-md hover:border-black hover:cursor-pointer bg-white flex flex-col" onClick={() => openDetail(v.uid)}>
                                    <div>
                                        <img src={v.thumb} className="w-full rounded-t-md" />
                                    </div>
                                    <div className="p-3 h-full">
                                        <div className="flex flex-col justify-between h-full">
                                            <div>
                                                <div className="bg-gray-500 text-white text-xs leading-none py-1 px-2 rounded-md inline-block">{v.category}</div>
                                                <div className="mt-3 text-lg font-semibold">{v.title}</div>
                                            </div>
                                            <div className="mt-2 text-gray-500 text-sm">
                                                {v.keyword?.map((vv: any, ii: number) => (
                                                    <span key={ii}>#{vv} </span>
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                ) : (
                    <div className="p-10">서비스가 없습니다.</div>
                )}
                <ListPagenation props={params} getPagePost={getPagePost} />
            </div>
        </>
    );
}

export default B2bGoodsTmplList;
