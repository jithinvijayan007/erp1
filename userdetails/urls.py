from django.conf.urls import url
from userdetails.views import GenerateGuest,GroupsList,AddUsers,ViewUser,loginCheck,CompanyTypeahead,BrandTypeahead,UpdateUser,GroupTypeahead,UpdateUserPassword,ChangeUserStatus,BranchTypeahead,UserTypeahead,ReligionCasteList
from userdetails.views import AddUsers,ViewUser,loginCheck,CompanyTypeahead,BrandTypeahead,UpdateUser,GroupTypeahead,UpdateUserPassword,ChangeUserStatus,BranchTypeahead,UserTypeahead,AddUserBI,WebVersionGet,ChangePassword,AddEcomUser
urlpatterns = [
url(r'^adduser/',AddUsers.as_view(), name='adduser'),
url(r'^viewuser/',ViewUser.as_view(), name='viewuser'),
url(r'^login/',loginCheck.as_view(), name='login'),
url(r'^get_company_list/',CompanyTypeahead.as_view(), name='get_company_list'),
url(r'^get_brand_list/',BrandTypeahead.as_view(),name='get_brands_list'),
url(r'^get_user_list/',ViewUser.as_view(),name='get_user_list'),
url(r'^updateuserdata/',UpdateUser.as_view(), name='adduser'),
url(r'^get_group_list/',GroupTypeahead.as_view(),name='get_brands_list'),
url(r'^updateuserpassword/',UpdateUserPassword.as_view(), name='updateuserpassword'),
url(r'^get_branch_list/',BranchTypeahead.as_view(),name='get_branch_list'),
url(r'^changeuseractivestatus/',ChangeUserStatus.as_view(), name='changeuseractivestatus'),
url(r'^user_typeahead/',UserTypeahead.as_view(),name='user_typeahead'),
url(r'^group_list/',GroupsList.as_view(),name='group_list'),
url(r'^generate_guest/',GenerateGuest.as_view(),name='generate_guest'),
url(r'^user_add_api/',AddUserBI.as_view(),name='user_add_api'),
url(r'^url_web_version/',WebVersionGet.as_view(),name='WebVersionGet'),
url(r'^change_passward/',ChangePassword.as_view(),name='ChangePassword'),
url(r'^user_ecom_api/',AddEcomUser.as_view(),name='user_ecom_api'),
url(r'^religion_list/', ReligionCasteList.as_view(), name='religion_list'),
]
