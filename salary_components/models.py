from django.db import models

class SalaryComponents(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_name = models.CharField(max_length=50, blank=True, null=True)
    vchr_code = models.CharField(max_length=5, blank=True, null=True)
    vchr_remarks = models.CharField(max_length=350, blank=True, null=True)
    bln_exclude = models.NullBooleanField()
    int_order = models.IntegerField(blank=True, null=True)
    bln_active = models.NullBooleanField()
    int_type = models.IntegerField(blank=True, null=True)#0.Allowances 1.Deductions
    bln_fixed_allowance = models.NullBooleanField()

    class Meta:
        managed = False
        db_table = 'salary_components'
    def __str__(self):
        return self.vchr_name
