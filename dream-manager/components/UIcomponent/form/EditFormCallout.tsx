/*
    last update : 2024-01-02
    필수 : title
    [2024-01-03] 페이지 헤더 담당, title_sub 있으면 랜더링
    [2024-01-03] callout은 최소 빈 배열 '[]' 을 보내줘야함.
*/

import { cls } from '@/libs/utils';

export default function EditformCallout(props: any) {
    const { title, title_sub, callout, className } = props;
    return (
        <div className={cls('callout', className)}>
            <div className="py-8 text-center">
                <div className="text-2xl mb-2">{title}</div>
                {title_sub && <div className="">{title_sub}</div>}
            </div>
            {callout.length > 0 && (
                <div className="shadow mb-5 border">
                    <div className="bd-callout-info text-sm">
                        {callout?.map((v: any, i: number) => (
                            <div className="bd-callout-item text-slate-600" key={`callout-${i}`} dangerouslySetInnerHTML={{ __html: v }}></div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
