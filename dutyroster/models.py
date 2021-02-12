from django.db import models
from userdetails.models import UserDetails
from django.contrib.auth.models import User as AuthUser
from django.contrib.postgres.fields import JSONField


class DutyRoster(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_employee = models.ForeignKey(UserDetails, models.DO_NOTHING, blank=True, null=True)
    json_dates = JSONField(blank=True, null=True)#[]
    int_month = models.IntegerField(blank=True, null=True)
    int_year = models.IntegerField(blank=True, null=True)
    bln_active = models.NullBooleanField()
    fk_created = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True,related_name = 'duty_roaster_fk_created' )
    fk_updated = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True,related_name = 'duty_roaster_fk_updated')
    dat_created = models.DateTimeField(blank=True, null=True)
    dat_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'duty_roster'
    def __str__(self):
        return self.fk_employee.username


class WeekoffLeave(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_employee = models.ForeignKey(UserDetails, models.DO_NOTHING)
    dat_from = models.DateField()
    dat_to = models.DateField()
    dat_created = models.DateTimeField(auto_now_add=True)
    int_status = models.IntegerField(blank=True, null=True, default=0) # -1. Rejected, 0. Cancelled, 1. Applied, 2. Approved, 3. Verified
    fk_approved = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True, related_name = 'weekoff_leave_fk_approved')
    dat_approve = models.DateTimeField(blank=True, null=True)
    fk_verified = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True, related_name = 'weekoff_leave_fk_verified')
    dat_verified = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'weekoff_leave'

    def __str__(self):
        return self.fk_employee.username
