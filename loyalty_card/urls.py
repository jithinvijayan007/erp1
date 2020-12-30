from django.conf.urls import url
from loyalty_card.views import LoyaltyCardAPIView,DeleteLoyaltyCardAPIView,OtpVarification,LoyaltyFooterApi

urlpatterns = [
    url(r'^loyalty_card/$',LoyaltyCardAPIView.as_view(),name='loyalty_card'),
    url(r'^loyalty_card_delete/$',DeleteLoyaltyCardAPIView.as_view(),name='loyalty_card_delete'),
    url(r'^otp_varification/$',OtpVarification.as_view(),name='otp_varification'),
    url(r'^footer_loyalty_point/$',LoyaltyFooterApi.as_view(),name='footer_loyalty_point'),
]
