from django.conf.urls import url
from .views import CreditSettlement,CreditCustTypeahead,AddReceipt,ApproveReceipt,AddReceiptAPI,AddReceiptPending,PrintReceiptView,PrintReceiptView,ListReceiptForPayment,BankTypeahead,ReceiptList,ReceiptOrderList


urlpatterns = [
    url(r'^add/$', AddReceipt.as_view(), name='AddReceipt'),
    url(r'^approve/$', ApproveReceipt.as_view(), name='approve'),
    url(r'^add_receipt_api/', AddReceiptAPI.as_view(), name='add_receipt_api'),
    url(r'^add_receipt_pending/', AddReceiptPending.as_view(), name='add_receipt_pending'),
    url(r'^print_receipt/', PrintReceiptView.as_view(), name='print_receipt'),
    url(r'^banktypeahead/', BankTypeahead.as_view(), name='banktypeahead'),
    url(r'^receipt_list/', ListReceiptForPayment.as_view(), name='receipt_list'),
    url(r'^list_receipt/', ReceiptList.as_view(), name='list_receipt'),
    url(r'^receipt_order_list/', ReceiptOrderList.as_view(), name='receipt_order_list'),
    url(r'^creditCustTypeahead/', CreditCustTypeahead.as_view(), name='creditCustTypeahead'),
    url(r'^credit_settlement/', CreditSettlement.as_view(), name='credit_settlement'),
]
