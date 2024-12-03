import { cls } from '@/libs/utils';

export default function ListTable(props: any) {
    const { children, className } = props;
    return (
        <div className={cls(className)}>
            <div className={cls('list-table border-t border-t-black')}>
                <table className={cls('border-s border-gray-200')}>{children}</table>
            </div>
        </div>
    );
}
