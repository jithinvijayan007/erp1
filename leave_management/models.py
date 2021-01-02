from django.db import models
from userdetails.models import UserDetails
# Create your models here.


class LeaveType(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_name = models.CharField(max_length=100)
    dbl_leaves_per_month = models.FloatField(blank=True, null=True)
    dbl_leaves_per_year = models.FloatField(blank=True, null=True)
    int_year = models.IntegerField()
    vchr_remarks = models.CharField(max_length=300, blank=True, null=True)
    fk_desig = models.ForeignKey('job_position.JobPosition', models.DO_NOTHING, blank=True, null=True)
    fk_company = models.ForeignKey('company.Company', models.DO_NOTHING, blank=True, null=True)
    bln_active = models.BooleanField(default=True)
    bln_exclude_count = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'leave_type'
    def __str__(self):
        return self.vchr_name


class Leave(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    dat_from = models.DateTimeField(blank=True, null=True)
    dat_to = models.DateTimeField(blank=True, null=True)
    dbl_days = models.FloatField(blank=True, null=True)
    chr_leave_mode = models.CharField(max_length=2)
    vchr_reason = models.TextField()
    int_status = models.IntegerField() # 1. Pending, 2. Approved, 3. Rejected, 4. Cancelled
    dat_approved = models.DateTimeField(blank=True, null=True)
    dat_applied = models.DateTimeField()
    fk_approved = models.ForeignKey(UserDetails, models.DO_NOTHING, blank=True, null=True,related_name ='fk_leave_approved')
    fk_leave_type = models.ForeignKey('LeaveType', models.DO_NOTHING, blank=True, null=True)
    fk_user = models.ForeignKey(UserDetails, models.DO_NOTHING, blank=True, null=True,related_name ='fk_leave_employee')
    vchr_approve = models.TextField(blank=True, null=True)
    vchr_reject = models.TextField(blank=True, null=True)
    vchr_file = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'leave'
    def __str__(self):
        return self.fk_user


class Carryforward(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    int_year = models.IntegerField(blank=True, null=True)
    dbl_opening = models.FloatField(blank=True, null=True)
    fk_leave_type = models.ForeignKey('LeaveType', models.DO_NOTHING, blank=True, null=True)
    fk_user = models.ForeignKey(UserDetails, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'carryforward'
    def __str__(self):
        return self.fk_user


class SetLeave(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_leave_type = models.ForeignKey('LeaveType', models.DO_NOTHING, blank=True, null=True)
    fk_user = models.ForeignKey(UserDetails, models.DO_NOTHING, blank=True, null=True)
    dat_expiry = models.DateField(blank=True, null=True)
    int_status = models.IntegerField(blank=True, null=True) #0:assigned,1:applied,2:deleted
    vchr_remarks = models.TextField(blank=True, null=True)
    dat_created = models.DateTimeField(blank=True, null=True)
    fk_created = models.ForeignKey(UserDetails, models.DO_NOTHING, blank=True, null=True,related_name='createduser_by')
    class Meta:
        managed = False

        db_table = 'set_leave'
