from django.contrib import admin
from simpleui.admin import AjaxAdmin
from django.http import JsonResponse
from django.utils.html import format_html

from .models import Product, ProductSpec, PointsTransaction, RedemptionCode, ExchangeOrder


class ProductSpecInline(admin.TabularInline):
    model = ProductSpec
    extra = 0
    min_num = 1
    fields = ['name', 'points_required', 'stock', 'is_default']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'main_img', 'specs_list', 'created_at')
    fields = ['name', 'points_required', 'main_image', 'description']
    search_fields = ['name']
    list_filter = ['specs__points_required']
    inlines = [ProductSpecInline]

    def specs_list(self, obj):
        specs_str = ""
        for spec in obj.specs.all():
            specs_str += f'规格：{spec.name} 积分：{spec.points_required} 库存：{spec.stock}<br>'
        return format_html(specs_str)

    specs_list.short_description = '规格列表'

    def main_img(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" width="75" height="75" />', obj.main_image.url)

    main_img.short_description = '封面'


@admin.register(RedemptionCode)
class RedemptionCodeAdmin(AjaxAdmin):
    list_display = ('code', 'is_used', 'points_value', 'used_by', 'used_at')
    fields = ['code', 'points_value', 'is_used', 'used_by']
    search_fields = ['code']
    list_filter = ['used_by', 'is_used']
    list_per_page = 20
    actions = ['bulk_generate']

    def bulk_generate(self, request, queryset):
        total = request.POST.get('total', 0)
        points_value = request.POST.get('points_value', 1)
        redeem_list = []
        for i in range(0, int(total)):
            redeem_list.append(RedemptionCode(code=RedemptionCode.generate_code(), points_value=points_value))
        RedemptionCode.objects.bulk_create(redeem_list)
        tip_msg = f'批量生产兑换码 {total} 条'
        return JsonResponse(data={
            'status': 'success',
            'msg': tip_msg
        })

    bulk_generate.short_description = ' 批量'
    bulk_generate.type = 'success'
    bulk_generate.icon = 'fa fa-solid fa-hands-bubbles'

    bulk_generate.layer = {
        # 弹出层中的输入框配置

        # 这里指定对话框的标题
        'title': '批量生成兑换码',
        # 提示信息
        'tips': '兑换码用于兑换商品，默认兑换机积分为 1 ',
        # 确认按钮显示文本
        'confirm_button': '提交',
        # 取消按钮显示文本
        'cancel_button': '取消',

        # 弹出层对话框的宽度，默认50%
        'width': '30%',

        # 表单中 label的宽度，对应element-ui的 label-width，默认80px
        'labelWidth': "80px",
        'params': [{
            'type': 'input',
            'key': 'total',
            'size': 'small',
            'width': '300px',
            'label': '数量',
            'require': True
        },{
            'type': 'input',
            'key': 'points_value',
            'size': 'small',
            'width': '300px',
            'label': '积分值',
            'value': '1',
            'require': True
        }]
        #{
        #     'type': 'select',
        #     'key': 'prize',
        #     'label': '奖品',
        #     'width': '300px',
        #     'size': 'small',
        #     'value': '',
        #     'require': True,
        #     'options': Redeem.prize_list(),
        # }]

    }


@admin.register(PointsTransaction)
class PointsTransactionAdmin(AjaxAdmin):
    list_filter = ('user__mobile',)
    list_display = ('user', 'amount', 'transaction_type', 'description', 'created_at')


@admin.register(ExchangeOrder)
class ExchangeOrderAdmin(AjaxAdmin):
    list_filter = ('status',)
    search_fields = ['user__mobile', 'tracking_number']
    list_display = ('user', 'tracking_number', 'status', 'note', 'harvest','created_at')

