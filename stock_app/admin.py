
from django.contrib import admin
from stock_app.models import Stockmaster,Stockdetails

# Register your models here.

class StockmasterAdmin(admin.ModelAdmin):
    list_display = ['vchr_purchase_order_number','fk_supplier','dat_added','vchr_payment_mode','fk_branch']
    list_filter = ['fk_company',]
    search_fields = ['vchr_purchase_order_number','vchr_payment_mode']
admin.site.register(Stockmaster,StockmasterAdmin)

class StockdetailsAdmin(admin.ModelAdmin):
    list_display = ['fk_stock_master','fk_item','int_qty','int_available']
admin.site.register(Stockdetails,StockdetailsAdmin)
