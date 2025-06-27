from django.contrib import admin
from django.forms import ModelForm, Media
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.conf import settings
from .models import Store, Plush


class StoreAdminForm(ModelForm):
    """自定义店铺表单，集成高德地图"""

    class Meta:
        model = Store
        fields = '__all__'

    class Media:
        css = {
            'all': ('admin/css/store_admin.css',)
        }
        js = (
            f'https://webapi.amap.com/maps?v=2.0&key={getattr(settings, "AMAP_API_KEY", "")}',
            'admin/js/amap_widget.js',
        )


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    form = StoreAdminForm
    list_display = ['name', 'address', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'address', 'phone']

    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'address', 'phone', 'description')
        }),
        ('位置信息', {
            'fields': ('latitude', 'longitude', 'map_widget'),
            'description': '点击地图选择店铺位置，或输入地址搜索获取坐标'
        }),
        ('营业信息', {
            'fields': ('business_hours', 'is_active')
        }),
    )

    readonly_fields = ['map_widget']

    def map_widget(self, obj):
        """地图插件"""
        return mark_safe(f'''
                <div style="margin: 10px 0;">
                    <input type="text" id="address-input" placeholder="输入地址名称搜索..." 
                           style="width: 400px; padding: 5px; margin-right: 10px;">
                    <button type="button" id="search-btn" style="padding: 5px 10px;">搜索地址</button>
                </div>
                <div id="amap-container" style="width: 750px; height: 400px; margin: 10px 0;"></div>
                <div id="location-info" style="margin: 10px 0; color: #666;"></div>
                ''')

    map_widget.short_description = '地图选择'

    class Media:
        css = {
            'all': ('admin/css/store_admin.css',)
        }
        js = (
            f'https://webapi.amap.com/maps?v=2.0&key={getattr(settings, "AMAP_API_KEY", "")}',
            'admin/js/amap_widget.js',
        )


@admin.register(Plush)
class PlushAdmin(admin.ModelAdmin):
    list_display = ['name','main_img','is_latest', 'created_at']
    list_filter = ['is_latest']
    search_fields = ['name']

    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'is_latest', 'main_image')
        }),
        ('周边详情', {
            'fields': ('description',)
        }),
    )

    def main_img(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" width="auto" height="75" />', obj.main_image.url)

    main_img.short_description = '封面'
