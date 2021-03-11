from django.conf.urls import url
from .views import AddRewardApi,RewardsList,GetRewardDetails


urlpatterns = [
        url(r'^add_reward/$',AddRewardApi.as_view(),name='add_reward'),
        url(r'^reward_list/$',RewardsList.as_view(),name='reward_list'),
        url(r'^get_reward/$',GetRewardDetails.as_view(),name='get_reward'),
       
        ]
