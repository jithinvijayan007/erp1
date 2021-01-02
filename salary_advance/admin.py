from django.contrib import admin
from .models import *
# Register your models here.


class SalaryAdvanceAdmin(admin.ModelAdmin):
    list_display = ['fk_employee', 'dbl_amount', 'int_month', 'int_year', 'int_status', 'bln_active']
    list_filter = ['bln_active','int_status']
    search_fields = ['vchr_purpose', 'vchr_remarks', 'fk_employee__username', 'fk_employee__first_name', 'fk_employee__last_name']
admin.site.register(SalaryAdvance, SalaryAdvanceAdmin)
