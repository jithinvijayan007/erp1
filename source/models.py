from django.db import models
from company.models import Company as CompanyDetails
from expenses.models import ExpensesCategory

# Create your models here.
class Source(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_source_name = models.CharField(max_length=15, blank=True, null=True)
    bln_status = models.NullBooleanField()
    bln_is_campaign = models.NullBooleanField()
    fk_company = models.ForeignKey(CompanyDetails, models.DO_NOTHING, blank=True, null=True)
    fk_category = models.ForeignKey(ExpensesCategory, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'source'

    def __str__(self):
            return str(self.vchr_source_name)
