from django.conf.urls import url
from supplier.views import AddSupplier,ListSupplier,ViewSupplier,EditSupplier,CategoryTypeahead,TaxclassTypeahead,DeleteSupplier,SupplierHistory,SupplierTypeHead

urlpatterns = [
    url(r'^add_supplier/$', AddSupplier.as_view(), name='add_supplier'),
    url(r'^list_supplier/$', ListSupplier.as_view(), name='list_supplier'),
    url(r'^get_suplier_by_id/$', ViewSupplier.as_view(), name='view_supplier'),
    url(r'^update_supplier/$', EditSupplier.as_view(), name='update_supplier'),
    url(r'^get_category_list/$', CategoryTypeahead.as_view(), name='get_category_list'),
    url(r'^get_tax_class_list/$', TaxclassTypeahead.as_view(), name='get_tax_class_list'),
    url(r'^delete_supplier/$', DeleteSupplier.as_view(), name='delete_supplier'),
    url(r'^supplier_history/$', SupplierHistory.as_view(), name='supplier_history'),
    url(r'^supplier_typeahead/$', SupplierTypeHead.as_view(), name='SupplierTypeHead'),

]
