const map = new AMap.Map('map-container', { zoom: 18, resizeEnable: true });
const overlay = document.getElementById('overlay');
let markers = [];
overlay.addEventListener('click', (e) => {
    if (e.target === overlay) {
        overlay.style.display = 'none';
    }
});
function setMarker(lat, lng) {
    overlay.style.display = 'flex';
    if (!map) throw new Error("地图未初始化！");

    if (markers.length > 0) {
        map.remove(markers); // 批量移除标记
        markers = [];
    }

    const marker = new AMap.Marker({
        position: new AMap.LngLat(lng, lat), // 经纬度顺序为[经度,纬度]
        icon: new AMap.Icon({
            size: new AMap.Size(20, 26),
            image: '/assets/images/location.png',
        })
    });

    marker.setMap(map);
    markers.push(marker);
    map.setCenter([lng, lat])
    return marker; // 返回标记对象以便后续操作
}