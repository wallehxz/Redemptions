from django.contrib import admin
from django.utils.html import format_html
from .models import Series, Prize

admin.site.site_header = '福赏管理'
admin.site.site_title = '福赏'
admin.site.index_title = '福赏管理系统'


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ('logo_img', 'name',  'prizes_count', 'created_at')
    search_fields = ['name']
    list_per_page = 10

    def logo_img(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="75" height="75" />', obj.logo.url)
        return "No Image"
    logo_img.short_description = '头图'

    def prizes_count(self, obj):
        return obj.prizes.count()
    prizes_count.short_description = '奖品数量'

    def edit_link(self, obj):
        return format_html(
            '<a href="{url}">编辑</a>',
            url=f"{obj.id}"
        )
    edit_link.short_description = '操作'


@admin.register(Prize)
class PrizeAdmin(admin.ModelAdmin):
    list_display = ('logo_img', 'name', 'series','inventory','redeems_count', 'created_at')
    fields = ('series', 'logo','inventory', 'name')
    search_fields = ['name']
    list_filter = ['series']
    list_per_page = 10

    def logo_img(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="75" height="75" />', obj.logo.url)
        return "No Image"

    logo_img.short_description = '头图'

    def redeems_count(self, obj):
        if obj.redeems.count() > 0:
            html = f"<a href='/admin/redeem/redeem/?prize__id__exact={obj.id}'>查看 [{obj.redeems.count()}]</a>"
            return format_html(html)
        else:
            return '--'

    redeems_count.short_description = '兑换码数量'

    def edit_link(self, obj):
        return format_html(
            '<a href="{url}">编辑</a>',
            url=f"{obj.id}"
        )

    edit_link.short_description = '操作'

