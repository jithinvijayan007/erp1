from django.conf.urls import url
from .views import DailySalesReport,CustomerTypeahead,DailyBranchStockReport,ClientOutstandingReport,DetailedSalesReport,gdotreport,RechargeProfitReport,ProductProfitReport,SmartChoiceReport,PurchaseReport,BranchStockHistory,SmartChoiceSaleReport
from .views2 import CreditSaleReport,StockTransferHistoryExport
from .views_bi import ServiceReportMobile
urlpatterns = [
    url(r'^daily_sales_report/$', DailySalesReport.as_view(), name='daily_sales_report'),
    url(r'^customer_typeahead/$', CustomerTypeahead.as_view(), name='customer_typeahead'),
    url(r'^daily_branch_stock_report/$',DailyBranchStockReport.as_view(), name='daily_branch_stock_report'),
    url(r'^client_outstanding_report/$',ClientOutstandingReport.as_view(), name='client_statement_report'),
    url(r'^detailed_sales_report/$',DetailedSalesReport.as_view(), name='DetailedSalesReport'),
    url(r'^stock_history/$',BranchStockHistory.as_view(), name='stock_history'),
    url(r'^purchase_report/$',PurchaseReport.as_view(), name='PurchaseReport'),
    url(r'^gdot_report/$',gdotreport.as_view(), name='gdotreport'),
    url(r'^recharge_profit_report/$',RechargeProfitReport.as_view(), name='RechargeProfitReport'),
    url(r'^product_profit_report/$',ProductProfitReport.as_view(), name='ProductProfitReport'),
    url(r'^smart_choice_report/$',SmartChoiceReport.as_view(), name='SmartChoiceReport'),
    url(r'^smart_choice_sale_report/$',SmartChoiceSaleReport.as_view(), name='SmartChoiceSalesReport'),
    url(r'^credit_sale_report/$',CreditSaleReport.as_view(), name='credit_sale_report'),
    url(r'^stock_transfer_history/$',StockTransferHistoryExport.as_view(), name='stock_transfer_history'),
    # url(r'^service_wise_mobile/$','afsdf', name='service_wise_mobile'),
    url(r'^service_wise_mobile/$',ServiceReportMobile.as_view(),name='service_wise_mobile'),

    #url(r'^purchase_report/$',PurchaseReport.as_view(), name='PurchaseReport'),

    ]
