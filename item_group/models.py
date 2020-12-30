from django.db import models
from django.contrib.auth.models import User

# Create your models here.



class ItemGroup(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_item_group = models.CharField(max_length=30, blank=True, null=True)
    int_status = models.IntegerField(blank=True, null=True,default=0)# 0. Active -1. delete,
    fk_created = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,related_name='group_fk_created')
    fk_updated = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,related_name='group_fk_updated')
    dat_created = models.DateTimeField(blank=True, null=True)
    dat_updated = models.DateTimeField(blank=True, null=True)
    vchr_group_code = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'item_group'
