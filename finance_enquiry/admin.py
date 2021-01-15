from django.contrib import admin
from finance_enquiry.models import FinanceSchema,FinanceCustomerDetails,EnquiryFinance

# Register your models here.

class FinanceSchemaAdmin(admin.ModelAdmin):
    list_display = ['vchr_schema']
    search_fields = ['vchr_schema']
admin.site.register(FinanceSchema,FinanceSchemaAdmin)

class EnquiryFinanceAdmin(admin.ModelAdmin):
    list_display = ['fk_financiers','vchr_delivery_order_no','fk_enquiry_master','vchr_finance_status']
    list_filter = ['vchr_finance_status']
    search_fields = ['vchr_finance_status','vchr_delivery_order_no','vchr_name_in_card','fk_financiers__vchr_name','fk_enquiry_master__vchr_enquiry_num']
admin.site.register(EnquiryFinance,EnquiryFinanceAdmin)


class FinanceCustomerDetailsAdmin(admin.ModelAdmin):
    list_display = ['fk_schema','fk_enquiry_finance','vchr_branch_name']
    list_filter = ['vchr_id_type','vchr_bank_name',]
    search_fields = ['vchr_id_number','vchr_pan_number','vchr_bank_name','bint_account_number','vchr_branch_name','vchr_cheque_number']
admin.site.register(FinanceCustomerDetails,FinanceCustomerDetailsAdmin)
