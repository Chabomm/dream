import React, { useState, forwardRef, useImperativeHandle, useRef } from 'react';
import { cls } from '@/libs/utils';

const OverlayFilter = forwardRef((props, ref) => {
    const [open, setOpen] = useState<boolean>(false);
    const onToggle = () => setOpen(!open);

    useImperativeHandle(ref, () => ({
        init,
    }));

    const [filter, setFilter] = useState<any>({});
    function init(v: any) {
        setFilter(v);
        onToggle();
    }

    return (
        <>
            {open && (
                <div className="absolute bg-white border z-20 shadow-sm left-96 mt-3 rounded">
                    <div className="overlay_backdrop z-10" onClick={onToggle}></div>
                    <div className="grid grid-cols-4 gap-6 py-3 px-1 relative z-20">
                        <div className="col-span-4">
                            <label className="form-label pt-3 px-3">고객사</label>
                            <div className="w-60 h-96 overflow-y-auto">
                                {filter.partner_id?.map((v: any, i: number) => (
                                    <label key={i} className="w-full px-3 py-2 block cursor-pointer bg-white hover:bg-slate-100 rounded">
                                        <input id={`partner_id-${i}`} type="checkbox" value={v.key} name="partner_id" className="me-3" />
                                        <span className="font-bold">{v.partner_id}</span>
                                    </label>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
});

OverlayFilter.displayName = 'OverlayFilter';
export default OverlayFilter;
