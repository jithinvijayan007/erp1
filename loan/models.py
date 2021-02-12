from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class LoanRequest(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_employee = models.ForeignKey('userdetails.UserDetails', models.DO_NOTHING, blank=True, null=True)
    dbl_loan_amt = models.FloatField(blank=True, null=True)
    int_tenure = models.IntegerField(blank=True, null=True)
    int_month = models.IntegerField(blank=True, null=True)
    int_year = models.IntegerField(blank=True, null=True)
    txt_remarks = models.TextField(blank=True, null=True)
    dat_created = models.DateTimeField(auto_now_add=True)
    dat_updated = models.DateTimeField(blank=True, null=True)
    int_status = models.IntegerField(blank=True, null=True, default=0) # -1) Rejected, 0) Requested, 1) Approved
    bln_mob_loan = models.NullBooleanField()
    fk_created = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True, related_name = 'loan_request_fk_created')
    fk_updated = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True, related_name = 'loan_request_fk_updated')
    class Meta:
        managed = False
        db_table = 'loan_request'

    def __str__(self):
        return self.k_employee


class LoanDetails(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_request = models.ForeignKey(LoanRequest, models.DO_NOTHING, blank=True, null=True)
    dbl_amount = models.FloatField(blank=True, null=True)
    int_month = models.IntegerField(blank=True, null=True)
    int_year = models.IntegerField(blank=True, null=True)
    txt_remarks = models.TextField(blank=True, null=True)
    dat_created = models.DateTimeField(auto_now_add=True)
    dat_updated = models.DateTimeField(blank=True, null=True)
    int_status = models.IntegerField(blank=True, null=True, default=0) # -2) deactive, -1) Exclude, 0) Default, 1) Processed
    fk_created = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True, related_name = 'loan_details_fk_created')
    fk_updated = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True, related_name = 'loan_details_fk_updated')
    class Meta:
        managed = False
        db_table = 'loan_details'

    def __str__(self):
        return self.fk_request
