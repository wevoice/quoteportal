# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-10 16:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0010_auto_20161210_1114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='name',
            field=models.CharField(max_length=128, unique=True),
        ),
    ]
