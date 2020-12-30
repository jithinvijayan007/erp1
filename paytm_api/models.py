from django.db import models
from invoice.models import PartialInvoice,SalesMaster
from django.contrib.auth.models import User as AuthUser
# Create your models here.
class PaytmPointData(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_partial = models.ForeignKey(PartialInvoice, models.DO_NOTHING, blank=True, null=True)
    int_status = models.SmallIntegerField(blank=True, null=True) #0:open  1:closed -1 returned
    dat_created = models.DateTimeField(blank=True, null=True)
    fk_created = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True)
    dat_updated = models.DateTimeField(blank=True, null=True)
    fk_invoice = models.ForeignKey(SalesMaster, models.DO_NOTHING, blank=True, null=True)
    vchr_ref_num = models.CharField(max_length=100, blank=True, null=True)
    dbl_amount = models.FloatField(blank=True, null=True)
    dbl_pts = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'paytm_point_data'