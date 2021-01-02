from django.contrib import admin
from .models import *
# Register your models here.


class CountryAdmin(admin.ModelAdmin):
    list_display = ['vchr_code', 'vchr_name']
    search_fields = ['vchr_code', 'vchr_name']
admin.site.register(Country, CountryAdmin)


class StateAdmin(admin.ModelAdmin):
    list_display = ['vchr_code', 'vchr_name','fk_country']
    list_filter = ['fk_country']
    search_fields = ['vchr_code', 'vchr_name','fk_country__vchr_name']
admin.site.register(State, StateAdmin)


class DistrictAdmin(admin.ModelAdmin):
    list_display = ['vchr_code', 'vchr_name','fk_state']
    list_filter = ['fk_state']
    search_fields = ['vchr_code', 'vchr_name','fk_state__vchr_name']
admin.site.register(District, DistrictAdmin)


class PhysicalLocationAdmin(admin.ModelAdmin):
    list_display = ['vchr_physical_loc']
    search_fields = ['vchr_physical_loc']
admin.site.register(PhysicalLocation, PhysicalLocationAdmin)
