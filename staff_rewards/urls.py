from django.conf.urls import url
from .views import RewardPaidSave,AddReward,GetRewardDetails,AreaSearch,RewardsList,StaffRewardList,StaffRewardList,StaffByBranch,RewardPaidList,RewardPaidListDownload


urlpatterns = [
        url(r'^get_reward/$',GetRewardDetails.as_view(),name='get_reward'),
        url(r'^paid_reward/$',RewardPaidSave.as_view(),name='paid_reward'),
        url(r'^add_reward/$',AddReward.as_view(),name='add_reward'),
        url(r'area_search/$',AreaSearch.as_view(),name='area_search'),
        url(r'^rewards_list/$',RewardsList.as_view(),name='rewards_list'),
        url(r'^staff_rewards_list/$',StaffRewardList.as_view(),name='staff_rewards_list'),
        url(r'^staff_by_branch/$',StaffByBranch.as_view(),name='staff_rewards_list'),
        url(r'^reward_paid_list/$',RewardPaidList.as_view(),name='reward_paid_list'),
        url(r'^reward_paid_download/$',RewardPaidListDownload.as_view(),name='reward_paid_download'),
        ]
