# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2020-03-25 17:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20200325_1117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='certs',
            name='a_notes',
            field=models.CharField(max_length=256, verbose_name='域名A记录'),
        ),
    ]
