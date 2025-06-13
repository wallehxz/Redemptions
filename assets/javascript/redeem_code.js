const redeem_overlay = document.getElementById('redeem_overlay');
const redeem_close = document.getElementById('redeem_close');
function showRedeem() {
    redeem_overlay.style.display = 'flex';
}
redeem_close.addEventListener('click', (e) => {
    redeem_overlay.style.display = 'none';
});

function showRedeemNotice(message, type = 'success') {
    const notification = document.getElementById('redeem_message');
    notification.textContent = message;
    notification.style.display = 'block';
    notification.classList.add(type);

    // 5 秒后隐藏通知
    setTimeout(() => {
        notification.classList.remove(type);
        notification.style.display = 'none';
    }, 5000); // 5000 毫秒 = 5 秒
}

const inputs = document.querySelectorAll('.redeem_input.flex-col');

// 为每个输入框添加事件监听
inputs.forEach((input, index) => {
    let isComposing = false;
    input.addEventListener('compositionstart', () => {
        isComposing = true;
    });

    input.addEventListener('compositionend', (e) => {
        isComposing = false;
        e.target.value = e.target.value.replace(/[^a-zA-Z0-9]/g, '');
        e.target.value = e.target.value.toUpperCase();
    });

    input.addEventListener('input', (e) => {
        // 限制输入长度为 4
        // if (!isComposing) {
        //     e.target.value = e.target.value.toUpperCase();
        //     e.target.value = e.target.value.replace(/[^a-zA-Z0-9]/g, '');
        // }
        e.target.value = e.target.value.replace(/[^a-zA-Z0-9]/g, '');
        e.target.value = e.target.value.toUpperCase();
        if (e.target.value.length > 4 && index > 0) {
            e.target.value = e.target.value.slice(0, 4);
        }

        // 如果输入满 4 个字符，自动聚焦到下一个输入框
        if (e.target.value.length === 4 && index < inputs.length - 1 && index > 0) {
            inputs[index + 1].focus();
        }
    });

    // 监听退格键，删除字符后自动聚焦到上一个输入框
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Backspace' && e.target.value.length === 0 && index > 0) {
            inputs[index - 1].focus();
        }
    });
});

function redeemCode() {
    const inputs = document.querySelectorAll('input[class="redeem_input flex-col"]'); // 获取所有输入框
    const values = Array.from(inputs).map(input => input.value); // 提取值
    const redeem_code = values.join('-');
    if (redeem_code.length < 19) {
        showRedeemNotice('请输入有效的兑换码', 'warning');
        return;
    }
    const url = '/credits/redeem_points';
    // 发送 POST 请求
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json', // 设置请求头
        },
        body: JSON.stringify({redeem_code: redeem_code}), // 将数据转换为 JSON 格式
    })
        .then(response => response.json()) // 解析响应为 JSON
        .then(result => {
            showRedeemNotice(result.msg, result.status)
            if (result.status === 'success') {
                inputs.forEach(input => {
                    input.value = ''; // 清空输入框
                });
                document.getElementById('user_points').textContent = result.points;
            }
        });
}