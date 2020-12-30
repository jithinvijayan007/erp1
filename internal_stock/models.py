from django.db import models
from django.contrib.auth.models import User as AuthUser
from branch.models import Branch
from item_category.models import Item
from purchase.models import GrnDetails
from django.contrib.postgres.fields import JSONField
from supplier.models import Supplier
from userdetails.models import Userdetails
# Create your models here.

class StockRequestDocumentManager(models.Manager):
    def create_stock_doc(self, str_new_doc_no):
         stock_request = self.create(vchr_stkrqst_num=str_new_doc_no)
         return stock_request

class StockRequest(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_from = models.ForeignKey(Branch, models.DO_NOTHING, blank=True, null=True,related_name='frombranch')
    fk_to = models.ForeignKey(Branch, models.DO_NOTHING, blank=True, null=True,related_name='tobranch')
    dat_request = models.DateTimeField(blank=True, null=True)
    vchr_stkrqst_num = models.CharField(max_length=20, blank=True, null=True)
    dat_expected = models.DateTimeField(blank=True, null=True)
    vchr_remarks = models.TextField(blank=True, null=True)
    fk_created = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True,related_name='stockrequestcreated')
    dat_created = models.DateTimeField(blank=True, null=True)
    fk_updated = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True,related_name='stockrequestupdate')
    dat_updated = models.DateTimeField(blank=True, null=True)
    int_doc_status = models.IntegerField(blank=True, null=True)
    int_status = models.IntegerField(blank=True, null=True) #####1.TM APPROVAL REQESUTED , 2.TM APROVAL ,3.APPROVED, 4.REJECTED
    vchr_reject = models.TextField(blank=True, null=True)
    vchr_approve = models.TextField(blank=True, null=True)
    int_automate = models.IntegerField(blank=True, null=True) # 1-Manual,2-Automate,3-Responsed Automate
    # bln_approved = models.IntegerField(blank=True, null=True)###(True -aproved,False-Rejected)
    vchr_rej_remark = models.TextField(blank=True, null=True)
    # objects = StockRequestDocumentManager()

    class Meta:
        managed = False
        db_table = 'stock_request'



class IsrDetails(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_request = models.ForeignKey(StockRequest, models.DO_NOTHING, blank=True, null=True)
    fk_item = models.ForeignKey(Item, models.DO_NOTHING, blank=True, null=True)
    int_qty = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'isr_details'

class StockTransferDocumentManager(models.Manager):
    def create_stock_trans(self, str_new_doc_no):
         stock_transfer = self.create(vchr_stktransfer_num=str_new_doc_no)
         return stock_transfer

class CourierMaster(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_name = models.CharField(max_length=100, blank=True, null=True)
    vchr_gst_no = models.CharField(max_length=100, blank=True, null=True)
    json_vehicle_no = JSONField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'courier_master'

class StockTransfer(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_request = models.ForeignKey(StockRequest, models.DO_NOTHING, blank=True, null=True)
    fk_from = models.ForeignKey(Branch, models.DO_NOTHING, blank=True, null=True,related_name='frombranchtransfer')
    fk_to = models.ForeignKey(Branch, models.DO_NOTHING, blank=True, null=True,related_name='tobranchtransfer')
    vchr_stktransfer_num=models.CharField(max_length=20, blank=True, null=True)
    dat_transfer = models.DateTimeField(blank=True, null=True)
    dat_acknowledge = models.DateTimeField(blank=True, null=True)
    vchr_remarks = models.TextField(blank=True, null=True)
    fk_created = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True,related_name='stocktransfercreated')
    dat_created = models.DateTimeField(blank=True, null=True)
    fk_updated = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True,related_name='stocktransferupdated')
    dat_updated = models.DateTimeField(blank=True, null=True)
    int_doc_status = models.IntegerField(blank=True, null=True)
    int_acknowledge = models.IntegerField(blank=True, null=True)
    int_status = models.IntegerField(blank=True, null=True)###(0-billed,1-Transferred,2-Recieved,3-acknowledged,5-partillay received)
    vchr_sap_doc_num = models.CharField(max_length=10, blank=True, null=True)
    dat_sap_doc_date = models.DateTimeField(blank=True, null=True)
    vchr_eway_bill_no = models.CharField(max_length=25, blank=True, null=True)
    bln_direct_transfer = models.BooleanField(default=False)
    vchr_vehicle_num = models.CharField(max_length=20, blank=True, null=True)
    vchr_irn_no = models.CharField(max_length=100, blank=True, null=True)
    txt_qr_code = models.TextField(blank=True, null=True)

    # objects = StockRequestDocumentManager()
    class Meta:
        managed = False
        db_table = 'stock_transfer'


class IstDetails(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_transfer = models.ForeignKey(StockTransfer, models.DO_NOTHING, blank=True, null=True)
    fk_pd = models.ForeignKey(GrnDetails, models.DO_NOTHING, blank=True, null=True)
    fk_item = models.ForeignKey(Item, models.DO_NOTHING, blank=True, null=True)
    int_qty = models.IntegerField(blank=True, null=True)
    jsn_imei = JSONField(blank=True, null=True)
    dbl_rate = models.FloatField(blank=True, null=True)
    # batchno = models.BigIntegerField(blank=True, null=True)
    jsn_batch_no = JSONField(blank=True, null=True)  # This field type is a guess.
    class Meta:
        managed = False
        db_table = 'ist_details'





class TransferModeDetails(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_transfer = models.ForeignKey(StockTransfer, models.DO_NOTHING, blank=True, null=True)
    int_medium = models.IntegerField(blank=True, null=True)
    vchr_name_responsible = models.CharField(max_length=30, blank=True, null=True)
    bnt_contact_number = models.BigIntegerField(blank=True, null=True)
    bnt_number = models.CharField(max_length=50, blank=True, null=True)
    fk_created = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True,related_name='createdusertransfermod')
    dat_created = models.DateTimeField(blank=True, null=True)
    fk_updated = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True,related_name='updatedusertransfermod')
    dat_updated = models.DateTimeField(blank=True, null=True)
    int_doc_status = models.IntegerField(blank=True, null=True)
    int_packet_no = models.IntegerField(blank=True, null=True)
    int_packet_received = models.IntegerField(blank=True, null=True)
    dbl_expense = models.FloatField(blank=True, null=True)
    fk_courier = models.ForeignKey(CourierMaster, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False

        db_table = 'transfer_mode_details'




class TransferHistory(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_transfer = models.ForeignKey(StockTransfer, models.DO_NOTHING, blank=True, null=True)
    fk_created = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True,related_name='createduser')
    dat_created = models.DateTimeField(blank=True, null=True)
    fk_updated = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True,related_name='updateduser')
    dat_updated = models.DateTimeField(blank=True, null=True)
    vchr_status = models.CharField(max_length=30, blank=True, null=True)
    int_doc_status = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False

        db_table = 'transfer_history'


class StockTransferImeiDetails(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_details = models.ForeignKey(IstDetails, models.DO_NOTHING, blank=True, null=True)
    fk_grn_details = models.ForeignKey(GrnDetails, models.DO_NOTHING, blank=True, null=True)
    jsn_imei =JSONField(blank=True, null=True)  # This field type is a guess.
    jsn_batch_no =JSONField(blank=True, null=True)  # This field type is a guess.
    int_qty =  models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'stock_transfer_imei_details'


class PurchaseRequest(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_supplier = models.ForeignKey(Supplier, models.DO_NOTHING, blank=True, null=True)
    fk_branch = models.ForeignKey(Branch, models.DO_NOTHING, blank=True, null=True)
    dat_request = models.DateTimeField(blank=True, null=True)
    int_status = models.IntegerField(blank=True, null=True)
    fk_created = models.ForeignKey(Userdetails, models.DO_NOTHING, blank=True, null=True)
    dat_created = models.DateTimeField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'purchase_request'


class PurchaseRequestDetails(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_request = models.ForeignKey(PurchaseRequest, models.DO_NOTHING, blank=True, null=True)
    fk_item = models.ForeignKey(Item, models.DO_NOTHING, blank=True, null=True)
    int_qty = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'purchase_request_details'
