from django.conf.urls import url
from ledger_report import views

urlpatterns = [
    url(r'ledger_view',views.ledger_view.as_view(),name = 'ledger_view'),
    url(r'system_ac_typeahead',views.SystemACTypeahead.as_view(), name = 'SystemACTypeahead'),
    url(r'branch_wise_ledger',views.BranchWiseLedger.as_view(),name = 'branch_wise_ledger'),
]
