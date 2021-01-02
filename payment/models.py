from django.db import models
from branch.models import Branch
from userdetails.models import UserDetails as Userdetails
from invoice.models import Bank
from django.contrib.postgres.fields import JSONField
from accounts_map.models import AccountsMap

# Create your models here.
#class PaymentDocumentManager(models.Manager):
 #   def create_payment_doc(self, str_new_doc_no):
  #       payment = self.create(vchr_doc_num=vchr_doc_num)
   #      return payment

class Payment(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_doc_num = models.CharField(max_length=50, blank=True, null=True)
    dat_payment = models.DateTimeField(blank=True, null=True)
    int_fop = models.IntegerField(blank=True, null=True)#1.cash 2.bank
    int_payee_type = models.IntegerField(blank=True, null=True)#1.Adv. Refund 2.staff 3.expenses 4.contra 5.customer 6. Ventor
    fk_payee_id = models.IntegerField(blank=True, null=True)#if int_payee_type 1.customer_id 2.staff_id 3.expenses_id

    fk_branch = models.ForeignKey(Branch, models.DO_NOTHING, blank=True, null=True)
    dbl_amount = models.FloatField(blank=True, null=True)
    vchr_remarks = models.TextField(blank=True, null=True)
    fk_created = models.ForeignKey(Userdetails, models.DO_NOTHING, blank=True, null=True,related_name='payment_fk_created')
    fk_updated = models.ForeignKey(Userdetails, models.DO_NOTHING, blank=True, null=True,related_name='payment_fk_updated')
    fk_approved_by = models.ForeignKey(Userdetails, models.DO_NOTHING, blank=True, null=True,related_name='payment_fk_approved_by')
    int_doc_status = models.IntegerField(blank=True, null=True)
    dat_created = models.DateTimeField(blank=True, null=True)
    dat_updated = models.DateTimeField(blank=True, null=True)
    int_approved = models.IntegerField(blank=True, null=True)
    fk_bank = models.ForeignKey(Bank, models.DO_NOTHING, blank=True, null=True)
    fk_accounts_map = models.ForeignKey(AccountsMap, models.DO_NOTHING, blank=True, null=True)
    # objects = PaymentDocumentManager()

    class Meta:
        managed = False
        db_table = 'payment'

class ContraDetails(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    json_denomination = JSONField(blank=True, null=True)  # This field type is a guess.
    fk_payment = models.ForeignKey(Payment, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False

        db_table = 'contra_details'


class SapPayment(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_code = models.CharField(max_length=50, blank=True, null=True)
    vchr_description = models.CharField(max_length=150, blank=True, null=True)
    dbl_amount = models.FloatField(blank=True, null=True)
    int_tran_id = models.IntegerField(blank=True, null=True)
    int_type = models.IntegerField(blank=True, null=True)
    doc_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sap_payment'
