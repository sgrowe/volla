# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-11 13:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('activity', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='when',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
