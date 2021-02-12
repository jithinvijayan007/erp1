from django.conf.urls import url
from group_level.views import GetGroupforLevel,SaveGroupLevel

urlpatterns = [
    url(r'^get_group_for_level/$', GetGroupforLevel.as_view(),name='get_group_for_level'),
    url(r'^save_group_level/$', SaveGroupLevel.as_view(),name='save_group_level'),
]
