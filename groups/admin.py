from django.contrib import admin
from groups.models import Groups
# Register your models here.


class GroupsAdmin(admin.ModelAdmin):
    list_display = ['vchr_code','vchr_name','int_status']
    list_filter = ['int_status']
    search_fields = ['vchr_code','vchr_name']    
admin.site.register(Groups,GroupsAdmin)
