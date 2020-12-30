from django.conf.urls import url
from quotation.views import ItemTypeaheadTax,AddQuotation,QuotationPrint,QuotationList
urlpatterns = [
    url(r'^item_tax_typeahead/$', ItemTypeaheadTax.as_view(), name='item_tax_typeahead'),
    url(r'^add/$', AddQuotation.as_view(), name='add'),
    url(r'^print/$', QuotationPrint.as_view(), name='print'),
    url(r'^list/$', QuotationList.as_view(), name='list'),

]
