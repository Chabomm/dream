import type { NextPage } from 'next';
import React from 'react';
import Layout from '@/components/Layout';
import IntranetBoardPostList from './board/list';

const NoticeManager: NextPage = (props: any) => {
    return (
        <Layout user={props.user} title="indendkorea admin console" nav_id={107} crumbs={['공지사항', '고객사 공지사항']}>
            <IntranetBoardPostList board_uid={3} user={props.user} />
        </Layout>
    );
};

export default NoticeManager;
