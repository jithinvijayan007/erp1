from django.conf.urls import url,include
from exchange_sales.views import ExchangeSales,ImeiTypeahead,BranchTypeaheadExchange
urlpatterns = [
    url(r'exchange_sales', ExchangeSales.as_view(), name='exchange_sales_list'),
    url(r'imei_typeahead', ImeiTypeahead.as_view(), name='imei_typeahead'),
    url(r'exchange_branch_typeahead', BranchTypeaheadExchange.as_view(), name='exchange_branch_typeahead'),
]
