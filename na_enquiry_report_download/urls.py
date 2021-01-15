from django.conf.urls import url
from na_enquiry_report_download.views import NAReportDownload
urlpatterns=[
    url(r'^na_report_pdf$',NAReportDownload.as_view(),name='na_report_pdf'),

]
