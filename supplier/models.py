from django.db import models

from item_category.models import TaxMaster
from django.contrib.auth.models import User
from category.models import OtherCategory
from states.models import States
class Supplier(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_name = models.CharField(max_length=100, blank=True, null=True)
    dat_from = models.DateTimeField(blank=True, null=True)
    vchr_code = models.CharField(max_length=50, blank=True, null=True)
    int_credit_days = models.IntegerField(blank=True, null=True)
    bint_credit_limit = models.BigIntegerField(blank=True, null=True)
    int_po_expiry_days = models.IntegerField(blank=True, null=True)
    vchr_tin_no = models.CharField(max_length=50, blank=True, null=True)
    vchr_cst_no = models.CharField(max_length=50, blank=True, null=True)
    vchr_gstin = models.CharField(max_length=100, blank=True, null=True)
    vchr_gstin_status = models.CharField(max_length=50, blank=True, null=True)
    fk_tax_class = models.ForeignKey(TaxMaster, models.DO_NOTHING, blank=True, null=True)
    vchr_account_group = models.CharField(max_length=50, blank=True, null=True)
    vchr_bank_account = models.CharField(max_length=50, blank=True, null=True)
    vchr_pan_no = models.CharField(max_length=50, blank=True, null=True)
    vchr_pan_status = models.CharField(max_length=50, blank=True, null=True)
    is_act_del = models.IntegerField(blank=True, null=True)
    fk_updated = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,related_name="supplier_updated")
    fk_created = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,related_name="supplier_created")
    dat_created = models.DateTimeField(blank=True, null=True)
    dat_updated = models.DateTimeField(blank=True, null=True)
    fk_category = models.ForeignKey(OtherCategory, models.DO_NOTHING, blank=True, null=True)
    int_batch_no_offset = models.IntegerField(blank=True, null=True,default=0)

    '''when is_act_del is     0, supplier is active, 2, supplier is de-active,
                          -1, supplier is deleted'''
    def __str__(self):
        return self.vchr_name

    class Meta:
        managed = False
        db_table = 'supplier'


class AddressSupplier(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_address = models.CharField(max_length=185, blank=True, null=True)
    vchr_email = models.CharField(max_length=30, blank=True, null=True)
    bint_phone_no = models.BigIntegerField(blank=True, null=True)
    int_pin_code = models.IntegerField(blank=True, null=True)
    fk_supplier = models.ForeignKey(Supplier, models.DO_NOTHING, blank=True, null=True)
    fk_states = models.ForeignKey(States, models.DO_NOTHING, blank=True, null=True)
    bln_status = models.NullBooleanField()
    bln_primary = models.NullBooleanField()

    def __str__(self):
        return self.vchr_address

    class Meta:
        managed = False

        db_table = 'address_supplier'

class ContactPersonSupplier(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_name = models.CharField(max_length=100, blank=True, null=True)
    vchr_designation = models.CharField(max_length=30, blank=True, null=True)
    vchr_department = models.CharField(max_length=30, blank=True, null=True)
    vchr_office = models.CharField(max_length=30, blank=True, null=True)
    bint_mobile_no = models.BigIntegerField(blank=True, null=True)
    bint_mobile_no2 = models.BigIntegerField(blank=True, null=True)
    fk_supplier = models.ForeignKey(Supplier, models.DO_NOTHING, blank=True, null=True)
    bln_status = models.NullBooleanField()

    def __str__(self):
        return self.vchr_name

    class Meta:
        managed = False

        db_table = 'contact_person_supplier'

class SupplierLog(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_remarks = models.TextField(blank=True, null=True)
    vchr_status = models.CharField(max_length=20, blank=True, null=True)
    dat_created = models.DateTimeField(blank=True, null=True)
    fk_created = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True)
    fk_supplier = models.ForeignKey(Supplier, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False

        db_table = 'supplier_log'
