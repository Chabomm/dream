import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
    return (
        <Html lang="ko">
            <Head>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" />
                <link rel="stylesheet" href="/resource/_lib/CKEditor.css" />
            </Head>
            <body>
                <Main />
                <NextScript />
            </body>
        </Html>
    );
}
