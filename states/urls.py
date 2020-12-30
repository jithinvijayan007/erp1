from django.conf.urls import url,include
from states.views import StatesTypeahead, DistrictTypeahead, LocationTypeahead

urlpatterns = [
    url(r'^states_typeahead/$', StatesTypeahead.as_view(), name='states_typeahead'),
    url(r'^states_typehead/$', StatesTypeahead.as_view(), name='states_typeahead'),
    url(r'^district_typeahead/$', DistrictTypeahead.as_view(), name='district_typeahead'),
    url(r'^location_typeahead/$', LocationTypeahead.as_view(), name='location_typeahead'),
]
