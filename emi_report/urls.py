from django.conf.urls import url
from emi_report.views import *

urlpatterns = [
    url(r'^lst_credit_debit/',ListCraditDebit.as_view(),name='lst_credit_debit')
]
