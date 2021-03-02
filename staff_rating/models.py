from django.db import models
from userdetails.models import UserDetails as UserModel
from enquiry.models import EnquiryMaster
from customer.models import CustomerDetails as CustomerModel
# Create your models here.
class StaffRating(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    # vchr_remarks = models.TextField(blank=True, null=True)
    dbl_rating = models.FloatField(blank=True, null=True)
    fk_enquiry_master = models.ForeignKey(EnquiryMaster, models.DO_NOTHING, null=True, blank=True)
    fk_user = models.ForeignKey(UserModel, models.DO_NOTHING, null=True, blank=True)
    fk_customer = models.ForeignKey(CustomerModel, models.DO_NOTHING, null=True, blank=True)
    # vchr_staff_impression = models.CharField(max_length=250, blank=True, null=True)
    # vchr_cust_satisfied = models.CharField(max_length=100, blank=True, null=True)
    dat_created = models.DateTimeField(blank=True, null=True)

    vchr_comments = models.TextField(blank=True, null=True)
    vchr_staff_attitude = models.CharField(max_length=50)
    vchr_staff_knowledge = models.CharField(max_length=50)
    vchr_store_ambience = models.CharField(max_length=50)
    vchr_recommended = models.CharField(max_length=50)
    vchr_know_about = models.CharField(max_length=50)

    def __str__(self):
        return "{}".format(self.fk_user)

    class Meta:
        managed = True
        db_table = 'staff_rating'
