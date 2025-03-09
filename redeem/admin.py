from django.contrib import admin
from django.http import JsonResponse, HttpResponse
from simpleui.admin import AjaxAdmin
from openpyxl import Workbook
from openpyxl.styles import Alignment,Font,PatternFill
from datetime import datetime
from .models import Redeem, Redemption

def prize_list():
    return Redeem.prize_list()

@admin.register(Redeem)
class RedeemAdmin(AjaxAdmin):
    list_display = ('number', 'prize', 'series_name','status', 'created_at')
    fields = ('prize', 'status', 'number')
    list_filter = ['prize', 'status']
    search_fields = ['number']

    actions = ['bulk_generate', 'export_data']

    def series_name(self, obj):
        return obj.prize.series.name if obj.prize else ''
    series_name.short_description = '所属系列'

    def export_data(self, request, queryset):
        wb = Workbook()
        ws = wb.active
        ws.title = '兑换码列表'

        header_font = Font(bold=True, color='FFFFFF')
        header_fill = PatternFill(start_color='4F81BD', end_color='4F81BD', fill_type='solid')
        headers = ['兑换码', '奖品名称', '所属系列', '状态', '创建时间']
        for i, header in enumerate(headers):
            ws.cell(row=1, column=i+1, value=header)
            ws.cell(row=1, column=i+1).font = header_font
            ws.cell(row=1, column=i+1).fill = header_fill
            ws.cell(row=1, column=i+1).alignment = Alignment(horizontal='center')

        for obj in queryset:
            row = [obj.number, obj.prize.name, obj.prize.series.name, obj.get_status_display(),
                   obj.created_at.strftime('%Y-%m-%d %H:%M:%S')]
            ws.append(row)

        for col in ws.columns:
            max_length = max(len(str(cell.value)) for cell in col)
            ws.column_dimensions[col[0].column_letter].width = max_length + 10

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"兑换码_{timestamp}_数据.xlsx"
        response["Content-Disposition"] = f'attachment; filename*=UTF-8 ''{filename}'
        wb.save(response)
        return response

    export_data.short_description = ' 导出'
    export_data.type = 'warning'
    export_data.icon = 'fa fa-solid fa-file-export'

    def bulk_generate(self, request, queryset):
        total = request.POST.get('count', 0)
        redeem_list = []
        prefix = request.POST.get('prefix', None)
        if prefix:
            if len(prefix) >= 4:
                prefix = prefix[:4]
            else:
                return JsonResponse(data={
                    'status': 'error',
                    'msg': '前缀系列ODE长度不足4个字符'
                })
            for i in range(0, int(total)):
                redeem_list.append(Redeem(number=Redeem.generate_prefix(prefix), prize_id= request.POST.get('prize')))
        else:
            for i in range(0, int(total)):
                redeem_list.append(Redeem(number=Redeem.generate_number(), prize_id= request.POST.get('prize')))
        Redeem.objects.bulk_create(redeem_list)
        return JsonResponse(data={
            'status': 'success',
            'msg': '处理成功！'
        })

    bulk_generate.short_description = ' 批量'
    bulk_generate.type = 'success'
    bulk_generate.icon = 'fa fa-solid fa-bowl-rice'

    bulk_generate.layer = {
        # 弹出层中的输入框配置

        # 这里指定对话框的标题
        'title': '批量生成兑换码',
        # 提示信息
        'tips': '兑换码格式为 XUK9-CRPM-VX4Y-F1AH ，由4部分组成，每部分为4个字符，'
                '可以指定第一部分字符串为统一内容前缀。如不指定前缀，请留空，则随机生成。',
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
            'key': 'prefix',
            'size': 'small',
            'width': '300px',
            'label': '前缀'
        }, {
            'type': 'input',
            'key': 'count',
            'size': 'small',
            'width': '300px',
            'label': '数量',
            'require': True
        },  {
            'type': 'select',
            'key': 'prize',
            'label': '奖品',
            'width': '300px',
            'size': 'small',
            'value': '',
            'require': True,
            'options': prize_list(),
        }]
    }

@admin.register(Redemption)
class RedemptionAdmin(admin.ModelAdmin):
    list_display = ('prize','redeem','consumer', 'shipping', 'express_order','status', 'created_at')
    fields = ('prize','redeem', 'consumer', 'shipping', 'express_order','status')
# Register your models here.
