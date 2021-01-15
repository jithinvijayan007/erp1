from django.db import models
from enquiry.models import EnquiryMaster
from userdetails.models import UserDetails as UserModel
from item_category.models import Item as Items
from brands.models  import Brands
from products.models import Products
# from item_category.models import Brands, Items,Products
from stock_app.models import Stockdetails
from django.contrib.postgres.fields import JSONField
from userdetails.models import Financiers

class MobileEnquiry(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_enquiry_master = models.ForeignKey(EnquiryMaster, models.DO_NOTHING)
    fk_brand = models.ForeignKey(Brands, models.DO_NOTHING)
    fk_item = models.ForeignKey(Items, models.DO_NOTHING)
    int_quantity = models.IntegerField()
    dbl_amount = models.FloatField(blank=True, null=True) #selling price of n items
    vchr_enquiry_status = models.CharField(max_length=50)
    vchr_colour = models.CharField(max_length=50)
    vchr_spec = models.CharField(max_length=100)
    vchr_remarks = models.TextField(blank=True, null=True)
    fk_stockdetails = models.ForeignKey(Stockdetails, models.DO_NOTHING, blank=True, null=True)

    int_sold = models.IntegerField(blank=True, null=True)
    dbl_sup_amount  = models.IntegerField(blank=True, null=True) # supplier amount per piece
    dbl_buyback = models.IntegerField(blank=True, null=True)
    dbl_discount = models.IntegerField(blank=True, null=True)
    dbl_min_price = models.IntegerField(blank=True, null=True) # min price for single piece
    dbl_max_price = models.IntegerField(blank=True, null=True) # max price for single piece
    dbl_imei_json = JSONField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'mobile_enquiry'

class TabletEnquiry(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_enquiry_master = models.ForeignKey(EnquiryMaster, models.DO_NOTHING)
    fk_brand = models.ForeignKey(Brands, models.DO_NOTHING)
    fk_item = models.ForeignKey(Items, models.DO_NOTHING)
    int_quantity = models.IntegerField()
    dbl_amount = models.FloatField(blank=True, null=True)
    vchr_enquiry_status = models.CharField(max_length=50)
    vchr_remarks = models.TextField(blank=True, null=True)
    fk_stockdetails = models.ForeignKey(Stockdetails, models.DO_NOTHING, blank=True, null=True)

    int_sold = models.IntegerField(blank=True, null=True)
    dbl_sup_amount  = models.IntegerField(blank=True, null=True)
    dbl_buyback = models.IntegerField(blank=True, null=True)
    dbl_discount = models.IntegerField(blank=True, null=True)
    dbl_min_price = models.IntegerField(blank=True, null=True)
    dbl_max_price = models.IntegerField(blank=True, null=True)
    dbl_imei_json = JSONField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tablet_enquiry'


class ComputersEnquiry(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_enquiry_master = models.ForeignKey(EnquiryMaster, models.DO_NOTHING)
    fk_brand = models.ForeignKey(Brands, models.DO_NOTHING)
    fk_item = models.ForeignKey(Items, models.DO_NOTHING)
    int_quantity = models.IntegerField()
    dbl_amount = models.FloatField(blank=True, null=True)
    vchr_enquiry_status = models.CharField(max_length=50)
    vchr_remarks = models.TextField(blank=True, null=True)
    fk_stockdetails = models.ForeignKey(Stockdetails, models.DO_NOTHING, blank=True, null=True)

    int_sold = models.IntegerField(blank=True, null=True)
    dbl_sup_amount  = models.IntegerField(blank=True, null=True)
    dbl_buyback = models.IntegerField(blank=True, null=True)
    dbl_discount = models.IntegerField(blank=True, null=True)
    dbl_min_price = models.IntegerField(blank=True, null=True)
    dbl_max_price = models.IntegerField(blank=True, null=True)
    dbl_imei_json = JSONField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'computers_enquiry'


class AccessoriesEnquiry(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_enquiry_master = models.ForeignKey(EnquiryMaster, models.DO_NOTHING)
    fk_brand = models.ForeignKey(Brands, models.DO_NOTHING)
    fk_item = models.ForeignKey(Items, models.DO_NOTHING)
    int_quantity = models.IntegerField()
    dbl_amount = models.FloatField(blank=True, null=True)
    vchr_enquiry_status = models.CharField(max_length=50)
    vchr_remarks = models.TextField(blank=True, null=True)
    fk_stockdetails = models.ForeignKey(Stockdetails, models.DO_NOTHING, blank=True, null=True)

    int_sold = models.IntegerField(blank=True, null=True)
    dbl_sup_amount  = models.IntegerField(blank=True, null=True)
    dbl_buyback = models.IntegerField(blank=True, null=True)
    dbl_discount = models.IntegerField(blank=True, null=True)
    dbl_min_price = models.IntegerField(blank=True, null=True)
    dbl_max_price = models.IntegerField(blank=True, null=True)
    dbl_imei_json = JSONField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'accessories_enquiry'

class MobileFollowup(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_mobile = models.ForeignKey(MobileEnquiry, models.DO_NOTHING)
    dat_followup = models.DateTimeField(blank=True, null=True)
    fk_user = models.ForeignKey(UserModel, models.DO_NOTHING, blank=True, null=True, related_name='mobile_fk_user')
    vchr_notes = models.CharField(max_length=250, blank=True, null=True)
    vchr_enquiry_status = models.CharField(max_length=50)
    int_status = models.IntegerField(blank=True, null=True)
    dbl_amount = models.FloatField(blank=True, null=True)
    fk_updated = models.ForeignKey(UserModel, models.DO_NOTHING, blank=True, null=True, related_name='mobile_fk_updated')
    dat_updated = models.DateTimeField(blank=True, null=True)

    int_quantity = models.IntegerField()


    class Meta:
        managed = False
        db_table = 'mobile_followup'

class TabletFollowup(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_tablet = models.ForeignKey(TabletEnquiry, models.DO_NOTHING)
    dat_followup = models.DateTimeField(blank=True, null=True)
    fk_user = models.ForeignKey(UserModel, models.DO_NOTHING, blank=True, null=True, related_name='tablet_fk_user')
    vchr_notes = models.CharField(max_length=250, blank=True, null=True)
    vchr_enquiry_status = models.CharField(max_length=50)
    int_status = models.IntegerField(blank=True, null=True)
    dbl_amount = models.FloatField(blank=True, null=True)
    fk_updated = models.ForeignKey(UserModel, models.DO_NOTHING, blank=True, null=True, related_name='tablet_fk_updated')
    dat_updated = models.DateTimeField(blank=True, null=True)

    int_quantity = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tablet_followup'

class ComputersFollowup(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_computers = models.ForeignKey(ComputersEnquiry, models.DO_NOTHING)
    dat_followup = models.DateTimeField(blank=True, null=True)
    fk_user = models.ForeignKey(UserModel, models.DO_NOTHING, blank=True, null=True, related_name='computer_fk_user')
    vchr_notes = models.CharField(max_length=250, blank=True, null=True)
    vchr_enquiry_status = models.CharField(max_length=50)
    int_status = models.IntegerField(blank=True, null=True)
    dbl_amount = models.FloatField(blank=True, null=True)
    fk_updated = models.ForeignKey(UserModel, models.DO_NOTHING, blank=True, null=True, related_name='computer_fk_updated')
    dat_updated = models.DateTimeField(blank=True, null=True)

    int_quantity = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'computers_followup'

class AccessoriesFollowup(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_accessories = models.ForeignKey(AccessoriesEnquiry, models.DO_NOTHING)
    dat_followup = models.DateTimeField(blank=True, null=True)
    fk_user = models.ForeignKey(UserModel, models.DO_NOTHING, blank=True, null=True, related_name='accessories_fk_user')
    vchr_notes = models.CharField(max_length=250, blank=True, null=True)
    vchr_enquiry_status = models.CharField(max_length=50)
    int_status = models.IntegerField(blank=True, null=True)
    dbl_amount = models.FloatField(blank=True, null=True)
    fk_updated = models.ForeignKey(UserModel, models.DO_NOTHING, blank=True, null=True, related_name='accessories_fk_updated')
    dat_updated = models.DateTimeField(blank=True, null=True)

    int_quantity = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'accessories_followup'

class ItemEnquiry(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_enquiry_master = models.ForeignKey(EnquiryMaster, models.DO_NOTHING,related_name='item_fk_enquiry')
    fk_product = models.ForeignKey(Products, models.DO_NOTHING,related_name='item_fk_product')
    fk_brand = models.ForeignKey(Brands, models.DO_NOTHING,related_name='item_fk_brand')
    fk_item = models.ForeignKey(Items, models.DO_NOTHING,related_name='item_fk_item')

    int_quantity = models.IntegerField()
    dbl_amount = models.FloatField(blank=True, null=True)
    vchr_enquiry_status = models.CharField(max_length=50)
    vchr_remarks = models.TextField(blank=True, null=True)
    # fk_stockdetails = models.ForeignKey(Stockdetails, models.DO_NOTHING, blank=True, null=True,related_name='item_fk_stockdetails')
    int_sold = models.IntegerField(blank=True, null=True)
    dbl_sup_amount = models.IntegerField(blank=True, null=True)
    # dbl_buyback = models.IntegerField(blank=True, null=True)
    # dbl_discount = models.IntegerField(blank=True, null=True)
    dbl_min_price = models.IntegerField(blank=True, null=True)
    dbl_max_price = models.IntegerField(blank=True, null=True)
    dbl_imei_json = JSONField(blank=True, null=True)  # This field type is a guess.
    int_fop = models.IntegerField(blank=True, null=True ,default = 0) # int form of payment 0 -by hand,1-finance
    dbl_buy_back_amount = models.FloatField(blank=True, null=True)
    dbl_discount_amount = models.FloatField(blank=True, null=True)
    dbl_gdp_amount = models.FloatField(blank=True, null=True,default=0.0)
    dbl_gdew_amount = models.FloatField(blank=True, null=True,default=0.0)
    int_type = models.IntegerField(blank=True, null=True,default=0)
    # dbl_exchange_amt = models.FloatField(blank=True, null=True)
    # vchr_exc_imei = models.CharField(max_length=50)
    # fk_item_exchange = models.ForeignKey(ItemExchange, models.DO_NOTHING, blank=True, null=True)
    dbl_actual_gdp = models.FloatField(blank=True, null=True)
    dat_gdp = models.DateTimeField(blank=True, null=True)
    dbl_actual_gdew = models.FloatField(blank=True, null=True)
    dat_gdew = models.DateTimeField(blank=True, null=True)
    dbl_actual_est_amt = models.FloatField(blank=True, null=True)
    bln_smart_choice = models.BooleanField(default=False)
    dat_sale = models.DateTimeField(blank=True, null=True) #INVOICED or LOST
    dbl_indirect_discount_amount = models.FloatField(blank=True, null=True)
    dbl_cost_price = models.FloatField(blank=True, null=True)
    dbl_dealer_price = models.FloatField(blank=True, null=True)
    dbl_mop_price = models.FloatField(blank=True, null=True)
    dbl_myg_price = models.FloatField(blank=True, null=True)
    dbl_tax = models.FloatField(blank=True, null=True)
    json_tax = JSONField(blank=True, null=True)  # This field type is a guess.


    dbl_mrp_price = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'item_enquiry'

    def __str__(self):
        return "{}".format(self.pk_bint_id)


class ItemFollowup(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_item_enquiry = models.ForeignKey(ItemEnquiry, models.DO_NOTHING)
    dat_followup = models.DateTimeField(blank=True, null=True)
    fk_user = models.ForeignKey(UserModel, models.DO_NOTHING, blank=True, null=True, related_name='item_fk_user')
    vchr_notes = models.CharField(max_length=250, blank=True, null=True)
    vchr_enquiry_status = models.CharField(max_length=50)
    int_status = models.IntegerField(blank=True, null=True)
    dbl_amount = models.FloatField(blank=True, null=True)
    fk_updated = models.ForeignKey(UserModel, models.DO_NOTHING, blank=True, null=True, related_name='item_fk_updated')
    dat_updated = models.DateTimeField(blank=True, null=True)
    int_quantity = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return str(self.fk_item_enquiry)
    class Meta:
        managed = False
        db_table = 'item_followup'



class Notification(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_module = models.CharField(max_length=100)
    vchr_message = models.CharField(max_length=100)
    vchr_url = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    int_doc_id = models.CharField(max_length=100)
    bln_active_status = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'notification'
    def __str__(self):
        return str(self.vchr_message)



class GDPRange(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    dbl_from = models.FloatField(blank=True,null=True)
    dbl_to = models.FloatField(blank=True,null=True)
    dbl_amt = models.FloatField(blank=True,null=True)
    int_type = models.IntegerField()

    def __str__(self):
            return str(self.dbl_from+'-'+self.dbl_to)
    class Meta:
        managed = False

        db_table = 'gdp_range'

class ItemExchange(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_item = models.ForeignKey(Items, models.DO_NOTHING, blank=True, null=True)
    vchr_filename_json = JSONField(blank=True, null=True)  # This field type is a guess.
    dbl_exchange_amt = models.FloatField(blank=True, null=True)
    vchr_exc_imei = models.CharField(max_length=50, blank=True, null=True)
    fk_item_enquiry = models.ForeignKey(ItemEnquiry, models.DO_NOTHING, blank=True, null=True)
    class Meta:
        managed = False

        db_table = 'item_exchange'

    def __str__(self):
        return "{}".format(self.fk_item_enquiry)

class EnquiryFinanceImages(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_bill_image = models.CharField(max_length=350, blank=True, null=True)
    vchr_delivery_image = models.CharField(max_length=350, blank=True, null=True)
    vchr_proof1 = models.CharField(max_length=350, blank=True, null=True)
    vchr_proof2 = models.CharField(max_length=350, blank=True, null=True)
    fk_enquiry_master = models.ForeignKey(EnquiryMaster, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False

        db_table = 'enquiry_finance_images'
