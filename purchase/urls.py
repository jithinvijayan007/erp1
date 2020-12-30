from django.conf.urls import url
from purchase.views import doc_num_generator1,ItemSpareTypeahead,DirectTransferApi,ImeiScan,BranchList,SupplierTypeahead,ItemTypeahead,PurchaseOrderRequest,PORequestListView,PurchaseOrderList,PurschaseApi,GnrListApi,PurchaseVoucherApi,BatchItemUniqueCheck

urlpatterns = [
        url(r'^branch_list/$', BranchList.as_view(), name='branch_list'),
        url(r'^supplier_typeahead/$', SupplierTypeahead.as_view(), name='supplier_typeahead'),
        url(r'^item_typeahead/$', ItemTypeahead.as_view(), name='item_typeahead'),

        url(r'^imei_scan/$', ImeiScan.as_view(), name='imei_scan'),
        url(r'^save_purchase_order/$', PurchaseOrderRequest.as_view(), name='save_purchase_order'),
        url(r'^list_purchase_order/$', PORequestListView.as_view(), name='list_purchase_order'),
        url(r'^list_order_num/$', PurchaseOrderList.as_view(), name='list_order_num'),
        url(r'^purchase_api/$', PurschaseApi.as_view(), name='purchase_api'),
        url(r'^purchase_list/$', GnrListApi.as_view(), name='purchase_list'),
        url(r'^purchase_voucher/$', PurchaseVoucherApi.as_view(), name='purchase_voucher'),
        url(r'^batch_unique_check/$', BatchItemUniqueCheck.as_view(), name='BatchItemUniqueCheck'),
        url(r'^direct_transfer/$', DirectTransferApi.as_view(), name='direct_transfer'),
        url(r'^item_spare_typeahead/$', ItemSpareTypeahead.as_view(), name='item_spare_typeahead'),
        # LG 27-06-2020
        url(r'^docnum/$',doc_num_generator1.as_view(),name= 'doc_num_generator1'),


    ]
