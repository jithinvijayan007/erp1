from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField

class Type(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_name = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'type'

class Terms(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    jsn_terms = JSONField(blank=True, null=True) #{"1":"","2":,"3":""}
    fk_type = models.ForeignKey(Type, models.DO_NOTHING, blank=True, null=True)
    int_status = models.IntegerField(blank=True, null=True) # 0.active,1.editted,2.deactive,-1.delete
    fk_created = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,related_name="terms_fk_created")
    dat_created = models.DateTimeField(blank=True, null=True)
    fk_updated = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,related_name="terms_fk_updated")
    dat_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'terms'
