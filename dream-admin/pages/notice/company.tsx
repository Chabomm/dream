import type { NextPage } from 'next';
import React, { useEffect } from 'react';
import Layout from '@/components/Layout';
import IntranetBoardPostList from './board/list';

const NoticeCompany: NextPage = (props: any) => {
    return (
        <Layout user={props.user} title="indendkorea admin console" nav_id={108} crumbs={['공지사항', '사내 공지사항']}>
            <IntranetBoardPostList board_uid={2} user={props.user} />
        </Layout>
    );
};

export default NoticeCompany;
