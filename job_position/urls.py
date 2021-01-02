from django.conf.urls import url
from job_position.views import AddJobPosition,JobPositionFilter
urlpatterns = [
    url(r'^add_job/',AddJobPosition.as_view(), name='add_job'),
    url(r'^list/',JobPositionFilter.as_view(), name='list'),

]
