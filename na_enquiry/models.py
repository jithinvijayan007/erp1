from django.db import models
from userdetails.models import UserDetails as UserAppUsermodel
from customer.models import CustomerDetails as CustomerAppCustomermodel
from company.models import Company as CompanyDetails
from location.models import Country as Countries
# from airport.models import Airport
# from station.models import Station
from source.models import Source
from branch.models import Branch
from priority.models import Priority
from django.contrib.postgres.fields import JSONField,ArrayField
from django.contrib.postgres.fields import JSONField
# Create your models here.

class NaEnquiryMasterDocumentManager(models.Manager):
    def create_enquiry_num(self, str_new_doc_no):
         enquiry_num = self.create(vchr_enquiry_num=str_new_doc_no)
         return enquiry_num

class NaEnquiryMaster(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_enquiry_num = models.CharField(max_length=50)
    fk_customer = models.ForeignKey(CustomerAppCustomermodel, models.DO_NOTHING)
    vchr_customer_type = models.CharField(max_length=50)
    fk_assigned = models.ForeignKey(UserAppUsermodel, models.DO_NOTHING, blank=True, null=True,related_name = 'na_enquiry_master_assigned_by')
    fk_created_by = models.ForeignKey(UserAppUsermodel, models.DO_NOTHING, related_name = 'na_enquiry_master_created_by')
    fk_updated_by = models.ForeignKey(UserAppUsermodel, models.DO_NOTHING, blank=True, null=True,related_name = 'na_enquiry_master_updated_by')
    dat_created_at = models.DateTimeField(blank=True, null=True)
    dat_updated_at = models.DateTimeField(blank=True, null=True)
    fk_company = models.ForeignKey(CompanyDetails, models.DO_NOTHING)
    fk_branch = models.ForeignKey(Branch, models.DO_NOTHING)
    fk_source = models.ForeignKey(Source, models.DO_NOTHING)
    vchr_remarks = models.TextField(blank=True, null=True)
    objects = NaEnquiryMasterDocumentManager()

    def __str__(self):
            return str(self.vchr_enquiry_num)

    class Meta:
        managed = False
        db_table = 'na_enquiry_master'

class NaEnquiryDetails(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_na_enquiry_master = models.ForeignKey(NaEnquiryMaster, models.DO_NOTHING)
    vchr_product = models.CharField(max_length=20)
    vchr_brand = models.CharField(max_length=20)
    vchr_item = models.CharField(max_length=25)
    vchr_color = models.CharField(max_length=25, blank=True, null=True)
    int_quantity = models.IntegerField()
    vchr_remarks = models.CharField(max_length=50, blank=True, null=True)
    json_product_spec = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False

        db_table = 'na_enquiry_details'

    def __str__(self):
            return str(self.fk_na_enquiry_master)
