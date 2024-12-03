# https://umeshmk.github.io/Tailwindcss-cheatsheet/
# https://nerdcave.com/tailwind-cheat-sheet
# https://tailwindcomponents.com/components

# https://flowbite-react.com/modal/
# https://demos.creative-tim.com/soft-ui-dashboard-pro-tailwind/pages/pages/account/settings.html
# https://reactjsexample.com/tag/ui/

# fontawesome search
https://fontawesome.com/v5/search?o=r&m=free

# 개별페이지에 style 정의 (임시나 테스트용도로 사용 권장)
<style jsx>
    {`
        .back {
            padding: 10px;
            background-color: dodgerblue;
            color: white;
            margin: 10px;
        }
    `}
</style>

# foreach map
{posts.map((v: any, i: number) => (
    <div
        key={i}
        onClick={e => {
            godetail(v.uid);
        }}
    >
        <div className="back">
            <img src={v.thumb} />
            <strong> {v.title}</strong>
        </div>
    </div>
))}

# render에 작은따옴표
&lsquo;인천e몰&rsquo; => '인천e몰'


# set State 함수에 에러날때 (빌드용)
setTraces && setTraces(trace && []);

# state 값 render에서 확인
<pre className="mb-5">
    <div className="grid grid-cols-2 gap-4">
        <div>
            <div className="font-bold mb-3 text-red-500">filter</div>
            {JSON.stringify(filter, null, 4)}
        </div>
        <div>
            <div className="font-bold mb-3 text-red-500">s.values</div>
            {JSON.stringify(s.values, null, 4)}
        </div>
    </div>
</pre>

# sqlalc in절 검색
.in_


# nextjs 에서 json 파일 쓰기 (server side 에서 )
const fs = require('fs');
fs.writeFileSync('./example.json', JSON.stringify({}));

# [python] 
## 삼항연산자
[True일때] if a > 5 else [False일때]

import os
import json
import requests

# jsonable_encoder
from fastapi.encoders import jsonable_encoder
