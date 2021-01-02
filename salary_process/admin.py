from django.contrib import admin
from .models import *
# Register your models here.


class SalaryProcessedAdmin(admin.ModelAdmin):
    list_display = ['fk_employee', 'int_month','int_year','dbl_net_salary','int_status']
    list_filter = ['int_status','int_year','int_month']
    search_fields = ['fk_employee__username', 'fk_employee__first_name', 'fk_employee__last_name', 'vchr_remarks']
admin.site.register(SalaryProcessed, SalaryProcessedAdmin)


class SalaryDetailsAdmin(admin.ModelAdmin):
    list_display = ['fk_employee', 'dbl_bp', 'dbl_da']
    list_filter = ['int_status','dat_updated']
    search_fields = ['fk_employee__username', 'fk_employee__first_name', 'fk_employee__last_name']
admin.site.register(SalaryDetails, SalaryDetailsAdmin)


class VariablePayAdmin(admin.ModelAdmin):
    list_display = ['fk_employee', 'int_month', 'int_year', 'int_status']
    list_filter = ['int_status','int_year','int_month']
    search_fields = ['fk_employee__username', 'fk_employee__first_name', 'fk_employee__last_name']
admin.site.register(VariablePay, VariablePayAdmin)
