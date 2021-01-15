from django.conf.urls import url
from . import views
from priority import views0_2

urlpatterns = [
    url(r'^priority/$', views.PriorityAPIView.as_view(),name='priority'),
    url(r'^prioritydelete/$', views.PriorityDeleteAPIView.as_view(),name='prioritydelete'),

    # mobile app urlpatterns
    url(r'^v0.2/priority/$', views.PriorityAPIView.as_view(),name='priority'),
    url(r'^v0.2/prioritydelete/$', views.PriorityDeleteAPIView.as_view(),name='prioritydelete'),
]
