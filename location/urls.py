from django.conf.urls import url
from location.views import StatesList ,PhysicalLocationList,CountryList,StateListNew,DistrictList
urlpatterns = [
    url(r'^list_states/',StatesList.as_view(), name='list_states'),
    url(r'^list_loc/',PhysicalLocationList.as_view(), name='physical_loc'),
    url(r'^country_list/',CountryList.as_view(), name='country_list'),
    url(r'^state_list/',StateListNew.as_view(), name='state_list'),
    url(r'^district_list/',DistrictList.as_view(), name='district_list'),

]
