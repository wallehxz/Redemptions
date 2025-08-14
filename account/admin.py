import json
from django.contrib import admin, messages
from django.db.models import Q
from django.http import JsonResponse
from simpleui.admin import AjaxAdmin
from account.models import Consumer, Shipping, Region


@admin.register(Consumer)
class ConsumerAdmin(admin.ModelAdmin):
    search_fields = ('mobile', )
    list_display = ('mobile', 'openid', 'username', 'role_name', 'last_login', 'date_joined')
    list_filter = ['mobile', 'sales_rep', 'is_superuser']
    list_per_page = 20

    def role_name(self, obj):
        return obj.role_display()
    role_name.short_description = '角色'


@admin.register(Shipping)
class ShippingAdmin(admin.ModelAdmin):
    list_display = ('nick_name', 'mobile', 'is_default', 'address')
    list_per_page = 20


def region_set_province():
    provinces = Region.objects.filter(Q(city='0') & Q(area='0') & Q(town='0'))
    for p in provinces:
        cities = Region.objects.filter(Q(province=p.province) & ~Q(city='0') & Q(area='0') & Q(town='0'))
        if len(cities) > 0:
            print(f'设置 {p.name} 城市 {cities.count()}')
            cities.update(parent=p.id)
            for c in cities:
                areas = Region.objects.filter(Q(province=p.province) & Q(city=c.city) & ~Q(area='0') & Q(town='0'))
                if len(areas) > 0:
                    print(f'设置 {p.name} {c.name} 市区 {areas.count()}')
                    areas.update(parent=c.id)
                    for a in areas:
                        towns = Region.objects.filter(Q(province=p.province) & Q(city=c.city) & Q(area=a.area) & ~Q(town='0'))
                        if len(towns) > 0:
                            print(f'设置 {p.name} {c.name} {a.name} 乡镇街道 {towns.count()}')
                            towns.update(parent=a.id)
        else:
            print(f'设置直辖市区')
            areas = Region.objects.filter(Q(province=p.province) & ~Q(city='0') & ~Q(area='0') & Q(town='0'))
            if len(areas) > 0:
                areas.update(parent=p.id)
                print(f'设置 {p.name} 市区 {areas.count()}')
                for a in areas:
                    towns = Region.objects.filter(Q(province=p.province) & ~Q(city='0') & Q(area=a.area) & ~Q(town='0'))
                    if len(towns) > 0:
                        print(f'设置 {p.name} {a.name} 街道 {towns.count()}')
                        towns.update(parent=a.id)


@admin.register(Region)
class RegionAdmin(AjaxAdmin):
    list_display = ('name', 'parent', 'children_area')
    search_fields = ['name', 'code']
    actions = ['export_data',]
    list_per_page = 20

    def children_area(self, obj):
        if obj.children.count() > 0:
            return f'{obj.children.count()} 区域'
        else:
            return '--'

    children_area.short_description = '下辖区域'

    def export_data(self, request, queryset):
        # 这里的upload 就是和params中配置的key一样
        if Region.objects.all().count() > 100:
            return JsonResponse(data={
                'status': 'error',
                'msg': '已存在省市区域数据!'
            })
        else:
            json_file = request.FILES['upload']
            data = json.load(json_file)
            region_list = []
            for item in data:
                region_list.append(Region(code=item.get('code'),
                    name=item.get('name'),
                    province=item.get('province'),
                    city=item.get('city'),
                    area=item.get('area'),
                    town=item.get('town'),
                ))
            Region.objects.bulk_create(region_list)
            region_set_province()
            return JsonResponse(data={
                'status': 'success',
                'msg': '处理成功！'
            })

    export_data.short_description = '地区数据'
    export_data.type = 'success'
    export_data.icon = 'el-icon-upload'
    export_data.enable = True

    export_data.layer = {
        'title': '导入区域数据',
        'tips': '请勿重复导入区域管理数据',
        'params': [{
            'type': 'file',
            'key': 'upload',
            'label': '文件'
        }]
    }

# Register your models here.
