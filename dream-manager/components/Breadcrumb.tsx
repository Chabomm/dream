import Link from 'next/link';

export default function Breadcrumb(props: any) {
    const { crumbs, nav_id } = props;

    return (
        <>
            {crumbs.length > 0 && (
                <nav className="flex py-3 text-gray-700 rounded-lg bg-gray-50">
                    <ol className="flex items-center space-x-3">
                        <li className="flex items-center leading-none">
                            <i className="fas fa-home fa-xs mr-2"></i>
                            <Link href="/" className="text-sm font-medium text-gray-700 hover:text-gray-900 relative">
                                홈 <span className="text-gray-50 absolute top-4 left-0">{nav_id}</span>
                            </Link>
                        </li>
                        {crumbs?.map((v: any, i: number) => (
                            <li key={i} className="leading-none flex items-center">
                                <i className="fas fa-chevron-right fa-xs mr-3"></i>
                                <div className="text-sm font-medium text-gray-700 hover:text-gray-900">{v}</div>
                            </li>
                        ))}
                    </ol>
                </nav>
            )}
        </>
    );
}
