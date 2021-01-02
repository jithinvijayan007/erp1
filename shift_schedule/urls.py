from django.conf.urls import url
from shift_schedule.views import *

urlpatterns = [
    url(r'^add_shift/',AddShift.as_view(), name='add_shift'),
    url(r'^list_shift/',ListShift.as_view(), name='list_shift'),
    url(r'^shift_exemption/', ShiftExemptionAPI.as_view(), name='shift_exemption'),
    url(r'^shift_exemption_list/',ShiftExemptionList.as_view(), name='shift_exemption_list'),
]
