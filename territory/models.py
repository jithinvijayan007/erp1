from django.db import models
from zone.models import Zone
from company.models import Company
# Create your models here.


class Territory(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_zone = models.ForeignKey(Zone, models.DO_NOTHING, blank=True, null=True)
    vchr_code = models.CharField(max_length=50, blank=True, null=True)
    vchr_name = models.CharField(max_length=150, blank=True, null=True)
    bln_active = models.NullBooleanField()
    fk_company = models.ForeignKey(Company, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'territory'
    def __str__(self):
        return self.vchr_name
