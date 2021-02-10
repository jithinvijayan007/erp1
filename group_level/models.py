from django.db import models
from groups.models import Groups

# Create your models here.
class GroupLevel(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    int_level = models.IntegerField(blank=True, null=True)
    fk_group = models.ForeignKey(Groups, models.DO_NOTHING)
    vchr_filter = models.CharField(max_length=100, blank=True, null=True)

    class Meta:

        managed = False
        db_table = 'group_level'
