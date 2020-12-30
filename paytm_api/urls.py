from django.conf.urls import url
from .views import GetPaytmPoints,ValidateCustPoint,RedeemLoyaltyPoint,ReverseRedeemPoint

urlpatterns = [
    # url(r'^add_payment/$',AddPayment.as_view(),name='add_payment'),
    url(r'^getpaytmpoint',GetPaytmPoints.as_view(),name='getpaytmpoint'),
    url(r'^validate_cust_point',ValidateCustPoint.as_view(),name='validate_cust_point'),
    url(r'^redeem_loyalty_point',RedeemLoyaltyPoint.as_view(),name='redeem_loyalty_point'),
    url(r'^reverse_loyalty_point',ReverseRedeemPoint.as_view(),name='redeem_loyalty_point'),
    ]
