# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-17 11:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lines', '0002_auto_20170416_1823'),
    ]

    operations = [
        migrations.AddField(
            model_name='line',
            name='xml',
            field=models.TextField(default='', verbose_name='XML'),
        ),
    ]
