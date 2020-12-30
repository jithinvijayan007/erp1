from django.conf.urls import url
from item_lookup_module.views import ItemLookupApi

urlpatterns = [
        url(r'^item_lookup/$', ItemLookupApi.as_view(), name='item_lookup'),
]
