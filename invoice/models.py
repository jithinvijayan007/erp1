from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User as AuthUser
from userdetails.models import Userdetails
from customer.models import CustomerDetails
from company.models import FinancialYear
from branch.models import Branch
from coupon.models import Coupon
from loyalty_card.models import LoyaltyCard
from item_category.models import Item
from states.models import States,Location,District
from customer.models import CustomerDetails,SalesCustomerDetails
# Create your models here.

# class SalesMasterManager(models.Manager):
#     def create_sale(self, ins_sales_customer,ins_branch,str_inv_num,str_remarks,dbl_total_amt,dbl_rounding_off,dct_addition,dct_deduction,
#                     json_total_tax,dbl_total_discount,int_offer,dbl_total_tax,dbl_coupon_amt,fk_financial_year,
#                     dbl_total_buyback,fk_loyalty_id,dbl_loyalty,ins_staff,fk_created,fk_coupon_id,vchr_sap_key,dat_sap_doc_date,int_sale_type,vchr_reff_no):
#          invoicing = self.create(fk_customer = ins_sales_customer,fk_branch = ins_branch,vchr_invoice_num = str_inv_num,
#          dat_invoice = date.today(),vchr_remarks = str_remarks,dat_created = datetime.now(),int_doc_status = 1,
#          dbl_total_amt = dbl_total_amt,dbl_rounding_off = dbl_rounding_off,jsn_addition = json.dumps(dct_addition),jsn_deduction = json.dumps(dct_deduction),
#          dbl_total_tax = dbl_total_tax,dbl_discount = dbl_total_discount + int_offer,json_tax = json_total_tax,
#          dbl_buyback = dbl_total_buyback,fk_loyalty_id = fk_loyalty_id,dbl_loyalty = dbl_loyalty,fk_staff = ins_staff,fk_created = fk_created,fk_coupon_id = fk_coupon_id,
#          dbl_coupon_amt = dbl_coupon_amt, fk_financial_year = fk_financial_year,dbl_rounding_off = models.FloatField(blank=True, null=True)
#             jsn_addition = models.TextField(blank=True, null=True)  # This field type is a guess.
#             jsn_deduction = models.TextField(blank=True, null=True)  # This field type is a guess.
#             vchr_sap_key = models.CharField(max_length=10, blank=True, null=True)
#             dat_sap_doc_date = models.DateTimeField(blank=True, null=True)
#             int_sale_type = models.IntegerField(blank=True, null=True,default=0)
#             vchr_reff_no = models.CharField(max_length=30, blank=True, null=True)
#             int_order_no = models.CharField(max_length=30, blank=True, null=True)
#             dbl_cust_outstanding = models.FloatField(blank=True, null=True))
#          return invoicing


class SalesMasterDocumentManager(models.Manager):
    def create_inv_num(self, str_new_doc_no):
         inv_num = self.create(vchr_invoice_num=str_new_doc_no)
         return inv_num

class SalesMaster(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    # -------------------------------------------------------------------------------------------------------------------------------------
    fk_customer = models.ForeignKey(SalesCustomerDetails, models.DO_NOTHING, blank=True, null=True) # comment before run the script(sales_customer_add)
    # fk_customer = models.ForeignKey(CustomerDetails, models.DO_NOTHING, blank=True, null=True)      #  comment after run the script
    # fk_sales_customer = models.ForeignKey(SalesCustomerDetails, models.DO_NOTHING, blank=True, null=True) #comment after run the script
    # -------------------------------------------------------------------------------------------------------------------------------------
    fk_branch = models.ForeignKey(Branch, models.DO_NOTHING, blank=True, null=True)
    dat_invoice = models.DateField(blank=True, null=True)
    fk_staff = models.ForeignKey(Userdetails, models.DO_NOTHING, blank=True, null=True, related_name='sales_master_fk_staff')
    vchr_invoice_num = models.CharField(max_length=50, blank=True, null=True)
    vchr_remarks = models.CharField(max_length=500, blank=True, null=True)
    vchr_journal_num = models.CharField(max_length=50, blank=True, null=True)
    vchr_delete_remark = models.CharField(max_length=500, blank=True, null=True)
    dbl_total_amt = models.FloatField(blank=True, null=True)
    dbl_total_tax = models.FloatField(blank=True, null=True)
    json_tax = JSONField()
    dbl_discount = models.FloatField(blank=True, null=True)
    fk_loyalty = models.ForeignKey(LoyaltyCard, models.DO_NOTHING, blank=True, null=True)
    dbl_loyalty = models.FloatField(blank=True, null=True)
    dbl_buyback = models.FloatField(blank=True, null=True)
    dbl_supplier_amount = models.FloatField(blank=True, null=True)
    fk_coupon = models.ForeignKey(Coupon, models.DO_NOTHING, blank=True, null=True)
    dbl_coupon_amt = models.FloatField(blank=True, null=True)
    int_doc_status = models.IntegerField(blank=True, null=True)
    dat_created = models.DateTimeField(blank=True, null=True)
    dat_updated = models.DateTimeField(blank=True, null=True)
    fk_created = models.ForeignKey(Userdetails, models.DO_NOTHING, blank=True, null=True, related_name='sales_master_fk_created')
    fk_updated = models.ForeignKey(Userdetails, models.DO_NOTHING, blank=True, null=True, related_name='sales_master_fk_updated')
    fk_financial_year = models.ForeignKey(FinancialYear, models.DO_NOTHING, blank=True, null=True)
    dbl_rounding_off = models.FloatField(blank=True, null=True)
    jsn_addition = models.TextField(blank=True, null=True)  # This field type is a guess.
    jsn_deduction = models.TextField(blank=True, null=True)  # This field type is a guess.
    vchr_sap_key = models.CharField(max_length=10, blank=True, null=True)
    dat_sap_doc_date = models.DateTimeField(blank=True, null=True)
    int_sale_type = models.IntegerField(blank=True, null=True,default=0)
    vchr_reff_no = models.CharField(max_length=30, blank=True, null=True)
    int_order_no = models.CharField(max_length=30, blank=True, null=True)
    dbl_cust_outstanding = models.FloatField(blank=True, null=True)
    txt_qr_code = models.TextField(blank=True, null=True)
    vchr_irn_no = models.CharField(max_length=100, blank=True, null=True)
    # objects = SalesMasterDocumentManager()
    class Meta:
        managed = False
        db_table = 'sales_master'
    def __str__(self):
        return str(self.vchr_invoice_num)


class SalesDetails(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_master = models.ForeignKey(SalesMaster, models.DO_NOTHING, blank=True, null=True)
    fk_item = models.ForeignKey(Item, models.DO_NOTHING, blank=True, null=True)
    int_qty = models.IntegerField(blank=True, null=True)
    dbl_amount = models.FloatField(blank=True, null=True)
    dbl_tax = models.FloatField(blank=True, null=True)
    dbl_discount = models.FloatField(blank=True, null=True)
    dbl_buyback = models.FloatField(blank=True, null=True)
    json_tax = JSONField()
    vchr_batch = models.CharField(max_length=50, blank=True, null=True)
    json_imei = JSONField()
    int_doc_status = models.IntegerField(blank=True, null=True)
    dbl_supplier_amount = models.FloatField(blank=True, null=True)
    dbl_selling_price = models.FloatField(blank=True, null=True)
    int_sales_status = models.IntegerField(blank=True, null=True) # 0. Return, 1. Sale, 2. Smart Chhoice, 3. Service, 4. Jio
    dbl_indirect_discount = models.FloatField(blank=True, null=True)
    dbl_dealer_price = models.FloatField(blank=True, null=True)
    dbl_cost_price = models.FloatField(blank=True, null=True)
    dbl_mrp = models.FloatField(blank=True, null=True)
    dbl_mop = models.FloatField(blank=True, null=True)
    dbl_tax_percentage = models.FloatField(blank=True, null=True)


    class Meta:
        managed = False
        db_table = 'sales_details'
    def __str__(self):
        return str(self.fk_item.vchr_item_code)

class PartialInvoice(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    json_data = JSONField()
    int_enq_master_id = models.BigIntegerField(blank=True, null=True)
    int_active = models.IntegerField(blank=True, null=True, default=0)
    dat_created = models.DateTimeField(blank=True, null=True)
    dat_invoice = models.DateTimeField(blank=True, null=True)
    fk_invoice = models.ForeignKey(SalesMaster, models.DO_NOTHING, blank=True, null=True)
    int_status = models.IntegerField(blank=True, null=True) #20.Ecommerce(Third-Party)
    int_approve = models.IntegerField(blank=True, null=True, default=0) #0:default,1:Admin UnApproved,2: Admin Approved,3:Credit Requested,4:Credit Sale Approved,5:Credit Sale Rejected
    json_updated_data = JSONField()
    int_sale_type =  models.IntegerField(blank=True, null=True) #1.Ecommerce(Third-Party)
    class Meta:
        managed = False
        db_table = 'partial_invoice'
    def __str__(self):
        return str(self.pk_bint_id)


class CustServiceDelivery(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_sales_master = models.ForeignKey(SalesMaster, models.DO_NOTHING, blank=True, null=True)
    fk_customer = models.ForeignKey(CustomerDetails, models.DO_NOTHING, blank=True, null=True)
    vchr_cust_name = models.CharField(max_length=100, blank=True, null=True)
    int_mobile = models.BigIntegerField(blank=True, null=True)
    txt_address = models.TextField(blank=True, null=True)
    vchr_landmark = models.CharField(max_length=200, blank=True, null=True)
    vchr_gst_no = models.CharField(max_length=30, blank=True, null=True)
    fk_location = models.ForeignKey(Location, models.DO_NOTHING, blank=True, null=True)
    fk_state = models.ForeignKey(States, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cust_service_delivery'
    def __str__(self):
        return str(self.vchr_cust_name)

class LoyaltyCardInvoice(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_loyalty = models.ForeignKey(LoyaltyCard, models.DO_NOTHING, blank=True, null=True)
    fk_customer = models.ForeignKey(CustomerDetails, models.DO_NOTHING, blank=True, null=True)
    int_points = models.BigIntegerField(blank=True, null=True, default=0)
    dbl_amount = models.FloatField(blank=True, null=True)
    fk_invoice = models.ForeignKey(SalesMaster, models.DO_NOTHING, blank=True, null=True)
    dat_invoice = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'loyalty_card_invoice'
    def __str__(self):
        return str(self.fk_invoice.vchr_invoice_num)

class Bank(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_name = models.CharField(max_length=50)
    int_status = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bank'

class PaymentDetails(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_sales_master = models.ForeignKey('SalesMaster', models.DO_NOTHING)
    int_fop = models.IntegerField() # 0. Finance, 1. Cash, 2. Debit Card, 3. Credit Card, 4.Receipt, 5 Paytm, 6.Paytm Mall,7 Bharath Qr
    vchr_card_number = models.CharField(max_length=20, blank=True, null=True)
    vchr_name = models.CharField(max_length=100, blank=True, null=True)
    vchr_finance_schema = models.CharField(max_length=20, blank=True, null=True)
    vchr_reff_number = models.CharField(max_length=100, blank=True, null=True)
    dbl_receved_amt = models.FloatField(blank=True, null=True)
    dbl_finance_amt = models.FloatField(blank=True, null=True)
    dat_created_at = models.DateTimeField(auto_now_add=True)
    dbl_cc_charge = models.FloatField(blank=True, null=True)
    fk_bank = models.ForeignKey(Bank, models.DO_NOTHING, blank=True, null=True)


    class Meta:
        managed = False
        db_table = 'payment_details'
    def __str__(self):
        return str(self.fk_sales_master.vchr_invoice_num)

class SalesMasterJioDocumentManager(models.Manager):
    def create_inv_num(self, str_new_doc_no):
         inv_num = self.create(vchr_invoice_num=str_new_doc_no)
         return inv_num

class SalesMasterJio(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)

    # ----------------------------------------------------------------------------------------------------------------------------------------------------
    fk_customer = models.ForeignKey(SalesCustomerDetails, models.DO_NOTHING, blank=True, null=True) # comment before run the script(sales_customer_add)
    # fk_customer = models.ForeignKey(CustomerDetails, models.DO_NOTHING, blank=True, null=True)      # comment after run the script
    # fk_sales_customer = models.ForeignKey(SalesCustomerDetails, models.DO_NOTHING, blank=True, null=True) #comment after run the script
    # ----------------------------------------------------------------------------------------------------------------------------------------------------

    fk_branch = models.ForeignKey(Branch, models.DO_NOTHING, blank=True, null=True)
    dat_invoice = models.DateField(blank=True, null=True)
    fk_staff = models.ForeignKey(Userdetails, models.DO_NOTHING, blank=True, null=True,related_name='assigned_staff')
    vchr_invoice_num = models.CharField(max_length=50, blank=True, null=True)
    vchr_remarks = models.CharField(max_length=500, blank=True, null=True)
    fk_item = models.ForeignKey(Item, models.DO_NOTHING, blank=True, null=True)
    int_qty = models.IntegerField(blank=True, null=True)
    vchr_batch = models.CharField(max_length=50, blank=True, null=True)
    json_imei = JSONField()
    dbl_total_amt = models.FloatField(blank=True, null=True)
    dbl_rounding_off = models.FloatField(blank=True, null=True)
    int_doc_status = models.IntegerField(blank=True, null=True)
    dat_created = models.DateTimeField(blank=True, null=True)
    dat_updated = models.DateTimeField(blank=True, null=True)
    fk_created = models.ForeignKey(Userdetails, models.DO_NOTHING, blank=True, null=True,related_name='created_staff')
    fk_updated = models.ForeignKey(Userdetails, models.DO_NOTHING, blank=True, null=True,related_name='updated_staff')
    int_fop = models.IntegerField()
    vchr_card_number = models.CharField(max_length=20, blank=True, null=True)
    vchr_name = models.CharField(max_length=100, blank=True, null=True)
    # vchr_finance_schema = models.CharField(max_length=20, blank=True, null=True)
    vchr_reff_number = models.CharField(max_length=100, blank=True, null=True)
    dbl_receved_amt = models.FloatField(blank=True, null=True)
    fk_financial_year = models.ForeignKey(FinancialYear, models.DO_NOTHING, blank=True, null=True)
    fk_bank = models.ForeignKey(Bank, models.DO_NOTHING, blank=True, null=True)
    # objects = SalesMasterJioDocumentManager()

    class Meta:
        managed = False
        db_table = 'sales_master_jio'



class FinanceScheme(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_schema = models.CharField(max_length=30, blank=True, null=True)
    dat_from = models.DateField(blank=True, null=True)
    dat_to = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'finance_scheme'
class TheftDetails(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    dat_purchase = models.DateField(blank=True, null=True)
    int_days_missing = models.IntegerField(blank=True, null=True)
    int_depreciation_amt = models.BigIntegerField(blank=True, null=True)
    fk_purchase_branch = models.ForeignKey(Branch, models.DO_NOTHING, blank=True, null=True)
    fk_partial_invoice = models.ForeignKey(PartialInvoice, models.DO_NOTHING, blank=True, null=True)
    fk_created = models.ForeignKey(Userdetails, models.DO_NOTHING, blank=True, null=True,related_name="theft_created")
    dat_created = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'theft_details'


class Depreciation(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    int_days_upto = models.IntegerField(blank=True, null=True)
    int_dep_percentage = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'depreciation'

class FinanceDetails(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_payment = models.ForeignKey(PaymentDetails, models.DO_NOTHING, blank=True, null=True)
    dbl_finance_amt = models.FloatField(blank=True, null=True)
    dbl_receved_amt = models.FloatField(blank=True, null=True)
    dbl_processing_fee = models.FloatField(blank=True, null=True)
    dbl_margin_fee = models.FloatField(blank=True, null=True)
    dbl_service_amt = models.FloatField(blank=True, null=True)
    dbl_dbd_amt = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'finance_details'

class GDPRange(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    dbl_from = models.FloatField(blank=True,null=True)
    dbl_to = models.FloatField(blank=True,null=True)
    dbl_amt = models.FloatField(blank=True,null=True)
    int_type = models.IntegerField() #1.GDP,2.GDEW,3.GDP & GDEW


    class Meta:
        managed = False

        db_table = 'gdp_range'
