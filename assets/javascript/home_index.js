// 获取所有输入框
const inputs = document.querySelectorAll('.redeem_input.flex-col');

// 为每个输入框添加事件监听
inputs.forEach((input, index) => {
    let isComposing = false;
    input.addEventListener('compositionstart', () => {
        isComposing = true;
    });

    input.addEventListener('compositionend', (e) => {
        isComposing = false;
    });

    input.addEventListener('input', (e) => {
        // 限制输入长度为 4
        e.target.value = e.target.value.toUpperCase();
        if (e.target.value.length > 4 && index > 0) {
            e.target.value = e.target.value.slice(0, 4);
        }

        // 如果输入满 4 个字符，自动聚焦到下一个输入框
        if (e.target.value.length === 4 && index < inputs.length - 1 && index > 0) {
            inputs[index + 1].focus();
        }

        if (!isComposing) {
            e.target.value = e.target.value.replace(/[^a-zA-Z0-9]/g, '');
        }
    });

    // 监听退格键，删除字符后自动聚焦到上一个输入框
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Backspace' && e.target.value.length === 0 && index > 0) {
            inputs[index - 1].focus();
        }
    });
});


// script.js
const overlay = document.getElementById('overlay');
const closeBtn = document.getElementById('close-btn');
const seriesTitle = document.getElementById('series-title');
const prizeList = document.querySelector('.prize-list');

// 点击按钮，显示遮罩层并加载奖品列表
function showPrizes(seriesId, seriesName) {
    document.body.style.overflowY = 'hidden';
    document.body.style.position = 'fixed'; // 防止页面跳动

    // 更新遮罩层标题
    seriesTitle.textContent = `${seriesName}奖品`;
    // 清空奖品列表
    prizeList.innerHTML = '';

    fetch(`/get_prizes?series_id=${seriesId}`) // Django 后端接口
        .then(response => response.json())
        .then(data => {
            // 动态加载奖品
            data.forEach(prize => {
                const prizeItem = document.createElement('div');
                prizeItem.classList.add('prize-item');
                prizeItem.innerHTML = `
              <div class="logo"><img src="${prize.image}" alt="${prize.name}"></div>
              <div class="pirze_name">${prize.name}</div>
              <div class="prize_info">${prize.description}</div>
            `;
                prizeList.appendChild(prizeItem);
            });
            if (data.length === 1) {
                document.querySelector('.prize-container').style.overflowX = 'hidden';
            }

            // 显示遮罩层
            overlay.style.display = 'flex';
        })
        .catch(error => {
            console.error('加载奖品失败:', error);
            alert('加载奖品失败，请稍后重试！');
        });

    // 显示遮罩层
    overlay.style.display = 'flex';
}

// 点击关闭按钮，隐藏遮罩层
closeBtn.addEventListener('click', () => {
    overlay.style.display = 'none';
    document.body.style.overflowY = '';
    document.querySelector('.prize-container').style.overflowX = 'auto';
    document.body.style.position = '';
});

// 点击遮罩层外部，隐藏遮罩层
overlay.addEventListener('click', (e) => {
    if (e.target === overlay) {
        overlay.style.display = 'none';
        document.body.style.overflowY = '';
        document.querySelector('.prize-container').style.overflowX = 'auto';
        document.body.style.position = '';
    }
});

function redemption() {
    const inputs = document.querySelectorAll('input[type="text"]'); // 获取所有输入框
    const values = Array.from(inputs).map(input => input.value); // 提取值
    const redeem_code = values.join('-');
    if (redeem_code.length < 19) {
        showNotification('请输入有效的抽奖码', 'warning');
        return;
    }
    const url = '/redemption';
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
            showNotification(result.msg, result.status)
            if (result.status === 'success') {
                location.href = `/redemptions/show/${result.id}`;
            }
        })
        .catch(error => {
            showNotification(result.msg)
        });

}

// 显示通知的函数
function showNotification(message, type = 'success') {
    const message_tip = document.getElementById('message');
    message_tip.textContent = message;
    const notification = document.getElementById('notification');
    notification.classList.add('show');
    notification.classList.add(type);

    // 5 秒后隐藏通知
    setTimeout(() => {
        notification.classList.remove('show');
        notification.classList.remove(type);
    }, 5000); // 5000 毫秒 = 5 秒
}

const desc_overlay = document.getElementById('desc_overlay');
const desc_close = document.getElementById('desc_close');
desc_overlay.addEventListener('click', (e) => {
    if (e.target === desc_overlay) {
        desc_overlay.style.display = 'none';
    }
});

desc_close.addEventListener('click', (e) => {
    desc_overlay.style.display = 'none';
});

function showDesc() {
    desc_overlay.style.display = 'flex';
}