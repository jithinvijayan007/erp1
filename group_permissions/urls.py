from django.conf.urls import url
from group_permissions.views import SidebarAPI

urlpatterns = [
        url(r'^sidebar/',SidebarAPI.as_view(),name='sidebar'),
]