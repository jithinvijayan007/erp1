from django.db import models
from company.models import Company as CompanyDetails
from branch.models import Branch
# Create your models here.
class ExpensesCategory(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_category_name = models.CharField(max_length=50)

    def __str__(self):
        return str(self.vchr_category_name)

    class Meta:
        managed = False
        db_table = 'expenses_category'

class Expenses(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_name = models.CharField(max_length=50)
    fk_company = models.ForeignKey(CompanyDetails, models.DO_NOTHING, blank=True, null=True)
    bln_recurring = models.NullBooleanField()
    bln_status = models.BooleanField()
    fk_category = models.ForeignKey(ExpensesCategory, models.DO_NOTHING, blank=True, null=True)
    dat_expiry = models.DateField(blank=True, null=True)
    dbl_amount = models.FloatField(blank=True, null=True)
    fk_branch = models.ForeignKey(Branch, models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return str(self.vchr_name)

    class Meta:
        managed = False
        db_table = 'expenses'

class Payments(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_doc_num = models.CharField(max_length=100, blank=True, null=True)
    vchr_expenses = models.CharField(max_length=1000, blank=True, null=True)
    dbl_amount = models.FloatField(blank=True, null=True)
    dat_payment = models.DateTimeField(blank=True, null=True)
    fk_branch = models.ForeignKey(Branch, models.DO_NOTHING, blank=True, null=True)
    dat_created = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payments'
