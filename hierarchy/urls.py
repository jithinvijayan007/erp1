from django.conf.urls import url
from .views import HierarchyApi,Levels

urlpatterns = [
        url(r'^hierarchy',HierarchyApi.as_view(),name='add'),
        url(r'^levels',Levels.as_view(),name='levels'),
        
        # url(r'^list/',SidebarAPI.as_view(),name='sidebar'),
]
