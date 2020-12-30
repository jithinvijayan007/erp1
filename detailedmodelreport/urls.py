from django.conf.urls import url
from .views import DetailedModelWiseSalesReport
urlpatterns = [
    url(r'^detailed_model_wise_sales_report/$',DetailedModelWiseSalesReport.as_view(), name='DetailedModelWiseSalesReport')
    ]