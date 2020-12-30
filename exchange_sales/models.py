from django.db import models
from django.contrib.postgres.fields import JSONField
from branch.models import Branch
from item_category.models import Item
from invoice.models import SalesDetails
# Create your models here.
class ExchangeStock(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    jsn_imei = JSONField(blank=True, null=True)  # This field type is a guess.
    jsn_avail = JSONField(blank=True, null=True)  # This field type is a guess.
    fk_branch = models.ForeignKey(Branch, models.DO_NOTHING, blank=True, null=True)
    fk_item = models.ForeignKey(Item, models.DO_NOTHING, blank=True, null=True)
    fk_sales_details = models.ForeignKey(SalesDetails, models.DO_NOTHING, blank=True, null=True)
    int_avail = models.IntegerField(blank=True, null=True)
    dat_exchanged = models.DateTimeField(blank=True, null=True)
    dbl_unit_price = models.FloatField(blank=True, null=True)
    int_status = models.IntegerField(default=0) # 0: availiable for sale, 1: not available for sales
    class Meta:
        managed = False
        db_table = 'exchange_stock'
