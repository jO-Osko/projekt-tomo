# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-08-10 12:42
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0022_auto_20160810_1221'),
    ]

    operations = [
        migrations.AlterOrderWithRespectTo(
            name='problem',
            order_with_respect_to='problem_set',
        ),
    ]