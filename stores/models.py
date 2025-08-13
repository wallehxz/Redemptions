from time import sleep
import requests
from django.db import models
from ckeditor.fields import RichTextField
from django.core.cache import cache
import math


class Store(models.Model):
    """店铺模型"""
    name = models.CharField('店铺名称', max_length=200)
    address = models.CharField('详细地址', max_length=500)
    navigation = models.CharField('导航地址', max_length=500, blank=True, null=True)
    phone = models.CharField('联系电话', max_length=20, blank=True)
    description = models.TextField('店铺描述', blank=True)

    # 地理位置信息
    latitude = models.FloatField('纬度', help_text='店铺所在位置的纬度')
    longitude = models.FloatField('经度', help_text='店铺所在位置的经度')

    # 营业信息
    business_hours = models.CharField('营业时间', max_length=100, blank=True)
    is_active = models.BooleanField('是否营业', default=True)

    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '店铺'
        verbose_name_plural = '店铺管理'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def calculate_distance(self, user_lat, user_lng):
        """
        计算用户位置与店铺的距离（单位：千米）
        使用Haversine公式计算球面距离
        """
        # 转换为弧度
        lat1_rad = math.radians(self.latitude)
        lng1_rad = math.radians(self.longitude)
        lat2_rad = math.radians(user_lat)
        lng2_rad = math.radians(user_lng)

        # Haversine公式
        dlat = lat2_rad - lat1_rad
        dlng = lng2_rad - lng1_rad

        a = (math.sin(dlat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))

        # 地球半径 (千米)
        r = 6371

        return c * r

    @classmethod
    def get_nearest_stores(cls, user_lat, user_lng, limit=10):
        """
        获取距离用户最近的店铺列表
        """
        stores = cls.objects.filter(is_active=True)
        store_distances = []

        for store in stores:
            distance = store.calculate_distance(user_lat, user_lng)
            store_distances.append((store, distance))

        # 按距离排序
        store_distances.sort(key=lambda x: x[1])

        # 返回最近的N个店铺
        if limit > 0:
            return store_distances[:limit]
        else:
            return store_distances

    @classmethod
    def get_name_for_address(cls, address):
        try:
            url = 'https://restapi.amap.com/v5/place/text'
            params = {
                'key': '12233ccf85da7031c00a3f4ca01eebd1',
                'keywords': address,
            }
            response = requests.get(url, params=params)
            result = response.json()
            name = result.get('pois', [])[0].get('name')
            return name
        except Exception as e:
            return None

    # from stores.models import Store
    # Store.update_all_navigation_with_address()
    @classmethod
    def update_all_navigation_with_address(cls):
        stores = cls.objects.filter(navigation=None).all()
        for store in stores:
            new_name = cls.get_name_for_address(store.address)
            if new_name is not None:
                sleep(0.35)
                print(f'更新 {store.id} 的导航地址为 {new_name}')
                store.navigation = new_name
                store.save()

    @classmethod
    def geocode_address(cls, address):
        try:
            url = 'https://restapi.amap.com/v5/place/text'
            params = {
                'key': '12233ccf85da7031c00a3f4ca01eebd1',
                'keywords': address,
            }
            response = requests.get(url, params=params)
            result = response.json()
            geocode = result.get('pois', [])[0].get('location').split(',')
            return {"latitude": float(geocode[1]), "longitude": float(geocode[0])}
        except Exception as e:
            return {"latitude": 0, "longitude": 0, 'address': address}


class Plush(models.Model):
    name = models.CharField(max_length=200,verbose_name='标题')
    main_image = models.ImageField(upload_to='plush/%Y%m%d/', null=True, blank=True, verbose_name='图床链接')
    is_latest = models.BooleanField(default=False, verbose_name='是否最新')
    description = RichTextField(verbose_name="详情内容", blank=True, null=True)
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '每期周边'
        verbose_name_plural = verbose_name
        ordering = ['-is_latest']

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        if self.is_latest:
            cache.set('fuxion_title', self.name, timeout=None)
            Plush.objects.filter(is_latest=True).update(is_latest=False)
            redis_client = cache._cache.get_client(write=False)
            for key in redis_client.scan_iter("*"):
                key_string = key.decode("utf-8")
                if 'trophy' in key_string:
                    redis_client.delete(key_string)
                    break
            super().save(*args, **kwargs)
