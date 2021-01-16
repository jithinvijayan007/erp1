from django.contrib import admin
# from inventory.models import Products,Brands, Items,ItemDetails,ItemGroup
# # Register your models here.

# class ProductsAdmin(admin.ModelAdmin):
#     list_display = ['vchr_product_name','fk_group','bln_visible']
#     list_filter = ['bln_visible','fk_group']
#     search_fields = ['vchr_product_name','fk_group__vchr_name']
# admin.site.register(Products,ProductsAdmin)

# class BrandsAdmin(admin.ModelAdmin):
#     list_display = ['vchr_brand_name','fk_company']
#     list_filter = ['fk_company']
#     search_fields = ['vchr_brand_name']
# admin.site.register(Brands,BrandsAdmin)

# class ItemsAdmin(admin.ModelAdmin):
#     list_display = ['vchr_item_code','vchr_item_name','fk_brand','fk_product','fk_item_group']
#     list_filter = ['fk_product']
#     search_fields = ['vchr_item_code','vchr_item_name','fk_brand__vchr_brand_name','fk_product__vchr_product_name']
# admin.site.register(Items,ItemsAdmin)

# class ItemDetailsAdmin(admin.ModelAdmin):
#     list_display = ['fk_item']
#     search_fields = ['fk_item__vchr_item_name','json_spec']
# admin.site.register(ItemDetails,ItemDetailsAdmin)

# class ItemGroupAdmin(admin.ModelAdmin):
#     list_display = ['vchr_item_group']
#     search_fields = ['vchr_item_group','int_status']
# admin.site.register(ItemGroup,ItemGroupAdmin)
