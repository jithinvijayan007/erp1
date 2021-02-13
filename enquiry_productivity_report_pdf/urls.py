from enquiry_productivity_report_pdf.views import ProductivityReportDownload
# from enquiry_solar.views import ItemTypeahead,BrandTypeahead
from django.conf.urls import url

urlpatterns=[
    url(r'^enq_productivity_pdf/$',ProductivityReportDownload.as_view(),name='enq_productivity_pdf'),

]
