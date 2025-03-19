// 保存地址
document.getElementById('address-form').addEventListener('submit', function (e) {
    e.preventDefault(); // 阻止表单默认提交行为

    // 获取表单数据
    const redemption_id = document.getElementById('redemption_id').value;
    const nick_name = document.getElementById('name').value;
    const is_default = $('#set_default').prop('checked')
    const mobile = document.getElementById('phone').value;
    let province = document.querySelector('#level1 .active');
    if (province) {
        province = province.innerHTML;
    } else {
        alert('请选择省份');
        return false;
    }
    let city = document.querySelector('#level2 .active');
    if (city) {
        city = city.innerHTML;
    } else {
        city = '';
    }
    let have_city = document.querySelector('#level2 .option');
    if (have_city && city === '') {
        alert('请选择城市');
        return false;
    }
    let district = document.querySelector('#level3 .active');
    if (district) {
        district = district.innerHTML;
    } else {
        district = '';
    }
    let have_district = document.querySelector('#level3 .option');
    if (have_district && district === '') {
        alert('请选择县区');
        return false;
    }
    let street = document.querySelector('#level4 .active');
    if (street) {
        street = street.innerHTML;
    } else {
        street = '';
    }
    let have_street = document.querySelector('#level4 .option');
    if (have_street && street === '') {
        alert('请选择街道');
        return false;
    }
    const address = document.getElementById('address').value;
    $.ajax({
        url: '/create_shipping', // 动态 URL
        method: 'POST',
        data: {
            redemption_id: redemption_id,
            nick_name: nick_name,
            mobile: mobile,
            province: province,
            city: city,
            is_default: is_default,
            district: district,
            street: street,
            address: address,
        },
        success: function (response) {
            if (redemption_id !== '') {
                window.location.href = '/redemptions';
            } else {
                window.location.href = '/shipping';
            }
        },
    });
});

document.getElementById('phone').addEventListener('input', function (e) {
    const input = e.target;
    let phone = input.value.replace(/\D/g, ''); // 去除非数字字符

    // 限制输入长度为11位
    if (phone.length > 11) {
        phone = phone.slice(0, 11);
    }

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
            e.target.placeholder = '请填写正确的手机号';
        }
    }

});

document.getElementById('phone').addEventListener('blur', function () {
    const phone = this.value; // 获取输入框的值
    if (phone.length !== 11) {
        this.value = '';
        this.placeholder = '请填写正确的手机号';
    }
});