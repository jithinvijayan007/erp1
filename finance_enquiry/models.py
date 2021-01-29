from django.db import models
from enquiry_mobile.models import EnquiryMaster
from userdetails.models import Financiers
from userdetails.models import UserDetails as AuthUser
from item_category.models import Item as Items
# Create your models here.



class FinanceSchema(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_schema = models.CharField(max_length=50, blank=True, null=True)
    fk_financier = models.ForeignKey(Financiers, models.DO_NOTHING, blank=True, null=True)
    dat_from = models.DateField(blank=True, null=True)
    dat_to = models.DateField(blank=True, null=True)
    fk_item = models.ForeignKey(Items, models.DO_NOTHING, blank=True, null=True)
    fk_created_by = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True)
    dat_created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'finance_scheme'

    def __str__(self):
            return str(self.vchr_schema)

class EnquiryFinance(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_financiers = models.ForeignKey(Financiers, models.DO_NOTHING, blank=True, null=True)
    vchr_finance_status = models.CharField(max_length=20, blank=True, null=True)
    vchr_remarks = models.CharField(max_length=200, blank=True, null=True)
    dbl_max_amt = models.FloatField(blank=True, null=True)
    vchr_name_in_card = models.CharField(max_length=50, blank=True, null=True)
    vchr_delivery_order_no = models.CharField(max_length=50, blank=True, null=True)
    fk_enquiry_master = models.ForeignKey(EnquiryMaster, models.DO_NOTHING,  blank=True, null=True)
    fk_financier_schema = models.ForeignKey(FinanceSchema, models.DO_NOTHING, blank=True, null=True)
    bln_eligible = models.NullBooleanField()
    int_status = models.IntegerField(blank=True, null=True,default=0)
    int_bajaj = models.IntegerField(blank=True, null=True) # 0)Not Bajaj Enquiry 1)Bajaj Enquiry 2)Image Uploaded
    
    class Meta:
        managed = False
        db_table = 'enquiry_finance'
    def __str__(self):
            return str(self.fk_financiers)


class FinanceCustomerDetails(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_schema = models.ForeignKey(FinanceSchema, models.DO_NOTHING, blank=True, null=True)
    fk_enquiry_finance = models.ForeignKey(EnquiryFinance, models.DO_NOTHING, blank=True, null=True)
    vchr_id_type = models.CharField(max_length=30, blank=True, null=True)
    vchr_id_number = models.CharField(max_length=50, blank=True, null=True)
    vchr_pan_number = models.CharField(max_length=30, blank=True, null=True)
    vchr_bank_name = models.CharField(max_length=100, blank=True, null=True)
    bint_account_number = models.BigIntegerField(blank=True, null=True)
    vchr_branch_name = models.CharField(max_length=100, blank=True, null=True)
    vchr_cheque_number = models.CharField(max_length=50, blank=True, null=True)
    vchr_initial_payment_type = models.CharField(max_length=50, blank=True, null=True)
    dbl_down_payment_amount = models.FloatField(blank=True, null=True)
    dbl_processing_fee = models.FloatField(blank=True, null=True)
    dbl_margin_money = models.FloatField(blank=True, null=True)
    dbl_dbd_amount = models.FloatField(blank=True, null=True)
    dbl_service_charge = models.FloatField(blank=True, null=True)
    dbl_net_loan_amount = models.FloatField(blank=True, null=True)


    class Meta:
        managed = False
        db_table = 'finance_customer_details'

    def __str__(self):
            return str(self.fk_enquiry_finance)
