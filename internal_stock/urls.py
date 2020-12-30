from django.conf.urls import url,include
from internal_stock.views import GetBranchDetails,AddRequest,GetRequestList,RequestView,ApproveRequest,GetdetailsByRequestNum,AddStockTransfer,\
CancelRequest,GetTransferList,TransferView,TransferSave,SaveAcknowledge,GetImeiList,ApproveMail,StockAgeReport,PurchaseRequestGenerateApi,\
SupplierTypeahead,SalesReportPurchase,ImeiBatchScan,CourierVehicleList,EwayBillGeneration
urlpatterns = [
    url(r'^get_details/$', GetBranchDetails.as_view(), name='get_branch'),
    url(r'^addrequest/$', AddRequest.as_view(), name='addrequest'),
    url(r'^getrequestlist/$', GetRequestList.as_view(), name='getrequestlist'),
    url(r'^requestview/$', RequestView.as_view(), name='requestview'),
    url(r'^approverequest/$', ApproveRequest.as_view(), name='approverequest'),
    url(r'^getdetailsbynumber/$', GetdetailsByRequestNum.as_view(), name='getdetailsbynumber'),
    url(r'^addstocktransfer/$', AddStockTransfer.as_view(), name='addstocktransfer'),
    url(r'^cancelrequest/$', CancelRequest.as_view(), name='cancelrequest'),
    url(r'^gettransferlist/$', GetTransferList.as_view(), name='gettransferlist'),
    url(r'^transferview/$', TransferView.as_view(), name='transferview'),
    url(r'^transfersave/$', TransferSave.as_view(), name='transfersave'),
    url(r'^acknowledgesave/$', SaveAcknowledge.as_view(), name='acknowledgesave'),
    url(r'^getimei/$', GetImeiList.as_view(), name='getimei'),
    url(r'^approve_mail/(?P<hash>\w+)/$', ApproveMail.as_view(),name='approve_mail'),
    url(r'^stock_age/$', StockAgeReport.as_view(), name='stock_age'),
    url(r'^purchase_request_list/$', PurchaseRequestGenerateApi.as_view(), name='purchase_request_list'),
    url(r'^suppliertypeahead/$', SupplierTypeahead.as_view(), name='suppliertypeahead'),
    url(r'^sales_report_purchase/$', SalesReportPurchase.as_view(), name='sales_report_purchase'),
    url(r'^imei_batch_scan/$', ImeiBatchScan.as_view(), name='imei_batch_scan'),
 url(r'^courier_vehicle_typehead/$', CourierVehicleList.as_view(), name='courier_vehicle_typehead'),
 url(r'^eway_bill/$', EwayBillGeneration.as_view(), name='eway_billl'),
 url(r'^imei_check/$', EwayBillGeneration.as_view(), name='imei_check'),



]
