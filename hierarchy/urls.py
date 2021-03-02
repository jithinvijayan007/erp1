from django.conf.urls import url
from .views import HierarchyApi,Levels,HierarchyGroup,GetHierarchyGroup
from .views_hrms import ReportingHierarchy,HierarchyReport
from group_permissions.views import SidebarAPI

urlpatterns = [
        url(r'^hierarchy',HierarchyApi.as_view(),name='add'),
        url(r'^levels',Levels.as_view(),name='levels'),
        url(r'^groups/',HierarchyGroup.as_view()),
        url(r'^get_groups/',GetHierarchyGroup.as_view()),
        url(r'^list/',SidebarAPI.as_view(),name='sidebar'),
        url(r'^reporting_hierarchy/', ReportingHierarchy.as_view(), name='reporting_hierarchy'),
         url(r'^hierarchy_report/', HierarchyReport.as_view(), name='hierarchy_report'),
]
