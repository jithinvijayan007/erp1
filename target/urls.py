from django.conf.urls import url

from target.views import Brands_List,Target_Save

from target.views import Monthlypercent
from target.views import Brands_List


urlpatterns = [
    url(r'^targetpercentage/$',Monthlypercent.as_view(),name='Monthlypercent'),
    url(r'^BrandsList/$', Brands_List.as_view(),name='BrandsList'),
    url(r'^Target_Save/$', Target_Save.as_view(),name='Target_Save'),
    url(r'^$',Monthlypercent.as_view(),name='Monthlypercent'),
]
