import React, { useState } from 'react';
import DaumPostCode from 'react-daum-postcode';

interface Props {
    daumModal?: any;
    setDaumModal?: any;
    handleCompleteFormSet?: any;
}

export default function DaumPost({ daumModal, setDaumModal, handleCompleteFormSet }: Props) {
    const [open, setOpen] = useState<boolean>(false);
    const [show, setShow] = useState<boolean>(false);

    const onToggle = () => {
        setShow(!open);
        setOpen(!open);
    };

    const handleComplete = (data: any) => {
        handleCompleteFormSet(data);
        closeModal();
    };

    const closeModal = () => {
        setDaumModal(false);
    };

    return (
        <>
            <div className="daum-popup flex fixed">
                <div className="relative w-80 mx-auto max-w-sm">
                    <div className="shadow-lg relatives flex flex-col w-full bg-white outline-none focus:outline-none py-3">
                        <DaumPostCode onComplete={handleComplete} autoClose className="post-code" />
                    </div>
                </div>
            </div>
            <div className="offcanvas-backdrop fade" onClick={closeModal}></div>
        </>
    );
}
