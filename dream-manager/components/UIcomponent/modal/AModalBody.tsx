/*
    last update : 2024-01-24
    필수 : childen
    [2024-01-24] className by.namgu
*/

export default function AModalBody(props: any) {
    const { children, className } = props;
    return <div className={`overflow-y-auto ${className}`}>{children}</div>;
}
