from django.db import models
from userdetails.models import UserDetails as AuthUser
# from reminder

# Create your models here.
class Reminder(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    dat_created_at = models.DateTimeField(blank=True, null=True)
    dat_updated_at = models.DateTimeField(blank=True, null=True)
    vchr_title = models.CharField(max_length=50)
    vchr_description = models.CharField(max_length=200)
    dat_reminder = models.DateTimeField()

    def __str__(self):
            return str(self.vchr_title)

    class Meta:
        managed = False
        db_table = 'reminder'
