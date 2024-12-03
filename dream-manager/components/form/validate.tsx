export default function validate(values: any) {
    const errors: any = {};
    const focusing: any = [];
    Object.keys(values).map(v => {
        const el = document.querySelector("[name='" + v + "']");
        if ((el as HTMLElement)?.getAttribute('is_mand') === 'true' && !values[v]) {
            errors[v] = '필수 항목 입니다.';
            focusing.push(v);
        } else if ((el as HTMLElement)?.getAttribute('is_mand') === 'true' && (el as HTMLElement)?.getAttribute('type') === 'checkbox' && JSON.stringify(values[v]) == '[]') {
            errors[v] = '필수 항목 입니다.';
            focusing.push(v);
        }
        if ((el as HTMLElement)?.getAttribute('is_email') === 'true' && values[v] && !/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i.test(values[v])) {
            errors[v] = '입력된 이메일이 유효하지 않습니다.';
            focusing.push(v);
        }
        if ((el as HTMLElement)?.getAttribute('is_bizno') === 'true' && values[v] && !/^(\d{3,3})+[-]+(\d{2,2})+[-]+(\d{5,5})/i.test(values[v])) {
            errors[v] = '입력된 사업자등록번호가 유효하지 않습니다.';
            focusing.push(v);
        }
        if ((el as HTMLElement)?.getAttribute('is_mobile') === 'true' && values[v] && !/^(01[016789]{1}|02|0[3-9]{1}[0-9]{1})-?[0-9]{3,4}-?[0-9]{4}$/i.test(values[v])) {
            errors[v] = '입력된 휴대전화번호가 유효하지 않습니다.';
            focusing.push(v);
        }
        if ((el as HTMLElement)?.getAttribute('is_number') === 'true' && values[v] && !/^[0-9]*$/i.test(values[v])) {
            errors[v] = '숫자만 입력 가능합니다. 다시 입력해주세요.';
            focusing.push(v);
        }
        if ((el as HTMLElement)?.getAttribute('is_certification') === 'true' && values[v] && !/^[0-9]{6}$/i.test(values[v])) {
            errors[v] = '입력된 인증번호가 유효하지 않습니다.';
            focusing.push(v);
        }
    });

    if (focusing.length > 0) {
        (document.querySelector("[name='" + focusing[0] + "']") as HTMLElement)?.focus();
    }

    return errors;
}
