from django.db import models
from company.models import Company as CompanyDetails

# Create your models here.
class Priority(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_priority_name = models.CharField(max_length=15, blank=True, null=True)
    bln_status = models.NullBooleanField()
    fk_company = models.ForeignKey(CompanyDetails, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'priority'

    def __str__(self):
            return str(self.vchr_priority_name)
