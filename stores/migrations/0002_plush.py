# Generated by Django 5.2.1 on 2025-06-26 05:12

import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Plush',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='主题名称')),
                ('main_image', models.ImageField(null=True, upload_to='plush/%Y%m%d/', verbose_name='主图')),
                ('is_latest', models.BooleanField(default=False, verbose_name='是否最新')),
                ('description', ckeditor.fields.RichTextField(blank=True, null=True, verbose_name='周边详情')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '玩偶周边',
                'verbose_name_plural': '玩偶周边',
                'ordering': ['-is_latest'],
            },
        ),
    ]
