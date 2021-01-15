from django.contrib import admin
from source.models import Source
# Register your models here.

class SourceAdmin(admin.ModelAdmin):
    list_display = ['vchr_source_name','bln_is_campaign','fk_category','bln_status']
    list_filter = ['bln_is_campaign','fk_category','bln_status']
    search_fields = ['vchr_source_name']
admin.site.register(Source,SourceAdmin)
