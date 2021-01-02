from django.conf.urls import url
from zone.views import ZoneList
urlpatterns = [
    url(r'^list_zone/',ZoneList.as_view(), name='list_zone'),
]
