from django.contrib import admin
from .models import *
# Register your models here.


class ShiftScheduleAdmin(admin.ModelAdmin):
    list_display = ['vchr_code', 'vchr_name', 'time_shift_from', 'time_shift_to','int_status']
    list_filter = ['int_status','bln_allowance','bln_night','time_shift_from','time_shift_to']
    search_fields = ['vchr_name', 'vchr_code', 'vchr_remark']
admin.site.register(ShiftSchedule, ShiftScheduleAdmin)


class EmployeeShiftAdmin(admin.ModelAdmin):
    list_display = ['fk_employee', 'int_shift_type', 'bln_active']
    list_filter = ['bln_active']
    search_fields = ['fk_employee__username', 'fk_employee__first_name', 'fk_employee__last_name']
admin.site.register(EmployeeShift, EmployeeShiftAdmin)
