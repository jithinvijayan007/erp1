from django.contrib import admin
# from .models import *
# Register your models here.


# class LeaveTypeAdmin(admin.ModelAdmin):
#     list_display = ['vchr_name', 'dbl_leaves_per_year', 'int_year', 'fk_desig', 'bln_active']
#     list_filter = ['bln_active', 'int_year', 'fk_company', 'fk_desig']
#     search_fields = ['vchr_name', 'fk_desig__vchr_name', 'vchr_remarks']
# admin.site.register(LeaveType, LeaveTypeAdmin)


# class LeaveAdmin(admin.ModelAdmin):
#     list_display = ['fk_user', 'dat_from', 'dat_to', 'fk_leave_type', 'leave_mode', 'int_status']
#     list_filter = ['int_status', 'dat_from', 'dat_to', 'chr_leave_mode']
#     search_fields = ['vchr_reason', 'fk_leave_type__vchr_name', 'fk_user__username', 'fk_user__first_name', 'fk_user__last_name']
#     def leave_mode(self,obj):
#         if obj.chr_leave_mode == 'M':
#             return 'Morning'
#         elif obj.chr_leave_mode == 'E':
#             return 'Evening'
#         elif obj.chr_leave_mode == 'F':
#             return 'Full Day'
#         elif obj.chr_leave_mode == 'N':
#             return 'Night'
# admin.site.register(Leave, LeaveAdmin)


# class CarryforwardAdmin(admin.ModelAdmin):
#     list_display = ['fk_user', 'fk_leave_type', 'int_year', 'dbl_opening']
#     list_filter = ['fk_leave_type', 'int_year']
#     search_fields = ['fk_leave_type__vchr_name', 'fk_user__username', 'fk_user__first_name', 'fk_user__last_name']
# admin.site.register(Carryforward, CarryforwardAdmin)
