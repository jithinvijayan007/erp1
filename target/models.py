from django.db import models
from userdetails.models import UserDetails as UserAppUsermodel
from brands.models import Brands
# Create your models here.

class Target_Master(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_fin_type = models.CharField(max_length=10)
    int_year = models.IntegerField()
    dbl_target = models.FloatField(blank=True, null=True)
    int_target_type = models.IntegerField()
    fk_created = models.ForeignKey(UserAppUsermodel, models.DO_NOTHING,related_name='fk_created_target')
    dat_created = models.DateTimeField(blank=True, null=True, auto_now = True)
    fk_updated = models.ForeignKey(UserAppUsermodel, models.DO_NOTHING,null =True,related_name='fk_updated_target')
    dat_updated = models.DateTimeField(blank=True, null=True)
    bln_active = models.NullBooleanField()
    bln_all=models.BooleanField()
    fk_user = models.ForeignKey(UserAppUsermodel, models.DO_NOTHING)

    def __str__(self):
        return "{}".format(self.pk_bint_id)

    class Meta:
        managed = False
        db_table = 'target_master'
        ordering = ['pk_bint_id']

class Target_Details(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_master = models.ForeignKey(Target_Master, models.DO_NOTHING)
    fk_brand = models.ForeignKey(Brands, models.DO_NOTHING)
    int_target_type = models.IntegerField()
    int_month = models.IntegerField(blank=True, null=True)
    vchr_month = models.CharField(max_length=15)
    int_year = models.IntegerField()
    dbl_target = models.FloatField(blank=True, null=True)
    fk_user = models.ForeignKey(UserAppUsermodel, models.DO_NOTHING)

    def __str__(self):
        return "{}".format(self.pk_bint_id)

    class Meta:
        managed = False
        db_table = 'target_details'
        ordering = ['pk_bint_id']
