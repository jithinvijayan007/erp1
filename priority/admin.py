from django.contrib import admin
from priority.models import Priority
# Register your models here.

class PriorityAdmin(admin.ModelAdmin):
    list_display = ['vchr_priority_name','fk_company','bln_status']
    list_filter = ['bln_status','fk_company']
    search_fields = ['vchr_priority_name']
admin.site.register(Priority,PriorityAdmin)
