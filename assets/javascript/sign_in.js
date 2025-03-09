// 获取验证码按钮
const captchaButton = document.getElementById('get-captcha');

// 倒计时功能
function startCountdown(seconds) {
    captchaButton.disabled = true;
    let remainingSeconds = seconds;

    const interval = setInterval(() => {
        captchaButton.textContent = `${remainingSeconds}秒后重试`;
        remainingSeconds--;

        if (remainingSeconds < 0) {
            clearInterval(interval);
            captchaButton.textContent = '获取验证码';
            captchaButton.disabled = false;
        }
    }, 1000);
}

// 模拟获取验证码
captchaButton.addEventListener('click', () => {
    // 这里可以添加发送验证码的逻辑
    const phone = document.getElementById('phone').value.replace(/\D/g, '');
    if (phone.length === 11) {
        const xhr = new XMLHttpRequest();
        const get_captcha_url = `/account/get_captcha?mobile=${phone}`;
        xhr.open('GET', get_captcha_url, true);
        xhr.send();
        const errorMessage = document.getElementById('error-message');
        errorMessage.style.display = 'block';
        // errorMessage.textContent = '验证码已发送，请注意查收';
        errorMessage.textContent = '【泡泡玛特】您的验证码是：123456，有效期5分钟，请勿泄露给他人。';
        // 5秒后隐藏提示信息
        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 3000);
        startCountdown(60); // 60秒倒计时
    } else {
        const errorMessage = document.getElementById('error-message');
        errorMessage.style.display = 'block';
        errorMessage.textContent = '请填写手机号';
        // 5秒后隐藏提示信息
        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 6000);
    }

});

document.getElementById('phone').addEventListener('input', function (e) {
    // const phone = e.target.value;
    // if (phone.length > 11) {
    //     e.target.value = phone.slice(0, 11); // 截取前11位
    // }

    const input = e.target;
    let phone = input.value.replace(/\D/g, ''); // 去除非数字字符

    // 限制输入长度为11位
    if (phone.length > 11) {
        phone = phone.slice(0, 11);
    }

    // 格式化手机号
    if (phone.length > 3 && phone.length <= 7) {
        phone = `${phone.slice(0, 3)} - ${phone.slice(3)}`;
    } else if (phone.length > 7) {
        phone = `${phone.slice(0, 3)} - ${phone.slice(3, 7)} - ${phone.slice(7, 11)}`;
    }

    // 更新输入框内容
    input.value = phone;

    // 保持光标位置
    const cursorPosition = input.selectionStart;
    if (cursorPosition === 4 || cursorPosition === 9) {
        input.setSelectionRange(cursorPosition + 1, cursorPosition + 1);
    }

    if (phone.length > 3) {
        const prefix = phone.slice(0, 3); // 取前3位
        const mobilePrefixes = ['134', '135', '136', '137', '138', '139', '147', '148', '150', '151', '152', '157', '158', '159', '165', '172', '178', '182', '183', '184', '187', '188', '198'];
        const unicomPrefixes = ['130', '131', '132', '145', '146', '155', '156', '166', '171', '175', '176', '185', '186'];
        const telecomPrefixes = ['133', '149', '153', '173', '174', '177', '180', '181', '189', '191', '199'];
        if (mobilePrefixes.includes(prefix)) {
            return '中国移动';
        } else if (unicomPrefixes.includes(prefix)) {
            return '中国联通';
        } else if (telecomPrefixes.includes(prefix)) {
            return '中国电信';
        } else {
            e.target.value = '';
            const errorMessage = document.getElementById('error-message');
            errorMessage.style.display = 'block';
            errorMessage.textContent = '请填写正确的手机号';
            // 5秒后隐藏提示信息
            setTimeout(() => {
                errorMessage.style.display = 'none';
            }, 3000);
        }
    }

});