# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2020-03-23 10:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Certs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45, unique=True, verbose_name='域名名称')),
                ('type', models.CharField(max_length=126, verbose_name='平台名称')),
                ('issued_by', models.CharField(max_length=64, null=True, verbose_name='颁发机构')),
                ('notbefore', models.CharField(blank=True, max_length=24, null=True, verbose_name='开始时间')),
                ('notafter', models.CharField(blank=True, max_length=24, null=True, verbose_name='到期时间')),
                ('remain_days', models.IntegerField(blank=True, default=4, null=True, verbose_name='剩余天数')),
                ('last_time', models.DateTimeField(auto_now_add=True, null=True, verbose_name='最后检查时间')),
                ('alarm', models.BooleanField(default=False, verbose_name='告警')),
                ('exptime', models.CharField(max_length=256, verbose_name='域名到期时间')),
                ('dreamin_days', models.IntegerField(blank=True, default=4, null=True, verbose_name='域名到期剩余天数')),
                ('dnsinfo', models.CharField(max_length=256, verbose_name='域名DNS详情')),
            ],
        ),
    ]
