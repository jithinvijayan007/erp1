from django.conf.urls import url
from .views import HierarchyApi,Levels,HierarchyGroup

urlpatterns = [
        url(r'^hierarchy',HierarchyApi.as_view(),name='add'),
        url(r'^levels',Levels.as_view(),name='levels'),
        url(r'^groups/',HierarchyGroup.as_view())
        # url(r'^list/',SidebarAPI.as_view(),name='sidebar'),
]
