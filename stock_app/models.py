from django.db import models

from company.models import Company as CompanyDetails
from branch.models import Branch
from userdetails.models import UserDetails as UserModel
from supplier.models import Supplier
# from  .models import Items
from item_category.models import Item as Items

from django.contrib.postgres.fields import JSONField


# Create your models here.
class Stockmaster(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_supplier = models.ForeignKey(Supplier, models.DO_NOTHING)
    dat_added = models.DateTimeField(blank=True, null=True)
    vchr_payment_mode = models.CharField(max_length=50)
    dbl_paid_amount = models.FloatField(blank=True, null=True)
    fk_branch = models.ForeignKey(Branch, models.DO_NOTHING)
    fk_company = models.ForeignKey(CompanyDetails, models.DO_NOTHING)
    fk_user = models.ForeignKey(UserModel, models.DO_NOTHING, related_name='fk_user')
    dat_updated = models.DateTimeField(blank=True, null=True)
    fk_updated = models.ForeignKey(UserModel, models.DO_NOTHING, blank=True, null=True , related_name='fk_updated_user_stock_master')
    vchr_purchase_order_number = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
            return str(self.fk_supplier)

    class Meta:
        managed = False
        db_table = 'stockmaster'



class Stockdetails(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_stock_master = models.ForeignKey(Stockmaster, models.DO_NOTHING)
    fk_item = models.ForeignKey(Items, models.DO_NOTHING)
    int_qty = models.IntegerField(blank=True, null=True)
    dbl_cost = models.FloatField(blank=True, null=True)
    dbl_min_selling_price = models.FloatField(blank=True, null=True)
    dbl_max_selling_price = models.FloatField(blank=True, null=True)
    int_available = models.IntegerField(blank=True, null=True)
    dbl_imei_json = JSONField(blank=True, null=True)

    def __str__(self):
            return str(self.fk_stock_master+'-'+self.fk_item)

    class Meta:
        managed = False
        db_table = 'stockdetails'
