from django.contrib import admin
from .models import *
# Register your models here.


class PtPeriodAdmin(admin.ModelAdmin):
    list_display = ['vchr_period_name', 'int_month_from', 'int_month_to', 'int_deduct_month']
    list_filter = ['bln_active']
    search_fields = ['vchr_period_name']
admin.site.register(PtPeriod, PtPeriodAdmin)


class ProfessionalTaxAdmin(admin.ModelAdmin):
    list_display = ['dbl_from_amt', 'dbl_to_amt', 'fk_period','dbl_tax']
    list_filter = ['bln_active']
    search_fields = ['fk_period__vchr_period_name']
admin.site.register(ProfessionalTax, ProfessionalTaxAdmin)
