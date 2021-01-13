from django.db import models
from userdetails.models import UserDetails
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
# from userdetails.models import UserDetails

# Create your models here.

class SalaryDetails(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_employee = models.ForeignKey(UserDetails, models.DO_NOTHING, blank=True, null=True,related_name="salary_detials_employee")
    dbl_bp = models.FloatField(blank=True, null=True)
    dbl_da = models.FloatField(blank=True, null=True)
    dbl_hra = models.FloatField(blank=True, null=True)
    dbl_cca = models.FloatField(blank=True, null=True)
    dbl_sa = models.FloatField(blank=True, null=True)
    dbl_wa = models.FloatField(blank=True, null=True)
    dbl_gross = models.FloatField(blank=True, null=True)
    json_deduction = JSONField(blank=True, null=True)#{'ESI': 4.0, 'WWF': 20, 'SalaryAdvance': 0, 'PF': 59.0}
    json_allowance = JSONField(blank=True, null=True)#{'ESI': 19.0, 'Gratuity': 20.0, 'WWF': 20, 'PF': 59.0}
    fk_created = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True, related_name = 'salary_detailss_fk_created')
    dat_created = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    fk_updated = models.ForeignKey(UserDetails, models.DO_NOTHING, blank=True, null=True,related_name = 'salary_details_fk_updated')
    dat_updated = models.DateTimeField(blank=True, null=True)
    int_status = models.IntegerField(blank=True, null=True)# -1. Deactive, 0. Hold, 1.Active

    class Meta:
        managed = False
        db_table = 'salary_details'
    def __str__(self):
        return self.fk_employee


class VariablePay(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_employee = models.ForeignKey(UserDetails, models.DO_NOTHING, blank=True, null=True)
    dbl_amount = models.FloatField(blank=True, null=True)
    int_month = models.IntegerField(blank=True, null=True)
    int_year = models.IntegerField(blank=True, null=True)
    dat_stoped = models.DateTimeField(blank=True, null=True)
    int_status = models.IntegerField(blank=True, null=True, default=1) #0-Deleted,1-New,2-Stopped
    txt_remarks = models.TextField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'variable_pay'
    def __str__(self):
        return self.fk_employee


class SalaryProcessed(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_employee = models.ForeignKey(UserDetails, models.DO_NOTHING, blank=True, null=True, related_name = 'salary_process_fk_employee')
    fk_details = models.ForeignKey(SalaryDetails, models.DO_NOTHING, blank=True, null=True)
    int_month = models.IntegerField(blank=True, null=True)
    int_year = models.IntegerField(blank=True, null=True)
    json_attendance = JSONField(blank=True, null=True)
    dbl_bp = models.FloatField(blank=True, null=True)
    dbl_da = models.FloatField(blank=True, null=True)
    dbl_hra = models.FloatField(blank=True, null=True)
    dbl_cca = models.FloatField(blank=True, null=True)
    dbl_wa = models.FloatField(blank=True, null=True)
    dbl_sa = models.FloatField(blank=True, null=True)
    dbl_gross = models.FloatField(blank=True, null=True)
    json_allowances = JSONField(blank=True, null=True)
    json_deductions = JSONField(blank=True, null=True)
    dbl_net_salary = models.FloatField(blank=True, null=True)
    dbl_monthly_ctc = models.FloatField(blank=True, null=True)
    dat_created = models.DateTimeField(blank=True, null=True)
    fk_created = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True, related_name = 'salary_processed_fk_created')
    dat_approval = models.DateTimeField(blank=True, null=True)
    fk_approved = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True, related_name = 'salary_processed_fk_approved')
    int_status = models.IntegerField(blank=True, null=True) # 0:prepared, 1:approved, -1:Rejected
    vchr_remarks = models.CharField(max_length=200, blank=True, null=True) # Remarks on hold
    fk_hold = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True)
    dat_hold = models.DateTimeField(blank=True, null=True)
    bln_hold = models.NullBooleanField()

    class Meta:
        managed = False
        db_table = 'salary_processed'
    def __str__(self):
        return self.fk_employee

class FixedAllowance(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_employee = models.ForeignKey(UserDetails, models.DO_NOTHING, blank=True, null=True)
    dbl_amount = models.FloatField(blank=True, null=True)
    int_month = models.IntegerField(blank=True, null=True)
    int_year = models.IntegerField(blank=True, null=True)
    dat_stoped = models.DateTimeField(blank=True, null=True)
    int_status = models.IntegerField(blank=True, null=True, default=1) #0-Deleted,1-New,2-Stopped
    txt_remarks = models.TextField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'fixed_allowance'
    def __str__(self):
        return self.fk_employee


