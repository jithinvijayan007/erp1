from django.contrib import admin
from .models import *
# Register your models here.


class LoanRequestAdmin(admin.ModelAdmin):
    list_display = ['fk_employee', 'dbl_loan_amt', 'int_tenure','int_month','int_year','int_status']
    list_filter = ['bln_mob_loan','int_status']
    search_fields = ['txt_remarks', 'fk_employee__username', 'fk_employee__first_name', 'fk_employee__last_name']
admin.site.register(LoanRequest, LoanRequestAdmin)


class LoanDetailsAdmin(admin.ModelAdmin):
    list_display = ['fk_request', 'dbl_amount', 'int_month','int_year','int_status']
    list_filter = ['int_status']
    search_fields = ['txt_remarks', 'fk_request__fk_employee__username', 'fk_request__fk_employee__first_name', 'fk_request__fk_employee__last_name']
admin.site.register(LoanDetails, LoanDetailsAdmin)
