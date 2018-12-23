# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-12-23 15:48
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account_app', '0015_auto_20181223_2131'),
    ]

    operations = [
        migrations.CreateModel(
            name='message',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('missionnum', models.IntegerField(choices=[(0, '分配'), (1, '会签'), (2, '定稿'), (3, '审批'), (4, '签订')], default=0)),
                ('contractnum', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='account_app.Contract')),
                ('username', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
