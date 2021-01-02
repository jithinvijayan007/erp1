from django.db import models
from django.contrib.postgres.fields import JSONField
from category.models import Category
from django.utils import timezone
# from userdetails.models import UserDetails as Userdetails

# Create your models here.
class Specifications(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_name = models.CharField(max_length=50)
    bln_status = models.NullBooleanField()

    class Meta:
        managed = False
        db_table = 'specifications'


class Products(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_name = models.CharField(max_length=50)
    fk_category = models.ForeignKey(Category, models.DO_NOTHING)
    # fk_specification = models.ForeignKey(Specifications, models.DO_NOTHING)
    # bln_sales = models.NullBooleanField() #true if sales,false if service
    int_status = models.IntegerField(default = 0)# 0. Active -1. delete,
    dat_created = models.DateTimeField()
    # fk_created = models.ForeignKey(UserDetails, models.DO_NOTHING ,blank=True, null=True,related_name = 'product_created_id')
    # fk_updated = models.ForeignKey(UserDetails, models.DO_NOTHING , blank=True, null=True,related_name = 'product_updated_id')
    # json_sales = JSONField(blank=True, null=True)  # This field type is a guess.22222
    int_sales = models.IntegerField(blank=True, null=True) #1 sales 2 service 3 sales and service
    int_type = models.IntegerField(blank=True, null=True,default=0)
    class Meta:
        managed = False
        db_table = 'products'
