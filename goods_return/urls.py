from django.conf.urls import url,include
from goods_return.views import *
urlpatterns = [
    url(r'^goods_list/$', GoodsList.as_view(), name='GoodsList'),
    url(r'^imei_list/$', ImeiList.as_view(), name='ImeiList'),
    url(r'^batch_list/$', BatchList.as_view(), name='BatchList'),
    url(r'^goods_return_save/$', GoodsReturn.as_view(), name='GoodsReturn'),
 ]