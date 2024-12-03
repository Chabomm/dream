import Layout from '@/components/Layout';
import { NextPage } from 'next';
import Link from 'next/link';

const Error500: NextPage = (props: any) => {
    const nav_id = '/500';
    const nav_name = 'Error500';
    return (
        <Layout user={props.user} title="indendkorea admin console" nav_id={0} crumbs={[]}>
            <div className="flex items-center justify-center error_page_conents">
                <section className="site-width py-24 text-center">
                    <div className="text-lg text-blue-700 font-bold">죄송합니다. 500 Error</div>
                    <div className="">서비스 이용에 불편을 드려 죄송합니다.</div>
                    <div className="">시스템 에러가 발생하여 페이지를 표시할 수 없습니다.</div>
                    <div className="">관리자에게 문의하시거나 잠시 후 다시 시도해주세요.</div>
                    <Link className="my-3 underline" href={`/`}>
                        홈으로
                    </Link>
                </section>
            </div>
        </Layout>
    );
};

export default Error500;
