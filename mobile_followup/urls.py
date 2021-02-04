from django.conf.urls import url

from mobile_followup.views import AddFollowup,FollowupHistory,FollowupApproveList,FollowupUpdate
urlpatterns = [
    url(r'^add_followup/$', AddFollowup.as_view(),name='add_followup'),
    url(r'^followup_history/$', FollowupHistory.as_view(),name='followup_history'),
    url(r'^followup_approve_list/$', FollowupApproveList.as_view(),name='followup_approve_list'),
    url(r'^followup_update/$', FollowupUpdate.as_view(),name='followup_update'),

]
