from django.contrib import admin
from .models import GeneralizeReport
# Register your models here.
class GeneralizeReportAdmin(admin.ModelAdmin):
    list_display = ['vchr_report_name','vchr_url_name']
    search_fields = ['vchr_report_name','vchr_query','vchr_url_name',]
admin.site.register(GeneralizeReport,GeneralizeReportAdmin)
