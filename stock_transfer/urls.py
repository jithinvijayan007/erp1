from django.conf.urls import url,include
from stock_transfer.views import ImeiList,BatchList,saveStockTransfer,CourierData,CourierVehicle

urlpatterns = [
    url(r'^imei_list/$', ImeiList.as_view(), name='ImeiList'),
    url(r'^batch_list/$', BatchList.as_view(), name='BatchList'),
    url(r'^courier_data/$', CourierData.as_view(), name='CourierData'),
    url(r'^courier_vehicle/$', CourierVehicle.as_view(), name='CourierVehicle'),
    url(r'^save_stock_transfer/$', saveStockTransfer.as_view(), name='saveStockTransfer'),
 ]