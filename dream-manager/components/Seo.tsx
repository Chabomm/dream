import Head from 'next/head';

export default function Seo({ title }) {
    return (
        <Head>
            <meta charSet="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1, user-scalable=no" />
            <meta name="description" content="indendkorea" />
            <meta name="keywords" content="indend,welfaredream" />
            <title>{`${title} | 기업과 임직원의 든든한 복지 파트너 복지드림`}</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" />
        </Head>
    );
}
