from django.conf.urls import url
from reminder.views import AddReminder,ListReminder,UpdateReminder,ViewReminder,NotifyReminder,RemoveReminder,CalendarListReminder
from reminder import views01

urlpatterns=[
    url(r'^add_reminder/$', AddReminder.as_view(),name='add_reminder'),
    url(r'^list_reminder/$', ListReminder.as_view(),name='list_reminder'),
    url(r'^update_reminder/$', UpdateReminder.as_view(),name='update_reminder'),
    url(r'^view_reminder/$', ViewReminder.as_view(),name='view_reminder'),
    url(r'^notify_reminder/$', NotifyReminder.as_view(),name='notify_reminder'),
    url(r'^remove_reminder/$', RemoveReminder.as_view(),name='remove_reminder'),
    url(r'^calendar_list_reminder/$', CalendarListReminder.as_view(),name='calendar_list_reminder'),
    url(r'^v0.1/add_reminder/$',views01. AddReminder.as_view(),name='add_reminder'),
    url(r'^v0.1/list_reminder/$', views01.ListReminder.as_view(),name='list_reminder'),
    url(r'^v0.1/view_reminder/$', views01.ViewReminder.as_view(),name='view_reminder'),
    # url(r'^update_reminder/$', views01.UpdateReminder.as_view(),name='update_reminder'),
    # url(r'^notify_reminder/$', views01.NotifyReminder.as_view(),name='notify_reminder'),
    # url(r'^remove_reminder/$', views01.RemoveReminder.as_view(),name='remove_reminder'),



]
