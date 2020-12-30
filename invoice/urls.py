from django.conf.urls import url
from invoice.views import CreditSaleAPI,BajajDeliveryImageAPI,SchemeList,CompleteApprovalMissing,ServiceCenterAndGDPFollowup,ServiceAddAssigned,TheftFollowup,AddFollowUpAPI,ListBallGame,AddAmountOfferAPI,SalesList,AddSalesAPI,AddInvoice,ItemAdvanceFilter,ApplyCoupon,InvoicePrintApi,InvoiceList,InvoiceListPrintApi,AddInvoiceJIO,Banklist,ReturnItemInvoice,GdpNormal,DeliveryChallanPrinf,BajajOnlineAPI,BajajApproveRejectAPI,SaveReturnedSales,EcomSalesCancelApi
# ,EInvoiceAPI
from receipt.views import ListReceipt

urlpatterns = [
        url(r'^sales_list/',SalesList.as_view(),name='sales_list'),
        url(r'^add_sales_api/',AddSalesAPI.as_view(),name='add_sales_api'),
        url(r'^add_invoice/',AddInvoice.as_view(),name='add_invoice'),
        url(r'^item_filter/',ItemAdvanceFilter.as_view(),name='item_filter'),
        url(r'^apply_coupon/',ApplyCoupon.as_view(),name='apply_coupon'),
        url(r'^invoice_print/',InvoicePrintApi.as_view(),name='invoice_print'),
        url(r'^receipt_list/',ListReceipt.as_view(),name='receipt_list'),
        url(r'^invoice_list/',InvoiceList.as_view(),name='invoice_list'),
        url(r'^invoice_print_list/',InvoiceListPrintApi.as_view(),name='invoice_print_list'),
        url(r'^add_invoice_jio/',AddInvoiceJIO.as_view(),name='add_invoice_jio'),
        url(r'^bank_typeahead/',Banklist.as_view(),name='bank_typeahead'),
        url(r'^add_amount_offer_api/',AddAmountOfferAPI.as_view(),name='add_amount_offer'),
        url(r'^list_ball_game/',ListBallGame.as_view(),name='list_ball_game'),
        url(r'^add_followup/',AddFollowUpAPI.as_view(),name='add_followup'),
        url(r'^theft_followup/',TheftFollowup.as_view(),name='theft_followup'),
        url(r'^service_add_assigned/',ServiceAddAssigned.as_view(),name='service_delivery_assigned'),
        url(r'^service_center_followup/',ServiceCenterAndGDPFollowup.as_view(),name='service_center_followup'),
        url(r'^complete_approval_missing/',CompleteApprovalMissing.as_view(),name='complete_approval_missing'),
        url(r'^scheme_typeahead/',SchemeList.as_view(),name='list_scheme'),
        url(r'^return_item_invoice/',ReturnItemInvoice.as_view(),name='return_item_invoice'),
        url(r'^gdp_normal/',GdpNormal.as_view(),name='gdp_normal'),

        url(r'^deliverychallan/',DeliveryChallanPrinf.as_view(),name='deliverychallan'),
        url(r'^bajaj_online/',BajajOnlineAPI.as_view(),name='bajaj_online'),
        url(r'^save_returned_sales/',SaveReturnedSales.as_view(),name='save_returned_sales'),
        url(r'^bajajapprovereject/',BajajApproveRejectAPI.as_view(),name='bajajapprovereject'),
        url(r'^bajajdeliveryimage/',BajajDeliveryImageAPI.as_view(),name='bajajdeliveryimage'),
        url(r'^credit_settlement/',CreditSaleAPI.as_view(),name='credit_settlement'),
        url(r'^cancel_ecom/',EcomSalesCancelApi.as_view(),name='cancel_ecom'),
        # url(r'^e_invoice/',EInvoiceAPI.as_view(),name='e_invoice'),



    ]
