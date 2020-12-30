from django.conf.urls import url
from tool_settings.views import ToolsApi,BranchListApi,AddDeductApi
urlpatterns = [
url(r'^tool_api/',ToolsApi.as_view(), name='tool_api'),
url(r'^branchlist/',BranchListApi.as_view(), name='branchlist'),
url(r'^add_deduct/',AddDeductApi.as_view(), name='AddDeductApi'),
]
