from django.db import models
from department.models import Department
# Create your models here.
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