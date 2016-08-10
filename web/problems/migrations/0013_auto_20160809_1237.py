# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-08-09 12:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0012_auto_20160809_1231'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='HistoricalProblem',
            new_name='HistoricalProblemContents',
        ),
        migrations.RenameModel(
            old_name='Problem',
            new_name='ProblemContents',
        ),
        migrations.AlterModelOptions(
            name='historicalproblemcontents',
            options={'get_latest_by': 'history_date', 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical problem contents'},
        ),

    ]

"""        migrations.AlterField(
            model_name='historicalpart',
            name='problem',
            field=models.ForeignKey(related_name='problems', default=1, to='problems.ProblemContents'),
            preserve_default=False,
        ),"""