from django.db import models
from states.models import Location
from company.models import Company


class Zone(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_code = models.CharField(max_length=50, blank=True, null=True)
    vchr_name = models.CharField(max_length=150, blank=True, null=True)
    bln_active = models.NullBooleanField()
    fk_state = models.ForeignKey(Location, models.DO_NOTHING, blank=True, null=True)
    fk_company = models.ForeignKey(Company, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'zone'
    def __str__(self):
        return self.vchr_name
