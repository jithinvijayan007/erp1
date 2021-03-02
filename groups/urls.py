from django.conf.urls import url
from groups.views import UserGroupsAdd,GroupEditView,GroupListView,CategoryListNew2,GroupCreateViewNew,GroupDeleteView,GroupPermissionCreateView, SidebarAPI

urlpatterns = [
        url(r'^groupedit/',GroupEditView.as_view(),name='groupedit'),
        url(r'^grouplist/',GroupListView.as_view(),name='grouplist'),
        url(r'^add/$', UserGroupsAdd.as_view(), name='UserGroupsAdd'),
        url(r'^get_category_list/$', CategoryListNew2.as_view(), name='get_category_list'),
        url(r'^grouppadd/$', GroupCreateViewNew.as_view(), name='grouppadd'),
        url(r'^delete_group/$', GroupDeleteView.as_view(), name='GroupDelete'),
        url(r'^permission_add/$', GroupPermissionCreateView.as_view(), name='permission_add'),
        url(r'^api_sidebar/$', SidebarAPI.as_view(),name='api_sidebar'),


]
