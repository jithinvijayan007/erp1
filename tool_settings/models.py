from django.contrib.postgres.fields import JSONField
from django.db import models


class Tools(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_tool_name = models.CharField(max_length=40, blank=True, null=True)
    vchr_tool_code = models.CharField(max_length=40, blank=True, null=True)
    jsn_data = JSONField(blank=True, null=True)  # This field type is a guess.
    int_status = models.IntegerField(blank=True, null=True)
    dat_from = models.DateTimeField(blank=True, null=True)
    dat_to = models.DateTimeField(blank=True, null=True)
    jsn_keys = JSONField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'tools'
