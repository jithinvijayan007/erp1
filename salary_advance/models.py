from django.db import models
from userdetails.models import UserDetails
# Create your models here.


class SalaryAdvance(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_employee = models.ForeignKey(UserDetails, models.DO_NOTHING, blank=True, null=True, related_name="fk_user")
    dbl_amount = models.FloatField(blank=True, null=True)
    vchr_purpose = models.CharField(max_length=200, blank=True, null=True)
    int_month = models.IntegerField(blank=True, null=True)
    int_year = models.IntegerField(blank=True, null=True)
    int_status = models.IntegerField(blank=True, null=True)#-1.rejected, 0.excluded, 1.request, 2.approved, 3.Processed
    bln_active = models.NullBooleanField()
    fk_approved = models.ForeignKey(UserDetails, models.DO_NOTHING, blank=True, null=True, related_name="fk_approved")
    dat_created = models.DateTimeField(blank=True, null=True)
    dat_updated = models.DateTimeField(blank=True, null=True)
    dat_approval = models.DateTimeField(blank=True, null=True)
    vchr_remarks = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'salary_advance'
    def __str__(self):
        return self.fk_employee
