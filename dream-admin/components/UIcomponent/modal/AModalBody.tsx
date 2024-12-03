export default function AModalBody(props: any) {
    const { children } = props;
    return <div className="overflow-y-auto">{children}</div>;
}
