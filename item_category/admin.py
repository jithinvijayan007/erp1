from django.contrib import admin
from item_category.models import TaxMaster,ItemCategory,Item
# Register your models here.


class TaxMasterAdmin(admin.ModelAdmin):
    list_display = ['vchr_name','int_intra_tax','bln_active']
    list_filter = ['bln_active','int_intra_tax']
    search_fields = ['vchr_name','vchr_name']
admin.site.register(TaxMaster,TaxMasterAdmin)


class ItemCategoryAdmin(admin.ModelAdmin):
    list_display = ['vchr_item_category','dat_created','vchr_hsn_code','vchr_sac_code']
    list_filter = ['int_status','dat_created']
    search_fields = ['vchr_item_category','vchr_hsn_code','vchr_sac_code']
admin.site.register(ItemCategory,ItemCategoryAdmin)


class ItemAdmin(admin.ModelAdmin):
    list_display = ['vchr_item_code','vchr_name','fk_brand','int_status']
    list_filter = ['int_status','dat_created']
    search_fields = ['vchr_item_code','vchr_name','fk_product','fk_brand__vchr_name','fk_item_category__vchr_item_category','fk_item_group__vchr_item_group']
admin.site.register(Item,ItemAdmin)
