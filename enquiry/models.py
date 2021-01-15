from django.db import models
from userdetails.models import UserDetails as AuthUser
from customer.models import CustomerDetails as CustomerAppCustomermodel
from company.models import Company as CompanyDetails
from location.models import Country as Countries

# from country.models import Countries
# from airport.models import Airport
# from station.models import Station
from source.models import Source
from branch.models import Branch
from priority.models import Priority
# from airline.models import AirlineDetails
# from inventory.models import Products,Brands,Items
from products.models import Products
from brands.models import Brands
from item_category.models import Item as Items
from stock_app.models import Stockdetails
# Create your models here.
class Offers(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_code = models.CharField(max_length=100, blank=True, null=True)
    vchr_details = models.CharField(max_length=100, blank=True, null=True)
    bln_item = models.NullBooleanField() # True : internal item, False : new item
    bln_active=models.BooleanField(default=False)
    fk_branch = models.ForeignKey(Branch, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'offers'
class Document(models.Model):
    pk_bint_id = models.AutoField(primary_key=True)
    vchr_module_name = models.CharField(max_length=50)
    vchr_short_code = models.CharField(max_length=5)
    int_number = models.IntegerField()
    fk_company = models.ForeignKey(CompanyDetails, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'document'

    def __str__(self):
        return str(self.vchr_module_name)

class EnquiryMasterDocumentManager(models.Manager):
    def create_enquiry_num(self, str_new_doc_no):
         enquiry_num = self.create(vchr_enquiry_num=str_new_doc_no)
         return enquiry_num

class EnquiryMaster(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    vchr_enquiry_num = models.CharField(max_length=50)
    fk_customer = models.ForeignKey(CustomerAppCustomermodel, models.DO_NOTHING, blank=True, null=True)
    fk_source = models.ForeignKey(Source, models.DO_NOTHING, blank=True, null=True)
    # vchr_enquiry_source = models.CharField(max_length=50)
    vchr_customer_type = models.CharField(max_length=50)
    # vchr_enquiry_priority = models.CharField(max_length=50)
    fk_priority = models.ForeignKey(Priority, models.DO_NOTHING, blank=True, null=True)
    fk_assigned = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True)
    # fk_branch = models.IntegerField() # use before running eqt.sql
    fk_branch = models.ForeignKey(Branch, models.DO_NOTHING) # use after running eqt.sql
    bln_sms = models.NullBooleanField()
    chr_doc_status = models.CharField(max_length=1)
    fk_created_by = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True, related_name = 'enquiry_master_created_by')
    fk_updated_by = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True, related_name = 'enquiry_master_updated_by')
    dat_created_at = models.DateTimeField(blank=True, null=True)
    dat_updated_at = models.DateTimeField(blank=True, null=True)
    fk_company = models.ForeignKey(CompanyDetails, models.DO_NOTHING, blank=True, null=True)
    vchr_hash = models.TextField(blank=True, null=True)
    dbl_partial_amt = models.FloatField(blank=True, null=True)
    fk_offers = models.ForeignKey(Offers, models.DO_NOTHING, blank=True, null=True)
    vchr_remarks = models.TextField(blank=True, null=True)
    int_customer_type = models.IntegerField(blank=True, null=True) # 1-bajaj,2-amazone,3-flip,4-e-commerce
    vchr_order_num = models.CharField(max_length=30, blank=True, null=True)
    int_sale_type = models.IntegerField(blank=True, null=True) #1. Ecom third_party api
    vchr_reference_num = models.CharField(max_length=30, blank=True, null=True)
    objects = EnquiryMasterDocumentManager()
    def __str__(self):
        return str(self.vchr_enquiry_num)

    class Meta:
        managed = False
        db_table = 'enquiry_master'

# class Train(models.Model):
#     pk_bint_id = models.BigAutoField(primary_key=True)
#     fk_enquiry_master = models.ForeignKey(EnquiryMaster, models.DO_NOTHING)
#     chr_type_of_travel = models.CharField(max_length=1, blank=True, null=True)
#     fk_source = models.ForeignKey(Station, models.DO_NOTHING, related_name = 'station_source')
#     fk_destination = models.ForeignKey(Station, models.DO_NOTHING, related_name = 'station_destination')
#     dat_departure = models.DateField()
#     dat_return = models.DateField(blank=True, null=True)
#     vchr_class = models.CharField(max_length=50)
#     vchr_train = models.CharField(max_length=50)
#     int_adults = models.IntegerField()
#     int_children = models.IntegerField()
#     int_infants = models.IntegerField()
#     vchr_remarks = models.CharField(max_length=250, blank=True, null=True)
#     vchr_enquiry_status = models.CharField(max_length=50)
#     dbl_estimated_amount = models.FloatField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'train'

# class Flights(models.Model):
#     pk_bint_id = models.BigAutoField(primary_key=True)
#     fk_enquiry_master = models.ForeignKey(EnquiryMaster, models.DO_NOTHING)
#     chr_type_of_travel = models.CharField(max_length=1, blank=True, null=True)
#     fk_source = models.ForeignKey(Airport, models.DO_NOTHING, related_name = 'airport_source')
#     fk_destination = models.ForeignKey(Airport, models.DO_NOTHING, related_name = 'airport_destination')
#     dat_departure = models.DateField()
#     dat_return = models.DateField(blank=True, null=True)
#     vchr_class = models.CharField(max_length=50)
#     # vchr_airline = models.CharField(max_length=50)
#     int_adults = models.IntegerField()
#     int_children = models.IntegerField()
#     int_infants = models.IntegerField()
#     vchr_remarks = models.CharField(max_length=250, blank=True, null=True)
#     vchr_enquiry_status = models.CharField(max_length=50)
#     dbl_estimated_amount = models.FloatField(blank=True, null=True)
#     fk_airline = models.ForeignKey(AirlineDetails, models.DO_NOTHING, blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'flights'


class Forex(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_enquiry_master = models.ForeignKey(EnquiryMaster, models.DO_NOTHING)
    dbl_amount = models.FloatField(blank=True, null=True)
    vchr_remarks = models.CharField(max_length=250, blank=True, null=True)
    vchr_from = models.CharField(max_length=50)
    vchr_to = models.CharField(max_length=50)
    vchr_enquiry_status = models.CharField(max_length=50)
    dbl_estimated_amount = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'forex'



class Hotel(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_enquiry_master = models.ForeignKey(EnquiryMaster, models.DO_NOTHING)
    fk_package = models.ForeignKey('Package', models.DO_NOTHING, blank=True, null=True)
    dat_check_in = models.DateField()
    dat_check_out = models.DateField()
    vchr_city = models.CharField(max_length=50)
    vchr_nationality = models.CharField(max_length=50)
    int_rooms = models.IntegerField(blank=True, null=True)
    dbl_budget = models.FloatField(blank=True, null=True)
    vchr_meal_type = models.CharField(max_length=50, blank=True, null=True)
    vchr_remarks = models.CharField(max_length=250, blank=True, null=True)
    vchr_star_rating = models.CharField(max_length=50, blank=True, null=True)
    vchr_enquiry_status = models.CharField(max_length=50)
    dbl_estimated_amount = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hotel'


class Other(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_enquiry_master = models.ForeignKey(EnquiryMaster, models.DO_NOTHING)
    vchr_description = models.CharField(max_length=250, blank=True, null=True)
    vchr_enquiry_status = models.CharField(max_length=50)
    dbl_estimated_amount = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'other'


class Package(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_enquiry_master = models.ForeignKey(EnquiryMaster, models.DO_NOTHING)
    dat_from = models.DateField()
    dat_to = models.DateField()
    int_adults = models.IntegerField(blank=True, null=True)
    int_children = models.IntegerField(blank=True, null=True)
    int_infants = models.IntegerField(blank=True, null=True)
    dbl_budget = models.FloatField(blank=True, null=True)
    vchr_sightseeing = models.CharField(max_length=50, blank=True, null=True)
    vchr_destination = models.CharField(max_length=50, blank=True, null=True)
    vchr_remarks = models.CharField(max_length=250, blank=True, null=True)
    vchr_enquiry_status = models.CharField(max_length=50)
    dbl_estimated_amount = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'package'



class Rooms(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_hotel = models.ForeignKey(Hotel, models.DO_NOTHING)
    vchr_room_type = models.CharField(max_length=50, blank=True, null=True)
    int_adults = models.IntegerField(blank=True, null=True)
    int_children = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rooms'

class Transport(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_enquiry_master = models.ForeignKey(EnquiryMaster, models.DO_NOTHING)
    fk_package = models.ForeignKey(Package, models.DO_NOTHING, blank=True, null=True)
    dat_from = models.DateTimeField()
    dat_to = models.DateTimeField()
    vchr_pick_up = models.CharField(max_length=50, blank=True, null=True)
    vchr_drop_off = models.CharField(max_length=50, blank=True, null=True)
    vchr_vehical_type = models.CharField(max_length=50, blank=True, null=True)
    int_seats = models.IntegerField(blank=True, null=True)
    int_adults = models.IntegerField(blank=True, null=True)
    int_children = models.IntegerField(blank=True, null=True)
    int_infants = models.IntegerField(blank=True, null=True)
    vchr_vehical_preferred = models.CharField(max_length=50, blank=True, null=True)
    vchr_facility = models.CharField(max_length=50, blank=True, null=True)
    vchr_remarks = models.CharField(max_length=250, blank=True, null=True)
    vchr_enquiry_status = models.CharField(max_length=50)
    dbl_estimated_amount = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transport'



class TravelInsurance(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_enquiry_master = models.ForeignKey(EnquiryMaster, models.DO_NOTHING)
    vchr_insurance_type = models.CharField(max_length=50)
    dat_from = models.DateField()
    dat_to = models.DateField()
    int_adults = models.IntegerField(blank=True, null=True)
    int_children = models.IntegerField(blank=True, null=True)
    int_infants = models.IntegerField(blank=True, null=True)
    vchr_remarks = models.CharField(max_length=250, blank=True, null=True)
    vchr_enquiry_status = models.CharField(max_length=50)
    dbl_estimated_amount = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'travel_insurance'




class Visa(models.Model):
    pk_bint_id = models.BigAutoField(primary_key=True)
    fk_enquiry_master = models.ForeignKey(EnquiryMaster, models.DO_NOTHING)
    vchr_visa_category = models.CharField(max_length=50)
    vchr_visit_type = models.CharField(max_length=50)
    vchr_duration_type = models.CharField(max_length=50)
    dbl_duration = models.FloatField(blank=True, null=True)
    int_adults = models.IntegerField(blank=True, null=True)
    int_children = models.IntegerField(blank=True, null=True)
    int_infants = models.IntegerField(blank=True, null=True)
    vchr_remarks = models.CharField(max_length=250, blank=True, null=True)
    vchr_enquiry_status = models.CharField(max_length=50)
    dbl_estimated_amount = models.FloatField(blank=True, null=True)
    fk_country = models.ForeignKey(Countries, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'visa'


# class TrainFollowup(models.Model):
#     pk_bint_id = models.BigAutoField(primary_key=True)
#     fk_train = models.ForeignKey(Train, models.DO_NOTHING)
#     vchr_notes = models.CharField(max_length=250, blank=True, null=True)
#     vchr_enquiry_status = models.CharField(max_length=50)
#     int_status = models.IntegerField(blank=True, null=True)
#     dbl_amount = models.FloatField(blank=True, null=True)
#     fk_user = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True, related_name='train_created_by')
#     fk_updated = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True, related_name='train_updated_by')
#     dat_followup = models.DateTimeField(blank=True, null=True)
#     dat_updated = models.DateTimeField(blank=True, null=True)

#     def __str__(self):
#         return str(self.pk_bint_id)

#     class Meta:
#         managed = False
#         db_table = 'train_followup'


# class FlightsFollowup(models.Model):
#     pk_bint_id = models.BigAutoField(primary_key=True)
#     fk_flights = models.ForeignKey(Flights, models.DO_NOTHING)
#     vchr_notes = models.CharField(max_length=250, blank=True, null=True)
#     vchr_enquiry_status = models.CharField(max_length=50)
#     int_status = models.IntegerField(blank=True, null=True)
#     dbl_amount = models.FloatField(blank=True, null=True)
#     fk_user = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True, related_name='flights_created_by')
#     fk_updated = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True, related_name='flights_updated_by')
#     dat_followup = models.DateTimeField(blank=True, null=True)
#     dat_updated = models.DateTimeField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'flights_followup'

# class ForexFollowup(models.Model):
#     pk_bint_id = models.BigAutoField(primary_key=True)
#     fk_forex = models.ForeignKey(Forex, models.DO_NOTHING)
#     vchr_notes = models.CharField(max_length=250, blank=True, null=True)
#     vchr_enquiry_status = models.CharField(max_length=50)
#     int_status = models.IntegerField(blank=True, null=True)
#     dbl_amount = models.FloatField(blank=True, null=True)
#     fk_user = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True, related_name='forex_created_by')
#     fk_updated = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True, related_name='forex_updated_by')
#     dat_followup = models.DateTimeField(blank=True, null=True)
#     dat_updated = models.DateTimeField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'forex_followup'

# class HotelFollowup(models.Model):
#     pk_bint_id = models.BigAutoField(primary_key=True)
#     fk_hotel = models.ForeignKey(Hotel, models.DO_NOTHING)
#     vchr_notes = models.CharField(max_length=250, blank=True, null=True)
#     vchr_enquiry_status = models.CharField(max_length=50)
#     int_status = models.IntegerField(blank=True, null=True)
#     dbl_amount = models.FloatField(blank=True, null=True)
#     fk_user = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True, related_name='hotel_created_by')
#     fk_updated = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True, related_name='hotel_updated_by')
#     dat_followup = models.DateTimeField(blank=True, null=True)
#     dat_updated = models.DateTimeField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'hotel_followup'

# class OtherFollowup(models.Model):
#     pk_bint_id = models.BigAutoField(primary_key=True)
#     fk_other = models.ForeignKey(Other, models.DO_NOTHING)
#     vchr_notes = models.CharField(max_length=250, blank=True, null=True)
#     vchr_enquiry_status = models.CharField(max_length=50)
#     int_status = models.IntegerField(blank=True, null=True)
#     dbl_amount = models.FloatField(blank=True, null=True)
#     fk_user = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True, related_name='other_created_by')
#     fk_updated = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True, related_name='other_updated_by')
#     dat_followup = models.DateTimeField(blank=True, null=True)
#     dat_updated = models.DateTimeField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'other_followup'

# class PackageFollowup(models.Model):
#     pk_bint_id = models.BigAutoField(primary_key=True)
#     fk_package = models.ForeignKey(Package, models.DO_NOTHING)
#     vchr_notes = models.CharField(max_length=250, blank=True, null=True)
#     vchr_enquiry_status = models.CharField(max_length=50)
#     int_status = models.IntegerField(blank=True, null=True)
#     dbl_amount = models.FloatField(blank=True, null=True)
#     fk_user = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True, related_name='package_created_by')
#     fk_updated = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True, related_name='package_updated_by')
#     dat_followup = models.DateTimeField(blank=True, null=True)
#     dat_updated = models.DateTimeField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'package_followup'

# class TransportFollowup(models.Model):
#     pk_bint_id = models.BigAutoField(primary_key=True)
#     fk_transport = models.ForeignKey(Transport, models.DO_NOTHING)
#     vchr_notes = models.CharField(max_length=250, blank=True, null=True)
#     vchr_enquiry_status = models.CharField(max_length=50)
#     int_status = models.IntegerField(blank=True, null=True)
#     dbl_amount = models.FloatField(blank=True, null=True)
#     fk_user = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True, related_name='transport_created_by')
#     fk_updated = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True, related_name='transport_updated_by')
#     dat_followup = models.DateTimeField(blank=True, null=True)
#     dat_updated = models.DateTimeField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'transport_followup'

# class TravelInsuranceFollowup(models.Model):
#     pk_bint_id = models.BigAutoField(primary_key=True)
#     fk_travel_insurance = models.ForeignKey(TravelInsurance, models.DO_NOTHING)
#     vchr_notes = models.CharField(max_length=250, blank=True, null=True)
#     vchr_enquiry_status = models.CharField(max_length=50)
#     int_status = models.IntegerField(blank=True, null=True)
#     dbl_amount = models.FloatField(blank=True, null=True)
#     fk_user = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True, related_name='travel_insurance_created_by')
#     fk_updated = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True, related_name='travel_insurance_updated_by')
#     dat_followup = models.DateTimeField(blank=True, null=True)
#     dat_updated = models.DateTimeField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'travel_insurance_followup'

# class VisaFollowup(models.Model):
#     pk_bint_id = models.BigAutoField(primary_key=True)
#     fk_visa = models.ForeignKey(Visa, models.DO_NOTHING)
#     vchr_notes = models.CharField(max_length=250, blank=True, null=True)
#     vchr_enquiry_status = models.CharField(max_length=50)
#     int_status = models.IntegerField(blank=True, null=True)
#     dbl_amount = models.FloatField(blank=True, null=True)
#     fk_user = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True, related_name='visa_created_by')
#     fk_updated = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True, related_name='visa_updated_by')
#     dat_followup = models.DateTimeField(blank=True, null=True)
#     dat_updated = models.DateTimeField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'visa_followup'

class AddAttachments(models.Model):
    pk_bint_id = models.AutoField(primary_key=True)
    vchr_logo = models.FileField(null=True,blank=True,max_length=300,upload_to='files/')
    fk_enquiry = models.ForeignKey(EnquiryMaster, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'add_attachments'