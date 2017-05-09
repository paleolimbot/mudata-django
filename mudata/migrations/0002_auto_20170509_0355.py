# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-09 03:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mudata', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='datumraw',
            options={'verbose_name_plural': 'raw data'},
        ),
        migrations.AlterField(
            model_name='dataset',
            name='dataset',
            field=models.SlugField(unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='column',
            unique_together=set([('dataset', 'table', 'column')]),
        ),
        migrations.AlterUniqueTogether(
            name='datum',
            unique_together=set([('dataset', 'location', 'param', 'x')]),
        ),
        migrations.AlterUniqueTogether(
            name='datumraw',
            unique_together=set([('dataset', 'location', 'param', 'x')]),
        ),
        migrations.AlterUniqueTogether(
            name='location',
            unique_together=set([('dataset', 'location')]),
        ),
        migrations.AlterUniqueTogether(
            name='param',
            unique_together=set([('dataset', 'param')]),
        ),
    ]
