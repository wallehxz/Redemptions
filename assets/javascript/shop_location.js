let userLocation = null;

window.onload = function () {
    if (navigator.geolocation) {
        // 自动请求位置（无用户点击触发）
        navigator.geolocation.getCurrentPosition(
            successCallback,
            errorCallback,
            {timeout: 10000} // 超时10秒
        );
    } else {
        console.error("浏览器不支持地理位置功能");
    }
};

function successCallback(position) {
    const lat = position.coords.latitude;   // 纬度
    const lng = position.coords.longitude;  // 经度
    userLocation = {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude
    };
    // 示例：显示在页面
    // reverseGeocode(lat, lng);
    findNearestStores();
}

function errorCallback(error) {
    switch (error.code) {
        case error.PERMISSION_DENIED:
            console.error("用户拒绝授权");
            break;
        case error.POSITION_UNAVAILABLE:
            console.error("位置不可用");
            break;
        case error.TIMEOUT:
            console.error("请求超时");
            break;
    }
}

function reverseGeocode(lat, lng) {
    fetch('/stores/api/reverse_geocode/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            latitude: lat,
            longitude: lng
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('location').textContent = data.address;
            }
        })
        .catch(error => {
            console.error('逆地理编码失败：', error);
        });
}

// 查找最近的店铺
function findNearestStores(limit=20) {
    if (!userLocation) {
        alert('请先获取您的位置');
        return;
    }

    fetch('/stores/api/nearest_stores/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            latitude: userLocation.latitude,
            longitude: userLocation.longitude,
            limit: limit
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // displayNearestStores(data.stores);
                displayNearestStoresOneByOne(data.stores);
            } else {
                alert('查询失败：' + data.error);
            }
        })
        .catch(error => {
            alert('查询出错：' + error.message);
        });
}

// 显示最近的店铺
function displayNearestStores(stores) {
    const container = document.getElementById('shop_list');
    container.innerHTML = '';
    stores.forEach((store, index) => {
        const col = document.createElement('div');
        col.className = 'item_shop';
        col.innerHTML = `
            <span class="text_shop_name">${store.name}</span>
            <div class="group_address justify-between">
                <span class="text_address">${store.address}</span>
                <div class="flex-row">
                    <img class="store_location" src="/assets/images/store_location.png"/>
                    <span class="text_distance">${store.distance}</span>
                </div>
            </div>
            <img class="more_line" src="/assets/images/shop_more_line.png"/>
        `;
        container.appendChild(col);
    });
}

function displayNearestStoresOneByOne(stores) {
    const container = document.getElementById('shop_list');
    container.innerHTML = '';
    let index = 0;

    // 递归添加函数
    function addStore() {
        if (index >= stores.length) return;

        const store = stores[index];
        const col = document.createElement('div');
        col.className = 'item_shop';
        col.innerHTML = `
            <span class="text_shop_name" onclick="setMarker(${store.latitude}, ${store.longitude})">${store.name}</span>
            <div class="group_address justify-between" onclick="openNav(${store.latitude}, ${store.longitude}, '${store.navigation}')">
                <span class="text_address">${store.address}</span>
                <div class="flex-row">
                    <img class="store_location" src="/assets/images/store_location.png"/>
                    <span class="text_distance">${store.distance}</span>
                </div>
            </div>
            <img class="more_line" src="/assets/images/shop_more_line.png"/>
        `;

        // 添加淡入动画
        col.style.opacity = '0';
        container.appendChild(col);

        // 触发CSS过渡
        setTimeout(() => {
            col.style.opacity = '1';
            col.style.transition = 'opacity 1s ease';
        }, 500);

        index++;
        setTimeout(addStore, 50); // 间隔300ms添加下一条
    }

    addStore(); // 启动渲染
}

function openNav(lat, lng, name) {
    window.open(`https://uri.amap.com/navigation?to=${lng},${lat},${encodeURIComponent(name)}&mode=car`);
    // 检测设备类型
    // if (navigator.userAgent.match(/(iPhone|iPod|iPad);?/i)) {
    //     window.location.href = `iosamap://navi?sourceApplication=web导航&poiname=${encodeURIComponent(name)}&lat=${lat}&lon=${lng}&dev=0&style=2`;
    // } else if (navigator.userAgent.match(/android/i)) {
    //     window.location.href = `androidamap://navi?sourceApplication=web导航&poiname=${encodeURIComponent(name)}&lat=${lat}&lon=${lng}&dev=0&style=2`;
    // } else {
    //     // 网页版备用方案
    //     window.open(`https://uri.amap.com/navigation?to=${lng},${lat},${encodeURIComponent(name)}&mode=car`);
    // }
}

const selectElement = document.getElementById("store-select");
const outputElement = document.getElementById("output");

selectElement.addEventListener("change", function () {
    const selectedValue = this.value; // 获取选中的 value
    const selectedText = this.options[this.selectedIndex].text; // 获取选中的文本

    outputElement.textContent = selectedText;
    if (selectedValue === "all") {
        findNearestStores(0);
    } else if (selectedValue === "nearby") {
        findNearestStores(20);
    }
});