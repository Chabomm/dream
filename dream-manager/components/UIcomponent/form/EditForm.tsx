import { cls } from '@/libs/utils';

/*
    last update : 2024-01-02
    필수 : children, onSubmit
*/
export default function EditForm(props: any) {
    const { children, onSubmit, className } = props;
    return (
        <form onSubmit={onSubmit} className={cls('mx-auto', className)} noValidate>
            {children}
        </form>
    );
}
