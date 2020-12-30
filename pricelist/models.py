from django.db import models
from item_category.models import Item
# Create your models here.
from django.contrib.auth.models import User


class PriceList(models.Model):

    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_item = models.ForeignKey(Item, models.DO_NOTHING, blank=True, null=True,related_name="item")
    dat_efct_from = models.DateTimeField(blank=True, null=True)
    fk_created = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,related_name="plist_created")
    dat_created = models.DateTimeField(blank=True, null=True)
    fk_updated = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,related_name="plist_updated")
    dat_updated = models.DateTimeField(blank=True, null=True)
    int_status = models.IntegerField(blank=True, null=True)# 0. Active -1. delete,
    dbl_supp_amnt = models.FloatField(blank=True, null=True)
    dbl_cost_amnt = models.FloatField(blank=True, null=True)
    dbl_mop = models.FloatField(blank=True, null=True)
    dbl_mrp = models.FloatField(blank=True, null=True)
    dbl_my_amt = models.FloatField(blank=True, null=True)
    dbl_dealer_amt = models.FloatField(blank=True, null=True)
    dbl_dealer_amt = models.FloatField(blank=True, null=True)
    int_myg_amt = models.FloatField(blank=True, null=True)
    int_dealer_amt = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'price_list'
