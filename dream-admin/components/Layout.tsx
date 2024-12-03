import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';

import Footer from '@/components/Footer';
import Header from '@/components/Header';
import Seo from '@/components/Seo';
import Aside from '@/components/Aside';
import Breadcrumb from '@/components/Breadcrumb';
import { checkNumeric } from '@/libs/utils';

export default function Layout({ children, title, nav_id, crumbs, user }) {
    const router = useRouter();

    const [navis, setNavis] = useState<any[]>([]);

    useEffect(() => {
        const navi_list = JSON.parse(window.localStorage.getItem('admin_menus') + '');

        var is_permission = false;

        if (navi_list + '' !== 'null' && typeof navi_list !== 'undefined') {
            navi_list.map((v: any) => {
                v.children.map((vv: any) => {
                    if (checkNumeric(vv.uid) == checkNumeric(nav_id)) {
                        v.open = 'open';
                        vv.active = 'active';
                        is_permission = true;
                    }
                });
            });
            setNavis(navi_list);
        }

        if (!is_permission && nav_id != '') {
            router.replace('/');
        }
    }, [router]);

    return (
        <>
            <Seo title={title} />
            <div className="h-screen w-full overflow-hidden bg-gray-50">
                <div className="flex h-full">
                    <Aside navi_list={navis} user={user} />
                    <div id="page_contents" className="w-full overflow-y-auto">
                        <Header navi_list={navis} nav_id={nav_id} />
                        <div className="pt-20 px-6 flex-1">
                            <Breadcrumb navi_list={navis} crumbs={crumbs} nav_id={nav_id} />
                            {children}
                            <Footer />
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
}
