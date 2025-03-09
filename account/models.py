import random
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.cache import cache


class Consumer(AbstractUser):
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')

    # class Meta:
    #     db_table = 'users'
    #     verbose_name = '消费者'
    #     verbose_name_plural = verbose_name

    def __str__(self):
        return self.mobile

    def role_display(self):
        if self.is_superuser:
            return '超级管理员'
        elif self.is_staff:
            return '员工'
        else:
            return '消费者'

    def generate_captcha(self):
        chars = '0123456789'
        # numbers = ''.join(random.choices(chars, k=6))
        numbers = '123456'
        cache.set(f'captcha_{self.mobile}', numbers, timeout=300)  # 5分钟有效
        self.send_message(numbers)

    def send_message(self, message):
        content = f'【泡泡玛特】您的验证码是：{message}，有效期5分钟，请勿泄露给他人。'
        print(content)

    def check_captcha(self, captcha):
        print(cache.get(f'captcha_{self.mobile}'))
        if cache.get(f'captcha_{self.mobile}') == captcha:
            return True
        return False



class Shipping(models.Model):
    consumer = models.ForeignKey(Consumer, on_delete=models.CASCADE, related_name='shippings', verbose_name='所属用户')
    is_default = models.BooleanField(default=False, verbose_name='是否默认')
    nick_name = models.CharField(max_length=100, verbose_name='真实姓名')
    mobile = models.CharField(max_length=11, verbose_name='联系手机')
    province = models.CharField(max_length=30, verbose_name='省份')
    city = models.CharField(max_length=30, verbose_name='城市')
    district = models.CharField(max_length=30, verbose_name='地区')
    street = models.CharField(max_length=30,null=True, blank=True,verbose_name='街道')
    address = models.CharField(max_length=200, verbose_name='详细地址')

    class Meta:
        db_table ='shippings'
        verbose_name = '收货地址'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.nick_name}-{self.address}"

    def full_address(self):
        return f"{self.province}{self.city}{self.district}{self.street}{self.address}"

class Region(models.Model):
    code = models.CharField(max_length=10, verbose_name='区域编码')
    name = models.CharField(max_length=50, verbose_name='名称')
    province = models.CharField(max_length=10, verbose_name='省份')
    city = models.CharField(max_length=10, verbose_name='城市')
    area = models.CharField(max_length=10, verbose_name='地区')
    town = models.CharField(max_length=10, verbose_name='乡镇')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children', verbose_name='上级区域')

    class Meta:
        db_table ='regions'
        verbose_name = '区域'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
