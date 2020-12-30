from django.db import models
from django.contrib.auth.models import User as AuthUser
from company.models import Company


# Create your models here.
class Groups(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_code = models.CharField(max_length=50, blank=True, null=True)
    vchr_name = models.CharField(max_length=150, blank=True, null=True)
    int_status = models.IntegerField(blank=True, null=True)# 0. Active -1. delete,
    fk_created = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True,related_name='userGroups_fk_created')
    dat_created = models.DateTimeField(blank=True, null=True)
    fk_updated = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True,related_name='userGroups_fk_updated')
    fk_company = models.ForeignKey(Company, models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return self.vchr_name 

    class Meta:
        managed = False
        db_table = 'groups'
