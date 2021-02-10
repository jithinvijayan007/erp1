from django.conf.urls import url,include
from enquiry.views import Enquiry,ImeiCheckApi,StockNearbyBranchsApi,ItemAgingCheck,StockCheck,EcomStockCheck,CustomerTypeahead, MobileBranchReport
from enquiry.views0_1 import EnquiryList, EnquiryView
urlpatterns = [
    url(r'^get_stock', Enquiry.as_view(), name='get_stock',),
    url(r'^imei_check', ImeiCheckApi.as_view(), name='ImeiCheckApi',),
    url(r'^stock_nearby_branchs', StockNearbyBranchsApi.as_view(), name='StockNearbyBranchsApi',),
    url(r'^item_aging_check', ItemAgingCheck.as_view(), name='ItemAgingCheck',),
    url(r'^stock_check', StockCheck.as_view(), name='stock_check'),
    url(r'^ecom_stock_check', EcomStockCheck.as_view(), name='ecom_stock_check'),
    url(r'^get_customer_list/$', CustomerTypeahead.as_view(),name='customer_typeahead'),
    url(r'^list/$', EnquiryList.as_view(),name='enquiry_list'),
    url(r'^enquiry_view/$', EnquiryView.as_view(),name='enquiry_view'),
    url(r'^mobilebranchreport/$', MobileBranchReport.as_view(),name='mobilebranchreport'),
    # url(r'^branchReportMobileTable', MobileBranchReportTable.as_view(), name='branchReportMobileTable'),


]
