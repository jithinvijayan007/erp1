from django.conf.urls import url
from loan.views import *


urlpatterns = [
            url(r'^request_loan/',LoanRequestAPIView.as_view(), name='request_loan'),
            url(r'^loan_requested/',LoanRequestedAPIView.as_view(), name='loan_requested'),
            url(r'^loan_report/',LoanReport.as_view(), name='loan_report'),
            url(r'^edit_loan/',EditLoan.as_view(), name='edit_loan'),
            ]
