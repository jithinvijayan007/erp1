from django.contrib import admin

from supplier.models import Supplier,AddressSupplier,ContactPersonSupplier
# Register your models here.
admin.site.register(AddressSupplier)
admin.site.register(ContactPersonSupplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['vchr_code','vchr_name','is_act_del']
    list_filter = ['is_act_del']
admin.site.register(Supplier,SupplierAdmin)
