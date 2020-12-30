
from django.db import models
from django.contrib.auth.models import User,AbstractUser
from groups.models import Groups
from company.models import Company
from branch.models import Branch
from brands.models import Brands
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User
from department.models import Department
from django.contrib.postgres.fields import JSONField


class Financiers(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_name = models.CharField(max_length=50)
    bln_active = models.BooleanField()
    vchr_code = models.CharField(max_length=10, blank=True, null=True)
    def __str__(self):
            return str(self.vchr_name)

    class Meta:
        managed = False

        db_table = 'financiers'


class Userdetails(User,models.Model):
    bint_phone = models.IntegerField(blank=True, null=True)
    vchr_pssrsttkn = models.CharField(max_length=30, blank=True, null=True)
    bint_passrstflg = models.IntegerField(blank=True, null=True)
    dat_passrsttime = models.DateTimeField(blank=True, null=True)
    fk_group = models.ForeignKey(Groups, models.DO_NOTHING, blank=True, null=True)
    fk_company = models.ForeignKey(Company, models.DO_NOTHING, blank=True, null=True)
    fk_branch = models.ForeignKey(Branch, models.DO_NOTHING, blank=True, null=True)
    fk_brand = models.ForeignKey(Brands, models.DO_NOTHING, blank=True, null=True)
    bint_usercode = models.IntegerField(blank=True, null=True)
    vchr_profpic = models.CharField(max_length=150, blank=True, null=True)
    dat_resapp = models.DateTimeField(blank=True, null=True)
    int_areaid = models.IntegerField(blank=True, null=True)
    dat_created = models.DateTimeField(blank=True, null=True)
    dat_updated = models.DateTimeField(blank=True, null=True)
    fk_created = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,related_name='user_fk_created')
    fk_updated = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,related_name='user_fk_updated')
    json_product=JSONField(blank=True, null=True)
    int_guest_user = models.IntegerField(blank=True, null=True,default=0)
    fk_department = models.ForeignKey(Department, models.DO_NOTHING, blank=True, null=True)



    class Meta:
        managed = False
        db_table = 'userdetails'

class GuestUserDetails(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_user = models.ForeignKey(Userdetails, models.DO_NOTHING, blank=True, null=True)
    session_expiry_time = models.DateTimeField(blank=True, null=True)
    fk_group = models.ForeignKey(Groups, models.DO_NOTHING, blank=True, null=True)
    fk_company = models.ForeignKey(Company, models.DO_NOTHING, blank=True, null=True)
    fk_branch = models.ForeignKey(Branch, models.DO_NOTHING, blank=True, null=True)
    dat_created = models.DateTimeField(blank=True, null=True)
    dat_updated = models.DateTimeField(blank=True, null=True)
    fk_created = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,related_name='created_by')
    fk_updated = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,related_name='updated_by')

    class Meta:
        managed = False
        db_table = 'guest_user_details'

class BackendUrls(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_backend_url = models.CharField(max_length=100, blank=True, null=True)
    vchr_module_name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.vchr_module_name
    class Meta:
        managed = False
        db_table = 'backend_urls'


class UserLogDetails(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_user = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True)
    fk_module = models.ForeignKey(BackendUrls, models.DO_NOTHING, blank=True, null=True)
    int_count = models.IntegerField(blank=True, null=True)
    json_ip = models.TextField(blank=True, null=True)  # This field type is a guess.
    dat_start_active = models.DateTimeField(blank=True, null=True)
    dat_last_active = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.fk_module.vchr_module_name +' / MODULE with count - '+ str(self.int_count) +' / USER - '+self.fk_user.username.title()
    class Meta:
        managed = False
        db_table = 'user_log_details'


class UserPermissions(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_user = models.ForeignKey(User, models.DO_NOTHING)
    jsn_branch = JSONField(blank=True, null=True)
    jsn_product = JSONField(blank=True, null=True)
    jsn_item_group = JSONField(blank=True, null=True)
    dat_created = models.DateTimeField(auto_now=True)
    bln_active = models.BooleanField(default=True)
    json_price_perm = JSONField(blank=True, null=True) #'{'bln_mop':false,'bln_mrp':mrp,'bln_dp':false,'bln_cost_price':false}'
    jsn_branch_type = JSONField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'user_permissions'
    def __str__(self):
        return self.fk_user.username
