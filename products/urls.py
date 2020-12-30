from django.conf.urls import url
from .views import AddProduct,GetCategoryData,ProductTypeHead


urlpatterns = [
    url(r'^add_product/$', AddProduct.as_view(), name='AddProduct'),
    url(r'^get_category/$', GetCategoryData.as_view(), name='GetCategoryData'),
    url(r'^product_typeahead/$', ProductTypeHead.as_view(), name='ProductTypeHead'),

]
