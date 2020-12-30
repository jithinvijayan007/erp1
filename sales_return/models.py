from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User as AuthUser
from item_category.models import Item
from invoice.models import SalesMaster,SalesDetails

# Create your models here.

class SalesReturnDocumentManager(models.Manager):
    def create_sales_return(self, str_new_doc_no):
         sales_return = self.create(vchr_doc_code=str_new_doc_no)
         return sales_return

class SalesReturn(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_sales = models.ForeignKey(SalesMaster, models.DO_NOTHING, blank=True, null=True,related_name='sales')
    fk_returned = models.ForeignKey(SalesMaster, models.DO_NOTHING, blank=True, null=True,related_name='returned')
    fk_item = models.ForeignKey(Item, models.DO_NOTHING, blank=True, null=True)
    int_qty = models.IntegerField(blank=True, null=True)
    dbl_amount = models.FloatField(blank=True, null=True)
    dbl_selling_price = models.FloatField(blank=True, null=True)
    jsn_imei = JSONField()
    dat_returned = models.DateField(blank=True, null=True)
    fk_staff = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True,related_name='assigned')
    dat_created = models.DateTimeField(blank=True, null=True)
    fk_created = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, related_name='creates')
    dat_updated = models.DateTimeField(blank=True, null=True)
    fk_updated = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, related_name='updates')
    int_doc_status = models.IntegerField(blank=True, null=True)
    bln_damaged = models.NullBooleanField()
    vchr_image = models.CharField(max_length=350, blank=True, null=True)
    vchr_remark = models.CharField(max_length=500, blank=True, null=True)
    vchr_doc_code = models.CharField(max_length=50, blank=True, null=True)
    fk_sales_details = models.ForeignKey(SalesDetails, models.DO_NOTHING, blank=True, null=True)
    dbl_indirect_discount = models.FloatField(blank=True, null=True)
    dbl_discount = models.FloatField(blank=True, null=True)
    dbl_buyback = models.FloatField(blank=True, null=True)
    objects = SalesReturnDocumentManager()
    vchr_old_inv_no = models.CharField(max_length=20, blank=True, null=True)


    class Meta:
        managed = False
        db_table = 'sales_return'
