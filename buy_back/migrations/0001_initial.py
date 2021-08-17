# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2021-08-16 19:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BuyBack',
            fields=[
                ('pk_bint_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('dat_start', models.DateTimeField(blank=True, null=True)),
                ('dat_end', models.DateTimeField(blank=True, null=True)),
                ('dbl_amount', models.FloatField(blank=True, null=True)),
                ('int_status', models.IntegerField(blank=True, default=1, null=True)),
            ],
            options={
                'db_table': 'buy_back',
                'managed': False,
            },
        ),
    ]
