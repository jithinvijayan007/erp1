from django.conf.urls import url
from django.contrib import admin
from pricelist.views import HistoryPriceList,ListPriceList,AddPriceList,DeletePriceList,EditPriceList,PriceListData

urlpatterns = [
    url(r'^historypricelist/$',HistoryPriceList.as_view(),name="historypricelist"),
    url(r'^listpricelist/$',ListPriceList.as_view(),name="listpricelist"),
    url(r'^addpricelist/$',AddPriceList.as_view(),name="addpricelist"),
    url(r'^deletepricelist/$',DeletePriceList.as_view(),name="deletepricelist"),
    url(r'^editpricelist/$',EditPriceList.as_view(),name="editpricelist"),
    url(r'^pricelistdata/$',PriceListData.as_view(),name="pricelistdata"),

]
