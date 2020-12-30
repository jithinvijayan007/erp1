from django.conf.urls import url
from stock_prediction.views import StockPrediction,ItemTypeahead,BranchList

urlpatterns = [
        url(r'^stock_prediction/$', StockPrediction.as_view(), name='stock_prediction'),
        url(r'^itemTypeahead/$', ItemTypeahead.as_view(), name='itemTypeahead'),
        url(r'^branchlist/$', BranchList.as_view(), name='branchlist'),
]
