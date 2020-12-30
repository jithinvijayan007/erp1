from django.conf.urls import url,include
from specialsales.views import viewList,addInvoice,invoiceView
urlpatterns = [
    url(r'^view_list/$', viewList.as_view(), name='viewList'),
    url(r'^add_invoice/$', addInvoice.as_view(), name='addInvoice'),
    url(r'^invoice_view/$', invoiceView.as_view(), name='invoiceView'),
 ]