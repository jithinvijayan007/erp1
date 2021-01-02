from django.db import models

# Create your models here.


class PtPeriod(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_period_name = models.CharField(max_length=150, blank=True, null=True)
    int_month_from = models.IntegerField(blank=True, null=True)
    int_month_to = models.IntegerField(blank=True, null=True)
    int_deduct_month = models.IntegerField(blank=True, null=True)
    bln_active = models.NullBooleanField()

    class Meta:
        managed = False
        db_table = 'pt_period'

    def __str__(self):
        return self.vchr_period_name


class ProfessionalTax(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    dbl_from_amt = models.FloatField(blank=True, null=True)
    dbl_to_amt = models.FloatField(blank=True, null=True)
    fk_period = models.ForeignKey(PtPeriod, models.DO_NOTHING, blank=True, null=True)
    dbl_tax = models.FloatField(blank=True, null=True)
    bln_active = models.NullBooleanField()

    class Meta:
        managed = False
        db_table = 'professional_tax'

    def __str__(self):
        return self.fk_period
