from django.conf.urls import url
from staff_rating.views import StaffRatingView

urlpatterns = [
url(r'(?P<hash>\w+)/$', StaffRatingView.as_view(),name='StaffRatingView'),
]
