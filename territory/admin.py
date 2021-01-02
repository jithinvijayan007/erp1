from django.contrib import admin

# Register your models here.
from territory.models import Territory

class TerritoryAdmin(admin.ModelAdmin):
    list_display = ['vchr_code', 'vchr_name', 'fk_zone', 'bln_active']
    list_filter = ['bln_active', 'fk_company']
    search_fields = ['vchr_code', 'vchr_name', 'fk_company__vchr_name', 'fk_zone__vchr_name']
admin.site.register(Territory, TerritoryAdmin)
