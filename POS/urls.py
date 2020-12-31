"""POS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from django.conf import settings
from django.views.static import serve
from rest_framework_jwt.views import obtain_jwt_token,verify_jwt_token,refresh_jwt_token

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^company/',include('company.urls', namespace='company')),
    url(r'^brands/',include('brands.urls', namespace='brands')),
    url(r'^branch/',include('branch.urls', namespace='branch')),
    url(r'^category/',include('category.urls',namespace='category')),
    url(r'^user/',include('userdetails.urls',namespace='user')),
    url(r'^products/',include('products.urls',namespace='products')),
    url(r'^itemgroup/',include('item_group.urls',namespace='itemgroup')),
    url(r'^itemcategory/',include('item_category.urls',namespace='item_category')),
    url(r'^supplier/',include('supplier.urls',namespace="supplier")),
    url(r'^dealer/',include('dealer.urls',namespace="dealer")),
    url(r'^purchase/',include('purchase.urls',namespace="purchase")),
    url(r'^invoice/',include('invoice.urls',namespace='invoice')),
    url(r'^internalstock/',include('internal_stock.urls',namespace='internalstock')),
    url(r'^branch_stock/',include('branch_stock.urls',namespace='branch_stock')),
    url(r'^states/',include('states.urls',namespace="states")),
    url(r'^enquiry/',include('enquiry.urls',namespace="enquiry")),
    url(r'^coupon/',include('coupon.urls',namespace="coupon")),
    url(r'^terms/',include('terms.urls',namespace="terms")),
    url(r'^pricelist/',include('pricelist.urls',namespace="pricelist")),
    url(r'^customer/',include('customer.urls',namespace="customer")),
    url(r'^loyaltycard/',include('loyalty_card.urls',namespace="loyaltycard")),
    url(r'^company_permissions/',include('company_permissions.urls',namespace="company_permissions")),
    url(r'^user_groups/',include('groups.urls',namespace="user_groups")),
    url(r'^stock_prediction/',include('stock_prediction.urls',namespace="stock_prediction")),
    url(r'^add_combo/',include('add_combo.urls',namespace="add_combo")),
    url(r'^dayclosure/',include('day_closure.urls',namespace="day_closure")),
    url(r'^group_permissions/',include('group_permissions.urls',namespace="group_permissions")),
    url(r'^item_lookup/',include('item_lookup_module.urls',namespace="item_lookup")),
    url(r'^case_closure/',include('case_closure.urls',namespace="case_closure")),
    url(r'^salesreturn/',include('sales_return.urls',namespace="salesreturn")),
    url(r'^receipt/',include('receipt.urls',namespace="receipt")),
    url(r'^payment/',include('payment.urls',namespace="payment")),
    url(r'^reports/',include('reports.urls',namespace="reports")),
    url(r'^tool_settings/',include('tool_settings.urls',namespace="tool_settings")),
    url(r'^quotation/',include('quotation.urls',namespace="quotation")),

    url(r'^accounts_map/',include('accounts_map.urls',namespace="accounts_map")),
    url(r'^exchange_sales/',include('exchange_sales.urls',namespace="exchange_sales")),
    url(r'^ledger/',include('ledger_report.urls',namespace = "ledger")),
    url(r'^transaction/',include('transaction.urls',namespace = "transaction")),
    url(r'^detailed_model/',include('detailedmodelreport.urls',namespace = "detailedmodelreport")),
    url(r'^emi_report/',include('emi_report.urls',namespace = "emi_report")),
    url(r'^scheme/',include('schema.urls',namespace = "scheme")),
    url(r'^special_sales/',include('specialsales.urls',namespace = "specialsales")),
    url(r'^stock_transfer/',include('stock_transfer.urls',namespace = "stocktransfer")),
    url(r'^goods_return/',include('goods_return.urls',namespace = "goodsreturn")),
    url(r'^staff_tracking/',include('staff_tracking.urls',namespace = "staff_tracking")),
    url(r'^paytm_api/',include('paytm_api.urls',namespace = "paytm_api")),
    url(r'^hierarchy/',include('hierarchy.urls',namespace="hierarchy")),

    #--------------------------------------------
    url(r'^api-token-auth/', obtain_jwt_token),
    url(r'^api-token-verify/', verify_jwt_token),
    url(r'^api-token-refresh/', refresh_jwt_token),


]

if settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', serve,
            {'document_root': settings.MEDIA_ROOT, }),
    ]
