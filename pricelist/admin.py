from django.contrib import admin
from pricelist.models import PriceList
# Register your models here.

class PriceListAdmin(admin.ModelAdmin):
    list_display = ['fk_item','dbl_cost_amnt','dbl_mrp','dat_efct_from']
    list_filter = ['int_status']
    search_fields = ['fk_item__vchr_item_code','fk_item__vchr_name']
admin.site.register(PriceList,PriceListAdmin)
