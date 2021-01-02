from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class SessionHandler(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_user = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,related_name ='sessionhandler')
    vchr_session_key = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'session_handler'
    def __str__(self):
        return self.fk_user
