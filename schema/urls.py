from django.conf.urls import url,include
from schema.views import addScheme,addSchemefrombi
urlpatterns = [
    url(r'^addscheme/$', addScheme.as_view(), name='addScheme'),
    url(r'^addschemebi/$', addSchemefrombi.as_view(), name='addSchemefrombi'),
 ]
