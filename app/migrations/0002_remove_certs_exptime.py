# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2020-03-23 11:29
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='certs',
            name='exptime',
        ),
    ]
