from django.conf.urls import url
from salary_components.views import AddSalaryComponents

urlpatterns = [
    url(r'^add_salary_components/',AddSalaryComponents.as_view(), name='salary_components'),
]
