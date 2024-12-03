import type { NextPage } from 'next';
import React from 'react';
import Layout from '@/components/Layout';
import IntranetBoardPostList from './board/list';

const NoticeWelfare: NextPage = (props: any) => {
    return (
        <Layout user={props.user} title="indendkorea admin console" nav_id={109} crumbs={['공지사항', '사내 복지정보']}>
            <IntranetBoardPostList board_uid={4} user={props.user} />
        </Layout>
    );
};

export default NoticeWelfare;
