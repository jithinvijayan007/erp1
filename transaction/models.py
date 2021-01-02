from django.db import models
from userdetails.models import UserDetails as Userdetails
from branch.models import Branch
from company.models import FinancialYear

# Create your models here.
class Transaction(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    dat_created = models.DateTimeField(blank=True, null=True)
    int_accounts_id = models.IntegerField(blank=True, null=True)
    int_account_type = models.IntegerField(blank=True, null=True) #* 1: Customer, 2: Staff, 3: Bank , 5: Ventor
    dbl_debit = models.FloatField()
    dbl_credit = models.FloatField()
    int_document_id = models.IntegerField(blank=True, null=True)
    int_document_type = models.IntegerField(blank=True, null=True)  # 1: receipt, 2: Payment, 3: Invoice 4 Journal
    fk_created = models.ForeignKey(Userdetails, models.DO_NOTHING, blank=True, null=True, related_name='fk_created_user')
    vchr_status = models.CharField(max_length=20, blank=True, null=True)#*
    fk_updated = models.ForeignKey(Userdetails, models.DO_NOTHING,  blank=True, null=True, related_name='fk_updated_user')
    dat_updated = models.DateTimeField(blank=True, null=True)
    fk_financialyear = models.ForeignKey(FinancialYear, models.DO_NOTHING, blank=True, null=True)
    int_type = models.IntegerField(blank=True, null=True)#*
    int_lock = models.IntegerField(blank=True, null=True)
    fk_branch = models.ForeignKey(Branch, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transaction'


class Journal(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_jv_num = models.CharField(max_length=100, blank=True, null=True)
    fk_debit_branch = models.ForeignKey(Branch, models.DO_NOTHING, blank=True, null=True,related_name='branchdebit')
    fk_credit_branch = models.ForeignKey(Branch, models.DO_NOTHING, blank=True, null=True,related_name='branchcredit')
    dat_journal = models.DateField(blank=True, null=True)
    int_debit_type = models.IntegerField(blank=True, null=True)# 1 - customer 2 - staff 3 - expenses 4- vendor 5 - cash 6- bank
    fk_debit_id = models.IntegerField(blank=True, null=True)
    int_credit_type = models.IntegerField(blank=True, null=True)# 1 - customer 2 - staff 3 - expenses 4- vendor 5 - cash 6- bank
    fk_credit_id = models.IntegerField(blank=True, null=True)
    dbl_amount = models.FloatField(blank=True, null=True)
    vchr_remarks = models.CharField(max_length=500, blank=True, null=True)
    dat_created = models.DateTimeField(blank=True, null=True)
    fk_created = models.ForeignKey(Userdetails, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'journal'
