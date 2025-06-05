from django.db import models
from series.models import Prize, Series
from account.models import Consumer, Shipping
from django.db import connection
import random

STATUS = (
    (0, '未使用'),
    (1, '已使用')
)


class Redeem(models.Model):
    number = models.CharField(max_length=30, unique=True, verbose_name='抽奖码')
    status = models.SmallIntegerField(choices=STATUS, default=0, verbose_name='状态')
    prize = models.ForeignKey(Prize, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='奖品',
                              related_name='redeems')
    series = models.ForeignKey(Series, on_delete=models.SET_NULL, null=True, blank=True,related_name='redeems', verbose_name='系列')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'redeems'
        verbose_name = '抽奖码'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.number

    @classmethod
    def generate_number(cls):
        chars = '0123456789ABCDEFGHJKLMNPQRSTUVWXYZ'
        numbers = ''.join(random.choices(chars, k=16))
        code = "-".join([numbers[i:i + 4] for i in range(0, 16, 4)])
        return code

    @classmethod
    def generate_prefix(cls, prefix):
        chars = '0123456789ABCDEFGHJKLMNPQRSTUVWXYZ'
        numbers = ''.join(random.choices(chars, k=12))
        code = "-".join([numbers[i:i + 4] for i in range(0, 12, 4)])
        return f"{prefix}-{code}"

    @classmethod
    def prize_list(cls):
        obj_list = Prize.objects.all()
        prize_list = []
        for obj in obj_list:
            prize_list.append({'key': obj.id, 'label': f"{obj.series.name}-{obj.name}"})
        return prize_list


class Redemption(models.Model):
    STATUS = (
        (0, '未发货'),
        (1, '已发货'),
        (2, '已收货')
    )
    EXPRESS = (
        ('顺丰速运', '顺丰速运'),
        ('京东物流', '京东物流'),
        ('中通快递', '中通快递'),
        ('圆通速递', '圆通速递'),
        ('申通快递', '申通快递'),
        ('韵达快递', '韵达快递'),
        ('百世快递', '百世快递'),
        ('邮政快递', '邮政快递'),
        ('德邦快递', '德邦快递'),
        ('极兔速递', '极兔速递'),
    )
    redeem = models.OneToOneField(Redeem, on_delete=models.CASCADE, related_name='redemption', verbose_name='兑换码')
    consumer = models.ForeignKey(Consumer, on_delete=models.SET_NULL, null=True, related_name='redemptions', verbose_name='用户')
    shipping = models.ForeignKey(Shipping, on_delete=models.SET_NULL, null=True, blank=True, related_name='shipping', verbose_name='收货地址')
    prize = models.ForeignKey(Prize, on_delete=models.SET_NULL, null=True, related_name='redemptions', verbose_name='奖品')
    express_order = models.CharField(max_length=100, null=True, blank=True, verbose_name='快递单号')
    express_name = models.CharField(max_length=50, choices=EXPRESS, null=True, blank=True, verbose_name='快递公司')
    status = models.SmallIntegerField(choices=STATUS, default=0, verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'redemptions'
        verbose_name = '兑换记录'
        verbose_name_plural = verbose_name

    def __str__(self):
        try:
            return f"{self.redeem.prize.name}-{self.redeem.number}"
        except:
            return f"{self.redeem.number}"

    def save(self, *args, **kwargs):
        if self.pk:
            old = Redemption.objects.get(pk=self.pk)
            if old.express_order != self.express_order:
                self.status = 1
            if self.express_order is None and self.status != 0:
                self.status = 0

        super().save(*args, **kwargs)
# Create your models here.
