import { cls } from '@/libs/utils';

export default function Callout(props: any) {
    const { title, title_sub, callout } = props;
    return (
        <div className="callout">
            <div className="flex items-end mt-4 mb-5">
                <div className="text-2xl me-3">{title}</div>
                {title_sub && <div className="title_sub ms-3">{title_sub}</div>}
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
