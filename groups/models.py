from django.db import models
from django.contrib.auth.models import User as AuthUser
from company.models import Company
from department.models import Department


# Create your models here.
class Groups(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_code = models.CharField(max_length=50, blank=True, null=True)
    vchr_name = models.CharField(max_length=150, blank=True, null=True)
    int_status = models.IntegerField(blank=True, null=True)
    fk_created = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True,related_name='fk_created_group_model')
    dat_created = models.DateTimeField(blank=True, null=True)
    fk_updated = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True,related_name='fk_updated_group_model')
    fk_company = models.ForeignKey(Company, models.DO_NOTHING, blank=True, null=True)
    dbl_experience = models.FloatField(blank=True, null=True)
    json_qualification = models.TextField(blank=True, null=True)  # This field type is a guess.
    vchr_age_limit = models.CharField(max_length=50, blank=True, null=True)
    txt_desc = models.TextField(blank=True, null=True)
    int_notice_period = models.IntegerField(blank=True, null=True)
    json_desc = models.TextField(blank=True, null=True)  # This field type is a guess.
    bln_admin = models.NullBooleanField()
    int_permission = models.IntegerField(blank=True, null=True)
    bln_brand = models.NullBooleanField()
    fk_department = models.ForeignKey(Department, models.DO_NOTHING, blank=True, null=True)
    int_area_type = models.IntegerField(blank=True, null=True)
    json_area_id = models.TextField(blank=True, null=True)  # This field type is a guess.
    bln_active = models.NullBooleanField()

    class Meta:
        managed = False
        db_table = 'groups'
