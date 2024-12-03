export default function ButtonGray({ children, onClick }) {
    return (
        <>
            <button type="button" className="btn-gray" onClick={onClick}>
                <div>{children}</div>
            </button>
            <style jsx>{`
                .btn-gray {
                    background-color: #fff;
                    padding: 0.3rem 0.6rem;
                    border: 1px solid #ccc;
                    font-size: 0.85rem;
                }
            `}</style>
        </>
    );
}
