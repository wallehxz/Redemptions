// 获取所有输入框
const inputs = document.querySelectorAll('.redeem-input');

// 为每个输入框添加事件监听
inputs.forEach((input, index) => {
    input.addEventListener('input', (e) => {
        // 限制输入长度为 4
        if (e.target.value.length > 4) {
            e.target.value = e.target.value.slice(0, 4);
        }

        // 如果输入满 4 个字符，自动聚焦到下一个输入框
        if (e.target.value.length === 4 && index < inputs.length - 1) {
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


// script.js
const overlay = document.getElementById('overlay');
const closeBtn = document.getElementById('close-btn');
const seriesTitle = document.getElementById('series-title');
const prizeList = document.querySelector('.prize-list');

// 模拟奖品数据
const prizesData = [
  { name: '奖品1', description: '这是奖品1的详细信息。', image: 'https://market.fp.ps.netease.com/file/6555ae90bf15885e01b83864GxMjSSjl05?fop=watermark/1/image/aHR0cDovL2ZwLWludC5wcy5uZXRlYXNlLmNvbS9zcGVjdC9maWxlLzY3Y2I5NmIwMjk0MzA5MTA5NTA1MzJjNWtkMjVpcmZYMDY_Zm9wPWltYWdlVmlldy8wL3cvMTMzMi9oLzY3Ni9mL2pwZw==/gravity/5/dx/0/dy/0/ws/0.7657%7Cwatermark/1/image/aHR0cDovL2ZwLWludC5wcy5uZXRlYXNlLmNvbS9tYXJrZXQvZmlsZS82NTU0OTdjOWM4YjJlYjBlZTRiMDQzZTBGWGpKc3JSUDA1/gravity/5/dx/0/dy/0%7CimageView/4/x/9/y/6/w/1314/h/876/f/webp/q/75'},
  { name: '奖品2', description: '这是奖品2的详细信息。', image: 'https://market.fp.ps.netease.com/file/6555ae90bf15885e01b83864GxMjSSjl05?fop=watermark/1/image/aHR0cDovL2ZwLWludC5wcy5uZXRlYXNlLmNvbS9zcGVjdC9maWxlLzY3YzFhMWU0ZjE2NDVkMTU0NTA2MDBjN0N2YWZES0YwMDY_Zm9wPWltYWdlVmlldy8wL3cvMTMzMi9oLzY3Ni9mL2pwZw==/gravity/5/dx/0/dy/0/ws/0.7657%7Cwatermark/1/image/aHR0cDovL2ZwLWludC5wcy5uZXRlYXNlLmNvbS9tYXJrZXQvZmlsZS82NTU0OTdjOWM4YjJlYjBlZTRiMDQzZTBGWGpKc3JSUDA1/gravity/5/dx/0/dy/0%7CimageView/4/x/9/y/6/w/1314/h/876/f/webp/q/75' },
  { name: '奖品3', description: '这是奖品3的详细信息。', image: 'https://spect.fp.ps.netease.com/file/67a8e712802443cb1374e91bKgFQLjb606?fop=imageView/4/x/314/y/100/w/1928/h/1300%7CimageView/2/w/392/h/260/f/webp/q/75' },
  { name: '奖品4', description: '这是奖品4的详细信息。', image: 'https://market.fp.ps.netease.com/file/65f59c78009583b32c367b34yfPsdQJ105?fop=imageView/6/f/webp/q/75' },
  { name: '奖品5', description: '这是奖品5的详细信息。', image: 'https://market.fp.ps.netease.com/file/6555ae90bf15885e01b83864GxMjSSjl05?fop=watermark/1/image/aHR0cDovL2ZwLWludC5wcy5uZXRlYXNlLmNvbS9zcGVjdC9maWxlLzY3Yzg1OWRmYjUyODIzYmE5ZDdlNzVhMUQ2MWg0bU1QMDY=/gravity/5/dx/0/dy/0/ws/0.7657%7Cwatermark/1/image/aHR0cDovL2ZwLWludC5wcy5uZXRlYXNlLmNvbS9tYXJrZXQvZmlsZS82NTU0OTdjOWM4YjJlYjBlZTRiMDQzZTBGWGpKc3JSUDA1/gravity/5/dx/0/dy/0%7CimageView/4/x/9/y/6/w/1314/h/876/f/webp/q/75' },
];

// 点击按钮，显示遮罩层并加载奖品列表
function showPrizes(seriesId) {
  // 更新遮罩层标题
  seriesTitle.textContent = '所有奖品';

  fetch(`/get_prizes?series_id=${seriesId}`) // Django 后端接口
    .then(response => response.json())
    .then(data => {
      // 更新遮罩层标题
      // seriesTitle.textContent = `系列${seriesId}奖品`;

      // 清空奖品列表
      prizeList.innerHTML = '';

      // 动态加载奖品
      data.forEach(prize => {
        const prizeItem = document.createElement('div');
        prizeItem.classList.add('prize-item');
        prizeItem.innerHTML = `
          <div style="width: 300px;height: 300px;"><img src="${prize.image}" alt="${prize.name}"></div>
          <h2>${prize.name}</h2>
          <p>${prize.description}</p>
        `;
        prizeList.appendChild(prizeItem);
      });

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
});

// 点击遮罩层外部，隐藏遮罩层
overlay.addEventListener('click', (e) => {
  if (e.target === overlay) {
    overlay.style.display = 'none';
  }
});

function redemption() {
    const inputs = document.querySelectorAll('input[type="text"]'); // 获取所有输入框
    const values = Array.from(inputs).map(input => input.value); // 提取值
    const redeem_code = values.join('-');
    if (redeem_code.length !== 19) {
        showNotification('请输入有效的兑换码！', 'warning');
        return;
    }
    const url = '/redemption';
    // 发送 POST 请求
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json', // 设置请求头
        },
        body: JSON.stringify({ redeem_code: redeem_code }), // 将数据转换为 JSON 格式
    })
    .then(response => response.json()) // 解析响应为 JSON
    .then(result => {
        showNotification(result.msg, result.status)
    })
    .catch(error => {
        showNotification(result.msg)
    });

}

// 显示通知的函数
function showNotification(message, type='success') {
    const message_tip = document.getElementById('message');
    message_tip.textContent = message;
    const notification = document.getElementById('notification');
    notification.classList.add('show');
    notification.classList.add(type);

    // 5 秒后隐藏通知
    setTimeout(() => {
    notification.classList.remove('show');
    }, 3000); // 5000 毫秒 = 5 秒
}
