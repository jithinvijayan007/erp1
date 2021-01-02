from django.contrib import admin
from .models import *
# Register your models here.


class JobPositionAdmin(admin.ModelAdmin):
    list_display = ['vchr_name', 'fk_department', 'int_area_type', 'bln_active']
    list_filter = ['bln_active','int_area_type','fk_department']
    search_fields = ['vchr_name', 'fk_department__vchr_name']
admin.site.register(JobPosition, JobPositionAdmin)
