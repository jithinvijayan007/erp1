from django.db import models
from django.contrib.postgres.fields import JSONField

# Create your models here.

class GeneralizeReport(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_report_name = models.CharField(max_length=50)
    vchr_query = models.TextField()
    json_data = JSONField()  # This field type is a guess.
    vchr_url_name = models.CharField(max_length=50, blank=True, null=True)
    json_filter = JSONField()  # This field type is a guess
    json_value = JSONField()  # This field type is a guess.
    def __str__(self):
        return self.vchr_url_name
    class Meta:
        managed = False
        db_table = 'generalize_report'
