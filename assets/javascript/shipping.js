$(document).ready(function () {
    // 获取所有 <select> 元素
    // const selectElements = $('select');
    //
    // // 遍历每个 <select> 元素并初始化 Select2
    // selectElements.each(function () {
    //     $(this).select2({
    //         width: '100%',
    //     });
    // });
});

const $province = $('#province');
const $city = $('#city');
const $city_group = $('#city_group');
const $district = $('#district');
const $district_group = $('#district_group');
const $street = $('#street');
const $street_group = $('#street_group');
$province.on('change', function () {
    const selectedProvince = $(this).val();
    $city.empty().append('<option value="">请选择城市</option>');
    $district.empty().append('<option value="">请选择区县</option>');
    $street.empty().append('<option value="">请选择街道</option>');

    if (selectedProvince) {
        $.ajax({
            url: '/region_children?parent_id=' + selectedProvince, // 请求地址
            method: 'GET', // 请求方法
            dataType: 'json', // 预期服务器返回的数据类型
            success: function (response) {
                // 请求成功时的回调函数
                $city_group.css('display', '');
                for (const city of response) {
                    $city.append(`<option value="${city.id}">${city.name}</option>`);
                }
            },
        });
    }
});

$city.on('change', function () {
    const selectedProvince = $(this).val();
    $district.empty().append('<option value="">请选择区县</option>');
    $street.empty().append('<option value="">请选择街道</option>');

    if (selectedProvince) {
        $.ajax({
            url: '/region_children?parent_id=' + selectedProvince, // 请求地址
            method: 'GET', // 请求方法
            dataType: 'json', // 预期服务器返回的数据类型
            success: function (response) {
                if (response.length > 0) {
                    $district_group.css('display', '');
                    $district.prop('required', true);
                }
                // 请求成功时的回调函数
                for (const city of response) {
                    $district.append(`<option value="${city.id}">${city.name}</option>`);
                }
            },
        });
    }
});

$district.on('change', function () {
    const selectedProvince = $(this).val();
    $street.empty().append('<option value="">请选择街道</option>');

    if (selectedProvince) {
        $.ajax({
            url: '/region_children?parent_id=' + selectedProvince, // 请求地址
            method: 'GET', // 请求方法
            dataType: 'json', // 预期服务器返回的数据类型
            success: function (response) {
                if (response.length > 0) {
                    $street_group.css('display', '');
                    $street.prop('required', true);
                }
                for (const city of response) {
                    $street.append(`<option value="${city.id}">${city.name}</option>`);
                }
            },
        });
    }
});

// 保存地址
document.getElementById('address-form').addEventListener('submit', function (e) {
    e.preventDefault(); // 阻止表单默认提交行为

    // 获取表单数据
    const redemption_id = document.getElementById('redemption_id').value;
    const nick_name = document.getElementById('name').value;
    const is_default = $('#set_default').prop('checked')
    const mobile = document.getElementById('phone').value;
    const province = $('#province option:selected').text();
    const city = $('#city option:selected').text();
    const district = $('#district option:selected').text();
    const street = $('#street option:selected').text();
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