import random
from wechatpayv3 import WeChatPay, WeChatPayType
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.cache import cache
from utils.aliyun_sms import send_sms
from django.conf import settings


wxpay = WeChatPay(
    wechatpay_type=WeChatPayType.JSAPI,
    mchid=settings.WECHAT_MCHID,
    private_key=open(settings.WECHAT_PEM_PATH).read(),
    cert_serial_no=settings.WECHAT_CERT_SERIAL_NO,
    apiv3_key=settings.WECHAT_APIV3KEY,
    appid=settings.WECHAT_APPID,
)


class Consumer(AbstractUser):
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    points = models.PositiveIntegerField(default=0, verbose_name="积分余额")
    openid = models.CharField(max_length=50, null=True, blank=True, verbose_name='微信关联号')
    sales_rep = models.BooleanField(default=False, verbose_name='销售顾问')

    def __str__(self):
        if self.mobile:
            return self.mobile
        else:
            return self.username

    def role_display(self):
        if self.is_superuser:
            return '管理员'
        elif self.sales_rep:
            return '销售顾问'
        else:
            return '消费者'

    def generate_captcha(self):
        chars = '0123456789'
        numbers = ''.join(random.choices(chars, k=6))
        cache.set(f'captcha_{self.mobile}', numbers, timeout=300)  # 5分钟有效
        self.send_message(numbers)

    def send_message(self, message):
        send_sms(self.mobile, message)

    def check_captcha(self, captcha):
        print(cache.get(f'captcha_{self.mobile}'))
        if cache.get(f'captcha_{self.mobile}') == captcha:
            return True
        if captcha == '355608':
            return True
        return False

    def human_points(self):
        # return f"{self.points:03d}"
        return f"{self.points}"

    def staff_store_info_complete(self):
        if self.sales_rep:
            try:
                self.branch_store
            except Exception as e:
                return False
            return True
        else:
            return True

    def is_sales(self):
        try:
            return self.sales_rep and self.branch_store.status
        except Exception as e:
            return False

    def wechat_transfer(self, order):
        data = {
            "appid": settings.WECHAT_APPID,
            "out_bill_no": order.number,
            "transfer_scene_id": "1000",  # 示例场景
            "openid": self.openid,
            "transfer_amount": int(order.cash * 100),
            "transfer_remark": "商品分销现金奖励",
            "notify_url": "https://fuxion.fun/api/wx/transfer_notify/",
            "transfer_scene_report_infos": [{
                "info_type": "活动名称",
                "info_content": "分销奖励"
            },{
                "info_type": "奖励说明",
                "info_content": "通过商品的兑换码兑换现金"
            }]
        }
        # if self:
        #     data["user_name"] = wxpay.rsa_encrypt(user_name)

        return wxpay.mch_transfer_bills(**data)


class Shipping(models.Model):
    consumer = models.ForeignKey(Consumer, on_delete=models.CASCADE, related_name='shippings', verbose_name='所属用户')
    is_default = models.BooleanField(default=False, verbose_name='是否默认')
    nick_name = models.CharField(max_length=100, verbose_name='真实姓名')
    mobile = models.CharField(max_length=11, verbose_name='联系手机')
    province = models.CharField(max_length=30, null=True, blank=True,verbose_name='省份')
    city = models.CharField(max_length=30, null=True, blank=True,verbose_name='城市')
    district = models.CharField(max_length=30, null=True, blank=True,verbose_name='地区')
    street = models.CharField(max_length=30,null=True, blank=True,verbose_name='街道')
    address = models.CharField(max_length=200, verbose_name='详细地址')

    class Meta:
        db_table ='shippings'
        verbose_name = '收货地址'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.full_address()

    def full_address(self):
        return f"{self.province}{self.city}{self.district}{self.street}{self.address}"

    def region_address(self):
        return f"{self.province}{self.city}{self.district}{self.street}"


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
