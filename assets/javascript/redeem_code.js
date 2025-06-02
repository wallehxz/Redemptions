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

document.getElementById('credit_redeem_code').addEventListener('input', (e) => {
    e.target.value = e.target.value.toUpperCase();
});

function redeemCode() {
    const redeem_code = document.getElementById('credit_redeem_code').value;
    if (redeem_code.length < 12) {
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
            document.getElementById('credit_redeem_code').value = '';
            if (result.status === 'success') {
                document.getElementById('user_points').textContent = result.points;
            }
        });
}