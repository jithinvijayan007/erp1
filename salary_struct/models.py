from django.db import models
from django.contrib.postgres.fields import JSONField
# Create your models here.


class SalaryStructure(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_name = models.CharField(max_length=50, blank=True, null=True)
    dbl_bp_da = models.FloatField(blank=True, null=True)
    dbl_da = models.FloatField(blank=True, null=True)
    json_rules =  JSONField(blank=True, null=True)  # This field type is a guess.
    bln_active = models.NullBooleanField()
    dbl_bp_da_per = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'salary_structure'

    def __str__(self):
        return self.vchr_name



class PfandEsiStructure(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    int_start_month = models.IntegerField(blank=True, null=True)
    int_start_year = models.IntegerField(blank=True, null=True)
    int_end_month = models.IntegerField(blank=True, null=True)
    int_end_year = models.IntegerField(blank=True, null=True)
    vchr_type = models.CharField(max_length=150, blank=True, null=True)
    dbl_empy_share = models.FloatField(blank=True, null=True)
    dbl_empr_share = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pfandesi_structure'
