from django.conf.urls import url
from django.contrib import admin
from item_group.views import AddItemGroup,ItemGroupTypeHead,ListItemGroup

urlpatterns= [
    url(r'^additemgroup/$',AddItemGroup.as_view(),name="additemgroup"),
    url(r'^item_group_typeahead/$',ItemGroupTypeHead.as_view(),name="ItemGroupTypeHead"),
    url(r'^listitemgroup/$',ListItemGroup.as_view(),name="listitemgroup"),
]
