export default function EditFormFileUploading(props: any) {
    // const { title, title_sub, callout } = props;
    return (
        <div className="fixed w-full left-0 top-0 h-screen bg-opacity-25 bg-white z-10 flex items-center justify-center">
            <div className="text-lg bg-white px-5 py-3 border rounded">
                <i className="fas fa-spinner me-2"></i>파일 업로드 중 ...
            </div>
        </div>
    );
}
