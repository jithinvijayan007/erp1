from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models.functions import Concat
from django.db.models import F, Q, Value, Case, When, CharField, Sum, Count
from loan.models import *
from datetime import datetime, date, timedelta
import calendar
from django.db import transaction
from HRMS_python import ins_logger
from sqlalchemy.orm.session import sessionmaker
from HRMS_python.dftosql import Savedftosql
from user_model.models import UserDetails
from django.contrib.auth.models import User as AuthUser
from salary_advance.models import SalaryAdvance
from hierarchy.models import HierarchyLevel
import traceback
import sys, os
import traceback
from aldjemy.core import get_engine
from sqlalchemy import and_, func , cast, Date, case, literal_column, or_, MetaData, desc, Integer, text
from os import path
from django.conf import settings
import pandas as pd
from pandas import ExcelWriter
# Create your views here.

Connection = sessionmaker()
sqlalobj = Savedftosql('','')
alengine = sqlalobj.engine
metadata = MetaData()
metadata.reflect(bind=alengine)
Connection.configure(bind=alengine)
engine = get_engine()
#
# def Session():
#     _Session = sessionmaker(bind = alengine)
#     return _Session()
# AuthUserSA = AuthUser.sa
# LoanRequestSA = LoanRequest.sa
# LoanDetailsSA = LoanDetails.sa
# UserDetailsSA = UserDetails.sa
# SalaryAdvanceSA =SalaryAdvance.sa


class LoanRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            with transaction.atomic():
                dbl_amount = request.data.get('intAmount')
                int_tenure = request.data.get('intTenure')
                int_month = request.data.get('intMonthYear').split('-')[0]
                int_year = request.data.get('intMonthYear').split('-')[1]
                bln_mob = request.data.get('blnMob')
                if not request.data.get('blnHRLoan'):
                    if request.user.is_superuser:
                        return Response({'status':0, 'message': 'User Not Allowed'})
                    if LoanDetails.objects.filter(fk_request__fk_employee_id=int_emp,int_month=int_month, int_year=int_year, fk_request__int_status__gte=0, fk_request__bln_mob_loan = bln_mob):
                        return Response({'status':0, 'message': 'Already Requested'})

                    ins_request = LoanRequest.objects.create(fk_employee = request.user.userdetails,
                                                dbl_loan_amt = dbl_amount,
                                                int_tenure = int_tenure,
                                                int_month = int_month,
                                                txt_remarks = request.data.get('strRemark'),
                                                int_year = int_year,
                                                bln_mob_loan = bln_mob,
                                                fk_created_id = request.user.id)
                else:

                    dbl_monthly_amt = request.data.get('intMonthlyAmt')
                    int_emp = request.data.get('intEmployeeId')
                    if LoanDetails.objects.filter(fk_request__fk_employee_id=int_emp,int_month=int_month, int_year=int_year, fk_request__int_status__gte=0, fk_request__bln_mob_loan = bln_mob):
                        return Response({'status':0, 'message': 'Already Requested'})
                    ins_request = LoanRequest.objects.create(fk_employee_id = int_emp,
                                                dbl_loan_amt = dbl_amount,
                                                int_tenure = int_tenure,
                                                int_month = int_month,
                                                txt_remarks = request.data.get('strRemark'),
                                                int_year = int_year,
                                                bln_mob_loan = bln_mob,
                                                int_status=1,
                                                fk_created_id = request.user.id)
                    dat_start = datetime.strptime('01-'+str(ins_request.int_month)+'-'+str(ins_request.int_year),"%d-%m-%Y")
                    dbl_monthly_amt = round(ins_request.dbl_loan_amt/ins_request.int_tenure, 2)
                    for i in range(0,ins_request.int_tenure):
                        LoanDetails.objects.create(fk_request_id = ins_request.pk_bint_id,
                                                    dbl_amount = dbl_monthly_amt,
                                                    int_month = dat_start.month,
                                                    int_year = dat_start.year,
                                                    fk_created_id = request.user.id)
                        dat_start = dat_start + timedelta(days=calendar.monthrange(dat_start.year, dat_start.month)[1])
            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})

    def get(self,request):
        try:
            if request.GET.get('strType') == 'REQUEST':
                ins_request = list(LoanRequest.objects.filter(int_status=0).annotate(intId = F('pk_bint_id'), strEMPName = Concat('fk_employee__first_name', Value(' '), 'fk_employee__last_name'), dblAmount = F('dbl_loan_amt'), intTenure = F('int_tenure'), intMonth = F('int_month'), intYear = F('int_year'),strRemark = F('txt_remarks')).values('intId','strEMPName','dblAmount','intTenure','intMonth','intYear','bln_mob_loan','strRemark'))
            elif request.GET.get('strType') == 'REQUESTED' and not request.user.is_superuser and request.user.userdetails.fk_department.vchr_name.upper() in ['HR & ADMIN']:
                ins_request = list(LoanRequest.objects.annotate(intId = F('pk_bint_id'), strEMPName = Concat('fk_employee__first_name', Value(' '), 'fk_employee__last_name'), dblAmount = F('dbl_loan_amt'), intTenure = F('int_tenure'),strRemark = F('txt_remarks') ,intMonth = F('int_month'), intYear = F('int_year'), strStatus = Case(When(int_status = -1,then = Value('Rejected')), When(int_status = 0, then = Value('Pending')),When(int_status = 1, then = Value('Approved')), output_field=CharField())).values('intId','strEMPName','dblAmount','intTenure','intMonth','intYear','strStatus','bln_mob_loan','bln_mob_loan','strRemark'))
            elif request.GET.get('strType') == 'REQUESTED' and not request.user.is_superuser:
                ins_request = list(LoanRequest.objects.filter(fk_employee=request.user.userdetails).annotate(intId = F('pk_bint_id'), strEMPName = Concat('fk_employee__first_name', Value(' '), 'fk_employee__last_name'), dblAmount = F('dbl_loan_amt'), intTenure = F('int_tenure'), intMonth = F('int_month'), strRemark = F('txt_remarks'),intYear = F('int_year'), strStatus = Case(When(int_status = -1,then = Value('Rejected')), When(int_status = 0, then = Value('Pending')),When(int_status = 1, then = Value('Approved')), output_field=CharField())).values('intId','strEMPName','dblAmount','intTenure','intMonth','intYear','strStatus','bln_mob_loan','bln_mob_loan','strRemark'))
            else:
                return Response({'status':1, 'data':[]})
            return Response({'status':1, 'data':ins_request})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})

    def put(self,request):
        try:
            str_type = request.data.get('strType')
            if not request.user.is_superuser and not request.user.userdetails.fk_desig.vchr_name.upper() in('SR. HR MANAGER'):
                return Response({'status':0,'message':'No Permission'})
            int_id = request.data.get('intLoanId')
            if str_type  != "SALARY ADVANCE":
                if request.data.get('intStatus')==1:
                    ins_request = LoanRequest.objects.filter(pk_bint_id=int_id).values('pk_bint_id', 'int_tenure', 'int_month', 'int_year', 'dbl_loan_amt')[0]
                    dat_start = datetime.strptime('01-'+str(ins_request['int_month'])+'-'+str(ins_request['int_year']),"%d-%m-%Y")
                    dbl_monthly_amt = round(ins_request['dbl_loan_amt']/ins_request['int_tenure'], 2)
                    for i in range(0,ins_request['int_tenure']):
                        LoanDetails.objects.create(fk_request_id = ins_request['pk_bint_id'],
                                                    dbl_amount = dbl_monthly_amt,
                                                    int_month = dat_start.month,
                                                    int_year = dat_start.year,
                                                    fk_created_id = request.user.id)
                        dat_start = dat_start + timedelta(days=calendar.monthrange(dat_start.year, dat_start.month)[1])
                    LoanRequest.objects.filter(pk_bint_id=int_id).update(int_status=1,fk_updated_id = request.user.id)
                else:
                    LoanRequest.objects.filter(pk_bint_id=int_id).update(int_status=-1,txt_remarks=request.data.get('strRemarks'),fk_updated_id = request.user.id)
            else:
                if request.data.get('intStatus')==1:
                    int_status = 2
                else:
                    int_status = -1
                SalaryAdvance.objects.filter(pk_bint_id = int_id).update(int_status = int_status,
                                                                       vchr_remarks = request.data.get("strRemarks"),
                                                                       dat_approval = datetime.now(),
                                                                       fk_approved_id = request.user.id)

            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


class LoanRequestedAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            int_emp_id = request.data.get('intId')
            int_month = int(request.data.get('intMonthYear').split('-')[0])
            int_year = int(request.data.get('intMonthYear').split('-')[1])
            int_user_id  = request.user.userdetails.user_ptr_id
            int_desig_id = request.user.userdetails.fk_desig_id
            int_dpt_name = request.user.userdetails.fk_department.vchr_name
            ins_hierarchy = HierarchyLevel.objects.filter(int_status=1, fk_reporting_to=int_desig_id).values('fk_designation_id')
            if int_month < 12:
                int_next_month = int_month + 1
                int_next_year = int_year
            else:
                int_next_month = 1
                int_next_year = int_year + 1
            lst_desig = []
            for item in ins_hierarchy:
                lst_desig.append(item['fk_designation_id'])
            lst_desig.append(request.user.userdetails.fk_desig_id)
            conn = engine.connect()
            if int_dpt_name == 'HR & ADMIN':
                if int_emp_id:

                    str_query = " SELECT ud.user_ptr_id,ud.vchr_employee_code, CONCAT(TRIM(au.first_name), ' ', CASE WHEN ud.vchr_middle_name IS NOT NULL THEN CONCAT(TRIM(ud.vchr_middle_name), ' ', TRIM(au.last_name)) ELSE TRIM(au.last_name) END) AS str_emp_name, CASE WHEN sldtl.str_type = 1 THEN 'SALARY ADVANCE' WHEN sldtl.str_type = 2 THEN 'MOBILE LOAN' WHEN sldtl.str_type = 3 THEN 'WORK LOAN' END AS str_type, sldtl.int_type_id, CASE WHEN sldtl.int_status = -2 THEN 'REJECTED' WHEN sldtl.int_status = -1 THEN 'EXCLUDED' WHEN sldtl.int_status = 0 THEN 'PENDING' WHEN sldtl.int_status = 1 THEN 'APPROVED' WHEN sldtl.int_status = 2 THEN 'PROCESSED' END AS str_status, sldtl.dbl_amount,sldtl.vchr_purpose FROM auth_user au JOIN user_details ud ON ud.user_ptr_id = au.id and ud.user_ptr_id = {2} JOIN ((SELECT fk_employee_id AS int_emp_id, 1 AS str_type, pk_bint_id AS int_type_id, CASE WHEN int_status = -1 THEN -2 WHEN int_status = 0 THEN -1 WHEN int_status = 1 THEN 0 WHEN int_status = 2 THEN 1 WHEN int_status = 3 THEN 2 END AS int_status, dbl_amount AS dbl_amount,vchr_purpose FROM salary_advance WHERE bln_active = TRUE AND int_month = {0} AND int_year = {1}) UNION (SELECT lrqst.fk_employee_id AS int_emp_id, CASE WHEN lrqst.bln_mob_loan = TRUE THEN 2 WHEN lrqst.bln_mob_loan = FALSE OR lrqst.bln_mob_loan IS NULL THEN 3 END AS str_type, CASE WHEN lrqst.int_status != 1 THEN lrqst.pk_bint_id WHEN lrqst.int_status = 1 AND ldtls.pk_bint_id IS NOT NULL THEN ldtls.pk_bint_id END int_type_id, CASE WHEN lrqst.int_status = -1 THEN -2 WHEN lrqst.int_status = 0 THEN 0 WHEN lrqst.int_status = 1 AND ldtls.int_status = 0 THEN 1 WHEN ldtls.int_status = -1 THEN -1 WHEN ldtls.int_status = 1 THEN 2 END AS int_status, CASE WHEN lrqst.int_status != 1 THEN lrqst.dbl_loan_amt WHEN lrqst.int_status = 1 THEN ldtls.dbl_amount END AS dbl_amount,lrqst.txt_remarks as vchr_purpose FROM loan_request lrqst FULL JOIN loan_details ldtls ON ldtls.fk_request_id = lrqst.pk_bint_id AND ldtls.int_status != -2 WHERE ((lrqst.int_status != 1 AND lrqst.int_month = {0} AND lrqst.int_year = {1}) OR (lrqst.int_status = 1 AND ldtls.int_month = {0} AND ldtls.int_year = {1})) AND lrqst.int_status != -1)) AS sldtl ON sldtl.int_emp_id = ud.user_ptr_id ORDER BY TRIM(TRIM(TRIM(ud.vchr_employee_code,'MYGC-'),'MYGE-'),'MYGT-')::INT"
                    rst_data = conn.execute(str_query.format(int_month,int_year,int_emp_id)).fetchall()

                else:
                    str_query = "SELECT ud.user_ptr_id,ud.vchr_employee_code, CONCAT(TRIM(au.first_name), ' ', CASE WHEN ud.vchr_middle_name IS NOT NULL THEN CONCAT(TRIM(ud.vchr_middle_name), ' ', TRIM(au.last_name)) ELSE TRIM(au.last_name) END) AS str_emp_name, CASE WHEN sldtl.str_type = 1 THEN 'SALARY ADVANCE' WHEN sldtl.str_type = 2 THEN 'MOBILE LOAN' WHEN sldtl.str_type = 3 THEN 'WORK LOAN' END AS str_type, sldtl.int_type_id, CASE WHEN sldtl.int_status = -2 THEN 'REJECTED' WHEN sldtl.int_status = -1 THEN 'EXCLUDED' WHEN sldtl.int_status = 0 THEN 'PENDING' WHEN sldtl.int_status = 1 THEN 'APPROVED' WHEN sldtl.int_status = 2 THEN 'PROCESSED' END AS str_status, sldtl.dbl_amount,sldtl.vchr_purpose FROM auth_user au JOIN user_details ud ON ud.user_ptr_id = au.id JOIN ((SELECT fk_employee_id AS int_emp_id, 1 AS str_type, pk_bint_id AS int_type_id, CASE WHEN int_status = -1 THEN -2 WHEN int_status = 0 THEN -1 WHEN int_status = 1 THEN 0 WHEN int_status = 2 THEN 1 WHEN int_status = 3 THEN 2 END AS int_status, dbl_amount AS dbl_amount,vchr_purpose FROM salary_advance WHERE bln_active = TRUE AND int_month = {0} AND int_year = {1}) UNION (SELECT lrqst.fk_employee_id AS int_emp_id, CASE WHEN lrqst.bln_mob_loan = TRUE THEN 2 WHEN lrqst.bln_mob_loan = FALSE OR lrqst.bln_mob_loan IS NULL THEN 3 END AS str_type, CASE WHEN lrqst.int_status != 1 THEN lrqst.pk_bint_id WHEN lrqst.int_status = 1 AND ldtls.pk_bint_id IS NOT NULL THEN ldtls.pk_bint_id END int_type_id, CASE WHEN lrqst.int_status = -1 THEN -2 WHEN lrqst.int_status = 0 THEN 0 WHEN lrqst.int_status = 1 AND ldtls.int_status = 0 THEN 1 WHEN ldtls.int_status = -1 THEN -1 WHEN ldtls.int_status = 1 THEN 2 END AS int_status, CASE WHEN lrqst.int_status != 1 THEN lrqst.dbl_loan_amt WHEN lrqst.int_status = 1 THEN ldtls.dbl_amount END AS dbl_amount,lrqst.txt_remarks as vchr_purpose FROM loan_request lrqst FULL JOIN loan_details ldtls ON ldtls.fk_request_id = lrqst.pk_bint_id AND ldtls.int_status != -2 WHERE ((lrqst.int_status != 1 AND lrqst.int_month = {0} AND lrqst.int_year = {1}) OR (lrqst.int_status = 1 AND ldtls.int_month = {0} AND ldtls.int_year = {1})) AND lrqst.int_status != -1)) AS sldtl ON sldtl.int_emp_id = ud.user_ptr_id ORDER BY TRIM(TRIM(TRIM(ud.vchr_employee_code,'MYGC-'),'MYGE-'),'MYGT-')::INT"
                    rst_data = conn.execute(str_query.format(int_month,int_year)).fetchall()

            else:
                str_query = "SELECT ud.user_ptr_id,ud.vchr_employee_code, CONCAT(TRIM(au.first_name), ' ', CASE WHEN ud.vchr_middle_name IS NOT NULL THEN CONCAT(TRIM(ud.vchr_middle_name), ' ', TRIM(au.last_name)) ELSE TRIM(au.last_name) END) AS str_emp_name, CASE WHEN sldtl.str_type = 1 THEN 'SALARY ADVANCE' WHEN sldtl.str_type = 2 THEN 'MOBILE LOAN' WHEN sldtl.str_type = 3 THEN 'WORK LOAN' END AS str_type, sldtl.int_type_id, CASE WHEN sldtl.int_status = -2 THEN 'REJECTED' WHEN sldtl.int_status = -1 THEN 'EXCLUDED' WHEN sldtl.int_status = 0 THEN 'PENDING' WHEN sldtl.int_status = 1 THEN 'APPROVED' WHEN sldtl.int_status = 2 THEN 'PROCESSED' END AS str_status, sldtl.dbl_amount,sldtl.vchr_purpose FROM auth_user au JOIN user_details ud ON ud.user_ptr_id = au.id and ud.fk_desig_id in ({2}) JOIN ((SELECT fk_employee_id AS int_emp_id, 1 AS str_type, pk_bint_id AS int_type_id, CASE WHEN int_status = -1 THEN -2 WHEN int_status = 0 THEN -1 WHEN int_status = 1 THEN 0 WHEN int_status = 2 THEN 1 WHEN int_status = 3 THEN 2 END AS int_status, dbl_amount AS dbl_amount,vchr_purpose FROM salary_advance WHERE bln_active = TRUE AND int_month = {0} AND int_year = {1}) UNION (SELECT lrqst.fk_employee_id AS int_emp_id, CASE WHEN lrqst.bln_mob_loan = TRUE THEN 2 WHEN lrqst.bln_mob_loan = FALSE OR lrqst.bln_mob_loan IS NULL THEN 3 END AS str_type, CASE WHEN lrqst.int_status != 1 THEN lrqst.pk_bint_id WHEN lrqst.int_status = 1 AND ldtls.pk_bint_id IS NOT NULL THEN ldtls.pk_bint_id END int_type_id, CASE WHEN lrqst.int_status = -1 THEN -2 WHEN lrqst.int_status = 0 THEN 0 WHEN lrqst.int_status = 1 AND ldtls.int_status = 0 THEN 1 WHEN ldtls.int_status = -1 THEN -1 WHEN ldtls.int_status = 1 THEN 2 END AS int_status, CASE WHEN lrqst.int_status != 1 THEN lrqst.dbl_loan_amt WHEN lrqst.int_status = 1 THEN ldtls.dbl_amount END AS dbl_amount,lrqst.txt_remarks as vchr_purpose FROM loan_request lrqst FULL JOIN loan_details ldtls ON ldtls.fk_request_id = lrqst.pk_bint_id AND ldtls.int_status != -2 WHERE ((lrqst.int_status != 1 AND lrqst.int_month = {0} AND lrqst.int_year = {1}) OR (lrqst.int_status = 1 AND ldtls.int_month = {0} AND ldtls.int_year = {1})) AND lrqst.int_status != -1)) AS sldtl ON sldtl.int_emp_id = ud.user_ptr_id ORDER BY TRIM(TRIM(TRIM(ud.vchr_employee_code,'MYGC-'),'MYGE-'),'MYGT-')::INT"
                rst_data = conn.execute(str_query.format(int_month,int_year,str(lst_desig)[1:-1])).fetchall()
            lst_data = []
            for data in rst_data:
                dct_data = {}
                dct_data['strEmpCode'] = data.vchr_employee_code
                dct_data['strEMPName'] = data.str_emp_name
                dct_data['strType'] = data.str_type
                dct_data['intId'] = data.int_type_id
                dct_data['strStatus'] = data.str_status
                dct_data['dblAmount'] = int(data.dbl_amount)
                dct_data['strRemark'] = data.vchr_purpose
                dct_data['dblBlnc'] = None
                dct_data['dblNext'] = None
                dct_data['intEmpId'] = data.user_ptr_id
                if data.str_type == 'SALARY ADVANCE':
                    if  data.str_status != 'REJECTED':
                        ins_blnc = SalaryAdvance.objects.filter(fk_employee_id = data.user_ptr_id,int_status = 2,bln_active = True).aggregate(Sum('dbl_amount'))
                        ins_next = SalaryAdvance.objects.filter(int_month = int_next_month,int_year = int_next_year,fk_employee_id = data.user_ptr_id,int_status = 2,bln_active = True).values('pk_bint_id','dbl_amount','int_month')
                        if ins_blnc['dbl_amount__sum']:
                            dct_data['dblBlnc'] = int(ins_blnc['dbl_amount__sum'])
                        if ins_next:
                            dct_data['dblNext'] = ins_next[0]['dbl_amount']

                else:
                    if data.str_status != 'REJECTED':
                        ins_request_id = LoanDetails.objects.filter(pk_bint_id = data.int_type_id ).values('fk_request_id').first()
                        ins_blnc = LoanDetails.objects.filter(fk_request_id = ins_request_id['fk_request_id'],int_status = 0).aggregate(Sum('dbl_amount'))
                        ins_next = LoanDetails.objects.filter(int_month = int_next_month,int_year = int_next_year,fk_request_id = ins_request_id['fk_request_id'],int_status = 0).values('dbl_amount')
                        if ins_blnc['dbl_amount__sum']:
                            dct_data['dblBlnc'] = int(ins_blnc['dbl_amount__sum'])
                        if ins_next:
                            dct_data['dblNext'] = ins_next[0]['dbl_amount']
                lst_data.append(dct_data)
            conn.close()
            return Response({'status':1, 'data':lst_data})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})

    def put(self,request):
        try:
            """ Edit and Exclude salary advance and loan in a month"""
            if not request.user.userdetails.fk_department.vchr_name=='HR & ADMIN':
                return Response({'status':0,'message':'No Permission'})
            if request.data.get('intMonthYear'):
                int_month = int(request.data.get('intMonthYear').split('-')[0])
                int_year = int(request.data.get('intMonthYear').split('-')[1])
            int_requst_id = request.data.get('intId')
            flt_chenge_amount = request.data.get('fltAmount')
            str_type = request.data.get('strType')
            ins_current = LoanDetails.objects.filter(pk_bint_id = int_requst_id).values('pk_bint_id','int_month','dbl_amount','fk_request_id','txt_remarks')
            ins_last =  LoanDetails.objects.filter(Q(int_year__gt=int_year, int_month__lte=int_month)|Q(int_year__gte=int_year, int_month__gte=int_month), fk_request_id = ins_current[0]['fk_request_id'], int_status = 0).values('pk_bint_id','int_month','dbl_amount','int_year','int_status').order_by('-int_year', '-int_month')
            dct_tenuer_amt = LoanDetails.objects.filter(fk_request_id = ins_current[0]['fk_request_id']).exclude(int_status=-1).values('dbl_amount').annotate(flt_tenuer_amt=Count('dbl_amount')).order_by('-flt_tenuer_amt').first()
            ins_pending_loan = LoanDetails.objects.filter(Q(int_year__gt=int_year, int_month__lte=int_month)|Q(int_year__gte=int_year, int_month__gte=int_month),fk_request_id = ins_current[0]['fk_request_id'], int_status=0).values('fk_request_id').annotate(flt_pending=Sum('dbl_amount')).values('flt_pending')
            if flt_chenge_amount:
                if float(flt_chenge_amount) > ins_pending_loan[0]['flt_pending']:
                    return Response({'status':0,'message':'Amount should not be greater than balance amount'})

            with transaction.atomic():
                if str_type in ('WORK LOAN','MOBILE LOAN'):
                    if flt_chenge_amount:

                        """ Edit current month amount """
                        int_blnc_amount = ins_current[0]['dbl_amount'] - float(flt_chenge_amount)
                        if ins_last.first()['int_month'] == 12:
                            month = 1
                            year = ins_last.first()['int_year']+1
                        else:
                            month = ins_last.first()['int_month']+1
                            year = ins_last.first()['int_year']
                        if int_blnc_amount > 0:
                            LoanDetails.objects.filter(pk_bint_id = int_requst_id).update(dbl_amount = flt_chenge_amount, txt_remarks=request.data.get('strRemarks'))
                            flt_last_amt = ins_last.first()['dbl_amount']+int_blnc_amount

                            if flt_last_amt > dct_tenuer_amt['dbl_amount']:
                                LoanDetails.objects.filter(pk_bint_id = ins_last.first()['pk_bint_id']).update(dbl_amount = dct_tenuer_amt['dbl_amount'],fk_updated_id = request.user.id)
                                while flt_last_amt>0:
                                    flt_last_amt = flt_last_amt-dct_tenuer_amt['dbl_amount']
                                    if flt_last_amt >= dct_tenuer_amt['dbl_amount']:
                                        LoanDetails.objects.create(fk_request_id = ins_current[0]['fk_request_id'],
                                                                    int_month = month,
                                                                    int_year = year,
                                                                    dbl_amount = dct_tenuer_amt['dbl_amount'],
                                                                    dat_created = datetime.now(),
                                                                    int_status = 0,
                                                                    fk_created_id = request.user.id)
                                    elif flt_last_amt > 0:
                                        LoanDetails.objects.create(fk_request_id = ins_current[0]['fk_request_id'],
                                                                    int_month = month,
                                                                    int_year = year,
                                                                    dbl_amount = flt_last_amt,
                                                                    dat_created = datetime.now(),
                                                                    int_status = 0,
                                                                    fk_created_id = request.user.id)
                                    if month == 12:
                                        month = 1
                                        year += 1
                                    else:
                                         month += 1
                            else:
                                LoanDetails.objects.filter(pk_bint_id = ins_last.first()['pk_bint_id']).update(dbl_amount = flt_last_amt,fk_updated_id = request.user.id)
                        else:
                            if ins_pending_loan[0]['flt_pending'] < float(flt_chenge_amount):
                                return Response({'status':0,'reason':'Invalid Amount'})
                            flt_amt = float(flt_chenge_amount) - ins_current[0]['dbl_amount']
                            LoanDetails.objects.filter(pk_bint_id = int_requst_id).update(dbl_amount = flt_chenge_amount)
                            for dct_data in ins_last:
                                if dct_data['int_month'] == int_month and dct_data['int_year'] == int_year:
                                    break
                                elif flt_amt >= dct_tenuer_amt['dbl_amount'] or dct_data['dbl_amount']-flt_amt < 0:
                                    LoanDetails.objects.filter(pk_bint_id = dct_data['pk_bint_id']).update(int_status = -2)
                                elif flt_amt>0 and flt_amt < dct_tenuer_amt['dbl_amount']:
                                    LoanDetails.objects.filter(pk_bint_id = dct_data['pk_bint_id']).update(dbl_amount = dct_data['dbl_amount']-flt_amt)
                                else:
                                    break
                                flt_amt = flt_amt-dct_data['dbl_amount']
                    else:

                        """ exclude current month amount """

                        if ins_last and ins_current:
                            if ins_last.first()['int_month'] == 12:
                                month = 1
                                year = ins_last.first()['int_year']+1
                            else:
                                month = ins_last.first()['int_month']+1
                                year = ins_last.first()['int_year']
                            if ins_last.first()['dbl_amount'] and ins_current[0]['dbl_amount']:
                                LoanDetails.objects.filter(pk_bint_id = int_requst_id,int_month = int_month,int_year = int_year).update(int_status = -1,dbl_amount = 0,fk_updated_id = request.user.id,txt_remarks =  request.data.get('strRemarks'))
                                if ins_last.first()['dbl_amount'] == ins_current[0]['dbl_amount']:

                                    LoanDetails.objects.create(fk_request_id = ins_current[0]['fk_request_id'],
                                                                int_month = month,
                                                                int_year = year,
                                                                dbl_amount = ins_current[0]['dbl_amount'],
                                                                dat_created = datetime.now(),
                                                                int_status = 0,
                                                                txt_remarks = ins_current[0]['txt_remarks'],
                                                                fk_created_id = request.user.id)
                                else:
                                    LoanDetails.objects.filter(pk_bint_id = ins_last.first()['pk_bint_id']).update(dbl_amount = ins_current[0]['dbl_amount'],fk_updated_id = request.user.id)
                                    LoanDetails.objects.create(fk_request_id = ins_current[0]['fk_request_id'],
                                                                int_month = month,
                                                                int_year = year,
                                                                dbl_amount = ins_last.first()['dbl_amount'],
                                                                dat_created = datetime.now(),
                                                                int_status = 0,
                                                                txt_remarks = ins_current[0]['txt_remarks'],
                                                                fk_created_id = request.user.id)
                else:
                    if request.data.get('fltAmount'):
                        flt_adnc = float(request.data.get('fltAmount'))
                    else:
                        flt_adnc = 0
                    ins_crnt_amnt = SalaryAdvance.objects.filter(pk_bint_id = int_requst_id,int_month = int_month,int_year = int_year,bln_active=True,int_status = 2).values('dbl_amount','fk_employee_id')
                    ins_total = SalaryAdvance.objects.filter(fk_employee_id = ins_crnt_amnt[0]['fk_employee_id'],bln_active=True,int_status = 2).values('dbl_amount','int_month','int_year').order_by('-pk_bint_id')
                    if ins_crnt_amnt[0]['fk_employee_id']:
                        int_emp_id = ins_crnt_amnt[0]['fk_employee_id']
                    else:
                        int_emp_id = None
                    if ins_total[0]['int_month'] == 12:
                        month = 1
                        year = ins_total[0]['int_year']+1
                    else:
                        month = ins_total[0]['int_month']+1
                        year = ins_total[0]['int_year']
                    if flt_adnc:

                        """ edit salary advance """

                        if flt_adnc < ins_crnt_amnt[0]['dbl_amount']:
                            int_blnc_amount = ins_crnt_amnt[0]['dbl_amount'] - flt_adnc
                            SalaryAdvance.objects.create(fk_employee_id = int_emp_id,
                                                    int_month = month,
                                                    int_year = year,
                                                    dbl_amount = int_blnc_amount,
                                                    int_status = 2,
                                                    bln_active = True,
                                                    fk_approved_id =  request.user.userdetails.user_ptr_id,
                                                    dat_approval = datetime.now(),
                                                    dat_created = datetime.now(),
                                                    vchr_purpose = request.data.get('strRemark'))
                        SalaryAdvance.objects.filter(pk_bint_id = int_requst_id,int_month = int_month,int_year = int_year,bln_active=True,int_status = 2).update(dbl_amount = flt_adnc,dat_updated = datetime.now())
                    else:

                        """ exclude salary advance """
                        int_amount = ins_crnt_amnt[0]['dbl_amount']
                        SalaryAdvance.objects.filter(pk_bint_id = int_requst_id).update(int_status = -1,bln_active = False)
                        SalaryAdvance.objects.create(fk_employee_id =int_emp_id,
                                                    int_month = month,
                                                    int_year = year,
                                                    dbl_amount = int_amount,
                                                    int_status = 2,
                                                    bln_active = True,
                                                    fk_approved_id =  request.user.userdetails.user_ptr_id,
                                                    dat_approval = datetime.now(),
                                                    dat_created = datetime.now(),
                                                    vchr_purpose = request.data.get('strRemark'))



            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})
    def patch(self,request):
        try:
            str_type = request.data.get('strType')
            int_requst_id = request.data.get('intId')
            lst_data = []
            if str_type in ('WORK LOAN','MOBILE LOAN'):
                ins_id = LoanDetails.objects.filter(pk_bint_id = int_requst_id).values('fk_request_id')
                ins_request_data = LoanRequest.objects.filter(pk_bint_id = ins_id[0]['fk_request_id']).exclude(int_status=-2).annotate(full_name=Concat('fk_employee__first_name', Value(' '), Case(When(fk_employee__vchr_middle_name = None, then=F('fk_employee__last_name')), default=Concat('fk_employee__vchr_middle_name', Value(' '), 'fk_employee__last_name'),
                output_field = CharField()), output_field = CharField())).values('int_month','int_year','fk_employee__fk_department__vchr_name','fk_employee__vchr_employee_code','fk_employee__fk_branch__vchr_name','dbl_loan_amt','full_name','txt_remarks').order_by('int_year', 'int_month')
                ins_details = LoanDetails.objects.filter(fk_request_id = ins_id[0]['fk_request_id']).exclude(int_status=-2).values('dbl_amount','int_month','int_year','int_status','txt_remarks').order_by('int_year', 'int_month')
                ins_pending_loan = LoanDetails.objects.filter(fk_request_id = ins_id[0]['fk_request_id'], int_status=0).values('fk_request_id').annotate(flt_pending=Sum('dbl_amount')).values('flt_pending')
                dct_details ={}
                dct_details['strEmpName'] = ins_request_data[0]['full_name']
                dct_details['strEmpCode'] = ins_request_data[0]['fk_employee__vchr_employee_code']
                dct_details['intStartMonth'] = ins_request_data[0]['int_month']
                dct_details['strStartMonth'] = datetime(2000, ins_request_data[0]['int_month'], 1, 0, 0).strftime('%b')
                dct_details['intStartYear'] = ins_request_data[0]['int_year']
                dct_details['strDepartment'] = ins_request_data[0]['fk_employee__fk_department__vchr_name']
                dct_details['strBranch'] = ins_request_data[0]['fk_employee__fk_branch__vchr_name']
                dct_details['intTotalAmount'] = ins_request_data[0]['dbl_loan_amt']
                dct_details['intpendingAmount'] = ins_pending_loan[0]['flt_pending'] if ins_pending_loan else 0
                dct_details['strReamrks'] = ins_request_data[0]['txt_remarks']
                for data in ins_details:
                    dct_data ={}
                    dct_data['intMonth'] = data['int_month']
                    dct_data['strMonth'] = datetime(2000, data['int_month'], 1, 0, 0).strftime('%b')
                    dct_data['intYear'] = data['int_year']
                    dct_data['intAmount'] = data['dbl_amount']
                    if data['int_status'] == 1:
                        dct_data['strStatus'] = 'Processed'
                    elif data['int_status'] == -1:
                        dct_data['strStatus'] = 'Excluded'
                    else:
                        dct_data['strStatus'] = 'Pending'
                    dct_data['strRemarks'] = data['txt_remarks']
                    lst_data.append(dct_data)
            else:
                ins_id = SalaryAdvance.objects.filter(pk_bint_id = int_requst_id).values('fk_employee_id').order_by('int_year', 'int_month')
                ins_details = SalaryAdvance.objects.filter(fk_employee_id = ins_id[0]['fk_employee_id']).exclude(int_status__in = [-1]).annotate(full_name=Concat('fk_employee__first_name', Value(' '), Case(When(fk_employee__vchr_middle_name = None, then=F('fk_employee__last_name')), default=Concat('fk_employee__vchr_middle_name', Value(' '), 'fk_employee__last_name'), output_field = CharField()), output_field = CharField())).values('full_name','dbl_amount','int_month','int_year','int_status','fk_employee__fk_branch__vchr_name','fk_employee__fk_department__vchr_name','fk_employee__vchr_employee_code','bln_active','vchr_purpose').order_by('int_year', 'int_month')
                ins_pending_loan = SalaryAdvance.objects.filter(fk_employee_id = ins_id[0]['fk_employee_id'], int_status__in=[1, 2]).values('fk_employee_id').annotate(flt_pending=Sum('dbl_amount')).values('flt_pending')
                dct_details ={}
                dct_details['strEmpName'] = ins_details[0]['full_name']
                dct_details['strEmpCode'] = ins_details[0]['fk_employee__vchr_employee_code']
                dct_details['strDepartment'] = ins_details[0]['fk_employee__fk_department__vchr_name']
                dct_details['intStartMonth'] = ins_details[0]['int_month']
                dct_details['strStartMonth'] = datetime(2000, ins_details[0]['int_month'], 1, 0, 0).strftime('%b')
                dct_details['strBranch'] = ins_details[0]['fk_employee__fk_branch__vchr_name']
                dct_details['intStartYear'] = ins_details[0]['int_year']
                dct_details['intTotalAmount'] = ins_pending_loan[0]['flt_pending'] if ins_pending_loan else 0
                dct_details['intpendingAmount'] = ins_pending_loan[0]['flt_pending'] if ins_pending_loan else 0
                for data in ins_details:
                    dct_data ={}
                    dct_data['intAmount'] = data['dbl_amount']
                    dct_data['strRemarks'] = data['vchr_purpose']
                    dct_data['intMonth'] = data['int_month']
                    dct_data['strMonth'] = datetime(2000, data['int_month'], 1, 0, 0).strftime('%b')
                    dct_data['intYear'] = data['int_year']
                    if data['int_status'] == 3:
                        dct_data['strStatus'] = 'Processed'
                    elif data['int_status'] == 0:
                        dct_data['strStatus'] = 'Excluded'
                    else:
                        dct_data['strStatus'] = 'Pending'

                    lst_data.append(dct_data)
            return Response({'status':1,'lstData':lst_data,'dctDetails':dct_details})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno),'message':'Something went wrong'})


class LoanReport(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        try:
            conn = engine.connect()
            int_month = int(request.GET.get('intMonthYear').split('-')[0])
            int_year = int(request.GET.get('intMonthYear').split('-')[1])
            str_query = "SELECT ud.user_ptr_id,ud.vchr_employee_code, CONCAT(TRIM(au.first_name), ' ', CASE WHEN ud.vchr_middle_name IS NOT NULL THEN CONCAT(TRIM(ud.vchr_middle_name), ' ', TRIM(au.last_name)) ELSE TRIM(au.last_name) END) AS str_emp_name,rqst.dbl_loan_amt, rqst.int_tenure,rqst.txt_remarks,dtls.dbl_amount AS int_current,rqst.pk_bint_id FROM  auth_user au JOIN user_details ud ON ud.user_ptr_id = au.id JOIN loan_request AS rqst ON ud.user_ptr_id = rqst.fk_employee_id AND rqst.int_status = 1 JOIN loan_details AS dtls ON dtls.fk_request_id = rqst.pk_bint_id AND dtls.int_status in (0,1) AND dtls.int_month = {0} AND dtls.int_year = {1} GROUP BY ud.user_ptr_id,ud.vchr_employee_code,au.first_name,au.last_name,rqst.dbl_loan_amt,rqst.int_tenure,rqst.dat_created,rqst.txt_remarks,dtls.dbl_amount,rqst.pk_bint_id"
            rst_data = conn.execute(str_query.format(int_month,int_year)).fetchall()
            lst_data = []
            for data in rst_data:
                dct_data = {}
                dct_data['strEMPName'] = data.str_emp_name
                dct_data['strEMPCode'] = data.vchr_employee_code
                dct_data['intIssuedAmount'] = int(data.dbl_loan_amt)
                dct_data['strPurpose'] = data.txt_remarks
                dct_data['intNumOfEMI'] = data.int_tenure
                dct_data['intCurrent'] = data.int_current
                ins_blnc = LoanDetails.objects.filter(fk_request_id = data.pk_bint_id,int_status = 0).aggregate(Sum('dbl_amount'))
                date_created = LoanDetails.objects.filter(fk_request_id = data.pk_bint_id).values('dat_created').first()
                dct_data['intPending'] = 0
                if ins_blnc['dbl_amount__sum']:
                    dct_data['intPending'] = int(ins_blnc['dbl_amount__sum'])
                dct_data['dateApproved'] = datetime.strftime(date_created['dat_created'],'%d-%m-%Y')
                lst_data.append(dct_data)
            if lst_data == []:
                conn.close()
                return Response({'status':1,'lstData':lst_data,'data':''})

            file_name = 'LoanReport/loan_report' + datetime.strftime(date.today(), "%d-%m-%Y") + '.xlsx'
            if not path.exists(settings.MEDIA_ROOT + '/LoanReport/'):
                os.mkdir(settings.MEDIA_ROOT + '/LoanReport/')
            writer = pd.ExcelWriter(settings.MEDIA_ROOT + '/' + file_name, engine ='xlsxwriter')
            workbook = writer.book
            head_style = workbook.add_format({'font_size':11, 'bold':1, 'align': 'center','border':1,'border_color':'#000000'})
            head_style.set_pattern(1)
            head_style.set_bg_color('#bfbfbf')
            head_style.set_align('vcenter')

            row_style = workbook.add_format({'font_size':11, 'text_wrap': True})
            row_style.set_align('vcenter')
            worksheet = workbook.add_worksheet()

            title_style = workbook.add_format({'font_size':14, 'bold':1, 'align': 'center'})
            title_style.set_align('vcenter')
            title_style.set_pattern(1)
            title_style.set_bg_color('#ffe0cc')
            worksheet.merge_range('A1+:I1', 'Loan Report', title_style)
            worksheet.set_row(0, 30)
            worksheet.autofilter('A2:I2')
            worksheet.protect('',{'autofilter':True})

            int_row = 1
            worksheet.write(int_row, 0, 'EMP CODE', head_style)
            worksheet.write(int_row, 1, 'EMP NAME', head_style)
            worksheet.write(int_row, 2, 'ISSUED AMOUNT', head_style)
            worksheet.write(int_row, 3, 'PURPOSE', head_style)
            worksheet.write(int_row, 4, 'NO OF EMI', head_style)
            worksheet.write(int_row, 5, 'CURRENT MONTH AMOUNT', head_style)
            worksheet.write(int_row, 6, 'PENDING', head_style)
            worksheet.write(int_row, 7, 'DATE ISSUED', head_style)
            worksheet.set_column(0, 0, 13)
            worksheet.set_column(1, 1, 30)
            worksheet.set_column(2, 2, 13)
            worksheet.set_column(3, 3, 20)
            worksheet.set_column(4, 7, 13)
            worksheet.set_row(int_row, 13)
            for ins_data in lst_data:
                int_row += 1
                worksheet.write(int_row, 0, ins_data['strEMPCode'], row_style)
                worksheet.write(int_row, 1, ins_data['strEMPName'], row_style)
                worksheet.write(int_row, 2, ins_data['intIssuedAmount'], row_style)
                worksheet.write(int_row, 3, ins_data['strPurpose'], row_style)
                worksheet.write(int_row, 4, ins_data['intNumOfEMI'], row_style)
                worksheet.write(int_row, 5, ins_data['intCurrent'], row_style)
                worksheet.write(int_row, 6, str(ins_data['intPending']), row_style)
                worksheet.write(int_row, 7, str(ins_data['dateApproved']), row_style)
                worksheet.set_row(int_row, 20, row_style)
            writer.save()
            conn.close()
            return Response({'status':1,'lstData':lst_data,'data':request.scheme+'://'+request.get_host()+settings.MEDIA_URL+file_name})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno),'message':'Something went wrong'})


class EditLoan(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            if not request.user.userdetails.fk_department.vchr_name=='HR & ADMIN':
                return Response({'status':0,'message':'No Permission'})
            int_emp_id = request.data.get('intEmpId')
            int_requst_id = request.data.get('intId')
            int_amount = float(request.data.get('dblAmount'))
            if int_amount < 0:
                return Response({'status':1, 'message':'Amount should not be greater than balance amount'})
            with transaction.atomic():
                str_type = request.data.get('strType')
                if str_type != "SALARY ADVANCE":
                    ins_details = LoanDetails.objects.filter(pk_bint_id = int_requst_id).values('fk_request_id','fk_request__dbl_loan_amt','fk_request__int_tenure','fk_request__int_month','fk_request__int_year','fk_request__txt_remarks','fk_request__bln_mob_loan','txt_remarks').first()
                    ins_last =  LoanDetails.objects.filter(fk_request_id = ins_details['fk_request_id'], int_status = 0).values('pk_bint_id','int_month','dbl_amount','int_year','int_status').order_by('-int_year', '-int_month')
                    ins_blnc = LoanDetails.objects.filter(fk_request_id = ins_details['fk_request_id'],int_status = 0).aggregate(Sum('dbl_amount'))
                    dct_tenuer_amt = LoanDetails.objects.filter(fk_request_id = ins_details['fk_request_id']).exclude(int_status=-1).values('dbl_amount').annotate(flt_tenuer_amt=Count('dbl_amount')).order_by('-flt_tenuer_amt').first()
                    if ins_blnc['dbl_amount__sum']:
                        if int_amount < ins_blnc['dbl_amount__sum']:
                            int_chenges = ins_blnc['dbl_amount__sum'] - int_amount
                            flt_full_amount = ins_details['fk_request__dbl_loan_amt'] - int_chenges
                            flt_amt = float(int_chenges)
                            for dct_data in ins_last:
                                if flt_amt >= dct_tenuer_amt['dbl_amount']:
                                    LoanDetails.objects.filter(pk_bint_id = dct_data['pk_bint_id']).update(int_status = -2)
                                    flt_amt = flt_amt-dct_data['dbl_amount']
                                elif flt_amt>0 and flt_amt < dct_tenuer_amt['dbl_amount']:
                                    if dct_data['dbl_amount'] > flt_amt:
                                        LoanDetails.objects.filter(pk_bint_id = dct_data['pk_bint_id']).update(dbl_amount = dct_data['dbl_amount']-flt_amt)
                                        break
                                    else:
                                        LoanDetails.objects.filter(pk_bint_id = dct_data['pk_bint_id']).update(int_status = -2)
                                        flt_amt = flt_amt-dct_data['dbl_amount']
                                else:
                                    break
                        if float(int_amount) == 0.0:
                            for data in ins_last:
                                LoanDetails.objects.filter(pk_bint_id = data['pk_bint_id']).update(int_status = -2)
                            LoanRequest.objects.filter(pk_bint_id = ins_details['fk_request_id']).update(txt_remarks = request.data.get('strRemarks'))
                            return Response({'status':1})
                        elif int_amount > ins_blnc['dbl_amount__sum']:
                            if ins_last.first()['int_month'] == 12:
                                month = 1
                                year = ins_last.first()['int_year']+1
                            else:
                                month = ins_last.first()['int_month']+1
                                year = ins_last.first()['int_year']
                            int_chenges = int_amount - ins_blnc['dbl_amount__sum']
                            flt_full_amount = ins_details['fk_request__dbl_loan_amt'] + int_chenges
                            flt_amt = float(int_chenges)
                            for dct_data in ins_last:
                                if flt_amt > 0:
                                    if flt_amt >= dct_tenuer_amt['dbl_amount']:
                                        LoanDetails.objects.filter(pk_bint_id = dct_data['pk_bint_id']).update(dbl_amount = dct_tenuer_amt['dbl_amount'])
                                        flt_amt = (flt_amt+dct_data['dbl_amount'])-dct_tenuer_amt['dbl_amount']
                                    elif (dct_tenuer_amt['dbl_amount']) >= (flt_amt + dct_data['dbl_amount']):
                                        LoanDetails.objects.filter(pk_bint_id = dct_data['pk_bint_id']).update(dbl_amount =flt_amt + dct_data['dbl_amount'])
                                        flt_amt = 0.0
                                        break

                            while flt_amt > 0:
                                if flt_amt >= dct_tenuer_amt['dbl_amount']:
                                    LoanDetails.objects.create(fk_request_id = ins_details['fk_request_id'],
                                                            dbl_amount = dct_tenuer_amt['dbl_amount'],
                                                            int_month = month,
                                                            int_year = year,
                                                            dat_created = datetime.now(),
                                                            int_status = 0,
                                                            fk_created_id = request.user.id)
                                    flt_amt = flt_amt - dct_tenuer_amt['dbl_amount']
                                    if month == 12:
                                        month = 1
                                        year = year+1
                                    else:
                                        month = month+1
                                else:
                                    LoanDetails.objects.create(fk_request_id = ins_details['fk_request_id'],
                                                            dbl_amount = flt_amt,
                                                            int_month = month,
                                                            int_year = year,
                                                            dat_created = datetime.now(),
                                                            int_status = 0,
                                                            fk_created_id = request.user.id)
                                    flt_amt = flt_amt - dct_tenuer_amt['dbl_amount']
                                    if month == 12:
                                        month = 1
                                        year = year+1
                                    else:
                                        month = month+1
                        elif int_amount == ins_blnc['dbl_amount__sum']:
                            return Response({'status':1})
                        LoanRequest.objects.filter(pk_bint_id = ins_details['fk_request_id']).update(int_status = -1,fk_updated_id = request.user.id)
                        ins_data = LoanRequest.objects.create(fk_employee_id = int_emp_id,
                                                    dbl_loan_amt = flt_full_amount,
                                                    int_tenure = ins_details['fk_request__int_tenure'],
                                                    int_month = ins_details['fk_request__int_month'],
                                                    int_year = ins_details['fk_request__int_year'],
                                                    txt_remarks = request.data.get('strRemarks'),
                                                    dat_created = datetime.now(),
                                                    int_status = 1,
                                                    bln_mob_loan = ins_details['fk_request__bln_mob_loan'],
                                                    fk_created_id = request.user.id)
                        LoanDetails.objects.filter(fk_request_id = ins_details['fk_request_id']).update(fk_request_id = ins_data.pk_bint_id,fk_updated_id = request.user.id)
                else:
                    int_month = int(request.data.get('intMonthYear').split('-')[0])
                    int_year = int(request.data.get('intMonthYear').split('-')[1])
                    if request.data.get('dblAmount'):
                        flt_adnc = float(request.data.get('dblAmount'))
                    else:
                        flt_adnc = 0
                    ins_crnt_amnt = SalaryAdvance.objects.filter(pk_bint_id = int_requst_id,int_month = int_month,int_year = int_year,bln_active=True,int_status = 2).values('dbl_amount','fk_employee_id')
                    ins_total = SalaryAdvance.objects.filter(fk_employee_id = ins_crnt_amnt[0]['fk_employee_id'],bln_active=True,int_status = 2).values('pk_bint_id','dbl_amount','int_month','int_year').order_by('-pk_bint_id')
                    int_sum = SalaryAdvance.objects.filter(fk_employee_id = ins_crnt_amnt[0]['fk_employee_id'],bln_active=True,int_status = 2).aggregate(Sum('dbl_amount'))
                    if ins_crnt_amnt[0]['fk_employee_id']:
                        int_emp_id = ins_crnt_amnt[0]['fk_employee_id']
                    else:
                        int_emp_id = None
                    if ins_total[0]['int_month'] == 12:
                        month = 1
                        year = ins_total[0]['int_year']+1
                    else:
                        month = ins_total[0]['int_month']+1
                        year = ins_total[0]['int_year']
                    if flt_adnc == 0.0:
                        for data in ins_total:
                            SalaryAdvance.objects.filter(pk_bint_id = data['pk_bint_id']).update(bln_active=False,int_status = -1)
                        return Response({'status':1})
                    if flt_adnc:


                        if flt_adnc > int_sum['dbl_amount__sum']:
                            flt_blnc = flt_adnc - int_sum['dbl_amount__sum']
                            ins_crnt_amnt = ins_crnt_amnt[0]['dbl_amount'] + flt_blnc
                            SalaryAdvance.objects.filter(pk_bint_id = int_requst_id,int_month = int_month,int_year = int_year,bln_active=True,int_status = 2).update(dbl_amount = ins_crnt_amnt ,dat_updated = datetime.now(),vchr_purpose = request.data.get('strRemarks'))

                        elif flt_adnc < int_sum['dbl_amount__sum']:
                            flt_blnc = int_sum['dbl_amount__sum'] - flt_adnc
                            for dct_data in ins_total:
                                if flt_blnc >= dct_data['dbl_amount']:
                                    SalaryAdvance.objects.filter(pk_bint_id = dct_data['pk_bint_id']).update(int_status = -1,vchr_purpose = request.data.get('strRemarks'))
                                    flt_blnc = flt_blnc-dct_data['dbl_amount']
                                elif flt_blnc>0 and flt_blnc < dct_data['dbl_amount']:
                                    SalaryAdvance.objects.filter(pk_bint_id = dct_data['pk_bint_id']).update(dbl_amount = dct_data['dbl_amount']-flt_blnc,vchr_purpose = request.data.get('strRemarks'))
                                    break
                        else:
                            return Response({'status':1})
            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno), 'message':'Something went wrong'})
