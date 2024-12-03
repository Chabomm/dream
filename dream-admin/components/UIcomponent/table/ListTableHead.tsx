import { cls } from '@/libs/utils';

export default function ListTableHead(props: any) {
    const { children, className } = props;

    return (
        <thead className={cls('list-table-head', className)}>
            <tr>{children}</tr>
        </thead>
    );
}
