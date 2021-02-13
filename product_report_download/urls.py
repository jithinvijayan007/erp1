from django.conf.urls import url
from product_report_download.views import ProductReportDOwnload

urlpatterns = [
    url(r'^$',ProductReportDOwnload.as_view(),name='productreportdownload'),
]
