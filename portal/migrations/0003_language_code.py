# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-08 21:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0002_scoping_ost_elements'),
    ]

    operations = [
        migrations.AddField(
            model_name='language',
            name='code',
            field=models.CharField(default='tbd', max_length=16),
            preserve_default=False,
        ),
    ]