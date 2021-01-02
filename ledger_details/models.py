from django.db import models
from company.models import FinancialYear
from userdetails.models import UserDetails as Userdetails
# Create your models here.
class OpeningBalance(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_acc_no = models.CharField(max_length=20, blank=True, null=True)
    fk_financial = models.ForeignKey(FinancialYear, models.DO_NOTHING, blank=True, null=True)
    vchr_acc_name = models.CharField(max_length=300, blank=True, null=True)
    dbl_debit_amount = models.FloatField(blank=True, null=True)
    dbl_credit_amount = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'opening_balance'


class ImportFiles(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_file_name = models.CharField(max_length=50, blank=True, null=True)
    fk_uploaded_by = models.ForeignKey(Userdetails, models.DO_NOTHING, blank=True, null=True)
    dat_uploaded = models.DateField(blank=True, null=True)    
    int_type = models.BigIntegerField(blank=True, null=True)

    '''
        int_type denotes:

        1 - coupon
                    '''

    class Meta:
        managed = False
        db_table = 'import_files'
