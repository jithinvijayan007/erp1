from django.contrib import admin
from target.models import Target_Details,Target_Master
# Register your models here.

class Target_MasterAdmin(admin.ModelAdmin):
    list_display = ['vchr_fin_type','int_year','dbl_target','bln_active']
    list_filter = ['bln_active','int_target_type']
    search_fields = ['vchr_fin_type','dbl_target']
admin.site.register(Target_Master,Target_MasterAdmin)

class Target_DetailsAdmin(admin.ModelAdmin):
    list_display = ['fk_master','fk_brand','int_target_type','vchr_month']
    list_filter = ['int_year','vchr_month']
    search_fields = ['int_year','vchr_month','dbl_target']
admin.site.register(Target_Details,Target_DetailsAdmin)
