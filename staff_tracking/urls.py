from django.conf.urls import url,include
from .views import User_Track_list
urlpatterns = [
    url(r'^list/$', User_Track_list.as_view(), name='user-track_list'),
    
 ]
