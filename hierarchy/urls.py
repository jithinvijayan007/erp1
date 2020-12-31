from django.conf.urls import url
from .views import HierarchyApi

urlpatterns = [
        url(r'^hierarchy',HierarchyApi.as_view(),name='add'),
        # url(r'^list/',SidebarAPI.as_view(),name='sidebar'),
]