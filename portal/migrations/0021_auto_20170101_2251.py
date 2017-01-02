# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-02 03:51
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0020_pdfasset_total_pages'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PDFAsset',
            new_name='DTPAsset',
        ),
        migrations.AlterModelOptions(
            name='dtpasset',
            options={'verbose_name_plural': 'DTP Assets'},
        ),
        migrations.RenameField(
            model_name='dtpasset',
            old_name='editable_pdf_source_available',
            new_name='editable_source_available',
        ),
    ]
