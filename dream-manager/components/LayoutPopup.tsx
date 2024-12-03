import React from 'react';
import Seo from '@/components/Seo';
import { cls } from '@/libs/utils';

export default function LayoutPopup({ children, title, className }: any) {
    return (
        <div className={cls(className, 'pb-20 h-screen overflow-y-auto')}>
            <Seo title={title} />
            {children}
        </div>
    );
}
