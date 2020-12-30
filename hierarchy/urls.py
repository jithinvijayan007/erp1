from django.conf.urls import url,include
from hierarchy.views import AddHierarchyApi


urlpatterns = [
    url(r'^add_hierarchy/$', AddHierarchyApi.as_view(), name='AddHierarchyApi'),
]
