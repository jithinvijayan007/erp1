from django.contrib import admin
from zone.models import Zone
# Register your models here.


class ZoneAdmin(admin.ModelAdmin):
    list_display = ['vchr_code', 'vchr_name', 'bln_active']
    list_filter = ['bln_active','fk_company']
    search_fields = ['vchr_code', 'vchr_name', 'fk_state__vchr_name', 'fk_company__vchr_name']
admin.site.register(Zone, ZoneAdmin)
