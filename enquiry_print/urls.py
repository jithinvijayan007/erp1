from django.conf.urls import url
from django.contrib.auth import views as auth_views
from enquiry_print.views import EnquiryDownload

urlpatterns = [
url(r'^download/$',EnquiryDownload.as_view(),name='download'),
]
