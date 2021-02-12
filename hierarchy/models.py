from django.db import models
from department.models import Department
# Create your models here.
# from userdetails.models import UserDetails
class Hierarchy(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    int_level = models.SmallIntegerField(blank=True, null=True)
    vchr_name = models.CharField(max_length=100, blank=True, null=True)
    fk_department = models.ForeignKey(Department, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hierarchy'

class HierarchyData(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_name = models.CharField(max_length=100, blank=True, null=True)
    vchr_code = models.CharField(max_length=5, blank=True, null=True)
    fk_hierarchy = models.ForeignKey(Hierarchy, models.DO_NOTHING, blank=True, null=True)
    fk_hierarchy_data = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'hierarchy_data'

class HierarchyGroups(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_hierarchy = models.ForeignKey(Hierarchy, models.DO_NOTHING, blank=True, null=True)
    vchr_name = models.CharField(max_length=50, blank=True, null=True)
    int_status = models.SmallIntegerField(blank=True, null=True) # -1 deleted 1 active

    class Meta:
        managed = False
        db_table = 'hierarchy_groups'

class HierarchyLevel(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_department = models.ForeignKey('department.Department', models.DO_NOTHING)
    fk_designation = models.ForeignKey('job_position.JobPosition', models.DO_NOTHING, blank=True, null=True, related_name = 'fk_designation_id')
    fk_reporting_to = models.ForeignKey('job_position.JobPosition', models.DO_NOTHING, blank=True, null=True, related_name = 'fk_reporting_to_id')
    int_mode = models.IntegerField(blank=True, null=True, default=0) # 0. All, 1. Attendance, 2. Others
    dat_created = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    dat_updated = models.DateTimeField(blank=True, null=True, auto_now=True)
    fk_created = models.ForeignKey('userdetails.UserDetails', models.DO_NOTHING, blank=True, null=True, related_name = 'fk_hierarchy_created_id')
    fk_updated = models.ForeignKey('userdetails.UserDetails', models.DO_NOTHING, blank=True, null=True, related_name = 'fk_hierarchy_updated_id')
    int_status = models.IntegerField(blank=True, null=True, default=1)

    class Meta:
        managed = False
        db_table = 'hierarchy_level'
    def __str__(self):
        return self.fk_department.vchr_name