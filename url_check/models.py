from django.db import models
from django.contrib.auth.models import User
from company.models import Company as CompanyDetails
from userdetails.models import Company as UserDetails
from company_permissions.models import SubCategory

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


class UserDownloadLog(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_user = models.ForeignKey(UserDetails, models.DO_NOTHING)
    fk_sub_category = models.ForeignKey(SubCategory, models.DO_NOTHING, blank=True, null=True)
    dat_download = models.DateTimeField()
    vchr_dat_filter = models.TextField(blank=True, null=True)
    vchr_filter = models.TextField(blank=True, null=True)
    vchr_chart = models.TextField(blank=True, null=True)
    fk_company = models.ForeignKey(CompanyDetails, models.DO_NOTHING,related_name = 'urlcheck_downloadlog_company')

    class Meta:
        managed = False
        db_table = 'user_download_log'