from django.db import models
from ckeditor.fields import RichTextField
import math


class Store(models.Model):
    """店铺模型"""
    name = models.CharField('店铺名称', max_length=200)
    address = models.CharField('详细地址', max_length=500)
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
        return store_distances[:limit]


class Plush(models.Model):
    name = models.CharField(max_length=200,verbose_name='名称')
    main_image = models.ImageField(upload_to='plush/%Y%m%d/', null=True, verbose_name='封面图')
    is_latest = models.BooleanField(default=False, verbose_name='是否最新')
    description = RichTextField(verbose_name="", blank=True, null=True)
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '玩偶周边'
        verbose_name_plural = verbose_name
        ordering = ['-is_latest']

    def __str__(self):
        return f"{self.name}"

