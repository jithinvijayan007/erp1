from django.conf.urls import url
from territory.views import  TerritoryList 
urlpatterns = [
    url(r'^list_territory/',TerritoryList.as_view(), name='list_territory'),
]
