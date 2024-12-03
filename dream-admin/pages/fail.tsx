import type { NextPage, NextPageContext } from 'next';
import React from 'react';
import { useRouter } from 'next/router';

const Fail: NextPage = props => {
    const router = useRouter();

    return <>fail</>;
};

export default Fail;
