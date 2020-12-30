from django.db import models
from django.contrib.auth.models import User
from branch.models import Branch
from item_category.models import Item
from supplier.models import Supplier
from django.contrib.postgres.fields import JSONField

# Create your models here.

class PoMasterManager(models.Manager):
    def create_pomaster_doc(self, str_new_doc_no):
         pomaster_ = self.create(vchr_stktransfer_num=vchr_po_num)
         return pomaster_

class PoMaster(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_po_num = models.CharField(max_length=20, blank=True, null=True)
    dat_po = models.DateTimeField(blank=True, null=True)
    dat_po_expiry = models.DateTimeField(blank=True, null=True)
    fk_supplier = models.ForeignKey(Supplier, models.DO_NOTHING, blank=True, null=True)
    fk_branch = models.ForeignKey(Branch, models.DO_NOTHING, blank=True, null=True)
    vchr_notes = models.TextField(blank=True, null=True)
    fk_created = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,related_name='purchase_order_created_user')
    dat_created = models.DateTimeField(blank=True, null=True)
    fk_updated = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,related_name='purchase_order_updated_user')
    dat_updated = models.DateTimeField(blank=True, null=True)
    int_doc_status = models.IntegerField(blank=True, null=True)
    int_status = models.IntegerField(blank=True, null=True) # 1-Billed,0-ordered
    int_total_qty = models.IntegerField(blank=True, null=True)
    dbl_total_amount = models.FloatField(blank=True, null=True)
    # objects = PoMasterManager()

    class Meta:
        managed = False
        db_table = 'po_master'


class PoDetails(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_item = models.ForeignKey(Item, models.DO_NOTHING, blank=True, null=True)
    fk_po_master = models.ForeignKey(PoMaster, models.DO_NOTHING, blank=True, null=True)
    int_qty = models.IntegerField(blank=True, null=True)
    dbl_prate = models.FloatField(blank=True, null=True)
    dbl_total_amount = models.FloatField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'po_details'


class Document(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_module_name = models.CharField(max_length=50)
    vchr_short_code = models.CharField(max_length=5)
    int_number = models.IntegerField()
    fk_branch = models.ForeignKey(Branch, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'document'


class GrnMasterManager(models.Manager):
    def create_grnmaster_doc(self, str_new_doc_no):
         grnmaster_ = self.create(vchr_stktransfer_num=vchr_purchase_num)
         return grnmaster_

class GrnMaster(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_purchase_num = models.CharField(max_length=20, blank=True, null=True)
    dat_purchase = models.DateTimeField(blank=True, null=True)
    fk_supplier = models.ForeignKey(Supplier, models.DO_NOTHING, blank=True, null=True)
    fk_branch = models.ForeignKey(Branch, models.DO_NOTHING, blank=True, null=True)#[warehouses or head office only]
    fk_po = models.ForeignKey(PoMaster, models.DO_NOTHING, blank=True, null=True)
    int_fop = models.IntegerField(blank=True, null=True)
    dat_pay_before = models.DateTimeField(blank=True, null=True)
    dbl_total = models.FloatField(blank=True, null=True)
    vchr_notes = models.TextField(blank=True, null=True)
    fk_created = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,related_name='purchase_created_user')
    dat_created = models.DateTimeField(blank=True, null=True)
    fk_updated = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,related_name='purchase_updated_user')
    dat_updated = models.DateTimeField(blank=True, null=True)
    int_doc_status = models.IntegerField(blank=True, null=True)
    dbl_addition = models.FloatField(blank=True, null=True)
    dbl_deduction = models.FloatField(blank=True, null=True)
    dbl_roundoff_value = models.FloatField(blank=True, null=True)
    int_approve = models.IntegerField(blank=True, null=True)
    vchr_bill_no = models.CharField(max_length=20, blank=True, null=True)
    dat_bill = models.DateTimeField(blank=True, null=True)
    vchr_reject_reason = models.TextField(blank=True, null=True)
    dbl_bill_amount = models.FloatField(blank=True, null=True)
    vchr_bill_image = models.CharField(max_length=350, blank=True, null=True)
    # objects = GrnMasterManager()

    class Meta:
        managed = False
        db_table = 'grn_master'


class GrnDetails(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_item = models.ForeignKey(Item, models.DO_NOTHING, blank=True, null=True)
    fk_purchase = models.ForeignKey(GrnMaster, models.DO_NOTHING, blank=True, null=True)
    int_qty = models.IntegerField(blank=True, null=True)
    int_free = models.IntegerField(blank=True, null=True)
    int_avail = models.IntegerField(blank=True, null=True)
    int_damaged = models.IntegerField(blank=True, null=True)
    dbl_costprice = models.FloatField(blank=True, null=True)#[price of a single piece without tax and discount]
    dbl_dscnt_percent = models.FloatField(blank=True, null=True)#[total discount percent]
    dbl_dscnt_perunit = models.FloatField(blank=True, null=True)#[per single piece]
    dbl_discount = models.FloatField(blank=True, null=True)#[total discount]
    jsn_tax = JSONField(blank=True, null=True)  # This field type is a guess.(CGST:4,SGST:4)[per piece]
    dbl_tax = models.FloatField(blank=True, null=True)#[tax amount per piece]
    dbl_ppu = models.FloatField(blank=True, null=True)#[price of a single piece with tax and discount]
    dbl_total_amount = models.FloatField(blank=True, null=True)#[total amount]
    vchr_batch_no = models.CharField(max_length=30, blank=True, null=True)
    dbl_perpie_aditn = models.FloatField(blank=True, null=True)
    dbl_perpie_dedctn = models.FloatField(blank=True, null=True)
    jsn_imei = JSONField(blank=True, null=True)  # This field type is a guess.
    jsn_imei_avail = JSONField(blank=True, null=True)  # This field type is a guess.
    jsn_imei_dmgd = JSONField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'grn_details'


class PurchaseVoucherManager(models.Manager):
    def create_pur_vouch_doc(self, str_new_doc_no):
         pur_vouch = self.create(vchr_voucher_num=vchr_voucher_num)
         return pur_vouch

class PurchaseVoucher(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_voucher_num = models.CharField(max_length=20, blank=True, null=True)
    fk_supplier = models.ForeignKey(Supplier, models.DO_NOTHING, blank=True, null=True)
    fk_grn = models.ForeignKey(GrnMaster, models.DO_NOTHING, blank=True, null=True)
    dbl_voucher_amount = models.FloatField(blank=True, null=True)
    vchr_voucher_bill_no = models.CharField(max_length=20, blank=True, null=True)
    dat_voucher_bill = models.DateTimeField(blank=True, null=True)
    fk_created = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,related_name='bill_creater')
    dat_created = models.DateTimeField(blank=True, null=True)
    fk_updated = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True,related_name='bill_updater')
    dat_updated = models.DateTimeField(blank=True, null=True)
    vchr_remark = models.TextField(blank=True, null=True)
    int_doc_status = models.IntegerField(blank=True, null=True)
    # objects = PurchaseVoucherManager()

    class Meta:
        managed = False
        db_table = 'purchase_voucher'


class GrnrMaster(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_purchase_return_num = models.CharField(max_length=80, blank=True, null=True)
    dat_purchase_return = models.DateTimeField(blank=True, null=True)
    fk_branch = models.ForeignKey(Branch, models.DO_NOTHING, blank=True, null=True)
    dat_created = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'grnr_master'

class GrnrDetails(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_item = models.ForeignKey(Item, models.DO_NOTHING, blank=True, null=True)
    fk_master = models.ForeignKey(GrnrMaster, models.DO_NOTHING, blank=True, null=True)
    int_qty = models.IntegerField(blank=True, null=True)
    dbl_tax_rate = models.FloatField(blank=True, null=True)
    jsn_imei = models.TextField(blank=True, null=True)  # This field type is a guess.
    vchr_batch_no = models.CharField(max_length=80, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'grnr_details'

class GrnrImeiDetails(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_details = models.ForeignKey(GrnrDetails, models.DO_NOTHING, blank=True, null=True)
    fk_grn_details = models.ForeignKey(GrnDetails, models.DO_NOTHING, blank=True, null=True)
    jsn_imei = models.TextField(blank=True, null=True)  # This field type is a guess.
    jsn_batch_no = models.TextField(blank=True, null=True)  # This field type is a guess.
    int_qty = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'grnr_imei_details'
