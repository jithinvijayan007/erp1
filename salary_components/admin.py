from django.contrib import admin
from .models import *
# Register your models here.


class SalaryComponentsAdmin(admin.ModelAdmin):
    list_display = ['vchr_code', 'vchr_name', 'int_type', 'bln_active']
    list_filter = ['bln_active', 'int_type', 'bln_exclude']
    search_fields = ['vchr_name', 'vchr_code', 'vchr_remarks']
admin.site.register(SalaryComponents, SalaryComponentsAdmin)
