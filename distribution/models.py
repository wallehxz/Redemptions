import random
import secrets
import string
import uuid
from django.db import models
from account.models import Consumer
from redeem.models import Redeem

class BranchStore(models.Model):
    consumer = models.OneToOneField(Consumer, on_delete=models.SET_NULL, null=True, related_name='branch_store', verbose_name='员工')
    name = models.CharField(max_length=100, verbose_name='门店名称')
    address = models.CharField(max_length=200, verbose_name='详细地址')
    employee = models.CharField(max_length=20, verbose_name='员工姓名')
    status = models.BooleanField(default=False, verbose_name='审核状态')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'branch_stores'
        verbose_name = '门店信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CashRedemption(models.Model):
    number = models.CharField(max_length=30, unique=True, verbose_name='兑换码')
    redeem = models.OneToOneField(Redeem, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='抽奖码', related_name='cash_redemption')
    status = models.BooleanField(default=False, verbose_name='使用状态')
    cash = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='奖励金额')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'cash_redemptions'
        verbose_name = '现金兑换码'
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

    def redeem_number(self):
        return self.redeem.number if self.redeem is not None else ""


class CashExchange(models.Model):
    STATUS_CHOICES = (
        ('pending', '待提现'),
        ('processing', '提现中'),
        ('completed', '已提现'),
    )
    user = models.ForeignKey(Consumer, on_delete=models.CASCADE, verbose_name='员工')
    number = models.CharField(max_length=32, null=True, blank=True, verbose_name='流水编号')
    redemption = models.OneToOneField(CashRedemption, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='兑换码')
    cash = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='兑换金额')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='兑换状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    withdrawal_at  = models.DateTimeField(null=True, blank=True, verbose_name='提现时间')

    class Meta:
        ordering = ['-withdrawal_at']
        db_table = 'cash_exchanges'
        verbose_name = '兑换记录'
        verbose_name_plural = '兑换记录'

    def __str__(self):
        return f'{self.user.mobile} 兑换 {self.redemption.number}'

    def save(self, *args, **kwargs):
        if self.number is None:
            self.number = uuid.uuid4().hex.upper()
        super().save(*args, **kwargs)


class SalesInviteCode(models.Model):
    """销售邀请码"""
    code = models.CharField(
        max_length=16,
        unique=True,
        editable=False,
        verbose_name="邀请码"
    )
    is_used = models.BooleanField(default=False, verbose_name="已使用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "销售邀请码"
        verbose_name_plural = "销售邀请码"

    def __str__(self):
        return f"{self.code} ({'已用' if self.is_used else '未用'})"

    def save(self, *args, **kwargs):
        if not self.code:                 # 只在创建时生成
            self.code = self.generate_code()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_code(length=8):
        alphabet = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
# Create your models here.
