from django.conf.urls import url
from finance_enquiry.views import UpdateFinanceEligibility,UpdateFinanceEnquiry,AddFinanceCustomerAPIView,ListSchemeByItem

urlpatterns = [
    url(r'^updateeligibility/$', UpdateFinanceEligibility.as_view(),name='updateeligibility'),
    url(r'^updatefinance/$', UpdateFinanceEnquiry.as_view(),name='updatefinance'),
    url(r'^addfinancecustomer/$',AddFinanceCustomerAPIView.as_view(),name='addfinancecustomer'),
    url(r'^scheme_by_item/$',ListSchemeByItem.as_view(),name='scheme_by_item'),
]
