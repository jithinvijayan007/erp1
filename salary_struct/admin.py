from django.contrib import admin
from salary_struct.models import SalaryStructure
# Register your models here.


class SalaryStructureAdmin(admin.ModelAdmin):
    list_display = ['vchr_name', 'dbl_bp_da', 'dbl_da','bln_active']
    list_filter = ['bln_active']
    search_fields = ['vchr_name']
admin.site.register(SalaryStructure, SalaryStructureAdmin)
