from datetime import datetime
import random
from django.db import models, transaction
from django.db.models import Sum

from account.models import Consumer, Shipping
from ckeditor.fields import RichTextField


class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name="商品名称")
    main_image = models.ImageField(upload_to='products/%Y%m%d/', null=True, verbose_name='主图')
    description = RichTextField(verbose_name="商品描述")
    points_required = models.PositiveIntegerField(verbose_name="所需积分")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'products'
        verbose_name = "商品"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def all_stock(self):
        return ProductSpec.objects.filter(product=self).aggregate(total=Sum("stock"))["total"]

    def default_spec(self):
        return self.specs.filter(is_default=True).first()


class ProductSpec(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specs', verbose_name='所属商品')
    name = models.CharField(max_length=100, verbose_name='规格名称')
    points_required = models.PositiveIntegerField(verbose_name="所需积分")
    stock = models.PositiveIntegerField(default=0, verbose_name='库存')
    is_default = models.BooleanField(default=False, verbose_name='是否默认规格')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'product_specs'
        verbose_name = '商品规格'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class RedemptionCode(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="兑换码")
    points_value = models.PositiveIntegerField(default=1, null=True, blank=True, verbose_name="积分值")
    is_used = models.BooleanField(default=False, verbose_name="是否已使用")
    used_by = models.ForeignKey(Consumer, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="使用者")
    used_at = models.DateTimeField(null=True, blank=True, verbose_name="兑换时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = 'redemption_codes'
        verbose_name = "兑换码"
        verbose_name_plural = "兑换码"

    def __str__(self):
        return self.code

    @classmethod
    def generate_code(cls):
        chars = '0123456789ABCDEFGHJKLMNPQRSTUVWXYZ'
        code = ''.join(random.choices(chars, k=12))
        # code = "-".join([numbers[i:i + 4] for i in range(0, 16, 4)])
        return code


class PointsTransaction(models.Model):
    TRANSACTION_TYPE = (
        ('earn', '获得'),
        ('exchange', '兑换'),
    )

    user = models.ForeignKey(Consumer, on_delete=models.CASCADE, verbose_name="用户")
    amount = models.IntegerField(verbose_name="积分变动")
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE, verbose_name="交易类型")
    description = models.CharField(max_length=200, verbose_name="描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = 'points_transactions'
        verbose_name = "积分明细"
        verbose_name_plural = "积分明细"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.get_transaction_type_display()} - {self.amount}"

    def human_amount(self):
        if self.transaction_type == 'earn':
            return f"+{self.amount}"
        else:
            return f"-{self.amount}"


class ExchangeOrder(models.Model):
    """兑换订单模型"""
    ORDER_STATUS = (
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('shipped', '已发货'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
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

    order_number = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name='订单编号')
    user = models.ForeignKey(Consumer, on_delete=models.CASCADE, related_name='exchange_orders', verbose_name='用户订单')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='orders', verbose_name='商品')
    spec = models.ForeignKey(ProductSpec, verbose_name='商品规格', on_delete=models.PROTECT, related_name='orders')
    quantity = models.PositiveIntegerField(verbose_name='数量')
    total_points = models.DecimalField(verbose_name='总福力', max_digits=10, decimal_places=2)
    harvest = models.ForeignKey(Shipping, on_delete=models.PROTECT, verbose_name='收货地址')
    status = models.CharField(verbose_name='订单状态', max_length=20, choices=ORDER_STATUS, default='pending')
    express_name = models.CharField(max_length=50, choices=EXPRESS, null=True, blank=True, verbose_name='快递公司')
    tracking_number = models.CharField('物流单号', max_length=50, blank=True, null=True)
    note = models.TextField('备注', blank=True)
    created_at = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    class Meta:
        verbose_name = '兑换订单'
        verbose_name_plural = '兑换订单'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            with transaction.atomic():
                max_id = ExchangeOrder.objects.select_for_update().aggregate(
                    max_id=models.Max('id')
                )['max_id'] or 0
                next_id = max_id + 1
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                self.order_number = f"{timestamp}{next_id:05d}"
                super().save(*args, **kwargs)
        else:
            if self.pk:
                old = ExchangeOrder.objects.get(pk=self.pk)
                if old.tracking_number != self.tracking_number:
                    self.status = 'shipped'
                if self.tracking_number is None and self.status != 'pending':
                    self.status = 'pending'
                    self.express_name = None
            super().save(*args, **kwargs)

    def total(self):
        return int(self.total_points)
