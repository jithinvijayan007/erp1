from django.conf.urls import url
from .views import JournalView
urlpatterns = [
        url(r'^journal/',JournalView.as_view(), name='journal'),

]
