# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-16 09:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Line',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('ref', models.CharField(max_length=20, verbose_name='Internal line number of operator')),
                ('publicref', models.CharField(max_length=20, verbose_name='Line number')),
                ('operator', models.CharField(max_length=30)),
                ('network', models.CharField(max_length=30, verbose_name='Abbreviation for region')),
                ('colour', models.CharField(max_length=7)),
                ('mode', models.CharField(max_length=30, verbose_name='transport mode')),
            ],
        ),
        migrations.CreateModel(
            name='Variation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('fromstop', models.CharField(max_length=50, verbose_name='first stop')),
                ('tostop', models.CharField(max_length=50, verbose_name='terminus')),
                ('version', models.IntegerField(default=2, verbose_name='public transport version of OSM route relation')),
                ('line', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lines.Line')),
            ],
        ),
    ]
