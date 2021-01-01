from django.db import models
from department.models import Department
from company.models import Company
from django.contrib.postgres.fields import JSONField


class JobPosition(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_name = models.CharField(max_length=150, blank=True, null=True)
    fk_department = models.ForeignKey(Department, models.DO_NOTHING, blank=True, null=True)
    int_area_type = models.IntegerField(blank=True, null=True)#0.State 1.Territory 2.Zone
    json_area_id = JSONField(blank=True, null=True)#[id1,id2]
    fk_company = models.ForeignKey(Company, models.DO_NOTHING, blank=True, null=True)
    dbl_experience = models.FloatField(blank=True, null=True)
    json_qualification = JSONField(blank=True, null=True)#['xyz','asd']
    vchr_age_limit = models.CharField(max_length=50, blank=True, null=True)
    txt_desc = models.TextField(blank=True, null=True)
    int_notice_period = models.IntegerField(blank=True, null=True)
    json_desc = JSONField(blank=True, null=True)
    bln_brand = models.NullBooleanField(default=False)
    bln_admin = models.NullBooleanField()
    int_permission = models.IntegerField(blank=True, null=True) # 1. All permissions
    bln_active = models.NullBooleanField()


    class Meta:
        managed = False
        db_table = 'job_position'
    def __str__(self):
        return self.vchr_name


class JobQuesTypehead(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_desig = models.ForeignKey(JobPosition, models.DO_NOTHING, blank=True, null=True)
    vchr_name = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'job_ques_typehead'
