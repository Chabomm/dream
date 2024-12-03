import { cls } from '@/libs/utils';

export default function ListTableBody(props: any) {
    const { children } = props;
    return <tbody className={cls('list-table-body')}>{children}</tbody>;
}
