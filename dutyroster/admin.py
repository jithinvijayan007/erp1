from django.contrib import admin
from .models import *
# Register your models here.


class DutyRosterAdmin(admin.ModelAdmin):
    list_display = ['fk_employee', 'int_month', 'int_year', 'bln_active']
    list_filter = ['bln_active', 'int_year', 'int_month']
    search_fields = ['fk_employee__username', 'fk_employee__first_name', 'fk_employee__last_name']
admin.site.register(DutyRoster, DutyRosterAdmin)


class WeekoffLeaveAdmin(admin.ModelAdmin):
    list_display = ['fk_employee', 'dat_from', 'dat_to', 'fk_approved', 'fk_verified']
    list_filter = ['int_status', 'dat_created']
    search_fields = ['fk_employee__username', 'fk_employee__first_name', 'fk_employee__last_name']
admin.site.register(WeekoffLeave, WeekoffLeaveAdmin)
