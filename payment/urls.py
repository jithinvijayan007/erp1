from django.conf.urls import url
from payment.views import StaffTypeahead,AddPayment,ExpenseTypeahead,ViewPayment,BankList,DenominationList,ExpenseList,AddIncentiveApi,PaymentList

urlpatterns = [
    url(r'^add_payment/$',AddPayment.as_view(),name='add_payment'),
    url(r'^staff_typeahead/$',StaffTypeahead.as_view(),name='staff_typeahead'),
    url(r'^expenses_typeahead/$',ExpenseTypeahead.as_view(),name='expenses_typeahead'),
    url(r'^view_payment/$',ViewPayment.as_view(),name='view_payment'),
    url(r'^bank_list/$',BankList.as_view(),name='bank_list'),
    url(r'^denomination_list/$',DenominationList.as_view(),name='denomination_list'),
    url(r'^expenses_list/$',ExpenseList.as_view(),name='expenses_list'),
    url(r'^addincentive/$',AddIncentiveApi.as_view(),name='addincentive'),
    url(r'^payment_list/$',PaymentList.as_view(),name='payment_list'),
    ]
