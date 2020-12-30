from django.conf.urls import url,include
from sales_return.views import GetDetails,GetCustomer,SalesReturnList,SalesReturnView,GetReturnDetails,ImeiCheckView
urlpatterns = [
    url(r'^get_details/$', GetDetails.as_view(), name='get_details'),
    url(r'^get_details_customer/$', GetCustomer.as_view(), name='get_details_customer'),
    url(r'^sales_return_list/$', SalesReturnList.as_view(), name='sales_return_list'),
    url(r'^sales_return_view/$', SalesReturnView.as_view(), name='sales_return_view'),

    url(r'^get_return_details/$', GetReturnDetails.as_view(), name='get_return_details'),
    url(r'^check_imei/$', ImeiCheckView.as_view(), name='check_imei'),
 ]
