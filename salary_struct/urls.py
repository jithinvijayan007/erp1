from django.conf.urls import url
from salary_struct.views import *
urlpatterns = [
    url(r'^add/',AddSalaryStruct.as_view(), name='add'),
    url(r'^list/',SalaryStructureList.as_view(), name='list'),
    url(r'^list_com/',ComponentsList.as_view(), name='list_com'),
    url(r'^pfandesi_struct/',PFandESIstruct.as_view(), name='pfandesi_struct'),
    url(r'^current_pfandesi/',CurrentESIandPF.as_view(), name='current_pfandesi'),
    url(r'^chenge_struct/',chengeStruct.as_view(), name='chenge_struct'),
]
