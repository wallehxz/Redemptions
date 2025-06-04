const redemption_overlay = document.getElementById('redemption_overlay');
const redemption_close = document.getElementById('redemption_close');
function showRedemption() {
    redemption_overlay.style.display = 'flex';
}
redemption_close.addEventListener('click', (e) => {
    redemption_overlay.style.display = 'none';
});

function showNotice(message, type = 'success') {
    const notification = document.getElementById('redemption_message');
    notification.textContent = message;
    notification.style.display = 'block';
    notification.classList.add(type);

    // 5 秒后隐藏通知
    setTimeout(() => {
        notification.classList.remove(type);
        notification.style.display = 'none';
    }, 5000); // 5000 毫秒 = 5 秒
}

const minusBtn = document.getElementById('spec_amount_minus');
const plusBtn = document.getElementById('spec_amount_plus');
const orderAmount = document.getElementById('order_amount');
const specStock = document.getElementById('spec_stock');
const specPoints = document.getElementById('spec_points');
const totalPoints = document.getElementById('total_points');
const submitTotal = document.getElementById('redemption_submit');
const specId = document.getElementById('spec_id');
const userPoints = document.getElementById('user_points');
const harvestId = document.getElementById('harvest_id');
const productId = document.getElementById('product_id');

// 减少数量
minusBtn.addEventListener('click', () => {
    let currentValue = parseInt(orderAmount.textContent);
    let spec_points = parseInt(specPoints.textContent);
    if (currentValue > 1) {  // 最小值为1
        orderAmount.textContent = currentValue - 1;
        totalPoints.textContent = (currentValue - 1) * spec_points;
        submitTotal.textContent = '立即支付 ' + (currentValue - 1) * spec_points + ' 福力'
    }
});

// 增加数量（可选）
plusBtn.addEventListener('click', () => {
    let currentValue = parseInt(orderAmount.textContent);
    let spec_points = parseInt(specPoints.textContent);
    let user_points = parseInt(userPoints.textContent);
    if (user_points < (currentValue + 1) * spec_points) {
        showNotice('福力余额不足，增加数量失败', 'error');
        return false;
    }
    if (currentValue + 1 <= parseInt(specStock.textContent)) {
        orderAmount.textContent = currentValue + 1;
        totalPoints.textContent = (currentValue + 1) * spec_points;
        submitTotal.textContent = '立即支付 ' + (currentValue + 1) * spec_points + ' 福力'
    }
});

function selectSpec(element, points, stock, spec_id) {
    if (stock === 0) {
        showNotice('当前规格库存数量不足', 'error');
        return false;
    }
    specPoints.textContent = points;
    specStock.textContent = stock;
    totalPoints.textContent = points;
    specId.textContent = spec_id;
    orderAmount.textContent = '1';
    submitTotal.textContent = '立即支付 ' + points + ' 福力'
    document.querySelectorAll('.spec_item').forEach(item => {
        item.classList.remove('active');
    });
    element.classList.add('active');
}

function changeHarvest() {
    document.getElementById('box_harvests').style.display = 'block';
    document.getElementById('redemption_content').style.display = 'none';
    document.getElementById('box_title').textContent = '选择地址';
}

function selectHarvest(id, name, mobile, full_address) {
    document.getElementById('harvest_id').textContent = id;
    document.getElementById('harvest_full').textContent = full_address;
    document.getElementById('harvest_name').textContent = name;
    document.getElementById('harvest_mobile').textContent = mobile;
    document.getElementById('box_harvests').style.display = 'none';
    document.getElementById('redemption_content').style.display = 'block';
    document.getElementById('box_title').textContent = '商品兑换';
}

function redeemProduct() {
    if (isNaN(parseInt(userPoints.textContent))) {
        showNotice('请登录账户以兑换商品', 'error');
        return false;
    }
    if (isNaN(parseInt(specId.textContent))) {
        showNotice('请选择商品规格', 'warning');
        return false;
    }
    if (parseInt(userPoints.textContent) < parseInt(totalPoints.textContent)) {
        showNotice('福力余额不足，支付失败', 'error');
        return false;
    }
    if (isNaN(parseInt(harvestId.textContent))) {
        showNotice('收货地址为空，支付失败', 'error');
        return false;
    }
    $.ajax({
        url: '/credits/exchange_product', // 动态 URL
        method: 'POST',
        data: {
            product_id: parseInt(productId.textContent),
            spec_id: parseInt(specId.textContent),
            quantity: parseInt(orderAmount.textContent),
            harvest_id: parseInt(harvestId.textContent),
            total_points: parseInt(totalPoints.textContent),
        },
        success: function (response) {
            if (response.status === 'success') {
                window.location.href = '/credits/redemption/' + response.order_id;
            } else {
                showNotice(response.msg, response.status);
            }
        }
    });
}