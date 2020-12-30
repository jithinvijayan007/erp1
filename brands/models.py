from django.db import models

# Create your models here.
class Brands(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_code = models.CharField(max_length=50, blank=True, null=True)
    vchr_name = models.CharField(max_length=150, blank=True, null=True)
    int_status = models.IntegerField(default=1,blank=True, null=True) # 0. Active -1. delete,

    class Meta:
        managed = False
        db_table = 'brands'
