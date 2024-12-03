import { cls } from '@/libs/utils';

export default function ListTableCaption({ children }) {
    return <div className={cls('list-table-caption flex justify-between items-center px-3')}>{children}</div>;
}
