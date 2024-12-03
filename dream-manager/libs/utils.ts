export function cls(...classnames: string[]) {
    return classnames.join(' ');
}

export const checkNumeric = (x: any) => {
    try {
        var parsed = parseInt(x.toString().replace(/,/g, ''));
        if (isNaN(parsed)) {
            return 0;
        }
        return parsed;
    } catch (e) {
        return 0;
    }
};

export const null2Blank = (x: any) => {
    try {
        if (typeof x == 'undefined' || String(x) == 'null') {
            return '';
        } else {
            return String(x).trim();
        }
    } catch (e) {
        return '';
    }
};

export const flag2Bool = (x: any) => {
    try {
        if (typeof x === 'boolean') {
            return x;
        } else if (left(x, 1).toUpperCase() == 'T') {
            return true;
        } else if (left(x, 1).toUpperCase() == 'F') {
            return false;
        } else if (left(x, 1).toUpperCase() == 'Y') {
            return true;
        } else if (left(x, 1).toUpperCase() == 'N') {
            return false;
        } else {
            return false;
        }
    } catch (e) {
        return false;
    }
};

export function num2Cur(num: any) {
    if (typeof num === 'undefined' || num === null || num === '') {
        return 0;
    } else {
        return (num + '').toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }
}

export const dateToday = (date: any) => {
    if (typeof window === 'undefined') {
        return '';
    }
    const today = new Date();
    const timeValue = new Date(date);

    const betweenTime = Math.floor((today.getTime() - timeValue.getTime()) / 1000 / 60);
    if (betweenTime < 1) return '방금전';
    if (betweenTime < 60) {
        return `${betweenTime}분전`;
    }

    const betweenTimeHour = Math.floor(betweenTime / 60);
    if (betweenTimeHour < 24) {
        return `${betweenTimeHour}시간전`;
    }

    const betweenTimeDay = Math.floor(betweenTime / 60 / 24);
    if (betweenTimeDay > 365) {
        return dateformat(timeValue, 'YY.MM.DD');
    } else if (betweenTimeDay > 30) {
        return `${Math.floor(betweenTimeDay / 31)}개월전`;
    } else {
        return `${betweenTimeDay}일전`;
    }
};

export function dateformat(inputDate: any, f: any) {
    if (typeof inputDate === 'string') {
        inputDate = new Date(inputDate);
    }

    let date, month, year;

    date = inputDate.getDate();
    month = inputDate.getMonth() + 1;
    year = inputDate.getFullYear();
    date = date.toString().padStart(2, '0');
    month = month.toString().padStart(2, '0');

    if (f == 'YY.MM.DD') {
        return `${right(year + '', 2)}.${month}.${date}`;
    } else {
        return `${year}-${month}-${date}`;
    }
}

export function yyyymmdd_hhmmss() {
    let date, month, year, hours, minutes, second;
    date = new Date().getDate();
    month = new Date().getMonth() + 1;
    year = new Date().getFullYear();
    hours = new Date().getHours();
    minutes = new Date().getMinutes();
    second = new Date().getSeconds();

    date = date.toString().padStart(2, '0');
    month = month.toString().padStart(2, '0');
    year = year.toString().padStart(2, '0');
    hours = hours.toString().padStart(2, '0');
    minutes = minutes.toString().padStart(2, '0');
    second = second.toString().padStart(2, '0');

    return `${year}${month}${date}_${hours}${minutes}${second}`;
}

// left("abcd",2)
export function left(s: any, c: any) {
    return s.substr(0, c);
}

// right("abcd",2)
export function right(s: any, c: any) {
    return s.substr(-c);
}

// mid("abcd",1,2)
export function mid(s: any, c: any, l: any) {
    return s.substring(c, l);
}

// Trim 함수 ##################################################
// Ex) str = "    테 스트   ".trim(); => str = "테 스트";
// String.prototype.trim = function () {
//     return this.replace(/(^[ \t\n\r]*)|([ \t\n\r]*$)/g, '');
// };

// 문자열 공백제거 함수 ##################################################
// Ex) str = "    테 스   트   ".stripspace(); => str = "테스트";
// String.prototype.stripspace = function () {
//     return this.replace(/ /g, '');
// };

// 전체 문자열 바꾸기 함수 ##################################################
// Ex) str = "a테스트bcd테스트efg".replaceAll("테스트", ""); => str = "abcdefg";
// String.prototype.replaceAll = function (a, b) {
//     var s = this;
//     if (navigator.userAgent.toLowerCase().indexOf('msie') != -1) return s.replace(new RegExp(a, 'gi'), b);
//     else return s.split(a).join(b);
// };

export function setCookie(name: any, value: any, day: any) {
    const date = new Date();
    date.setTime(date.getTime() + day * 24 * 60 * 60 * 1000);
    document.cookie = name + '=' + value + ';expires=' + date.toUTCString() + ';path=/';
}

export function getCookie(name: any) {
    const cookies = document.cookie;
    if (cookies) {
        const value = document.cookie.match('(^|;) ?' + name + '=([^;]*)(;|$)');
        return value ? value[2] : null;
    } else {
        return;
    }
}

export function delCookie(name: any) {
    let date = new Date();
    date.setDate(date.getDate() - 100);
    let Cookie = `${name}=;Expires=${date.toUTCString()}`;
    document.cookie = Cookie;
}

export function getToken(ctx: any) {
    if (typeof ctx === 'undefined' || ctx === null) {
        return getCookie(`${process.env.NEXT_PUBLIC_TOKENNAME}`);
    } else {
        const token = ctx.req?.cookies[`${process.env.NEXT_PUBLIC_TOKENNAME}`];
        return token;
    }
}

export function getServerCookieToken(res: any) {
    return (res.headers['set-cookie'] as string[])
        .find(cookie => cookie.includes(`${process.env.NEXT_PUBLIC_TOKENNAME}`))
        ?.match(new RegExp(`^${process.env.NEXT_PUBLIC_TOKENNAME}=(.+?);`))?.[1];
}

export function getUserIP(ctx: any) {
    if (typeof ctx === 'undefined' || ctx === null) {
        return '0.0.0.0';
    } else {
        let ip;
        const { req } = ctx;
        if (req?.headers['x-forwarded-for']) {
            ip = (req.headers['x-forwarded-for'] as string).split(',')[0];
        } else if (req?.headers['x-real-ip']) {
            ip = req?.connection.remoteAddress;
        } else {
            ip = req?.connection.remoteAddress;
        }
        return ip;
    }
}

export function Unix_timestampConv() {
    return Math.floor(new Date().getTime() / 1000);
}

export function getAgentDevice(ctx: any) {
    const UA = ctx.req?.headers['user-agent'];
    const isMobile = Boolean(UA?.match(/Android|BlackBerry|iPhone|iPad|iPod|Opera Mini|IEMobile|WPDesktop/i));
    if (isMobile) return 'mobile';
    else return 'desktop';
}

export function getMobileDeviceOS(ctx: any) {
    var varUA = ctx.req?.headers['user-agent'].toLowerCase();
    if (varUA.indexOf('android') > -1) {
        return 'aos';
    } else if (varUA.indexOf('iphone') > -1 || varUA.indexOf('ipad') > -1 || varUA.indexOf('ipod') > -1) {
        return 'ios';
    } else {
        return 'other';
    }
}

export function staticReplace(response: string, ctx: any) {
    let return_value = response;
    return_value = return_value.replaceAll('#{DEVICE}', getAgentDevice(ctx));
    return return_value;
}

export function dateformatYYYYMMDD(format = '') {
    let date, month, year;
    date = new Date().getDate();
    month = new Date().getMonth() + 1;
    year = new Date().getFullYear();
    date = date.toString().padStart(2, '0');
    month = month.toString().padStart(2, '0');
    if (format.toUpperCase() == 'YYYY-MM-DD') {
        return `${year}-${month}-${date}`;
    } else {
        return `${year}${month}${date}`;
    }
}

export function dateformatYYYYMM(format = '') {
    let date, month, year;
    date = new Date().getDate();
    month = new Date().getMonth() + 1;
    year = new Date().getFullYear();
    month = month.toString().padStart(2, '0');
    if (format == 'YYYY-MM') {
        return `${year}-${month}`;
    } else {
        return `${year}${month}`;
    }
}
