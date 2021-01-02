from django.db import models
from customer.models import CustomerDetails
from userdetails.models import UserDetails as Userdetails
from item_category.models import Item
from invoice.models import SalesMaster,Bank
from branch.models import Branch
from payment.models import Payment
from sales_return.models import SalesReturn
import datetime
# Create your models here.

class PartialReceipt(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_branchcode = models.CharField(max_length=20, blank=True, null=True)
    vchr_item_code = models.CharField(max_length=20, blank=True, null=True)
    json_data = models.TextField(blank=True, null=True)  # This field type is a guess.
    fk_enquiry_master_id = models.BigIntegerField(blank=True, null=True)
    fk_receipt = models.ForeignKey('Receipt', models.DO_NOTHING, blank=True, null=True)
    dat_created = models.DateTimeField(blank=True, null=False)
    int_status = models.IntegerField(blank=True, null=True)
    bln_service = models.NullBooleanField()

    class Meta:
        managed = False
        db_table = 'partial_receipt'

class ReceiptDocumentManager(models.Manager):
    def create_recpt_num(self, str_new_doc_no):
         recpt_num = self.create(vchr_receipt_num=str_new_doc_no)
         return recpt_num

class Receipt(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    dat_issue = models.DateTimeField(blank=True, null=True)
    fk_customer = models.ForeignKey(CustomerDetails, models.DO_NOTHING, blank=True, null=True)
    int_fop = models.IntegerField(blank=True, null=True) #1 cash, 2 debit card , 3 credit card, 4 Cheque, 5 RTGS, 6 NEFT, 7 Paytm, 8 Paytm Mall, 9 Bharath Qr
    dbl_amount = models.FloatField(blank=True, null=True)
    vchr_remarks = models.TextField(blank=True, null=True)
    fk_created = models.ForeignKey(Userdetails, models.DO_NOTHING, blank=True, null=True,related_name = 'receipt_created_id' )
    fk_updated = models.ForeignKey(Userdetails, models.DO_NOTHING, blank=True, null=True, related_name = 'receipt_updated_id')
    int_doc_status = models.IntegerField(blank=True, null=True) #0 new, 1 updated,-1 deleted, 6 - Advance Booking
    dat_created = models.DateTimeField(blank=True, null=True)
    dat_updated = models.DateTimeField(blank=True, null=True)
    int_pstatus = models.IntegerField(blank=True, null=True)  # 0 - Received 1 - Pending, 6 - Advance Booking
    int_receipt_type = models.IntegerField(blank=True, null=True) # 1. Advance, 2. Pre-Booking, 3. Others 4. Service , 5. Financier, 6 - Advance Booking ,7-Credit Settlement,8-Gdp Receipt
    fk_item = models.ForeignKey(Item, models.DO_NOTHING, blank=True, null=True)
    vchr_bank = models.CharField(max_length=50, blank=True, null=True)
    vchr_transaction_id = models.CharField(max_length=50, blank=True, null=True)
    dat_approval = models.DateTimeField(blank=True, null=True)
    vchr_receipt_num = models.CharField(max_length=50, blank=True, null=True)
    fk_branch = models.ForeignKey(Branch, models.DO_NOTHING, blank=True, null=True)
    vchr_card_num = models.CharField(max_length=30, blank=True, null=True)
    fk_bank = models.ForeignKey(Bank, models.DO_NOTHING, blank=True, null=True)
    int_document_id = models.BigIntegerField(blank=True, null=True)
    vchr_sap_key = models.CharField(max_length=10, blank=True, null=True) # 404 - For sales Return receipt
    fk_sales_return = models.ForeignKey(SalesReturn, models.DO_NOTHING, blank=True, null=True)
    fk_sales_master = models.ForeignKey(SalesMaster, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'receipt'

class ReceiptInvoiceMatching(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    dbl_amount = models.FloatField(blank=True, null=True)
    dat_created = models.DateTimeField(blank=True, null=True)
    fk_sales_master = models.ForeignKey(SalesMaster, models.DO_NOTHING, blank=True, null=True)
    fk_receipt = models.ForeignKey(Receipt, models.DO_NOTHING, blank=True, null=True)
    fk_payment = models.ForeignKey(Payment, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'receipt_invoice_matching'
