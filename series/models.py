from django.db import models
from django.contrib import admin
from django.utils.html import format_html


class Series(models.Model):
    name = models.CharField(max_length=100, verbose_name='名称')
    logo = models.ImageField(upload_to='series/%Y%m%d/', null=True, verbose_name='头图')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'series'
        verbose_name = '系列'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class Prize(models.Model):
    name = models.CharField(max_length=100, verbose_name='名称')
    logo = models.ImageField(upload_to='prizes/%Y%m%d/', null=True, verbose_name='头图')
    series = models.ForeignKey(Series, on_delete=models.SET_NULL, null=True, related_name='prizes',verbose_name='系列')
    inventory = models.IntegerField(null=True, verbose_name='库存数量')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'prizes'
        verbose_name = '奖品'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

# Create your models here.
