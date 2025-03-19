document.addEventListener('DOMContentLoaded', function() {
    const level1 = document.getElementById('level1');
    const level2 = document.getElementById('level2');
    const level3 = document.getElementById('level3');
    const level4 = document.getElementById('level4');
    const select_confirm = document.getElementById('select_confirm');

    function fetchOptions(url, callback) {
        fetch(url)
            .then(response => response.json())
            .then(data => callback(data))
            .catch(error => console.error('Error fetching options:', error));
    }

    function updateLevel(levelElement, options) {
        levelElement.innerHTML = '';
        options.forEach(option => {
            const div = document.createElement('div');
            div.className = 'option';
            div.textContent = option.name;
            div.addEventListener('click', () => {
                Array.from(levelElement.children).forEach(child => child.classList.remove('active'));
                div.classList.add('active');
                if (levelElement === level1) {
                    fetchOptions(`/region_children?parent_id=${option.id}`, function (data) {
                        updateLevel(level2, data);
                    });
                    level3.innerHTML = '';
                    level4.innerHTML = '';
                    level4.style.display = 'none';
                    level1.classList.remove('grid25');
                    level2.classList.remove('grid25');
                    level3.classList.remove('grid25');
                    level4.classList.remove('grid25');
                } else if (levelElement === level2) {
                    fetchOptions(`/region_children?parent_id=${option.id}`, function (data) {
                        updateLevel(level3, data);
                    });
                } else if (levelElement === level3) {
                    fetchOptions(`/region_children?parent_id=${option.id}`, function (data) {
                        if (data.length > 0) {
                            level4.innerHTML = '';
                            level4.style.display = 'block';
                            level1.classList.add('grid25');
                            level2.classList.add('grid25');
                            level3.classList.add('grid25');
                            level4.classList.add('grid25');
                            updateLevel(level4, data);
                        }
                    });
                }
            });
            levelElement.appendChild(div);
        });
    }

    // 初始化第一级选项
    fetchOptions('/region_children?parent_id=0', function (data) {
        updateLevel(level1, data);
    });

    level1.addEventListener('wheel', function (event) {
        event.preventDefault();
        this.scrollBy(0, event.deltaY);
    });

    level2.addEventListener('wheel', function (event) {
        event.preventDefault();
        this.scrollBy(0, event.deltaY);
    });

    level3.addEventListener('wheel', function (event) {
        event.preventDefault();
        this.scrollBy(0, event.deltaY);
    });

    function addDragScroll(element) {
        let isDragging = false;
        let startY, scrollTop;

        element.addEventListener('mousedown', (e) => {
            isDragging = true;
            startY = e.pageY - element.offsetTop;
            scrollTop = element.scrollTop;
            element.style.cursor = 'grabbing';
        });

        element.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            e.preventDefault();
            const y = e.pageY - element.offsetTop;
            const walk = (y - startY) * 2; // 拖动速度
            element.scrollTop = scrollTop - walk;
        });

        element.addEventListener('mouseup', () => {
            isDragging = false;
            element.style.cursor = 'grab';
        });

        element.addEventListener('mouseleave', () => {
            isDragging = false;
            element.style.cursor = 'grab';
        });
    }

    // 为每个层级添加拖动功能
    addDragScroll(level1);
    addDragScroll(level2);
    addDragScroll(level3);
    select_confirm.addEventListener('click', () => {
       let province= document.querySelector('#level1 .active');
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
       if (have_city && city ==='') {
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
       if (have_district && district ==='') {
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
       if (have_street && street ==='') {
           alert('请选择街道');
           return false;
       }
       document.getElementById('regions').innerHTML = province + city + district + street;
       document.getElementById('desc_overlay').style.display = 'none';
    })
});