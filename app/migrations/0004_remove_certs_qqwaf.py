# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2020-03-25 10:37
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20200325_1029'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='certs',
            name='qqwaf',
        ),
    ]