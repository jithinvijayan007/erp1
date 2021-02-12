from django.conf.urls import url
from dutyroster.views import *
urlpatterns = [
    url(r'^add/',AddWeekOff.as_view(), name='add'),
    url(r'^list_employees/',ListEmployee.as_view(), name='list_employees'),
    url(r'^view/',ViewWeekOff.as_view(), name='view'),
    url(r'^weekoff_approve/', WeekoffApprove.as_view(), name='weekoff_approve'),
]
