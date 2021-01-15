from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^source/$', views.SourceAPIView.as_view(),name='source'),
    url(r'^sourcedelete/$', views.SourceDeleteAPIView.as_view(),name='sourcedelete'),

    # mobile app urls
    url(r'^v0.2/source/$', views.SourceAPIView.as_view(),name='source'),
    url(r'^v0.2/sourcedelete/$', views.SourceDeleteAPIView.as_view(),name='sourcedelete'),
]
