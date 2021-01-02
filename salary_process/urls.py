from django.conf.urls import url
from salary_process.views import *


urlpatterns = [
            # url(r'^employees_list/', ListEmployee.as_view(), name = 'employees_list'),
            # url(r'^salary_process/', SalaryProcess.as_view(), name = 'salary_process'),
            # url(r'^add_variable_pay_lop/', VariablePayAPI.as_view(), name = 'add_variable_pay_lop'),
            # url(r'^salary_split/', SalaryProcessSplit.as_view(), name = 'salary_split'),
            # url(r'^salary_report/', SalaryReportView.as_view(), name = 'salary_report'),
            # url(r'^emp_salary_report/', EmpSalaryReportView.as_view(), name = 'emp_salary_report'),
            # url(r'^esi_report/', ESIReportView.as_view(), name = 'esi_report'),
            # url(r'^pf_report/', PFReportView.as_view(), name = 'pf_report'),
            # url(r'^wwf_report/', WWFReportView.as_view(), name = 'wwf_report'),
            # url(r'^pay_report/', SalaryPayReportView.as_view(), name = 'pay_report'),
            # url(r'^esi_upload_report/', ESIUploadReport.as_view(), name = 'esi_upload_report'),
            # url(r'^pf_upload_report/', PFUploadReport.as_view(), name = 'pf_upload_report'),
            # url(r'^wps_upload_report/', WPSReport.as_view(), name = 'wps_upload_report'),
            # url(r'^salary_process_approval/', SaleryProcessApproval.as_view(), name = 'approval'),
            # url(r'^hold_salary/', HoldSalary.as_view(), name = 'hold_salary'),
            # url(r'^release_salary/', ReleaseHoldSalary.as_view(), name = 'release_salary'),
            url(r'^wps_group/', WpsAPI.as_view(), name = 'wps_group'),
            # url(r'^pt_report/', ProfessionalTaxReport.as_view(), name = 'pt_report'),
            # url(r'^fixed_allowance/', FixedAllowanceAPI.as_view(), name = 'fixed_allowance'),
            # url(r'^payslipdownload/', PaySlipDownload.as_view(), name = 'payslipdownload'),
            ]
