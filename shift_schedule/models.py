from django.db import models
from django.contrib.postgres.fields import JSONField
from userdetails.models import UserDetails
from django.contrib.auth.models import User

# Create your models here.
class ShiftSchedule(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_name = models.CharField(max_length=50, blank=True, null=True)
    vchr_code = models.CharField(max_length=25, blank=True, null=True)
    bln_night = models.NullBooleanField()
    time_shift_from = models.TimeField(blank=True, null=True)
    time_shift_to = models.TimeField(blank=True, null=True)
    time_break_from = models.TimeField(blank=True, null=True)
    time_break_to = models.TimeField(blank=True, null=True)
    time_break_hrs = models.DurationField(blank=True, null=True)
    time_shed_hrs = models.DurationField(blank=True, null=True)
    time_full_day =  models.DurationField(blank=True, null=True)
    time_half_day =  models.DurationField(blank=True, null=True)
    bln_allowance = models.NullBooleanField()
    dbl_allowance_amt = models.FloatField(blank=True, null=True)
    vchr_remark = models.TextField(blank=True, null=True)
    int_status = models.IntegerField(blank=True, null=True)#1.Active -1 Delete
    fk_created = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,related_name = 'shift_shed_fk_created')
    fk_updated = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,related_name= 'shift_shed_fk_updated')
    dat_created = models.DateTimeField(blank=True, null=True)
    dat_updated = models.DateTimeField(blank=True, null=True)
    bln_time_shift = models.BooleanField(default=False)
    int_shift_type = models.IntegerField(blank=True, null=True, default=0) # 0.Daily, 1.Weekly, 2.Monthly

    class Meta:
        managed = False
        db_table = 'shift_schedule'

    def __str__(self):
        return self.vchr_name

class EmployeeShift(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_employee = models.ForeignKey(UserDetails, models.DO_NOTHING, blank=True, null=True,related_name = 'employee_user')
    int_shift_type = models.IntegerField(blank=True, null=True) #0.Fixed 1.Variable 2.shift excempted
    json_shift = JSONField(blank=True, null=True) #{"lstShift": [id1,id2]}
    bln_active = models.NullBooleanField()
    fk_created = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,related_name = 'employee_fk_created')
    fk_updated = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,related_name = 'employee_fk_updated')
    dat_created = models.DateTimeField(blank=True, null=True)
    dat_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'employee_shift'
    def __str__(self):
        return self.fk_employee


class ShiftExemption(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    dat_start = models.DateField()
    dat_end = models.DateField(blank=True, null=True)
    int_type = models.IntegerField() # 0. Employee, 1. Department, 2. Designation, 3. Branch
    json_type_ids = JSONField() # {'int_type':0(all)/1(individual),'lst_type_ids':['1','2'], 'lst_emp_id':['1','2'],'lst_exclude_ids':['1','2']}
    json_punch_emps = JSONField(blank=True, null=True) # {'int_type':0(all)/1(individual),'lst_type_ids':['1','2'], 'lst_emp_id':['1','2'],'lst_exclude_ids':['1','2']}
    json_exclude = JSONField(blank=True, null=True) # {'int_type':0(date)/1(day), 'lst_type':['2020-07-17','2020-07-17']/['SUNDAY','SATURDAY'], 'lst_day_type':['1'(first)/'2'(second)...]}
    fk_created = models.ForeignKey(User, models.DO_NOTHING, related_name='shift_exemption_fk_created')
    dat_created = models.DateTimeField()
    int_status = models.IntegerField() # -1. Inactive, 1. Active
    class Meta:
        managed = False
        db_table = 'shift_exemption'
