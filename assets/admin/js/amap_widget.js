/**
 * 高德地图管理后台插件
 * 实现地址搜索、位置选择、坐标获取等功能
 */

class AmapWidget {
    constructor() {
        this.map = null;
        this.marker = null;
        this.geocoder = null;
        this.geolocation = null;
        this.initMap();
        this.bindEvents();
    }

    /**
     * 初始化地图
     */
    initMap() {
        // 等待DOM加载完成
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this._createMap());
        } else {
            this._createMap();
        }
    }

    _createMap() {
        const container = document.getElementById('amap-container');
        if (!container) {
            console.warn('地图容器未找到');
            return;
        }

        // 获取当前表单中的坐标值
        const latInput = document.getElementById('id_latitude');
        const lngInput = document.getElementById('id_longitude');
        
        let center = [116.397428, 39.90923]; // 默认北京坐标
        
        if (latInput && lngInput && latInput.value && lngInput.value) {
            center = [parseFloat(lngInput.value), parseFloat(latInput.value)];
        }

        // 创建地图实例
        this.map = new AMap.Map('amap-container', {
            zoom: 15,
            center: center,
            resizeEnable: true
        });

        // 如果有初始坐标，添加标记
        if (latInput && lngInput && latInput.value && lngInput.value) {
            this.addMarker(center, '当前店铺位置');
        }

        // 地图点击事件
        this.map.on('click', (e) => {
            this.onMapClick(e);
        });
    }

    /**
     * 绑定事件
     */
    bindEvents() {
        const searchBtn = document.getElementById('search-btn');

        const addressInput = document.getElementById('address-input');

        if (searchBtn) {
            searchBtn.addEventListener('click', () => this.searchAddress());
        }

        if (addressInput) {
            addressInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.searchAddress();
                }
            });
        }
    }

    /**
     * 地图点击事件处理
     */
    onMapClick(e) {
        const lng = e.lnglat.getLng();
        const lat = e.lnglat.getLat();
        
        this.updateCoordinates(lat, lng);
        this.addMarker([lng, lat], '选择的位置');
        
        // 逆地理编码获取地址
        // this.geocoder.getAddress([lng, lat], (status, result) => {
        //     if (status === 'complete' && result.regeocode) {
        //         const address = result.regeocode.formattedAddress;
        //         this.updateLocationInfo(`已选择位置：${address}`);
        //
        //         // 自动填充地址字段
        //         const addressField = document.getElementById('id_address');
        //         if (addressField && !addressField.value) {
        //             addressField.value = address;
        //         }
        //     }
        // });
    }

    /**
     * 添加或更新地图标记
     */
    addMarker(position, title = '位置') {
        // 移除旧标记
        if (this.marker) {
            this.map.remove(this.marker);
        }

        // 添加新标记
        this.marker = new AMap.Marker({
            position: position,
            title: title,
            icon: new AMap.Icon({
                size: new AMap.Size(20, 26),
                image: '/assets/images/location.png',
            })
        });

        this.map.add(this.marker);
        this.map.setCenter(position);
    }

    /**
     * 更新坐标字段
     */
    updateCoordinates(lat, lng) {
        const latInput = document.getElementById('id_latitude');
        const lngInput = document.getElementById('id_longitude');

        if (latInput) latInput.value = lat.toFixed(6);
        if (lngInput) lngInput.value = lng.toFixed(6);

        this.showSuccessMessage(`坐标已更新：${lat.toFixed(6)}, ${lng.toFixed(6)}`);
    }

    /**
     * 更新位置信息显示
     */
    updateLocationInfo(message) {
        const infoDiv = document.getElementById('location-info');
        if (infoDiv) {
            infoDiv.innerHTML = message;
        }
    }

    /**
     * 搜索地址
     */
    searchAddress() {
        const addressInput = document.getElementById('address-input');
        const searchBtn = document.getElementById('search-btn');
        
        if (!addressInput || !addressInput.value.trim()) {
            this.showErrorMessage('请输入地址名称');
            return;
        }

        const address = addressInput.value.trim();
        
        // 禁用搜索按钮
        if (searchBtn) {
            searchBtn.disabled = true;
            searchBtn.textContent = '搜索中...';
        }

        // this.geocoder.getLocation(address, (status, result) => {
        fetch(`/stores/api/search_store/?keywords=${address}`)
            .then(response => response.json()) // 获取JSON
            .then(result => {
                if (searchBtn) {
                    searchBtn.disabled = false;
                    searchBtn.textContent = '搜索地址';
                }
                if (result.pois.length > 0) {
                    const info = result.pois[0];
                    const location = info.location;
                    const [longitude, latitude] = location.split(',');
                    const lng = parseFloat(longitude);
                    const lat = parseFloat(latitude);
                    const full_address = `${info.pname}${info.cityname}${info.adname}${info.address}`;
                    this.updateCoordinates(lat, lng);
                    this.addMarker([lng, lat], address);
                    this.updateLocationInfo(`搜索到地址：${full_address}`);
                    const addressField = document.getElementById('id_address');
                    if (addressField) {
                        addressField.value = full_address;
                    }
                } else {
                    this.showErrorMessage('未找到该地址，请检查地址名称是否正确');
                }
                console.log('获取的数据:', result);
            })

    }


    /**
     * 显示成功消息
     */
    showSuccessMessage(message) {
        this.showMessage(message, 'success');
    }

    /**
     * 显示错误消息
     */
    showErrorMessage(message) {
        this.showMessage(message, 'error');
    }

    /**
     * 显示消息
     */
    showMessage(message, type = 'info') {
        const infoDiv = document.getElementById('location-info');
        if (!infoDiv) return;

        const className = type === 'error' ? 'error-message' : 
                         type === 'success' ? 'success-message' : '';
        
        infoDiv.innerHTML = `<div class="${className}">${message}</div>`;
        
        // 3秒后清除消息
        setTimeout(() => {
            if (infoDiv && infoDiv.querySelector(`.${className}`)) {
                infoDiv.innerHTML = '';
            }
        }, 5000);
    }
}

// 当页面加载完成时初始化地图插件
window.addEventListener('load', () => {
    // 确保AMap已加载
    if (typeof AMap !== 'undefined') {
        new AmapWidget();
    } else {
        console.error('高德地图API未正确加载');
    }
});
