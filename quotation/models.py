from django.db import models
from branch.models import Branch
from states.models import Location,States
from django.contrib.auth.models import User as AuthUser
from django.contrib.postgres.fields import JSONField

# Create your models here.
class QuotationManager(models.Manager):
    def create_quotation_doc(self, str_new_doc_no):
         quotation_ = self.create(vchr_voucher_num=vchr_voucher_num)
         return quotation_

class Quotation(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_doc_num = models.CharField(max_length=50, blank=True, null=True)
    fk_branch = models.ForeignKey(Branch, models.DO_NOTHING, blank=True, null=True)
    vchr_cust_name = models.CharField(max_length=100, blank=True, null=True)
    fk_state = models.ForeignKey(States, models.DO_NOTHING, blank=True, null=True)
    vchr_email = models.CharField(max_length=50, blank=True, null=True)
    bint_mobile = models.BigIntegerField(blank=True, null=True)
    txt_address = models.TextField(blank=True, null=True)
    txt_remarks = models.TextField(blank=True, null=True)
    vchr_gst_no = models.CharField(max_length=50, blank=True, null=True)
    jsn_data = JSONField(blank=True, null=True)
    fk_location = models.ForeignKey(Location, models.DO_NOTHING, blank=True, null=True)
    dat_created = models.DateTimeField(blank=True, null=True)
    fk_created = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True)
    int_active = models.IntegerField(blank=True, null=True,default= 0)
    dat_exp = models.DateField(blank=True, null=True)
    # objects = QuotationManager()

    class Meta:
        managed = False
        db_table = 'quotation'
