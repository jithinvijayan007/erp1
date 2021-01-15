from django.conf.urls import url

from stock_app.views import SupplierTypeHead, AddStock, ListStock,ViewStock
urlpatterns = [
    url(r'^api_supplier/$', SupplierTypeHead.as_view(),name='api_supplier'),
    url(r'^add_stock/$', AddStock.as_view(),name='add_stock'),
    url(r'^stock_list/$', ListStock.as_view(),name='stock_list'),
    url(r'^stock_view/$', ViewStock.as_view(),name='stock_view'),
]
