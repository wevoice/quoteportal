# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-02 03:04
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0018_pdfasset'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pdfasset',
            old_name='act_total_wordcount',
            new_name='total_wordcount',
        ),
        migrations.RemoveField(
            model_name='pdfasset',
            name='est_total_wordcount',
        ),
    ]
