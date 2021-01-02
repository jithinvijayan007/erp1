
from django.db import models
from django.contrib.auth.models import User,AbstractUser
from groups.models import Groups
from company.models import Company
from branch.models import Branch

from brands.models import Brands as Brand
from products.models import Products as Product

from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User
from department.models import Department
from django.contrib.postgres.fields import JSONField
from category.models import Category
from states.models import District
from salary_struct.models import SalaryStructure
from job_position.models import JobPosition
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


# class Userdetails(User,models.Model):
#     bint_phone = models.IntegerField(blank=True, null=True)
#     vchr_pssrsttkn = models.CharField(max_length=30, blank=True, null=True)
#     bint_passrstflg = models.IntegerField(blank=True, null=True)
#     dat_passrsttime = models.DateTimeField(blank=True, null=True)
#     fk_group = models.ForeignKey(Groups, models.DO_NOTHING, blank=True, null=True)
#     fk_company = models.ForeignKey(Company, models.DO_NOTHING, blank=True, null=True)
#     fk_branch = models.ForeignKey(Branch, models.DO_NOTHING, blank=True, null=True)
#     fk_brand = models.ForeignKey(Brands, models.DO_NOTHING, blank=True, null=True)
#     bint_usercode = models.IntegerField(blank=True, null=True)
#     vchr_profpic = models.CharField(max_length=150, blank=True, null=True)
#     dat_resapp = models.DateTimeField(blank=True, null=True)
#     int_areaid = models.IntegerField(blank=True, null=True)
#     dat_created = models.DateTimeField(blank=True, null=True)
#     dat_updated = models.DateTimeField(blank=True, null=True)
#     fk_created = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,related_name='user_fk_created')
#     fk_updated = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,related_name='user_fk_updated')
#     json_product=JSONField(blank=True, null=True)
#     int_guest_user = models.IntegerField(blank=True, null=True,default=0)
#     fk_department = models.ForeignKey(Department, models.DO_NOTHING, blank=True, null=True)



#     class Meta:
#         managed = False
#         db_table = 'userdetails'
class ReligionCaste(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_name = models.CharField(max_length=100, blank=True, null=True)
    bln_active = models.NullBooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'religion_caste'
    def __str__(self):
        return self.vchr_name

class UserDetails(User,models.Model):
    vchr_employee_code = models.CharField(max_length=50, blank=True, null=True)
    fk_category = models.ForeignKey(Category, models.DO_NOTHING, blank=True, null=True)
    bint_phone = models.BigIntegerField(blank=True, null=True)
    vchr_email = models.CharField(max_length=50, blank=True, null=True)
    vchr_middle_name = models.CharField(max_length=150, blank=True, null=True)
    dat_dob = models.DateField(blank=True, null=True)
    dat_doj = models.DateTimeField(blank=True, null=True)
    vchr_gender = models.CharField(max_length=15, blank=True, null=True)
    vchr_level = models.CharField(max_length=50, blank=True, null=True)
    vchr_grade = models.CharField(max_length=50, blank=True, null=True)
    fk_salary_struct = models.ForeignKey(SalaryStructure, models.DO_NOTHING, blank=True, null=True)
    fk_branch = models.ForeignKey(Branch, models.DO_NOTHING, blank=True, null=True)
    fk_department = models.ForeignKey(Department, models.DO_NOTHING, blank=True, null=True)
    fk_company = models.ForeignKey(Company, models.DO_NOTHING, blank=True, null=True)
    int_hierarchy_type = models.IntegerField(blank=True, null=True, default=0) # 0. All, 1. Department consider, 2. Direct reporting, 3. Department consider and Direct reporting
    fk_created = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,related_name = 'user_fk_created')
    fk_updated = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,related_name = 'user_fk_updated')
    dat_created = models.DateTimeField(blank=True, null=True)
    dat_updated = models.DateTimeField(blank=True, null=True)
    json_allowance = JSONField(blank=True, null=True)
    dbl_gross = models.FloatField(blank=True, null=True)
    fk_desig = models.ForeignKey(JobPosition, models.DO_NOTHING, blank=True, null=True)
    int_payment = models.IntegerField(blank=True, null=True)
    vchr_pan_no = models.CharField(max_length=150, blank=True, null=True)
    vchr_aadhar_no = models.CharField(max_length=150, blank=True, null=True)
    vchr_img = models.CharField(max_length=300, blank=True, null=True)
    vchr_bank_name = models.CharField(max_length=300, blank=True, null=True)
    vchr_acc_no = models.CharField(max_length=150, blank=True, null=True)
    vchr_ifsc = models.CharField(max_length=150, blank=True, null=True)
    fk_brand = models.ForeignKey(Brand, models.DO_NOTHING, blank=True, null=True)
    # fk_product = models.ForeignKey(Product, models.DO_NOTHING, blank=True, null=True)
    jsn_function =JSONField(blank=True, null=True)
    vchr_file_no = models.CharField(max_length=150, blank=True, null=True)
    json_physical_loc = JSONField(blank=True, null=True)
    vchr_address = models.TextField(blank=True, null=True)
    int_weekoff_type = models.IntegerField(blank=True, null=True)#0.Fixed 1.Variable
    vchr_weekoff_day = models.CharField(max_length=10, blank=True, null=True) #eg:MONDAY
    json_weekoff = JSONField(blank=True, null=True) # {"SUNDAY":{"0":"0"}, "SATURDAY":{"1":"0", "2":"09:00:00-18:00:00", "3":"0"}}
    dat_resignation = models.DateField(blank=True, null=True)
    txt_resignation_reason = models.TextField(blank=True, null=True)
    vchr_po = models.CharField(max_length=75, blank=True, null=True)
    vchr_land_mark = models.CharField(max_length=150, blank=True, null=True)
    vchr_place = models.CharField(max_length=100, blank=True, null=True)
    fk_dist = models.ForeignKey(District, models.DO_NOTHING, blank=True, null=True)
    int_pincode = models.IntegerField(blank=True, null=True)
    vchr_pf_no = models.CharField(max_length=100, blank=True, null=True)
    vchr_esi_no = models.CharField(max_length=100, blank=True, null=True)
    vchr_uan_no = models.CharField(max_length=100, blank=True, null=True)
    vchr_wwf_no = models.CharField(max_length=100, blank=True, null=True)
    bint_emergency_phno = models.BigIntegerField(blank=True, null=True)
    vchr_father_name = models.CharField(max_length=150, blank=True, null=True)
    vchr_salutation = models.CharField(max_length=10, blank=True, null=True)
    fk_religion = models.ForeignKey('ReligionCaste', models.DO_NOTHING, blank=True, null=True)
    vchr_marital_status = models.CharField(max_length=30, blank=True, null=True)
    vchr_blood_group = models.CharField(max_length=10, blank=True, null=True)
    vchr_emergency_person = models.CharField(max_length=100, blank=True, null=True)
    vchr_emergency_relation = models.CharField(max_length=30, blank=True, null=True)
    bln_pass_reset = models.NullBooleanField(default=False)
    vchr_password_reset_token = models.TextField(blank=True, null=True)
    dat_password_reset_timer = models.DateTimeField(blank=True, null=True)
    int_act_status = models.IntegerField(blank=True, null=True, default=1) # -2. Termination, -1. Inactive, 0. Hold, 1. Active
    fk_wps = models.ForeignKey('WPS', models.DO_NOTHING, blank=True, null=True, related_name = 'user_details_fk_wps')
    vchr_disease = models.CharField(max_length=400, blank=True, null=True)
    vchr_emp_remark = models.TextField(blank=True, null=True)
    int_official_num = models.BigIntegerField(blank=True, null=True)
    json_documents = JSONField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_details'
    def __str__(self):
        return self.username


class GuestUserDetails(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_user = models.ForeignKey(UserDetails, models.DO_NOTHING, blank=True, null=True)
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


###########################################################
#HRMS MODELS
class WPS(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_name = models.TextField(blank=True, null=True)
    dat_created = models.DateTimeField(blank=True, null=True)
    fk_created = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True, related_name = 'wps_fk_created')
    fk_updated = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True, related_name = 'wps_fk_updated')
    bln_active = models.NullBooleanField()
    class Meta:
        managed = False
        db_table = 'wps'


class EmpLeaveData(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_employee = models.ForeignKey(UserDetails, models.DO_NOTHING, blank=True, null=True)
    dbl_number = models.FloatField(blank=True, null=True)
    int_month = models.IntegerField(blank=True, null=True)
    int_year = models.IntegerField(blank=True, null=True)
    int_status = models.IntegerField(blank=True, null=True, default=1)

    class Meta:
        managed = False
        db_table = 'emp_leave_data'
    def __str__(self):
        return self.fk_employee

class AdminSettings(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_code = models.CharField(max_length=50, blank=True, null=True)
    vchr_name = models.CharField(max_length=50, blank=True, null=True)
    vchr_value = models.TextField(blank=True, null=True)  # This field type is a guess.
    int_value = models.IntegerField(blank=True, null=True)
    tim_punch_cool = models.TimeField(blank=True, null=True)
    fk_company = models.ForeignKey('company.Company', models.DO_NOTHING, blank=True, null=True)
    bln_enabled = models.NullBooleanField()

    class Meta:
        managed = False
        db_table = 'admin_settings'
