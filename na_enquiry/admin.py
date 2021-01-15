from django.contrib import admin
from na_enquiry.models import NaEnquiryMaster, NaEnquiryDetails

# Register your models here.

class NaEnquiryMasterAdmin(admin.ModelAdmin):
    list_display = ['vchr_enquiry_num','fk_customer','fk_branch','fk_source']
    list_filter = ['fk_source','fk_branch']
    search_fields = ['vchr_enquiry_num','vchr_enquiry_num']
admin.site.register(NaEnquiryMaster,NaEnquiryMasterAdmin)

class NaEnquiryDetailsAdmin(admin.ModelAdmin):
    list_display = ['fk_na_enquiry_master','vchr_item','vchr_color','int_quantity']
    list_filter = ['vchr_color','vchr_product']
    search_fields = ['vchr_product','vchr_brand','vchr_item','vchr_color','vchr_remarks']
admin.site.register(NaEnquiryDetails,NaEnquiryDetailsAdmin)
