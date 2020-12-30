from django.conf.urls import url
from .views import AddType,AddTerms,ListTerms,ViewTerms,EditTerms

urlpatterns = [
url(r'^add_type/$',AddType.as_view(),name="add_type"),
url(r'^add_terms/$',AddTerms.as_view(),name="add_terms"),
url(r'^list_terms/$',ListTerms.as_view(),name="list_terms"),
url(r'^view_terms/$',ViewTerms.as_view(),name="view_terms"),
url(r'^edit_terms/$',EditTerms.as_view(),name="edit_terms")
]
