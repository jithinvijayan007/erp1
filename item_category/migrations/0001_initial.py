# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2021-08-16 19:49
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('pk_bint_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('vchr_name', models.CharField(blank=True, max_length=100, null=True)),
                ('vchr_item_code', models.CharField(max_length=50, unique=True)),
                ('dbl_supplier_cost', models.FloatField(blank=True, null=True)),
                ('dbl_dealer_cost', models.FloatField(blank=True, null=True)),
                ('dbl_mrp', models.FloatField(blank=True, null=True)),
                ('dbl_mop', models.FloatField(blank=True, null=True)),
                ('json_specification_id', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('int_reorder_level', models.IntegerField(blank=True, null=True)),
                ('vchr_prefix', models.CharField(blank=True, max_length=40, null=True)),
                ('imei_status', models.NullBooleanField()),
                ('sale_status', models.NullBooleanField()),
                ('int_status', models.IntegerField(default=0)),
                ('dat_created', models.DateTimeField()),
                ('image1', models.CharField(blank=True, max_length=350, null=True)),
                ('image2', models.CharField(blank=True, max_length=350, null=True)),
                ('image3', models.CharField(blank=True, max_length=350, null=True)),
                ('dat_updated', models.DateTimeField(blank=True, null=True)),
                ('vchr_old_item_code', models.CharField(blank=True, max_length=50, null=True)),
                ('dbl_myg_amount', models.FloatField(blank=True, null=True)),
            ],
            options={
                'db_table': 'item',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ItemCategory',
            fields=[
                ('pk_bint_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('vchr_item_category', models.CharField(max_length=50)),
                ('json_tax_master', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('json_specification_id', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('int_status', models.IntegerField(default=0)),
                ('dat_created', models.DateTimeField()),
                ('vchr_hsn_code', models.CharField(blank=True, max_length=50, null=True)),
                ('vchr_sac_code', models.CharField(blank=True, max_length=50, null=True)),
            ],
            options={
                'db_table': 'item_category',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SapTaxMaster',
            fields=[
                ('pk_bint_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('vchr_code', models.CharField(blank=True, max_length=20, null=True)),
                ('vchr_name', models.CharField(blank=True, max_length=100, null=True)),
                ('dbl_rate', models.FloatField(blank=True, null=True)),
                ('jsn_tax_master', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'sap_tax_master',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='TaxMaster',
            fields=[
                ('pk_bint_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('vchr_name', models.CharField(blank=True, max_length=100, null=True)),
                ('int_intra_tax', models.IntegerField(blank=True, default=0, null=True)),
                ('bln_active', models.NullBooleanField()),
            ],
            options={
                'db_table': 'tax_master',
                'managed': False,
            },
        ),
    ]
