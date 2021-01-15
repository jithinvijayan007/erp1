from django.conf.urls import url

from na_enquiry.views import SaveEnquiry,PendingEnquiryList,EnquiryList,EnquiryView
urlpatterns=[
    url(r'^add_na_enquiry/$',SaveEnquiry.as_view(),name='add_na_enquiry'),
    url(r'^pending_enquiry_list/$', PendingEnquiryList.as_view(),name='pending_enquiry_list'),
    url(r'^enquiry_list/$', EnquiryList.as_view(),name='enquiry_list'),
    url(r'^enquiry_view/$', EnquiryView.as_view(),name='enquiry_view'),
]
