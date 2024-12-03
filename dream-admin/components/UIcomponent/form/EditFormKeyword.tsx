import { cls } from '@/libs/utils';

export default function EditFormKeyword({ skeyword_values, skeyword_type_values, skeyword_type_filter, handleChange, errors }) {
    return (
        <>
            <select
                name="skeyword_type"
                value={skeyword_type_values}
                onChange={handleChange}
                className={cls(errors['skeyword_type'] ? 'border-danger' : '', 'form-select mr-3')}
                style={{ width: 'auto' }}
            >
                <option value="">전체</option>
                {skeyword_type_filter?.map((v: any, i: number) => (
                    <option key={i} value={v.key}>
                        {v.text}
                    </option>
                ))}
            </select>
            <input
                type="text"
                name="skeyword"
                value={skeyword_values || ''}
                placeholder=""
                onChange={handleChange}
                className={cls(errors['skeyword'] ? 'border-danger' : '', 'form-control mr-3')}
                style={{ width: 'auto' }}
            />
        </>
    );
}
