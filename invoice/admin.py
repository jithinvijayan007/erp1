from django.contrib import admin
from invoice.models import PartialInvoice, SalesMaster, SalesDetails, LoyaltyCardInvoice, PaymentDetails, CustServiceDelivery,FinanceScheme
# Register your models here.


class PartialInvoiceAdmin(admin.ModelAdmin):
    list_display = ['fk_invoice','dat_created','dat_invoice']
    list_filter = ['int_active']
    search_fields = ['fk_invoice__vchr_invoice_num']
admin.site.register(PartialInvoice,PartialInvoiceAdmin)

class SalesMasterAdmin(admin.ModelAdmin):
    list_display = ['vchr_invoice_num','dat_invoice','fk_customer','fk_branch']
    list_filter = ['dat_invoice','fk_financial_year']
    search_fields = ['fk_customer__vchr_name','fk_customer__int_mobile','fk_branch__vchr_code','fk_branch__vchr_name']
admin.site.register(SalesMaster,SalesMasterAdmin)

class SalesDetailsAdmin(admin.ModelAdmin):
    list_display = ['fk_master','fk_item','int_qty','dbl_amount']
    search_fields = ['fk_master__vchr_invoice_num']
admin.site.register(SalesDetails,SalesDetailsAdmin)

class LoyaltyCardInvoiceAdmin(admin.ModelAdmin):
    list_display = ['fk_customer','fk_loyalty','fk_invoice','dat_invoice']
    list_filter = ['fk_loyalty','dat_invoice']
    search_fields = ['fk_loyalty__vchr_card_name','fk_customer__vchr_name','fk_invoice__vchr_invoice_num']
admin.site.register(LoyaltyCardInvoice,LoyaltyCardInvoiceAdmin)

class PaymentDetailsAdmin(admin.ModelAdmin):
    list_display = ['fk_sales_master','int_fop','vchr_name','dat_created_at']
    list_filter = ['int_fop','dat_created_at']
    search_fields = ['vchr_name','vchr_finance_schema','vchr_reff_number','fk_sales_master__vchr_invoice_num']
admin.site.register(PaymentDetails,PaymentDetailsAdmin)

class CustServiceDeliveryAdmin(admin.ModelAdmin):
    list_display = ['fk_sales_master','fk_customer','int_mobile','fk_location','fk_state']
    list_filter = ['fk_state']
    search_fields = ['vchr_cust_name','fk_customer__vchr_name','fk_location__vchr_name','fk_location__vchr_pin_code','fk_state__vchr_name','txt_address','vchr_landmark','vchr_gst_no']
admin.site.register(CustServiceDelivery,CustServiceDeliveryAdmin)
admin.site.register(FinanceScheme)
