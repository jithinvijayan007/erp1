
from django.db import models
from django.contrib.postgres.fields import JSONField
from products.models import Products
from item_group.models import ItemGroup
from products.models import Specifications
from brands.models import Brands
from userdetails.models import UserDetails as Userdetails
from datetime import datetime
from django.utils import timezone
from company.models import Company
# Create your models here.

class TaxMaster(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_name = models.CharField(max_length=100, blank=True, null=True)
    int_intra_tax = models.IntegerField(blank=True, null=True,default=0)
    bln_active = models.NullBooleanField()

    class Meta:
        managed = False
        db_table = 'tax_master'
    def __str__(self):
        return self.vchr_name

class ItemCategory(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_item_category = models.CharField(max_length=50)
    json_tax_master = JSONField(blank=True, null=True)  # This field type is a guess.
    json_specification_id = JSONField(blank=True, null=True)  # This field type is a guess.
    int_status = models.IntegerField(default = 0)# 0. Active -1. delete,
    dat_created = models.DateTimeField()
    fk_created = models.ForeignKey(Userdetails, models.DO_NOTHING ,blank=True, null=True,related_name = 'created_id')
    fk_updated = models.ForeignKey(Userdetails, models.DO_NOTHING , blank=True, null=True,related_name = 'updated_id')
    vchr_hsn_code = models.CharField(max_length=50, blank=True, null=True)
    vchr_sac_code = models.CharField(max_length=50, blank=True, null=True)
    fk_company = models.ForeignKey(Company, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'item_category'


class Item(models.Model):

    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_name = models.CharField(max_length=100, blank=True, null=True)
    fk_product = models.ForeignKey(Products, models.DO_NOTHING)
    fk_brand = models.ForeignKey(Brands, models.DO_NOTHING)
    vchr_item_code = models.CharField(unique=True, max_length=50)
    fk_item_category = models.ForeignKey(ItemCategory, models.DO_NOTHING)
    fk_item_group = models.ForeignKey(ItemGroup, models.DO_NOTHING)
    dbl_supplier_cost = models.FloatField(blank=True, null=True)
    dbl_dealer_cost = models.FloatField(blank=True, null=True)
    dbl_mrp = models.FloatField(blank=True, null=True)
    dbl_mop = models.FloatField(blank=True, null=True)
    json_specification_id = JSONField(blank=True, null=True)  # This field type is a guess.
    int_reorder_level = models.IntegerField(blank=True, null=True)
    vchr_prefix = models.CharField(max_length=40, blank=True, null=True)
    imei_status = models.NullBooleanField() #true if imei number in serial number ,false if automatic serial number
    sale_status = models.NullBooleanField() #true saleable ,false not saleable
    int_status = models.IntegerField(default = 0)# 0. Active -1. delete,
    dat_created = models.DateTimeField()
    fk_created = models.ForeignKey(Userdetails, models.DO_NOTHING ,blank=True, null=True,related_name = 'item_created_id')
    fk_updated = models.ForeignKey(Userdetails, models.DO_NOTHING ,blank=True, null=True, related_name = 'item_updated_id')
    image1 = models.CharField(max_length=350, blank=True, null=True)
    image2 = models.CharField(max_length=350, blank=True, null=True)
    image3 = models.CharField(max_length=350, blank=True, null=True)
    dat_updated = models.DateTimeField(blank=True, null=True)
    vchr_old_item_code = models.CharField(max_length=50, blank=True, null=True)
    dbl_myg_amount = models.FloatField(blank=True, null=True)
    fk_company = models.ForeignKey(Company, models.DO_NOTHING, blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'item'
    def __str__(self):
        return self.vchr_name + "  " + self.vchr_item_code


class SapTaxMaster(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_code = models.CharField(max_length=20, blank=True, null=True)
    vchr_name = models.CharField(max_length=100, blank=True, null=True)
    dbl_rate = models.FloatField(blank=True, null=True)
    jsn_tax_master = models.TextField(blank=True, null=True)  # This field type is a guess.


    class Meta:
        managed = False
        db_table = 'sap_tax_master'
