from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from userdetails.models import UserDetails,EmpLeaveData, AdminSettings,WPS
from django.db.models.functions import Concat, Cast, Substr
from django.contrib.postgres.fields.jsonb import KeyTransform, KeyTextTransform
from django.db.models import F, Value, Max, Min, Sum
from django.conf import settings
import psycopg2
import num2words
import pdfkit
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import random
import copy
import pandas as pd
from pandas import ExcelWriter
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import and_, func , cast, Date, case, literal_column, or_, MetaData, desc, Integer, text, extract
from category.models import Category
from django.db.models import F, Q, Value, Case, When, IntegerField, FloatField, CharField, DateField, BooleanField, Count, ExpressionWrapper, Func
from django.db.models.functions import Concat
from django.contrib.auth.models import User as AuthUser
from salary_struct.models import SalaryStructure, PfandEsiStructure
from salary_advance.models import SalaryAdvance
from attendance.models import PunchLog
from leave_management.models import *
from professional_tax.models import *
from bonus.models import *
from loan.models import *
from sqlalchemy.orm import mapper, aliased
from POS.dftosql import Savedftosql
from hierarchy.models import HierarchyLevel
import calendar
from salary_process.models import *
from collections import OrderedDict
import sys, os
from os import path
from POS import ins_logger
import traceback
import math
UserDetailsSA = UserDetails.sa
AuthUserSA = AuthUser.sa
VariablePaySA = VariablePay.sa
FixedAllowanceSA = FixedAllowance.sa


def Session():
    _Session = sessionmaker(bind = engine)
    return _Session()

sqlalobj = Savedftosql('','')
engine = sqlalobj.engine
metadata = MetaData()
metadata.reflect(bind=engine)
Connection = sessionmaker()
Connection.configure(bind=engine)




class WpsAPI(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        try:
            lst_data = WPS.objects.values('pk_bint_id','vchr_name')
            return Response({"status":1,'lstData':lst_data})
        except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
                    return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})



class ListEmployee(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            int_cat_id = request.data.get('intCategoryId')
            int_month = request.data.get('intMonth')
            int_year = request.data.get('intYear')
            now_date = datetime.now()

            dur_calendar = calendar.monthrange(int_year, int_month)
            str_start_date = str(int_year)+'-'+str(int_month)+'-1'
            str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(dur_calendar[1])

            if not request.user.is_superuser:
                ins_admin = AdminSettings.objects.filter(vchr_code='PAYROLL_PERIOD',bln_enabled=True,fk_company_id=request.user.userdetails.fk_company_id).values('vchr_value', 'int_value').first()
                if ins_admin and ins_admin['int_value'] != 0:
                    str_start_date = datetime.strftime(datetime.strptime(str(int_year)+'-'+str(int_month)+'-'+ins_admin['vchr_value'][0],'%Y-%m-%d')+timedelta(days=int(ins_admin['vchr_value'][0])*ins_admin['int_value']),'%Y-%m-')+ins_admin['vchr_value'][0]
                    str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(int(ins_admin['vchr_value'][0])-1)

            if int_month == now_date.month and int_year == now_date.year and now_date.day <= int(str_end_date.split('-')[2]):
                str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(now_date.day)

            dat_month_last = datetime.strptime(str_end_date, '%Y-%m-%d')
            dat_month_first = datetime.strptime(str_start_date, '%Y-%m-%d')

            str_filter = ''
            if int_cat_id:
                str_filter += ' AND cat.pk_bint_id = '+str(int_cat_id)
            lst_processed_emps = list(SalaryProcessed.objects.filter(int_month = int_month,int_year = int_year, int_status = 1).values_list('fk_employee_id', flat=True))
            if lst_processed_emps:
                str_filter += ' AND ud.user_ptr_id NOT IN('+str(lst_processed_emps)[1:-1]+')'

            rst_data = AllSalaryDetails(request, str(int_month)+'-'+str(int_year), str_start_date, str_end_date, str_filter)
            if not rst_data:
                return Response({'status':0,'reason':'No Data'})

            lst_data = []
            for ins_user in rst_data:
                dct_data = {}
                dct_data['intEMPId'] = ins_user['int_emp_id']
                dct_data['strEMPCode'] = ins_user['str_employee_code']
                dct_data['strName'] = ins_user['str_emp_name']
                dct_data['strCategoryName'] = ins_user['str_category_name']
                dct_data['strStructure'] = ins_user['str_salary_slab']
                dct_data['dblGross'] = ins_user['GROSS']
                dct_data['Monthly_CTC'] = ins_user['Monthly_CTC']
                lst_data.append(dct_data)

            return Response({'status':1, 'data': lst_data})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


class SalaryProcess(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            int_cat_id = request.data.get('intCategoryId',)
            int_month = request.data.get('intMonth')
            int_year = request.data.get('intYear')
            now_date = datetime.now()

            dur_calendar = calendar.monthrange(int_year, int_month)
            str_start_date = str(int_year)+'-'+str(int_month)+'-1'
            str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(dur_calendar[1])

            if not request.user.is_superuser:
                ins_admin = AdminSettings.objects.filter(vchr_code='PAYROLL_PERIOD',bln_enabled=True,fk_company_id=request.user.userdetails.fk_company_id).values('vchr_value', 'int_value').first()
                if ins_admin and ins_admin['int_value'] != 0:
                    str_start_date = datetime.strftime(datetime.strptime(str(int_year)+'-'+str(int_month)+'-'+ins_admin['vchr_value'][0],'%Y-%m-%d')+timedelta(days=int(ins_admin['vchr_value'][0])*ins_admin['int_value']),'%Y-%m-')+ins_admin['vchr_value'][0]
                    str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(int(ins_admin['vchr_value'][0])-1)

            if int_month == now_date.month and int_year == now_date.year and now_date.day <= int(str_end_date.split('-')[2]):
                str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(now_date.day)

            dat_month_last = datetime.strptime(str_end_date, '%Y-%m-%d')
            dat_month_first = datetime.strptime(str_start_date, '%Y-%m-%d')
            str_filter = ''
            if int_cat_id:
                str_filter += ' AND cat.pk_bint_id = '+str(int_cat_id)

            lst_processed_emps = list(SalaryProcessed.objects.filter(int_month = int_month,int_year = int_year, int_status = 1).values_list('fk_employee_id', flat=True))
            if lst_processed_emps:
                str_filter += ' AND ud.user_ptr_id NOT IN('+str(lst_processed_emps)[1:-1]+')'

            lst_data = []
            lst_salary_processed = []
            lst_loan_processed_id = []
            lst_emp_id = []
            lst_data = AllSalaryDetails(request, str(int_month)+'-'+str(int_year), str_start_date, str_end_date, str_filter)
            if not lst_data:
                return Response({'status':0,'reason':'No Data'})

            file_name = 'SalaryProcess/Salary_Details_' + datetime.strftime(date.today(), "%d-%m-%Y") + '.xlsx'
            if path.exists(file_name):
                os.remove(file_name)
            if not path.exists(settings.MEDIA_ROOT + '/SalaryProcess/'):
                os.mkdir(settings.MEDIA_ROOT + '/SalaryProcess/')
            writer = pd.ExcelWriter(settings.MEDIA_ROOT + '/' + file_name, engine ='xlsxwriter')
            workbook = writer.book
            worksheet = workbook.add_worksheet()

            title_style = workbook.add_format({'font_size':14, 'bold':1, 'border':1, 'align': 'center'})
            title_style.set_align('vcenter')
            title_style.set_pattern(1)
            title_style.set_bg_color('#ffe0cc')
            worksheet.merge_range('A1+:Y1', 'Salary Details ('+calendar.month_name[int_month]+' '+str(int_year)+')', title_style)

            head_style = workbook.add_format({'font_size':11, 'bold':1, 'align': 'center', 'border':1, 'border_color':'#000000'})
            head_style.set_pattern(1)
            head_style.set_bg_color('#bfbfbf')
            head_style.set_align('vcenter')

            sub_head_style = workbook.add_format({'font_size':11, 'align': 'center', 'border':1, 'border_color':'#000000', 'text_wrap': True})
            sub_head_style.set_pattern(1)
            sub_head_style.set_bg_color('#b0aca9')
            sub_head_style.set_align('vcenter')

            row_style = workbook.add_format({'font_size':11, 'text_wrap': True})
            row_style.set_align('vcenter')
            worksheet.set_row(0, 30)

            worksheet.protect()
            worksheet.merge_range('A2+:A3', 'Employee Code', head_style)
            worksheet.set_column(0, 0, 20)
            worksheet.set_row(1, 20)
            worksheet.merge_range('B2+:B3', 'Employee Name', head_style)
            worksheet.set_column(1, 1, 30)
            worksheet.set_row(2, 28)
            worksheet.merge_range('C2+:C3', 'Basic Pay + DA', head_style)
            worksheet.merge_range('D2+:D3', 'HRA', head_style)
            worksheet.merge_range('E2+:E3', 'CCA', head_style)
            worksheet.merge_range('F2+:F3', 'WA', head_style)
            worksheet.merge_range('G2+:G3', 'Special Allowances', head_style)
            worksheet.merge_range('H2+:H3', 'Gross Pay', head_style)
            worksheet.merge_range('I2+:I3', 'Variable Pay', head_style)
            worksheet.set_column(2, 8, 20)

            worksheet.merge_range('J2+:N2', 'Allowances (ER Share)', head_style)
            worksheet.write(2, 9, 'PF', sub_head_style)
            worksheet.write(2, 10, 'ESI', sub_head_style)
            worksheet.write(2, 11, 'WWF', sub_head_style)
            worksheet.write(2, 12, 'Gratuity', sub_head_style)
            worksheet.write(2, 13, 'Medical Insurance', sub_head_style)

            worksheet.merge_range('O2+:W2', 'Deductions (EE Share)', head_style)
            worksheet.write(2, 14, 'PF', sub_head_style)
            worksheet.write(2, 15, 'ESI', sub_head_style)
            worksheet.write(2, 16, 'WWF', sub_head_style)
            worksheet.write(2, 17, 'TDS', sub_head_style)
            worksheet.write(2, 18, 'P TAX', sub_head_style)
            worksheet.write(2, 19, 'Mobile Loan', sub_head_style)
            worksheet.write(2, 20, 'Work Loan', sub_head_style)
            worksheet.write(2, 21, 'Salary Advance', sub_head_style)
            worksheet.write(2, 22, 'Charity', sub_head_style)
            worksheet.merge_range('X2+:X3', 'Net. Salary', head_style)
            worksheet.merge_range('Y2+:Y3', 'Monthly CTC', head_style)
            worksheet.set_column(23, 24, 20)

            int_row = 3
            for dct_item in lst_data:
                worksheet.write(int_row, 0, dct_item['str_employee_code'], row_style)
                worksheet.write(int_row, 1, dct_item['str_emp_name'], row_style)
                worksheet.write(int_row, 2, dct_item['BP_DA'], row_style)
                worksheet.write(int_row, 3, dct_item['HRA'], row_style)
                worksheet.write(int_row, 4, dct_item['CCA'], row_style)
                worksheet.write(int_row, 5, dct_item['WA'], row_style)
                worksheet.write(int_row, 6, dct_item['SA'], row_style)
                worksheet.write(int_row, 7, dct_item['GROSS'], row_style)
                worksheet.write(int_row, 8, dct_item.get('VariablePay', 0), row_style)
                worksheet.write(int_row, 9, dct_item.get('Allowances', {}).get('PF', 0), row_style)
                worksheet.write(int_row, 10, dct_item.get('Allowances', {}).get('ESI', 0), row_style)
                worksheet.write(int_row, 11, dct_item.get('Allowances', {}).get('WWF', 0), row_style)
                worksheet.write(int_row, 12, dct_item.get('Allowances', {}).get('Gratuity', 0), row_style)
                worksheet.write(int_row, 13, dct_item.get('Allowances', {}).get('MedicalInsurance', 0), row_style)
                worksheet.write(int_row, 14, dct_item.get('Deductions', {}).get('PF', 0), row_style)
                worksheet.write(int_row, 15, dct_item.get('Deductions', {}).get('ESI', 0), row_style)
                worksheet.write(int_row, 16, dct_item.get('Deductions', {}).get('WWF', 0), row_style)
                worksheet.write(int_row, 17, dct_item.get('Deductions', {}).get('TDS', 0), row_style)
                worksheet.write(int_row, 18, dct_item.get('Deductions', {}).get('ProTax', 0), row_style)
                worksheet.write(int_row, 19, dct_item.get('Deductions', {}).get('MobileLoan', 0), row_style)
                worksheet.write(int_row, 20, dct_item.get('Deductions', {}).get('WorkLoan', 0), row_style)
                worksheet.write(int_row, 21, dct_item.get('Deductions', {}).get('SalaryAdvance', 0), row_style)
                worksheet.write(int_row, 22, dct_item.get('Deductions', {}).get('Charity', 0), row_style)
                worksheet.write(int_row, 23, dct_item.get('Net_Salary', 0.0), row_style)
                worksheet.write(int_row, 24, dct_item.get('Monthly_CTC', 0.0), row_style)

                # -- SalaryProcessed --
                lst_emp_id.append(dct_item['int_emp_id'])
                dct_attendace = {}
                dct_attendace['dct_details'] =  dct_item['json_attendance']
                dct_attendace['dur_worked_hour'] =  str(dct_item['dur_worked_hour'].days*24+dct_item['dur_worked_hour'].seconds //3600)+':'+str((dct_item['dur_worked_hour'].seconds % 3600)//60).zfill(2) if dct_item['dur_worked_hour'] else '0:00'
                dct_attendace['dur_less_hours'] =  str(dct_item['dur_less_hours'].days*24+dct_item['dur_less_hours'].seconds //3600)+':'+str((dct_item['dur_less_hours'].seconds % 3600)//60).zfill(2) if dct_item['dur_less_hours'] else '0:00'
                dct_attendace['dbl_less_hour_days'] =  dct_item['dbl_less_hour_days']
                dct_attendace['dbl_absent'] =  dct_item['dbl_absent']
                dct_attendace['dbl_lop_leave'] =  dct_item['dbl_lop_leave']
                dct_attendace['dbl_tot_lop'] =  dct_item['dbl_tot_lop']
                dct_attendace['dbl_present'] =  dct_item['dbl_present']
                dct_attendace['dbl_on_duty'] =  dct_item['dbl_on_duty']
                dct_attendace['dbl_casual_leave'] =  dct_item['dbl_leave']
                dct_attendace['dbl_combo'] =  dct_item['dbl_combo']
                dct_attendace['int_week_off'] =  dct_item['int_week_off']
                dct_attendace['int_holiday'] =  dct_item['int_holiday']
                ins_salary_processed = SalaryProcessed(
                                    fk_employee_id = dct_item['int_emp_id'],
                                    fk_details_id = dct_item['int_slry_dtls_id'],
                                    int_month = int_month,
                                    int_year = int_year,
                                    json_attendance = dct_attendace,
                                    dbl_bp = dct_item['BP_DA'],
                                    dbl_da = dct_item['DA'],
                                    dbl_hra = dct_item['HRA'],
                                    dbl_cca = dct_item['CCA'],
                                    dbl_wa = dct_item['WA'],
                                    dbl_sa = dct_item['SA'],
                                    dbl_gross = dct_item['GROSS'],
                                    json_allowances = dct_item['Allowances'],
                                    json_deductions = dct_item['Deductions'],
                                    dbl_net_salary = dct_item['Net_Salary'],
                                    dbl_monthly_ctc = dct_item['Monthly_CTC'],
                                    fk_created_id = request.user.id,
                                    dat_created = datetime.now(),
                                    int_status = 0)
                lst_salary_processed.append(ins_salary_processed)
                # -----------------
                if dct_item['int_mobile_loan_id']:
                    lst_loan_processed_id.append(dct_item['int_mobile_loan_id'])
                if dct_item['int_work_loan_id']:
                    lst_loan_processed_id.append(dct_item['int_work_loan_id'])
                int_row += 1
            writer.save()
            SalaryProcessed.objects.filter(int_month = int_month, int_year = int_year, fk_employee_id__in = lst_emp_id, int_status = 0).update(int_status = -1)
            SalaryProcessed.objects.bulk_create(lst_salary_processed)
            if lst_loan_processed_id:
                LoanDetails.objects.filter(pk_bint_id__in=lst_loan_processed_id).update(int_status=1)

            return Response({'status':1, 'data':request.scheme+'://'+request.get_host()+settings.MEDIA_URL+file_name})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


def GenerateSalaryProcessOld(dbl_gross, dct_structure, dct_allowances, dbl_leave_taken = 0, int_max_days = 30):
    dct_data = {}
    dct_data['HRA'] = 0.0
    dct_data['CCA'] = 0.0
    dct_data['WA'] = 0.0
    dct_data['SA'] = 0.0

    dct_data['Allowances'] = {}
    dct_data['Allowances']['WWF'] = 0.0
    dct_data['Allowances']['PF'] = 0.0
    dct_data['Allowances']['ESI'] = 0.0
    dct_data['Allowances']['Gratuity'] = 0.0

    dct_data['Deductions'] = {}
    dct_data['Deductions']['WWF'] = 0.0
    dct_data['Deductions']['PF'] = 0.0
    dct_data['Deductions']['ESI'] = 0.0
    dct_data['Deductions']['SalaryAdvance'] = 0.0

    if not dct_structure['dbl_bp_da_per']:
        dct_data['BP_DA'] = round((dct_structure['dbl_bp_da']+dct_structure['dbl_da']) * ((int_max_days - dbl_leave_taken)/int_max_days), 0) # Basic Pay + D.A
        dct_data['BP'] = round(dct_structure['dbl_bp_da'] * ((int_max_days - dbl_leave_taken)/int_max_days), 0) # Basic Pay
        dct_data['DA'] = round(dct_structure['dbl_da'] * ((int_max_days - dbl_leave_taken)/int_max_days), 0) # Dearness Allowance (DA)
    else:
        dct_data['BP_DA'] = round((dbl_gross*(dct_structure['dbl_bp_da_per']/100)) * ((int_max_days - dbl_leave_taken)/int_max_days), 0) # Basic Pay + D.A Percentage of Gross
    # import pdb; pdb.set_trace()
    if dct_structure['json_rules'].get('HRA') and dct_structure['json_rules']['HRA'].upper() != 'FALSE':
        lst_hra = dct_structure['json_rules']['HRA'].split('-')
        for int_hra_per in range(int(lst_hra[0]),int(lst_hra[-1])+1):

            dct_prv_data = {}
            dct_prv_data = copy.deepcopy(dct_data)
            bln_flag = False
            dct_data['HRA'] = round((dct_data['BP_DA']*(float(int_hra_per)/100)) * ((int_max_days - dbl_leave_taken)/int_max_days), 0) # HRA Percentage of Basic Pay + D.A Percentage
            if round(dbl_gross - (dct_data['BP_DA']+dct_data['HRA']+dct_data['CCA']+dct_data['WA']),0)>=0:
                dct_prv_data = copy.deepcopy(dct_data)
            if dct_structure['json_rules'].get('CCA') and dct_structure['json_rules']['CCA'].upper() != 'FALSE':
                lst_cca = dct_structure['json_rules']['CCA'].split('-')
                for int_cca_per in range(int(lst_cca[0]),int(lst_cca[-1])+1):
                    dct_data['CCA'] = round((dct_data['BP_DA']*(float(int_cca_per)/100)) * ((int_max_days - dbl_leave_taken)/int_max_days), 0) # CCA Percentage of Basic Pay + D.A Percentage
                    if round(dbl_gross - (dct_data['BP_DA']+dct_data['HRA']+dct_data['CCA']+dct_data['WA']),0)>=0:
                        dct_prv_data = copy.deepcopy(dct_data)
                    if dct_structure['json_rules'].get('WA') and dct_structure['json_rules']['WA'].upper() != 'FALSE' and dct_allowances.get('bln_esi') == True:
                        lst_wa = dct_structure['json_rules']['WA'].split('-')
                        for int_wa_per in range(int(lst_wa[0]),int(lst_wa[-1])+1):
                            dct_data['WA'] = round(((dbl_gross * ((int_max_days - dbl_leave_taken)/int_max_days))*(float(int_wa_per)/100)) * ((int_max_days - dbl_leave_taken)/int_max_days), 0)
                            if dbl_gross-dct_data['WA'] < 21000:
                                break
                    if dct_structure['json_rules'].get('SA') and dct_structure['json_rules']['SA']:
                        dct_data['SA'] = round(dbl_gross - (dct_data['BP_DA']+dct_data['HRA']+dct_data['CCA']+dct_data['WA']), 0) # Balance
                    if dct_data['SA']<0:
                        dct_data = dct_prv_data
                        bln_flag = True

                    # Allowances and Deductions
                    # --------WWF----------
                    if dct_allowances.get('bln_wwf') == True:
                        dct_data['Deductions']['WWF'] = dct_structure['json_rules'].get('Deductions').get('WWF')
                        dct_data['Allowances']['WWF'] = dct_structure['json_rules'].get('Allowances').get('WWF')

                    # --------PF----------
                    if dct_allowances.get('bln_pf') == True:
                        # take min of HRA
                        if dbl_gross-dct_data['HRA'] >15000:
                            dct_data['Deductions']['PF'] = round((15000)*((dct_structure['json_rules']['Deductions']['PF'])/100),0)
                            dct_data['Allowances']['PF'] = round((15000)*((dct_structure['json_rules']['Allowances']['PF'])/100),0)
                        else:
                            dct_data['Deductions']['PF'] = round((dbl_gross-dct_data['HRA'])*((dct_structure['json_rules']['Deductions']['PF'])/100),0)
                            dct_data['Allowances']['PF'] = round((dbl_gross-dct_data['HRA'])*((dct_structure['json_rules']['Allowances']['PF'])/100),0)

                    # --------ESI----------
                    if dct_allowances.get('bln_esi') == True and dbl_gross-dct_data['WA'] <21000:
                        dct_data['Deductions']['ESI'] = math.ceil((dbl_gross-dct_data['WA'])*((dct_structure['json_rules']['Deductions']['ESI'])/100))
                        dct_data['Allowances']['ESI'] = round((dbl_gross-dct_data['WA'])*((dct_structure['json_rules']['Allowances']['ESI'])/100),0)

                    if dct_data['Allowances']['ESI'] == 0.0 and dct_data['Deductions']['ESI'] == 0.0 and dct_allowances.get('bln_esi') == True and dct_structure['json_rules'].get('WA') and dct_structure['json_rules']['WA'].upper() != 'FALSE':
                        dct_data['WA'] = round(dbl_gross*(float(dct_structure['json_rules']['WA'].split('-')[0])/100)) # WA Percentage of Gross
                    # --------Gratuity----------
                    if dct_allowances.get('bln_gratuity') == True and dct_structure['json_rules']['Allowances']['Gratuity'].upper() != 'FALSE':
                        dct_data['Allowances']['Gratuity'] = round(dct_data['BP_DA']/26*15/12,0)

                    if bln_flag:
                        # bln_flag=False
                        break
            else:
                if dct_structure['json_rules'].get('WA') and dct_structure['json_rules']['WA'].upper() != 'FALSE' and dct_allowances.get('bln_esi') == True:
                    lst_wa = dct_structure['json_rules']['WA'].split('-')
                    for int_wa_per in range(int(lst_wa[0]),int(lst_wa[-1])+1):
                        dct_data['WA'] = round((dbl_gross*(float(int_wa_per)/100)) * ((int_max_days - dbl_leave_taken)/int_max_days), 0)
                        if dbl_gross-dct_data['WA'] < 21000:
                            break
                if dct_structure['json_rules'].get('SA') and dct_structure['json_rules']['SA']:
                    dct_data['SA'] = round(dbl_gross - (dct_data['BP_DA']+dct_data['HRA']+dct_data['CCA']+dct_data['WA']), 0) # Balance
                if dct_data['SA']<0:
                    dct_data = dct_prv_data
                    bln_flag = True

                # Allowances and Deductions
                # --------WWF----------
                if dct_allowances.get('bln_wwf') == True:
                    dct_data['Deductions']['WWF'] = dct_structure['json_rules'].get('Deductions').get('WWF')
                    dct_data['Allowances']['WWF'] = dct_structure['json_rules'].get('Allowances').get('WWF')

                # --------PF----------
                if dct_allowances.get('bln_pf') == True:
                    # take min of HRA
                    if dbl_gross-dct_data['HRA'] >15000:
                        dct_data['Deductions']['PF'] = round((15000)*((dct_structure['json_rules']['Deductions']['PF'])/100),0)
                        dct_data['Allowances']['PF'] = round((15000)*((dct_structure['json_rules']['Allowances']['PF'])/100),0)
                    else:
                        dct_data['Deductions']['PF'] = round((dbl_gross-dct_data['HRA'])*((dct_structure['json_rules']['Deductions']['PF'])/100),0)
                        dct_data['Allowances']['PF'] = round((dbl_gross-dct_data['HRA'])*((dct_structure['json_rules']['Allowances']['PF'])/100),0)

                # --------ESI----------
                if dct_allowances.get('bln_esi') == True and dbl_gross-dct_data['WA'] <21000:
                    dct_data['Deductions']['ESI'] = math.ceil((dbl_gross-dct_data['WA'])*((dct_structure['json_rules']['Deductions']['ESI'])/100))
                    dct_data['Allowances']['ESI'] = round((dbl_gross-dct_data['WA'])*((dct_structure['json_rules']['Allowances']['ESI'])/100),0)

                if dct_data['Allowances']['ESI'] == 0.0 and dct_data['Deductions']['ESI'] == 0.0 and dct_allowances.get('bln_esi') == True and dct_structure['json_rules'].get('WA') and dct_structure['json_rules']['WA'].upper() != 'FALSE':
                    dct_data['WA'] = round(dbl_gross*(float(dct_structure['json_rules']['WA'].split('-')[0])/100),0) # WA Percentage of Gross
                # --------Gratuity----------
                if dct_allowances.get('bln_gratuity') == True and dct_structure['json_rules']['Allowances']['Gratuity'].upper() != 'FALSE':
                    dct_data['Allowances']['Gratuity'] = round(dct_data['BP_DA']/26*15/12,0)

                if bln_flag:
                    break
            # if bln_flag:
            #     break
    else:
        if dct_structure['json_rules'].get('CCA') and dct_structure['json_rules']['CCA'].upper() != 'FALSE':
            lst_cca = dct_structure['json_rules']['CCA'].split('-')
            for int_cca_per in range(int(lst_cca[0]),int(lst_cca[-1])+1):
                bln_flag = False
                dct_prv_data = {}
                dct_prv_data = copy.deepcopy(dct_data)

                dct_data['CCA'] = round((dct_data['BP_DA']*(float(int_cca_per)/100)) * ((int_max_days - dbl_leave_taken)/int_max_days), 0) # CCA Percentage of Basic Pay + D.A Percentage
                if round(dbl_gross - (dct_data['BP_DA']+dct_data['HRA']+dct_data['CCA']+dct_data['WA']),0)>=0:
                    dct_prv_data = copy.deepcopy(dct_data)
                if dct_structure['json_rules'].get('WA') and dct_structure['json_rules']['WA'].upper() != 'FALSE' and dct_allowances.get('bln_esi') == True:
                    lst_wa = dct_structure['json_rules']['WA'].split('-')
                    for int_wa_per in range(int(lst_wa[0]),int(lst_wa[-1])+1):
                        dct_data['WA'] = round((dbl_gross*(float(int_wa_per)/100)) * ((int_max_days - dbl_leave_taken)/int_max_days), 0)
                        if dbl_gross-dct_data['WA'] < 21000:
                            break
                if dct_structure['json_rules'].get('SA') and dct_structure['json_rules']['SA']:
                    dct_data['SA'] = round(dbl_gross - (dct_data['BP_DA']+dct_data['HRA']+dct_data['CCA']+dct_data['WA']), 0) # Balance
                if dct_data['SA']<0:
                    dct_data = dct_prv_data
                    bln_flag = True

                # Allowances and Deductions
                # --------WWF----------
                if dct_allowances.get('bln_wwf') == True:
                    dct_data['Deductions']['WWF'] = dct_structure['json_rules'].get('Deductions').get('WWF')
                    dct_data['Allowances']['WWF'] = dct_structure['json_rules'].get('Allowances').get('WWF')

                # --------PF----------
                if dct_allowances.get('bln_pf') == True:
                    # take min of HRA
                    if dbl_gross-dct_data['HRA'] >15000:
                        dct_data['Deductions']['PF'] = round((15000)*((dct_structure['json_rules']['Deductions']['PF'])/100),0)
                        dct_data['Allowances']['PF'] = round((15000)*((dct_structure['json_rules']['Allowances']['PF'])/100),0)
                    else:
                        dct_data['Deductions']['PF'] = round((dbl_gross-dct_data['HRA'])*((dct_structure['json_rules']['Deductions']['PF'])/100),0)
                        dct_data['Allowances']['PF'] = round((dbl_gross-dct_data['HRA'])*((dct_structure['json_rules']['Allowances']['PF'])/100),0)

                # --------ESI----------
                if dct_allowances.get('bln_esi') == True and dbl_gross-dct_data['WA'] <21000:
                    # take a min of ESI
                    dct_data['Deductions']['ESI'] = math.ceil((dbl_gross-dct_data['WA'])*((dct_structure['json_rules']['Deductions']['ESI'])/100))
                    dct_data['Allowances']['ESI'] = round((dbl_gross-dct_data['WA'])*((dct_structure['json_rules']['Allowances']['ESI'])/100),0)

                if dct_data['Allowances']['ESI'] == 0.0 and dct_data['Deductions']['ESI'] == 0.0 and dct_allowances.get('bln_esi') == True and dct_structure['json_rules'].get('WA') and dct_structure['json_rules']['WA'].upper() != 'FALSE':
                    dct_data['WA'] = round(dbl_gross*(float(dct_structure['json_rules']['WA'].split('-')[0])/100),0) # WA Percentage of Gross
                # --------Gratuity----------
                if dct_allowances.get('bln_gratuity') == True and dct_structure['json_rules']['Allowances']['Gratuity'].upper() != 'FALSE':
                    dct_data['Allowances']['Gratuity'] = round(dct_data['BP_DA']/26*15/12,0)

                if bln_flag:
                    break
        else:
            dct_prv_data = {}
            dct_prv_data = copy.deepcopy(dct_data)
            if dct_structure['json_rules'].get('WA') and dct_structure['json_rules']['WA'].upper() != 'FALSE' and dct_allowances.get('bln_esi') == True:
                lst_wa = dct_structure['json_rules']['WA'].split('-')
                for int_wa_per in range(int(lst_wa[0]),int(lst_wa[-1])+1):
                    dct_data['WA'] = round((dbl_gross*(float(int_wa_per)/100)) * ((int_max_days - dbl_leave_taken)/int_max_days), 0)
                    if dbl_gross-dct_data['WA'] < 21000:
                        break
            if dct_structure['json_rules'].get('SA') and dct_structure['json_rules']['SA']:
                dct_data['SA'] = round(dbl_gross - (dct_data['BP_DA']+dct_data['HRA']+dct_data['CCA']+dct_data['WA']), 0) # Balance
            if dct_data['SA']<0:
                dct_data = dct_prv_data

            # Allowances and Deductions
            # --------WWF----------
            if dct_allowances.get('bln_wwf') == True:
                dct_data['Deductions']['WWF'] = dct_structure['json_rules'].get('Deductions').get('WWF')
                dct_data['Allowances']['WWF'] = dct_structure['json_rules'].get('Allowances').get('WWF')

            # --------PF----------
            if dct_allowances.get('bln_pf') == True:
                # take min of HRA
                if dbl_gross-dct_data['HRA'] >15000:
                    dct_data['Deductions']['PF'] = round((15000)*((dct_structure['json_rules']['Deductions']['PF'])/100),0)
                    dct_data['Allowances']['PF'] = round((15000)*((dct_structure['json_rules']['Allowances']['PF'])/100),0)
                else:
                    dct_data['Deductions']['PF'] = round((dbl_gross-dct_data['HRA'])*((dct_structure['json_rules']['Deductions']['PF'])/100),0)
                    dct_data['Allowances']['PF'] = round((dbl_gross-dct_data['HRA'])*((dct_structure['json_rules']['Allowances']['PF'])/100),0)

            # --------ESI----------
            if dct_allowances.get('bln_esi') == True and dbl_gross-dct_data['WA'] <21000:
                # take a min of ESI
                dct_data['Deductions']['ESI'] = math.ceil((dbl_gross-dct_data['WA'])*((dct_structure['json_rules']['Deductions']['ESI'])/100))
                dct_data['Allowances']['ESI'] = round((dbl_gross-dct_data['WA'])*((dct_structure['json_rules']['Allowances']['ESI'])/100),0)

            if dct_data['Allowances']['ESI'] == 0.0 and dct_data['Deductions']['ESI'] == 0.0 and dct_allowances.get('bln_esi') == True and dct_structure['json_rules'].get('WA') and dct_structure['json_rules']['WA'].upper() != 'FALSE':
                dct_data['WA'] = round(dbl_gross*(float(dct_structure['json_rules']['WA'].split('-')[0])/100),0) # WA Percentage of Gross
            # --------Gratuity----------
            if dct_allowances.get('bln_gratuity') == True and dct_structure['json_rules']['Allowances']['Gratuity'].upper() != 'FALSE':
                dct_data['Allowances']['Gratuity'] = round(dct_data['BP_DA']/26*15/12,0)

    dct_data['SA'] = round(dbl_gross - (dct_data.get('BP_DA',0)+dct_data.get('HRA',0)+dct_data.get('CCA',0)+dct_data.get('WA',0)),0) # Balance
    if dct_data['SA']<0:
        dct_data['SA'] = 0
        dct_data['BP_DA'] = dbl_gross
    dct_data['Deductions']['SalaryAdvance'] = dct_structure.get('dblAdvAmount',0)
    dct_data['Deductions']['Charity'] = dct_structure.get('dblCharity',0)
    dct_data['Deductions']['TDS'] = dct_structure.get('dblTds',0)
    dbl_tot_deductions = dct_data.get('Deductions',{}).get('PF',0) + dct_data.get('Deductions',{}).get('ESI',0) + dct_data.get('Deductions',{}).get('WWF',0) + dct_data.get('Deductions',{}).get('SalaryAdvance',0) + dct_data.get('Deductions',{}).get('Charity',0) + dct_data.get('Deductions',{}).get('TDS',0)
    dbl_tot_allowances = dct_data.get('Allowances',{}).get('PF',0) + dct_data.get('Allowances',{}).get('ESI',0) + dct_data.get('Allowances',{}).get('WWF',0) + dct_data.get('Allowances',{}).get('Gratuity',0)

    dbl_net_salary = dbl_gross - dbl_tot_deductions
    dbl_cost_to_company = dbl_gross + dbl_tot_allowances
    dct_data['Net_Salary'] = round(dbl_net_salary,0)
    dct_data['Monthly_CTC'] = round(dbl_cost_to_company,0)
    return dct_data

def GenerateSalaryProcess(dbl_gross, dct_structure, dct_allowances, dbl_leave_taken = 0, int_max_days = 30):

    dct_data = {}
    dct_data['HRA'] = 0.0
    dct_data['CCA'] = 0.0
    dct_data['WA'] = 0.0
    dct_data['SA'] = 0.0

    dct_data['Allowances'] = {}
    dct_data['Allowances']['WWF'] = 0.0
    dct_data['Allowances']['PF'] = 0.0
    dct_data['Allowances']['ESI'] = 0.0
    dct_data['Allowances']['Gratuity'] = 0.0

    dct_data['Deductions'] = {}
    dct_data['Deductions']['WWF'] = 0.0
    dct_data['Deductions']['PF'] = 0.0
    dct_data['Deductions']['ESI'] = 0.0
    dct_data['Deductions']['SalaryAdvance'] = 0.0
    if not dct_structure['dbl_bp_da_per']:
        dct_data['BP_DA'] = round((dct_structure['dbl_bp_da']+(dct_structure['dbl_da'] if dct_structure['dbl_da'] else 0)) * ((int_max_days - dbl_leave_taken)/int_max_days), 0) # Basic Pay + D.A
        dct_data['BP'] = round(dct_structure['dbl_bp_da'] * ((int_max_days - dbl_leave_taken)/int_max_days), 0) # Basic Pay
        dct_data['DA'] = round((dct_structure['dbl_da'] if dct_structure['dbl_da'] else 0) * ((int_max_days - dbl_leave_taken)/int_max_days), 0) # Dearness Allowance (DA)
    else:
        dct_data['BP_DA'] = round((dbl_gross*(dct_structure['dbl_bp_da_per']/100)) * ((int_max_days - dbl_leave_taken)/int_max_days), 0) # Basic Pay + D.A Percentage of Gross

    if dct_structure['json_rules'].get('HRA') and dct_structure['json_rules']['HRA'].upper() != 'FALSE':
        lst_hra = dct_structure['json_rules']['HRA'].split('-')
        # for int_hra_per in range(int(lst_hra[0])):
        if lst_hra[0]:
            int_hra_per = lst_hra[0]
            dct_prv_data = {}
            dct_prv_data = copy.deepcopy(dct_data)
            bln_flag = False
            dct_data['HRA'] = round((dbl_gross*(float(int_hra_per)/100)) * ((int_max_days - dbl_leave_taken)/int_max_days), 0) # HRA Percentage of Gross Percentage
            if round(dbl_gross - (dct_data['BP_DA']+dct_data['HRA']+dct_data['CCA']+dct_data['WA']),0)>=0:
                dct_prv_data = copy.deepcopy(dct_data)
            if dct_structure['json_rules'].get('CCA') and dct_structure['json_rules']['CCA'].upper() != 'FALSE':
                lst_cca = dct_structure['json_rules']['CCA'].split('-')
                # for int_cca_per in range(int(lst_cca[0])):
                if lst_cca[0]:
                    int_cca_per = lst_cca[0]
                    dct_data['CCA'] = round((dbl_gross*(float(int_cca_per)/100)) * ((int_max_days - dbl_leave_taken)/int_max_days), 0) # CCA Percentage of Gross Percentage
                    if round(dbl_gross - (dct_data['BP_DA']+dct_data['HRA']+dct_data['CCA']+dct_data['WA']),0)>=0:
                        dct_prv_data = copy.deepcopy(dct_data)
                    if dct_structure['json_rules'].get('WA') and dct_structure['json_rules']['WA'].upper() != 'FALSE' and dct_allowances.get('bln_esi') == True:
                        lst_wa = dct_structure['json_rules']['WA'].split('-')
                        # for int_wa_per in range(int(lst_wa[0])):
                        if lst_wa[0]:
                            int_wa_per = lst_wa[0]
                            dct_data['WA'] = round(((dbl_gross * ((int_max_days - dbl_leave_taken)/int_max_days))*(float(int_wa_per)/100)) * ((int_max_days - dbl_leave_taken)/int_max_days), 0)
                            if dbl_gross-dct_data['WA'] < 21000:
                                pass
                    if dct_structure['json_rules'].get('SA') and dct_structure['json_rules']['SA']:
                        dct_data['SA'] = round(dbl_gross - (dct_data['BP_DA']+dct_data['HRA']+dct_data['CCA']+dct_data['WA']), 0) # Balance
                    if dct_data['SA']<0:
                        dct_data = dct_prv_data
                        bln_flag = True

                    # Allowances and Deductions
                    # --------WWF----------
                    if dct_allowances.get('bln_wwf') == True:
                        dct_data['Deductions']['WWF'] = dct_structure['json_rules'].get('Deductions').get('WWF')
                        dct_data['Allowances']['WWF'] = dct_structure['json_rules'].get('Allowances').get('WWF')

                    # --------PF----------
                    if dct_allowances.get('bln_pf') == True:
                        # take min of HRA
                        if dbl_gross-dct_data['HRA'] >15000:
                            dct_data['Deductions']['PF'] = round((15000)*((dct_structure['json_rules']['Deductions']['PF'])/100),0)
                            dct_data['Allowances']['PF'] = round((15000)*((dct_structure['json_rules']['Allowances']['PF'])/100),0)
                        else:
                            dct_data['Deductions']['PF'] = round((dbl_gross-dct_data['HRA'])*((dct_structure['json_rules']['Deductions']['PF'])/100),0)
                            dct_data['Allowances']['PF'] = round((dbl_gross-dct_data['HRA'])*((dct_structure['json_rules']['Allowances']['PF'])/100),0)

                    # --------ESI----------
                    if dct_allowances.get('bln_esi') == True and dbl_gross-dct_data['WA'] <21000:
                        dct_data['Deductions']['ESI'] = math.ceil((dbl_gross-dct_data['WA'])*((dct_structure['json_rules']['Deductions']['ESI'])/100))
                        dct_data['Allowances']['ESI'] = round((dbl_gross-dct_data['WA'])*((dct_structure['json_rules']['Allowances']['ESI'])/100),0)

                    if dct_data['Allowances']['ESI'] == 0.0 and dct_data['Deductions']['ESI'] == 0.0 and dct_allowances.get('bln_esi') == True and dct_structure['json_rules'].get('WA') and dct_structure['json_rules']['WA'].upper() != 'FALSE':
                        dct_data['WA'] = round(dbl_gross*(float(dct_structure['json_rules']['WA'].split('-')[0])/100)) # WA Percentage of Gross
                    # --------Gratuity----------
                    if dct_allowances.get('bln_gratuity') == True and dct_structure['json_rules']['Allowances']['Gratuity'].upper() != 'FALSE':
                        dct_data['Allowances']['Gratuity'] = round(dct_data['BP_DA']/26*15/12,0)

                    if bln_flag:
                        # bln_flag=False
                        pass
            else:
                if dct_structure['json_rules'].get('WA') and dct_structure['json_rules']['WA'].upper() != 'FALSE' and dct_allowances.get('bln_esi') == True:
                    lst_wa = dct_structure['json_rules']['WA'].split('-')
                    for int_wa_per in range(int(lst_wa[0]),int(lst_wa[-1])+1):
                        dct_data['WA'] = round((dbl_gross*(float(int_wa_per)/100)) * ((int_max_days - dbl_leave_taken)/int_max_days), 0)
                        if dbl_gross-dct_data['WA'] < 21000:
                            pass
                if dct_structure['json_rules'].get('SA') and dct_structure['json_rules']['SA']:
                    dct_data['SA'] = round(dbl_gross - (dct_data['BP_DA']+dct_data['HRA']+dct_data['CCA']+dct_data['WA']), 0) # Balance
                if dct_data['SA']<0:
                    dct_data = dct_prv_data
                    bln_flag = True

                # Allowances and Deductions
                # --------WWF----------
                if dct_allowances.get('bln_wwf') == True:
                    dct_data['Deductions']['WWF'] = dct_structure['json_rules'].get('Deductions').get('WWF')
                    dct_data['Allowances']['WWF'] = dct_structure['json_rules'].get('Allowances').get('WWF')

                # --------PF----------
                if dct_allowances.get('bln_pf') == True:
                    # take min of HRA
                    if dbl_gross-dct_data['HRA'] >15000:
                        dct_data['Deductions']['PF'] = round((15000)*((dct_structure['json_rules']['Deductions']['PF'])/100),0)
                        dct_data['Allowances']['PF'] = round((15000)*((dct_structure['json_rules']['Allowances']['PF'])/100),0)
                    else:
                        dct_data['Deductions']['PF'] = round((dbl_gross-dct_data['HRA'])*((dct_structure['json_rules']['Deductions']['PF'])/100),0)
                        dct_data['Allowances']['PF'] = round((dbl_gross-dct_data['HRA'])*((dct_structure['json_rules']['Allowances']['PF'])/100),0)

                # --------ESI----------
                if dct_allowances.get('bln_esi') == True and dbl_gross-dct_data['WA'] <21000:
                    dct_data['Deductions']['ESI'] = math.ceil((dbl_gross-dct_data['WA'])*((dct_structure['json_rules']['Deductions']['ESI'])/100))
                    dct_data['Allowances']['ESI'] = round((dbl_gross-dct_data['WA'])*((dct_structure['json_rules']['Allowances']['ESI'])/100),0)

                if dct_data['Allowances']['ESI'] == 0.0 and dct_data['Deductions']['ESI'] == 0.0 and dct_allowances.get('bln_esi') == True and dct_structure['json_rules'].get('WA') and dct_structure['json_rules']['WA'].upper() != 'FALSE':
                    dct_data['WA'] = round(dbl_gross*(float(dct_structure['json_rules']['WA'].split('-')[0])/100),0) # WA Percentage of Gross
                # --------Gratuity----------
                if dct_allowances.get('bln_gratuity') == True and dct_structure['json_rules']['Allowances']['Gratuity'].upper() != 'FALSE':
                    dct_data['Allowances']['Gratuity'] = round(dct_data['BP_DA']/26*15/12,0)

                if bln_flag:
                    pass
            # if bln_flag:
            #     break
    else:
        if dct_structure['json_rules'].get('CCA') and dct_structure['json_rules']['CCA'].upper() != 'FALSE':
            lst_cca = dct_structure['json_rules']['CCA'].split('-')
            # for int_cca_per in range(int(lst_cca[0]),int(lst_cca[-1])+1):
            if lst_cca[0]:
                int_cca_per = lst_cca[0]
                bln_flag = False
                dct_prv_data = {}
                dct_prv_data = copy.deepcopy(dct_data)

                dct_data['CCA'] = round((dbl_gross*(float(int_cca_per)/100)) * ((int_max_days - dbl_leave_taken)/int_max_days), 0) # CCA Percentage of Basic Pay + D.A Percentage
                if round(dbl_gross - (dct_data['BP_DA']+dct_data['HRA']+dct_data['CCA']+dct_data['WA']),0)>=0:
                    dct_prv_data = copy.deepcopy(dct_data)
                if dct_structure['json_rules'].get('WA') and dct_structure['json_rules']['WA'].upper() != 'FALSE' and dct_allowances.get('bln_esi') == True:
                    lst_wa = dct_structure['json_rules']['WA'].split('-')
                    # for int_wa_per in range(int(lst_wa[0]),int(lst_wa[-1])+1):
                    if lst_wa[0]:
                        int_wa_per = lst_wa[0]
                        dct_data['WA'] = round((dbl_gross*(float(int_wa_per)/100)) * ((int_max_days - dbl_leave_taken)/int_max_days), 0)
                        if dbl_gross-dct_data['WA'] < 21000:
                            pass
                if dct_structure['json_rules'].get('SA') and dct_structure['json_rules']['SA']:
                    dct_data['SA'] = round(dbl_gross - (dct_data['BP_DA']+dct_data['HRA']+dct_data['CCA']+dct_data['WA']), 0) # Balance
                if dct_data['SA']<0:
                    dct_data = dct_prv_data
                    bln_flag = True

                # Allowances and Deductions
                # --------WWF----------
                if dct_allowances.get('bln_wwf') == True:
                    dct_data['Deductions']['WWF'] = dct_structure['json_rules'].get('Deductions').get('WWF')
                    dct_data['Allowances']['WWF'] = dct_structure['json_rules'].get('Allowances').get('WWF')

                # --------PF----------
                if dct_allowances.get('bln_pf') == True:
                    # take min of HRA
                    if dbl_gross-dct_data['HRA'] >15000:
                        dct_data['Deductions']['PF'] = round((15000)*((dct_structure['json_rules']['Deductions']['PF'])/100),0)
                        dct_data['Allowances']['PF'] = round((15000)*((dct_structure['json_rules']['Allowances']['PF'])/100),0)
                    else:
                        dct_data['Deductions']['PF'] = round((dbl_gross-dct_data['HRA'])*((dct_structure['json_rules']['Deductions']['PF'])/100),0)
                        dct_data['Allowances']['PF'] = round((dbl_gross-dct_data['HRA'])*((dct_structure['json_rules']['Allowances']['PF'])/100),0)

                # --------ESI----------
                if dct_allowances.get('bln_esi') == True and dbl_gross-dct_data['WA'] <21000:
                    # take a min of ESI
                    dct_data['Deductions']['ESI'] = math.ceil((dbl_gross-dct_data['WA'])*((dct_structure['json_rules']['Deductions']['ESI'])/100))
                    dct_data['Allowances']['ESI'] = round((dbl_gross-dct_data['WA'])*((dct_structure['json_rules']['Allowances']['ESI'])/100),0)

                if dct_data['Allowances']['ESI'] == 0.0 and dct_data['Deductions']['ESI'] == 0.0 and dct_allowances.get('bln_esi') == True and dct_structure['json_rules'].get('WA') and dct_structure['json_rules']['WA'].upper() != 'FALSE':
                    dct_data['WA'] = round(dbl_gross*(float(dct_structure['json_rules']['WA'].split('-')[0])/100),0) # WA Percentage of Gross
                # --------Gratuity----------
                if dct_allowances.get('bln_gratuity') == True and dct_structure['json_rules']['Allowances']['Gratuity'].upper() != 'FALSE':
                    dct_data['Allowances']['Gratuity'] = round(dct_data['BP_DA']/26*15/12,0)

                if bln_flag:
                    pass
        else:
            dct_prv_data = {}
            dct_prv_data = copy.deepcopy(dct_data)
            if dct_structure['json_rules'].get('WA') and dct_structure['json_rules']['WA'].upper() != 'FALSE' and dct_allowances.get('bln_esi') == True:
                lst_wa = dct_structure['json_rules']['WA'].split('-')
                # for int_wa_per in range(int(lst_wa[0]),int(lst_wa[-1])+1):
                if lst_wa[0]:
                    int_wa_per = lst_wa[0]
                    dct_data['WA'] = round((dbl_gross*(float(int_wa_per)/100)) * ((int_max_days - dbl_leave_taken)/int_max_days), 0)
                    if dbl_gross-dct_data['WA'] < 21000:
                        pass
            if dct_structure['json_rules'].get('SA') and dct_structure['json_rules']['SA']:
                dct_data['SA'] = round(dbl_gross - (dct_data['BP_DA']+dct_data['HRA']+dct_data['CCA']+dct_data['WA']), 0) # Balance
            if dct_data['SA']<0:
                dct_data = dct_prv_data

            # Allowances and Deductions
            # --------WWF----------
            if dct_allowances.get('bln_wwf') == True:
                dct_data['Deductions']['WWF'] = dct_structure['json_rules'].get('Deductions').get('WWF')
                dct_data['Allowances']['WWF'] = dct_structure['json_rules'].get('Allowances').get('WWF')

            # --------PF----------
            if dct_allowances.get('bln_pf') == True:
                # take min of HRA
                if dbl_gross-dct_data['HRA'] >15000:
                    dct_data['Deductions']['PF'] = round((15000)*((dct_structure['json_rules']['Deductions']['PF'])/100),0)
                    dct_data['Allowances']['PF'] = round((15000)*((dct_structure['json_rules']['Allowances']['PF'])/100),0)
                else:
                    dct_data['Deductions']['PF'] = round((dbl_gross-dct_data['HRA'])*((dct_structure['json_rules']['Deductions']['PF'])/100),0)
                    dct_data['Allowances']['PF'] = round((dbl_gross-dct_data['HRA'])*((dct_structure['json_rules']['Allowances']['PF'])/100),0)

            # --------ESI----------
            if dct_allowances.get('bln_esi') == True and dbl_gross-dct_data['WA'] <21000:
                # take a min of ESI
                dct_data['Deductions']['ESI'] = math.ceil((dbl_gross-dct_data['WA'])*((dct_structure['json_rules']['Deductions']['ESI'])/100))
                dct_data['Allowances']['ESI'] = round((dbl_gross-dct_data['WA'])*((dct_structure['json_rules']['Allowances']['ESI'])/100),0)

            if dct_data['Allowances']['ESI'] == 0.0 and dct_data['Deductions']['ESI'] == 0.0 and dct_allowances.get('bln_esi') == True and dct_structure['json_rules'].get('WA') and dct_structure['json_rules']['WA'].upper() != 'FALSE':
                dct_data['WA'] = round(dbl_gross*(float(dct_structure['json_rules']['WA'].split('-')[0])/100),0) # WA Percentage of Gross
            # --------Gratuity----------
            if dct_allowances.get('bln_gratuity') == True and dct_structure['json_rules']['Allowances']['Gratuity'].upper() != 'FALSE':
                dct_data['Allowances']['Gratuity'] = round(dct_data['BP_DA']/26*15/12,0)

    dct_data['SA'] = round(dbl_gross - (dct_data.get('BP_DA',0)+dct_data.get('HRA',0)+dct_data.get('CCA',0)+dct_data.get('WA',0)),0) # Balance
    if dct_data['SA']<0:
        dct_data['BP_DA'] = dct_data['BP_DA']+dct_data['SA']
        dct_data['SA'] = 0
        # dct_data['BP_DA'] = dbl_gross
    dct_data['Deductions']['SalaryAdvance'] = dct_structure.get('dblAdvAmount',0)
    dct_data['Deductions']['Charity'] = dct_structure.get('dblCharity',0)
    dct_data['Deductions']['TDS'] = dct_structure.get('dblTds',0)
    dbl_tot_deductions = dct_data.get('Deductions',{}).get('PF',0) + dct_data.get('Deductions',{}).get('ESI',0) + dct_data.get('Deductions',{}).get('WWF',0) + dct_data.get('Deductions',{}).get('SalaryAdvance',0) + dct_data.get('Deductions',{}).get('Charity',0) + dct_data.get('Deductions',{}).get('TDS',0)
    dbl_tot_allowances = dct_data.get('Allowances',{}).get('PF',0) + dct_data.get('Allowances',{}).get('ESI',0) + dct_data.get('Allowances',{}).get('WWF',0) + dct_data.get('Allowances',{}).get('Gratuity',0)

    dbl_net_salary = dbl_gross - dbl_tot_deductions
    dbl_cost_to_company = dbl_gross + dbl_tot_allowances
    dct_data['Net_Salary'] = round(dbl_net_salary,0)
    dct_data['Monthly_CTC'] = round(dbl_cost_to_company,0)
    return dct_data


class VariablePayAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            if request.GET.get('intVariablePayId'):
                VariablePay.objects.filter(pk_bint_id = request.GET.get('intVariablePayId')).update(int_status = 2, dat_stoped = datetime.now())
                return Response({'status':1})
            else:
                return Response({'status':0})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})
    def post(self,request):
        try:
            int_month = int(request.data['intMonthYear'].split('-')[0])
            int_year = int(request.data['intMonthYear'].split('-')[1])
            int_emp_id = request.data['intEmpId']
            if int_emp_id:
                if request.data['blnVariablePay'] and not VariablePay.objects.filter(fk_employee_id = int_emp_id, int_month = int_month, int_year = int_year):
                    VariablePay.objects.create(fk_employee_id = int_emp_id, dbl_amount = request.data['intAmount'], int_month = int_month, int_year = int_year,txt_remarks = request.data.get('strRemarks'))
                elif request.data['blnVariablePay']:
                    return Response({'status':0, 'message': 'Variable Pay Already added'})
            else:
                return Response({'status':0, 'message': 'No Employee'})
            return Response({'status':1})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


    def put(self, request):
        try:
            session = Connection()
            int_month = int(request.data['intMonthYear'].split('-')[0])
            int_year = int(request.data['intMonthYear'].split('-')[1])
            rst_variable_pay = session.query(UserDetailsSA.user_ptr_id, VariablePaySA.pk_bint_id.label('int_variable_pay_id'), UserDetailsSA.vchr_employee_code, func.concat(AuthUserSA.first_name, ' ',AuthUserSA.last_name).label('strName'), VariablePaySA.dbl_amount,VariablePaySA.int_month,VariablePaySA.int_year,VariablePaySA.txt_remarks)\
                                .join(AuthUserSA, AuthUserSA.id == UserDetailsSA.user_ptr_id)\
                                .outerjoin(VariablePaySA, or_(and_(VariablePaySA.fk_employee_id == UserDetailsSA.user_ptr_id, VariablePaySA.int_month <= int_month, VariablePaySA.int_year <= int_year, VariablePaySA.int_status == 1), and_(VariablePaySA.fk_employee_id == UserDetailsSA.user_ptr_id, VariablePaySA.int_status == 2, extract('month', VariablePaySA.dat_stoped) > int_month, extract('year', VariablePaySA.dat_stoped) >= int_year)))\
                                .group_by(UserDetailsSA.user_ptr_id, VariablePaySA.pk_bint_id, UserDetailsSA.vchr_employee_code, func.concat(AuthUserSA.first_name, ' ',AuthUserSA.last_name), VariablePaySA.dbl_amount)\
                                .filter(VariablePaySA.dbl_amount != None)

            if request.data.get('intId'):
                rst_variable_pay = rst_variable_pay.filter(UserDetailsSA.user_ptr_id == request.data['intId'])
            int_user_id  = request.user.userdetails.user_ptr_id
            int_desig_id = request.user.userdetails.fk_desig_id
            int_dpt_name = request.user.userdetails.fk_department.vchr_name
            ins_hierarchy = HierarchyLevel.objects.filter(int_status=1, fk_reporting_to=int_desig_id).values('fk_designation_id')

            lst_desig = []
            for item in ins_hierarchy:
                lst_desig.append(item['fk_designation_id'])
            if int_dpt_name != 'HR & ADMIN':
                if lst_desig:
                    rst_variable_pay = rst_variable_pay.filter(UserDetailsSA.fk_desig_id.in_(lst_desig))
            lst_data = []
            for rst_data in rst_variable_pay.all():
                dct_data = {}
                dct_data['intEMPId'] = rst_data.user_ptr_id
                dct_data['strEMPCode']  = rst_data.vchr_employee_code
                dct_data['strEMPName'] = rst_data.strName
                dct_data['intVariablePayId'] = rst_data.int_variable_pay_id
                dct_data['blnVariablePay'] = False
                dct_data['intMonthYear'] = str(calendar.month_abbr[rst_data.int_month])+"' "+str(rst_data.int_year)
                if rst_data.dbl_amount:
                    dct_data['blnVariablePay'] = True
                dct_data['dblAmount'] = rst_data.dbl_amount
                if rst_data.txt_remarks:
                    dct_data['strRemarks'] = rst_data.txt_remarks
                lst_data.append(dct_data)

            if lst_data == []:
                return Response({'status':1, 'data':lst_data})
            file_name = 'VariablePayReport/Variable_Pay_Report_' + datetime.strftime(date.today(), "%d-%m-%Y") + '.xlsx'
            if path.exists(file_name):
                os.remove(file_name)
            if not path.exists(settings.MEDIA_ROOT + '/VariablePayReport/'):
                os.mkdir(settings.MEDIA_ROOT + '/VariablePayReport/')
            writer = pd.ExcelWriter(settings.MEDIA_ROOT + '/' + file_name, engine ='xlsxwriter')
            workbook = writer.book
            worksheet = workbook.add_worksheet()

            title_style = workbook.add_format({'font_size':14, 'bold':1, 'align': 'center', 'border':1})
            title_style.set_align('vcenter')
            title_style.set_pattern(1)
            title_style.set_bg_color('#ffe0cc')
            # worksheet.merge_range('A1:P1', 'ESI Report ('+calendar.month_name[int_month]+' '+str(int_year)+')', title_style)
            worksheet.set_row(0, 30)

            head_style = workbook.add_format({'font_size':11, 'bold':1, 'align': 'center','border':1,'border_color':'#000000'})
            head_style.set_pattern(1)
            head_style.set_bg_color('#bfbfbf')
            head_style.set_align('vcenter')
            worksheet.autofilter('B2:P2')

            row_style = workbook.add_format({'font_size':11})
            row_style.set_align('vcenter')

            worksheet.protect('',{'autofilter':True})

            int_row = 1
            worksheet.write(int_row, 0, 'SL. No', head_style); worksheet.set_column(0, 0, 6)
            worksheet.write(int_row, 1, 'EMP CODE', head_style); worksheet.set_column(1, 1, 13)
            worksheet.write(int_row, 2, 'EMP NAME', head_style); worksheet.set_column(2, 2, 30)
            worksheet.write(int_row, 3, 'AMOUNT', head_style); worksheet.set_column(3, 3, 15)
            worksheet.write(int_row, 4, 'START DATE', head_style); worksheet.set_column(4, 4, 20)
            worksheet.set_row(int_row, 13)

            for ins_data in lst_data:
                int_row += 1
                worksheet.write(int_row, 0, int_row-1, row_style)
                worksheet.write(int_row, 1, ins_data.get('strEMPCode'), row_style)
                worksheet.write(int_row, 2, ins_data.get('strEMPName'), row_style)
                worksheet.write(int_row, 3, ins_data.get('dblAmount'), row_style)
                worksheet.write(int_row, 4, ins_data.get('intMonthYear'), row_style)
                worksheet.set_row(int_row, 10, row_style)
            writer.save()
            return Response({'status':1, 'data':lst_data,'report':request.scheme+'://'+request.get_host()+settings.MEDIA_URL+file_name})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})

    def patch(self, request):
        try:
            int_month = 0
            int_year = 0
            int_emp_id = 0
            if request.data.get('intMonthYear'):
                int_month = int(request.data['intMonthYear'].split('-')[0])
                int_year = int(request.data['intMonthYear'].split('-')[1])
                int_emp_id = request.data['intEmpId']

            if request.data.get('blnVariablePay') and VariablePay.objects.filter(pk_bint_id = request.data['intVariablePayId']):
                VariablePay.objects.filter(pk_bint_id = request.data['intVariablePayId']).update(dbl_amount = request.data['intAmount'], int_month = int_month, int_year = int_year,txt_remarks = request.data.get('strRemarks'))
            elif request.data.get('blnVariablePay'):
                VariablePay.objects.create(fk_employee_id = int_emp_id, dbl_amount = request.data['intAmount'], int_month = int_month, int_year = int_year)
            else:
                VariablePay.objects.filter(pk_bint_id = request.data['intVariablePayId']).update(int_status = 0)
            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


class SalaryProcessSplit(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            int_emp_id = request.data.get('intEMPId')
            int_month = request.data.get('intMonth')
            int_year = request.data.get('intYear')
            now_date = datetime.now()

            dur_calendar = calendar.monthrange(int_year, int_month)
            str_start_date = str(int_year)+'-'+str(int_month)+'-1'
            str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(dur_calendar[1])

            if not request.user.is_superuser:
                ins_admin = AdminSettings.objects.filter(vchr_code='PAYROLL_PERIOD',bln_enabled=True,fk_company_id=request.user.userdetails.fk_company_id).values('vchr_value', 'int_value').first()
                if ins_admin and ins_admin['int_value'] != 0:
                    str_start_date = datetime.strftime(datetime.strptime(str(int_year)+'-'+str(int_month)+'-'+ins_admin['vchr_value'][0],'%Y-%m-%d')+timedelta(days=int(ins_admin['vchr_value'][0])*ins_admin['int_value']),'%Y-%m-')+ins_admin['vchr_value'][0]
                    str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(int(ins_admin['vchr_value'][0])-1)

            if int_month == now_date.month and int_year == now_date.year and now_date.day <= int(str_end_date.split('-')[2]):
                str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(now_date.day)
            str_filter = ' AND ud.user_ptr_id = '+str(int_emp_id)

            rst_data = AllSalaryDetails(request, str(int_month)+'-'+str(int_year), str_start_date, str_end_date, str_filter)
            if not rst_data:
                return Response({'status':0,'reason':'No Data'})
            return Response({'status':1, 'data':rst_data[0]})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


class SalaryReportView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            int_cat_id = request.data.get('intCategoryId')
            int_month = int(request.data.get('intMonthYear').split('-')[0])
            int_year = int(request.data.get('intMonthYear').split('-')[1])
            now_date = datetime.now()

            dur_calendar = calendar.monthrange(int_year, int_month)
            str_start_date = str(int_year)+'-'+str(int_month)+'-1'
            str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(dur_calendar[1])

            if not request.user.is_superuser:
                ins_admin = AdminSettings.objects.filter(vchr_code='PAYROLL_PERIOD',bln_enabled=True,fk_company_id=request.user.userdetails.fk_company_id).values('vchr_value', 'int_value').first()
                if ins_admin and ins_admin['int_value'] != 0:
                    str_start_date = datetime.strftime(datetime.strptime(str(int_year)+'-'+str(int_month)+'-'+ins_admin['vchr_value'][0],'%Y-%m-%d')+timedelta(days=int(ins_admin['vchr_value'][0])*ins_admin['int_value']),'%Y-%m-')+ins_admin['vchr_value'][0]
                    str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(int(ins_admin['vchr_value'][0])-1)

            if int_month == now_date.month and int_year == now_date.year and now_date.day <= int(str_end_date.split('-')[2]):
                str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(now_date.day)

            str_filter = ''
            if int_cat_id:
                str_filter += ' AND cat.pk_bint_id = '+str(int_cat_id)
            if request.data.get('lstDesignation'):
                str_filter += ' AND desig.pk_bint_id IN ('+str(request.data.get('lstDesignation'))[1:-1]+')'
            if request.data.get('intDepartmentId'):
                str_filter += ' AND dept.pk_bint_id = '+str(request.data.get('intDepartmentId'))
            if request.data.get('lstBranch'):
                str_filter += ' AND brnch.pk_bint_id IN ('+str(request.data.get('lstBranch'))[1:-1]+')'
            if request.data.get('intSalaryFrom'):
                str_filter += ' AND ud.dbl_gross >= '+str(request.data.get('intSalaryFrom'))
            if request.data.get('intSalaryTo'):
                str_filter += ' AND ud.dbl_gross <= '+str(request.data.get('intSalaryTo'))

            if request.data.get('strPFType') == 'withPF':
                str_filter += " AND (slrydtl.json_deduction->>'PF')::float != 0.0"
                if request.data.get('intPFNumber'):
                    str_filter += " AND ud.vchr_uan_no = '"+str(request.data.get('intPFNumber'))+"'"
            elif request.data.get('strPFType') == 'withoutPF':
                str_filter += " AND (slrydtl.json_deduction->>'PF')::float = 0.0"

            if request.data.get('strESIType') == 'withESI':
                str_filter += " AND (slrydtl.json_deduction->>'ESI')::float != 0.0"
                if request.data.get('intESINumber'):
                    str_filter += " AND ud.vchr_esi_no = '"+str(request.data.get('intESINumber'))+"'"
            elif request.data.get('strESIType') == 'withoutESI':
                str_filter += " AND (slrydtl.json_deduction->>'ESI')::float = 0.0"

            if request.data.get('strWWFType') == 'withWWF':
                str_filter += " AND (slrydtl.json_deduction->>'WWF')::float != 0.0"
                if request.data.get('intWWFNumber'):
                    str_filter += " AND ud.vchr_wwf_no = '"+str(request.data.get('intWWFNumber'))+"'"
            elif request.data.get('strWWFType') == 'withoutWWF':
                str_filter += " AND (slrydtl.json_deduction->>'WWF')::float = 0.0"

            int_days = 30
            lst_data = AllSalaryDetails(request, str(int_month)+'-'+str(int_year), str_start_date, str_end_date, str_filter, int_days)
            if not lst_data:
                return Response({'status':0,'reason':'No Data'})

            file_name = 'SalaryReport/Salary_Report_' + datetime.strftime(date.today(), "%d-%m-%Y") + '.xlsx'
            if path.exists(file_name):
                os.remove(file_name)
            if not path.exists(settings.MEDIA_ROOT + '/SalaryReport/'):
                os.mkdir(settings.MEDIA_ROOT + '/SalaryReport/')
            writer = pd.ExcelWriter(settings.MEDIA_ROOT + '/' + file_name, engine ='xlsxwriter')
            workbook = writer.book
            worksheet = workbook.add_worksheet()

            title_style = workbook.add_format({'font_size':14, 'bold':1, 'align': 'center', 'border':1})
            title_style.set_align('vcenter')
            title_style.set_pattern(1)
            title_style.set_bg_color('#ffe0cc')
            worksheet.merge_range('A1+:AX1', 'Salary Report ('+calendar.month_name[int_month]+' '+str(int_year)+')', title_style)
            worksheet.set_row(0, 30)

            head_style = workbook.add_format({'font_size':11, 'bold':1, 'align': 'center','border':1,'border_color':'#000000'})
            head_style.set_pattern(1)
            head_style.set_bg_color('#bfbfbf')
            head_style.set_align('vcenter')
            worksheet.autofilter('B2:AX2')

            row_style = workbook.add_format({'font_size':11})
            row_style.set_align('vcenter')
            worksheet.protect('',{'autofilter':True})

            int_row = 1
            worksheet.write(int_row, 0, 'SL. No', head_style); worksheet.set_column(0, 0, 6)
            worksheet.write(int_row, 1, 'EMP CODE', head_style); worksheet.set_column(1, 1, 13)
            worksheet.write(int_row, 2, 'EMP NAME', head_style)
            worksheet.write(int_row, 3, 'BRANCH', head_style); worksheet.set_column(2, 3, 30)
            worksheet.write(int_row, 4, 'DEPARTMENT', head_style); worksheet.set_column(4, 4, 35)
            worksheet.write(int_row, 5, 'DESIGNATION', head_style); worksheet.set_column(5, 5, 30)
            worksheet.write(int_row, 6, 'PAYROLL GROUP', head_style); worksheet.set_column(6, 6, 18)
            worksheet.write(int_row, 7, 'DOJ', head_style); worksheet.set_column(7, 7, 13)
            worksheet.write(int_row, 8, 'BASIC PAY + DA', head_style); worksheet.set_column(8, 8, 18)
            worksheet.write(int_row, 9, 'HRA', head_style)
            worksheet.write(int_row, 10, 'CCA', head_style)
            worksheet.write(int_row, 11, 'WA', head_style); worksheet.set_column(9, 11, 10)
            worksheet.write(int_row, 12, 'SPEC ALLO', head_style)
            worksheet.write(int_row, 13, 'GROSS PAY', head_style); worksheet.set_column(12, 13, 13)
            worksheet.write(int_row, 14, 'PF ER', head_style)
            worksheet.write(int_row, 15, 'ESI ER', head_style)
            worksheet.write(int_row, 16, 'WWF ER', head_style); worksheet.set_column(14, 16, 11)
            worksheet.write(int_row, 17, 'GRATUITY', head_style)
            worksheet.write(int_row, 18, 'VARIABLE PAY', head_style)
            worksheet.write(int_row, 19, 'CTC WITH VP', head_style); worksheet.set_column(17, 19, 17)
            worksheet.write(int_row, 20, 'LOP', head_style); worksheet.set_column(20, 20, 8)
            worksheet.write(int_row, 21, 'ACTUAL', head_style); worksheet.set_column(21, 21, 10)
            worksheet.write(int_row, 22, 'NWD', head_style); worksheet.set_column(22, 22, 8)
            worksheet.write(int_row, 23, 'BASIC PAY + DA', head_style); worksheet.set_column(23, 23, 18)
            worksheet.write(int_row, 24, 'HRA', head_style)
            worksheet.write(int_row, 25, 'CCA', head_style)
            worksheet.write(int_row, 26, 'WA', head_style); worksheet.set_column(24, 26, 10)
            worksheet.write(int_row, 27, 'SPEC ALLO', head_style)
            worksheet.write(int_row, 28, 'GROSS PAY', head_style); worksheet.set_column(27, 28, 13)
            worksheet.write(int_row, 29, 'FIXED ALLOWANCE', head_style)
            worksheet.write(int_row, 30, 'VARIABLE PAY', head_style)
            worksheet.write(int_row, 31, 'TOTAL GROSS', head_style); worksheet.set_column(29, 31, 17)
            worksheet.write(int_row, 32, 'PF SALARY', head_style); worksheet.set_column(32, 32, 13)
            worksheet.write(int_row, 33, 'PF EE', head_style); worksheet.set_column(33, 33, 11)
            worksheet.write(int_row, 34, 'ESI SALARY', head_style); worksheet.set_column(34, 34, 13)
            worksheet.write(int_row, 35, 'ESI EE', head_style)
            worksheet.write(int_row, 36, 'WWF EE', head_style); worksheet.set_column(35, 36, 11)
            worksheet.write(int_row, 37, 'MOBILE LOAN', head_style);
            worksheet.write(int_row, 38, 'WORK LOAN', head_style); worksheet.set_column(37, 38, 16)
            worksheet.write(int_row, 39, 'SALARY ADVANCE', head_style); worksheet.set_column(39, 39, 19)
            worksheet.write(int_row, 40, 'CHARITY', head_style); worksheet.set_column(40, 40, 13)
            worksheet.write(int_row, 41, 'TDS', head_style)
            worksheet.write(int_row, 42, 'P TAX', head_style); worksheet.set_column(41, 42, 11)
            worksheet.write(int_row, 43, 'TOTAL DEDU', head_style); worksheet.set_column(43, 43, 14)
            worksheet.write(int_row, 44, 'NET PAY', head_style)
            worksheet.write(int_row, 45, 'PF ER', head_style)
            worksheet.write(int_row, 46, 'ESI ER', head_style)
            worksheet.write(int_row, 47, 'WWF ER', head_style); worksheet.set_column(44, 47, 11)
            worksheet.write(int_row, 48, 'GRATUITY', head_style);
            worksheet.write(int_row, 49, 'CTC', head_style); worksheet.set_column(47, 49, 15)
            worksheet.set_row(int_row, 23)
            for ins_data in lst_data:
                int_row += 1
                worksheet.write(int_row, 0, int_row-1, row_style)
                worksheet.write(int_row, 1, ins_data.get('str_employee_code'), row_style)
                worksheet.write(int_row, 2, ins_data.get('str_emp_name'), row_style)
                worksheet.write(int_row, 3, ins_data.get('str_branch'), row_style)
                worksheet.write(int_row, 4, ins_data.get('str_department'), row_style)
                worksheet.write(int_row, 5, ins_data.get('str_designation'), row_style)
                worksheet.write(int_row, 6, ins_data.get('str_category_name'), row_style)
                worksheet.write(int_row, 7, datetime.strftime(ins_data.get('dat_joined'), '%d-%m-%Y') if ins_data.get('dat_joined') else '', row_style)
                worksheet.write(int_row, 8, ins_data.get('dbl_bp'), row_style)
                worksheet.write(int_row, 9, ins_data.get('dbl_hra'), row_style)
                worksheet.write(int_row, 10, ins_data.get('dbl_cca'), row_style)
                worksheet.write(int_row, 11, ins_data.get('dbl_wa'), row_style)
                worksheet.write(int_row, 12, ins_data.get('dbl_sa'), row_style)
                worksheet.write(int_row, 13, ins_data.get('dbl_gross'), row_style)
                worksheet.write(int_row, 14, ins_data.get('json_allowance',{}).get('PF',0.0), row_style)
                worksheet.write(int_row, 15, ins_data.get('json_allowance',{}).get('ESI',0.0), row_style)
                worksheet.write(int_row, 16, ins_data.get('json_allowance',{}).get('WWF',0.0), row_style)
                worksheet.write(int_row, 17, ins_data.get('json_allowance',{}).get('Gratuity',0.0), row_style)
                worksheet.write(int_row, 18, ins_data.get('VariablePay',0.0), row_style)
                worksheet.write(int_row, 19, ins_data.get('dbl_monthly_ctc',0.0) + ins_data.get('VariablePay',0.0), row_style)
                worksheet.write(int_row, 20, ins_data.get('dbl_tot_lop'), row_style)
                worksheet.write(int_row, 21, int_days, row_style)
                worksheet.write(int_row, 22, int_days - ins_data.get('dbl_tot_lop'), row_style)
                worksheet.write(int_row, 23, ins_data.get('BP_DA'), row_style)
                worksheet.write(int_row, 24, ins_data.get('HRA'), row_style)
                worksheet.write(int_row, 25, ins_data.get('CCA'), row_style)
                worksheet.write(int_row, 26, ins_data.get('WA'), row_style)
                worksheet.write(int_row, 27, ins_data.get('SA'), row_style)
                worksheet.write(int_row, 28, ins_data.get('GROSS'), row_style)
                worksheet.write(int_row, 29, ins_data.get('FixedAllowance', 0.0), row_style)
                worksheet.write(int_row, 30, ins_data.get('VariablePay',0.0), row_style)
                worksheet.write(int_row, 31, ins_data.get('GROSS')+ins_data.get('VariablePay',0.0)+ins_data.get('FixedAllowance', 0.0), row_style)
                worksheet.write(int_row, 32, ins_data.get('PF_SALARY'), row_style)
                worksheet.write(int_row, 33, ins_data.get('Deductions',{}).get('PF') if ins_data.get('Deductions',{}).get('PF') else 0.0, row_style)
                worksheet.write(int_row, 34, ins_data.get('ESI_SALARY'), row_style)
                worksheet.write(int_row, 35, ins_data.get('Deductions',{}).get('ESI') if ins_data.get('Deductions',{}).get('ESI') else 0.0, row_style)
                worksheet.write(int_row, 36, ins_data.get('Deductions',{}).get('WWF') if ins_data.get('Deductions',{}).get('WWF') else 0.0, row_style)
                worksheet.write(int_row, 37, ins_data.get('Deductions',{}).get('MobileLoan') if ins_data.get('Deductions',{}).get('MobileLoan') else 0.0, row_style)
                worksheet.write(int_row, 38, ins_data.get('Deductions',{}).get('WorkLoan') if ins_data.get('Deductions',{}).get('WorkLoan') else 0.0, row_style)
                worksheet.write(int_row, 39, ins_data.get('Deductions',{}).get('SalaryAdvance') if ins_data.get('Deductions',{}).get('SalaryAdvance') else 0.0, row_style)
                worksheet.write(int_row, 40, ins_data.get('Deductions',{}).get('Charity') if ins_data.get('Deductions',{}).get('Charity') else 0.0, row_style)
                worksheet.write(int_row, 41, ins_data.get('Deductions',{}).get('TDS') if ins_data.get('Deductions',{}).get('TDS') else 0.0, row_style)
                worksheet.write(int_row, 42, ins_data.get('Deductions',{}).get('ProTax') if ins_data.get('Deductions',{}).get('ProTax') else 0.0, row_style)
                worksheet.write(int_row, 43, ins_data.get('Tot_Deduction'), row_style)
                worksheet.write(int_row, 44, ins_data.get('Net_Salary'), row_style)
                worksheet.write(int_row, 45, ins_data.get('Allowances',{}).get('PF') if ins_data.get('Allowances',{}).get('PF') else 0.0, row_style)
                worksheet.write(int_row, 46, ins_data.get('Allowances',{}).get('ESI') if ins_data.get('Allowances',{}).get('ESI') else 0.0, row_style)
                worksheet.write(int_row, 47, ins_data.get('Allowances',{}).get('WWF') if ins_data.get('Allowances',{}).get('WWF') else 0.0, row_style)
                worksheet.write(int_row, 48, ins_data.get('Allowances',{}).get('Gratuity') if ins_data.get('Allowances',{}).get('Gratuity') else 0.0, row_style)
                worksheet.write(int_row, 49, ins_data.get('Monthly_CTC'), row_style)
                worksheet.set_row(int_row, 20, row_style)
            writer.save()
            return Response({'status':1, 'data':request.scheme+'://'+request.get_host()+settings.MEDIA_URL+file_name})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


class EmpSalaryReportView(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            int_cat_id = request.data.get('intCategoryId')
            int_month = int(request.data.get('intMonthYear').split('-')[0])
            int_year = int(request.data.get('intMonthYear').split('-')[1])
            now_date = datetime.now()

            dur_calendar = calendar.monthrange(int_year, int_month)
            str_start_date = str(int_year)+'-'+str(int_month)+'-1'
            str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(dur_calendar[1])

            if not request.user.is_superuser:
                ins_admin = AdminSettings.objects.filter(vchr_code='PAYROLL_PERIOD',bln_enabled=True,fk_company_id=request.user.userdetails.fk_company_id).values('vchr_value', 'int_value').first()
                if ins_admin and ins_admin['int_value'] != 0:
                    str_start_date = datetime.strftime(datetime.strptime(str(int_year)+'-'+str(int_month)+'-'+ins_admin['vchr_value'][0],'%Y-%m-%d')+timedelta(days=int(ins_admin['vchr_value'][0])*ins_admin['int_value']),'%Y-%m-')+ins_admin['vchr_value'][0]
                    str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(int(ins_admin['vchr_value'][0])-1)

            if int_month == now_date.month and int_year == now_date.year and now_date.day <= int(str_end_date.split('-')[2]):
                str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(now_date.day)

            dat_month_last = datetime.strptime(str_end_date, '%Y-%m-%d')
            dat_month_first = datetime.strptime(str_start_date, '%Y-%m-%d')

            str_filter = ''
            if int_cat_id:
                str_filter += ' AND cat.pk_bint_id = '+str(int_cat_id)
            if request.data.get('lstDesignation'):
                str_filter += ' AND desig.pk_bint_id IN ('+str(request.data.get('lstDesignation'))[1:-1]+')'
            if request.data.get('intDepartmentId'):
                str_filter += ' AND dept.pk_bint_id = '+str(request.data.get('intDepartmentId'))
            if request.data.get('lstBranch'):
                str_filter += ' AND brnch.pk_bint_id IN ('+str(request.data.get('lstBranch'))[1:-1]+')'
            if request.data.get('intSalaryFrom'):
                str_filter += ' AND ud.dbl_gross >= '+str(request.data.get('intSalaryFrom'))
            if request.data.get('intSalaryTo'):
                str_filter += ' AND ud.dbl_gross <= '+str(request.data.get('intSalaryTo'))

            if request.data.get('strPFType') == 'withPF':
                str_filter += " AND (ud.json_allowance->>'bln_pf')::BOOLEAN=TRUE"
                if request.data.get('intPFNumber'):
                    str_filter += " AND ud.vchr_uan_no = '"+str(request.data.get('intPFNumber'))+"'"
            elif request.data.get('strPFType') == 'withoutPF':
                str_filter += " AND (ud.json_allowance->>'bln_pf')::BOOLEAN=FALSE"

            if request.data.get('strESIType') == 'withESI':
                str_filter += " AND (ud.json_allowance->>'bln_esi')::BOOLEAN=TRUE"
                if request.data.get('intESINumber'):
                    str_filter += " AND ud.vchr_esi_no = '"+str(request.data.get('intESINumber'))+"'"
            elif request.data.get('strESIType') == 'withoutESI':
                str_filter += " AND (ud.json_allowance->>'bln_esi')::BOOLEAN=FALSE"

            if request.data.get('strWWFType') == 'withWWF':
                str_filter += " AND (ud.json_allowance->>'bln_wwf')::BOOLEAN=TRUE"
                if request.data.get('intWWFNumber'):
                    str_filter += " AND ud.vchr_wwf_no = '"+str(request.data.get('intWWFNumber'))+"'"
            elif request.data.get('strWWFType') == 'withoutWWF':
                str_filter += " AND (ud.json_allowance->>'bln_wwf')::BOOLEAN=FALSE"

            lst_data = AllSalaryDetails(request, str(int_month)+'-'+str(int_year), str_start_date, str_end_date, str_filter)
            if not lst_data:
                return Response({'status':0,'reason':'No Data'})

            file_name = 'EmployeeSalaryReport/Emp_Salary_Report_' + datetime.strftime(date.today(), "%d-%m-%Y") + '.xlsx'
            if path.exists(file_name):
                os.remove(file_name)
            if not path.exists(settings.MEDIA_ROOT + '/EmployeeSalaryReport/'):
                os.mkdir(settings.MEDIA_ROOT + '/EmployeeSalaryReport/')
            writer = pd.ExcelWriter(settings.MEDIA_ROOT + '/' + file_name, engine ='xlsxwriter')
            workbook = writer.book
            worksheet = workbook.add_worksheet()

            title_style = workbook.add_format({'font_size':14, 'bold':1, 'align': 'center', 'border':1})
            title_style.set_align('vcenter')
            title_style.set_pattern(1)
            title_style.set_bg_color('#ffe0cc')
            worksheet.merge_range('A1+:AH1', 'Employee Salary Report ('+calendar.month_name[int_month]+' '+str(int_year)+')', title_style)
            worksheet.set_row(0, 30)

            head_style = workbook.add_format({'font_size':11, 'bold':1, 'align': 'center','border':1,'border_color':'#000000'})
            head_style.set_pattern(1)
            head_style.set_bg_color('#bfbfbf')
            head_style.set_align('vcenter')
            worksheet.autofilter('B2:AH2')

            row_style = workbook.add_format({'font_size':11})
            row_style.set_align('vcenter')

            worksheet.protect('',{'autofilter':True})

            int_row = 1
            worksheet.write(int_row, 0, 'SL. No', head_style); worksheet.set_column(0, 0, 6)
            worksheet.write(int_row, 1, 'EMP CODE', head_style); worksheet.set_column(1, 1, 13)
            worksheet.write(int_row, 2, 'EMP NAME', head_style)
            worksheet.write(int_row, 3, 'BRANCH', head_style); worksheet.set_column(2, 3, 30)
            worksheet.write(int_row, 4, 'DEPARTMENT', head_style); worksheet.set_column(4, 4, 35)
            worksheet.write(int_row, 5, 'DESIGNATION', head_style); worksheet.set_column(5, 5, 30)
            worksheet.write(int_row, 6, 'PAYROLL GROUP', head_style); worksheet.set_column(6, 6, 20)
            worksheet.write(int_row, 7, 'DOJ', head_style); worksheet.set_column(7, 7, 15)
            worksheet.write(int_row, 8, 'BASIC PAY + DA', head_style); worksheet.set_column(8, 8, 18)
            worksheet.write(int_row, 9, 'HRA', head_style)
            worksheet.write(int_row, 10, 'CCA', head_style)
            worksheet.write(int_row, 11, 'WA', head_style); worksheet.set_column(9, 11, 10)
            worksheet.write(int_row, 12, 'SPEC ALLO', head_style)
            worksheet.write(int_row, 13, 'GROSS PAY', head_style); worksheet.set_column(12, 13, 13)
            worksheet.write(int_row, 14, 'PF ER', head_style)
            worksheet.write(int_row, 15, 'ESI ER', head_style)
            worksheet.write(int_row, 16, 'WWF ER', head_style); worksheet.set_column(14, 16, 11)
            worksheet.write(int_row, 17, 'GRATUITY', head_style)
            worksheet.write(int_row, 18, 'VARIABLE PAY', head_style)
            worksheet.write(int_row, 19, 'CTC WITH VP', head_style); worksheet.set_column(17, 19, 17)

            worksheet.write(int_row, 20, 'FIXED ALLOWANCE', head_style)
            worksheet.write(int_row, 21, 'TOTAL GROSS', head_style); worksheet.set_column(20, 21, 17)
            worksheet.write(int_row, 22, 'PF SALARY', head_style); worksheet.set_column(22, 22, 13)
            worksheet.write(int_row, 23, 'PF', head_style)
            worksheet.write(int_row, 24, 'ESI', head_style)
            worksheet.write(int_row, 25, 'WWF', head_style); worksheet.set_column(23, 25, 11)

            worksheet.write(int_row, 26, 'MOBILE LOAN', head_style); worksheet.set_column(26, 26, 16)
            worksheet.write(int_row, 27, 'SALARY ADVANCE', head_style); worksheet.set_column(27, 27, 19)
            worksheet.write(int_row, 28, 'CHARITY', head_style); worksheet.set_column(28, 28, 13)
            worksheet.write(int_row, 29, 'TDS', head_style)
            worksheet.write(int_row, 30, 'P TAX', head_style); worksheet.set_column(29, 30, 11)
            worksheet.write(int_row, 31, 'TOTAL DEDU', head_style); worksheet.set_column(31, 31, 14)
            worksheet.write(int_row, 32, 'NET PAY', head_style)

            worksheet.write(int_row, 33, 'CTC', head_style); worksheet.set_column(32, 33, 10)
            worksheet.set_row(int_row, 23)

            for ins_data in lst_data:
                int_row += 1
                worksheet.write(int_row, 0, int_row-1, row_style)
                worksheet.write(int_row, 1, ins_data.get('str_employee_code'), row_style)
                worksheet.write(int_row, 2, ins_data.get('str_emp_name'), row_style)
                worksheet.write(int_row, 3, ins_data.get('str_branch'), row_style)
                worksheet.write(int_row, 4, ins_data.get('str_department'), row_style)
                worksheet.write(int_row, 5, ins_data.get('str_designation'), row_style)
                worksheet.write(int_row, 6, ins_data.get('str_category_name'), row_style)
                worksheet.write(int_row, 7, datetime.strftime(ins_data.get('dat_joined'), '%d-%m-%Y') if ins_data.get('dat_joined') else '', row_style)
                worksheet.write(int_row, 8, ins_data.get('dbl_bp'), row_style)
                worksheet.write(int_row, 9, ins_data.get('dbl_hra'), row_style)
                worksheet.write(int_row, 10, ins_data.get('dbl_cca'), row_style)
                worksheet.write(int_row, 11, ins_data.get('dbl_wa'), row_style)
                worksheet.write(int_row, 12, ins_data.get('dbl_sa'), row_style)
                worksheet.write(int_row, 13, ins_data.get('dbl_gross'), row_style)
                worksheet.write(int_row, 14, ins_data.get('json_allowance',{}).get('PF',0.0), row_style)
                worksheet.write(int_row, 15, ins_data.get('json_allowance',{}).get('ESI',0.0), row_style)
                worksheet.write(int_row, 16, ins_data.get('json_allowance',{}).get('WWF',0.0), row_style)
                worksheet.write(int_row, 17, ins_data.get('json_allowance',{}).get('Gratuity',0.0), row_style)
                worksheet.write(int_row, 18, ins_data.get('dbl_variable_pay',0.0), row_style)
                worksheet.write(int_row, 19, ins_data.get('dbl_monthly_ctc',0.0) - ins_data.get('dbl_fixed_allowance', 0.0), row_style)

                worksheet.write(int_row, 20, ins_data.get('dbl_fixed_allowance', 0.0), row_style)
                worksheet.write(int_row, 21, ins_data.get('dbl_gross')+ins_data.get('dbl_variable_pay',0.0)+ins_data.get('dbl_fixed_allowance', 0.0), row_style)
                worksheet.write(int_row, 22, ins_data.get('dbl_pf_salary'), row_style)
                worksheet.write(int_row, 23, ins_data.get('json_deductions',{}).get('PF') if ins_data.get('json_deductions',{}).get('PF') else 0.0, row_style)
                worksheet.write(int_row, 24, ins_data.get('json_deductions',{}).get('ESI') if ins_data.get('json_deductions',{}).get('ESI') else 0.0, row_style)
                worksheet.write(int_row, 25, ins_data.get('json_deductions',{}).get('WWF') if ins_data.get('json_deductions',{}).get('WWF') else 0.0, row_style)

                worksheet.write(int_row, 26, ins_data.get('json_deductions',{}).get('MobileLoan') if ins_data.get('json_deductions',{}).get('MobileLoan') else 0.0, row_style)
                worksheet.write(int_row, 27, ins_data.get('json_deductions',{}).get('SalaryAdvance') if ins_data.get('json_deductions',{}).get('SalaryAdvance') else 0.0, row_style)
                worksheet.write(int_row, 28, ins_data.get('json_deductions',{}).get('Charity') if ins_data.get('json_deductions',{}).get('Charity') else 0.0, row_style)
                worksheet.write(int_row, 29, ins_data.get('json_deductions',{}).get('TDS') if ins_data.get('json_deductions',{}).get('TDS') else 0.0, row_style)
                worksheet.write(int_row, 30, ins_data.get('dbl_pt_amt'), row_style)
                worksheet.write(int_row, 31, ins_data.get('dbl_tot_deductions',0), row_style)
                worksheet.write(int_row, 32, ins_data.get('dbl_net_salary'), row_style)

                worksheet.write(int_row, 33, ins_data.get('dbl_monthly_ctc'), row_style)
                worksheet.set_row(int_row, 20, row_style)
            writer.save()
            return Response({'status':1, 'data':request.scheme+'://'+request.get_host()+settings.MEDIA_URL+file_name})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


class ESIReportView(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            conn = engine.connect()

            int_cat_id = request.data.get('intCategoryId')
            int_month = int(request.data.get('intMonthYear').split('-')[0])
            int_year = int(request.data.get('intMonthYear').split('-')[1])
            now_date = datetime.now()

            dur_calendar = calendar.monthrange(int_year, int_month)
            str_start_date = str(int_year)+'-'+str(int_month)+'-1'
            str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(dur_calendar[1])

            if not request.user.is_superuser:
                ins_admin = AdminSettings.objects.filter(vchr_code='PAYROLL_PERIOD',bln_enabled=True,fk_company_id=request.user.userdetails.fk_company_id).values('vchr_value', 'int_value').first()
                if ins_admin and ins_admin['int_value'] != 0:
                    str_start_date = datetime.strftime(datetime.strptime(str(int_year)+'-'+str(int_month)+'-'+ins_admin['vchr_value'][0],'%Y-%m-%d')+timedelta(days=int(ins_admin['vchr_value'][0])*ins_admin['int_value']),'%Y-%m-')+ins_admin['vchr_value'][0]
                    str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(int(ins_admin['vchr_value'][0])-1)

            if int_month == now_date.month and int_year == now_date.year and now_date.day <= int(str_end_date.split('-')[2]):
                str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(now_date.day)

            dat_month_last = datetime.strptime(str_end_date, '%Y-%m-%d')
            dat_month_first = datetime.strptime(str_start_date, '%Y-%m-%d')

            str_query = "SELECT ud.user_ptr_id,ud.vchr_employee_code,ud.vchr_esi_no,ud.dat_doj,dept.vchr_name AS str_department, desig.vchr_name AS str_designation, brnch.vchr_name AS str_branch, CONCAT(TRIM(au.first_name), ' ', CASE WHEN ud.vchr_middle_name IS NOT NULL THEN CONCAT(TRIM(ud.vchr_middle_name), ' ', TRIM(au.last_name)) ELSE TRIM(au.last_name) END) AS str_emp_name, slpcd.dbl_bp, slpcd.dbl_da, slpcd.dbl_hra, slpcd.dbl_cca, slpcd.dbl_wa, slpcd.dbl_sa, slpcd.dbl_gross, slpcd.json_allowances, slpcd.json_deductions, slpcd.dbl_net_salary, slpcd.dbl_monthly_ctc, slpcd.json_attendance FROM auth_user au JOIN user_details ud ON ud.user_ptr_id = au.id AND ud.dat_doj <= '{3}'::DATE LEFT JOIN salary_processed slpcd ON slpcd.int_status = 0 AND slpcd.fk_employee_id = ud.user_ptr_id AND int_month={0} AND int_year={1} LEFT JOIN salary_details slydtl ON slydtl.pk_bint_id = slpcd.fk_details_id JOIN category cat ON cat.pk_bint_id = ud.fk_category_id LEFT JOIN department dept ON dept.pk_bint_id = ud.fk_department_id LEFT JOIN job_position desig ON desig.pk_bint_id = ud.fk_desig_id LEFT JOIN branch brnch ON brnch.pk_bint_id = ud.fk_branch_id WHERE (au.is_active = TRUE OR (au.is_active = FALSE AND ud.dat_resignation >= '{2}'::DATE)){4} ORDER BY TRIM(TRIM(TRIM(ud.vchr_employee_code,'MYGC-'),'MYGE-'),'MYGT-')::INT"
            str_filter = ''
            if int_cat_id:
                str_filter += ' AND cat.pk_bint_id = '+str(int_cat_id)
            if request.data.get('lstDesignation'):
                str_filter += ' AND desig.pk_bint_id IN ('+str(request.data.get('lstDesignation'))[1:-1]+')'
            if request.data.get('intDepartmentId'):
                str_filter += ' AND dept.pk_bint_id = '+str(request.data.get('intDepartmentId'))
            if request.data.get('lstBranch'):
                str_filter += ' AND brnch.pk_bint_id IN ('+str(request.data.get('lstBranch'))[1:-1]+')'
            if request.data.get('intSalaryFrom'):
                str_filter += ' AND ud.dbl_gross >= '+str(request.data.get('intSalaryFrom'))
            if request.data.get('intSalaryTo'):
                str_filter += ' AND ud.dbl_gross <= '+str(request.data.get('intSalaryTo'))

            if request.data.get('intESINumber'):
                str_filter += " AND ud.vchr_esi_no = '"+str(request.data.get('intESINumber'))+"'"
            str_filter += " AND (ud.json_allowance->>'bln_esi')::BOOLEAN=TRUE"
            str_query = str_query.format(str(int_month), str(int_year), str_start_date, str_end_date, str_filter)

            rst_data = conn.execute(str_query).fetchall()
            if not rst_data:
                conn.close()
                return Response({'status':0,'reason':'No Data'})
            lst_data = []
            for ins_user in rst_data:
                dct_user = dict(ins_user)
                int_days = 30
                ins_user_copy = copy.deepcopy(ins_user)
                dct_data = {}
                dct_data['str_emp_code'] = dct_user['vchr_employee_code']
                dct_data['str_emp_name'] = dct_user['str_emp_name']
                dct_data['str_esi_num'] = dct_user['vchr_esi_no']
                dct_data['str_department'] = dct_user['str_department']
                dct_data['str_designation'] = dct_user['str_designation']
                dct_data['str_branch'] = dct_user['str_branch']
                dct_data['dat_joined'] = datetime.strftime(dct_user['dat_doj'], '%d-%m-%Y') if dct_user['dat_doj'] else ''
                dct_user['json_attendance'] = dct_user.get('json_attendance') if dct_user.get('json_attendance') else {}
                dct_data['dbl_lop'] = dct_user.get('json_attendance',{}).get('dbl_tot_lop',0)
                dct_data['int_actual'] = int_days - dct_user.get('json_attendance',{}).get('dbl_tot_lop',0)
                dct_data['dbl_nwd'] = int_days
                dct_data['dbl_gross'] = dct_user['dbl_gross'] if dct_user['dbl_gross'] else 0.0
                dct_data['dbl_bp_da'] = dct_user['dbl_bp'] if dct_user['dbl_bp'] else 0.0
                dct_data['dbl_hra'] = dct_user['dbl_hra'] if dct_user['dbl_hra'] else 0.0
                dct_data['dbl_cca'] = dct_user['dbl_cca'] if dct_user['dbl_cca'] else 0.0
                dct_data['dbl_sa'] = dct_user['dbl_sa'] if dct_user['dbl_sa'] else 0.0
                dct_data['dbl_wa'] = dct_user['dbl_wa'] if dct_user['dbl_wa'] else 0.0
                dct_data['dbl_esi_salary'] = 0
                if dct_user['json_deductions'] and dct_user['json_deductions'].get('ESI'):
                    dct_data['dbl_esi_salary'] = dct_data['dbl_gross']-dct_data['dbl_wa']
                dct_user['json_allowances'] = dct_user.get('json_allowances') if dct_user.get('json_allowances') else {}
                dct_user['json_deductions'] = dct_user.get('json_deductions') if dct_user.get('json_deductions') else {}
                dct_data['ESI_ER'] = dct_user['json_allowances'].get('ESI') if dct_user['json_allowances'].get('ESI') else 0
                dct_data['ESI_EE'] = dct_user['json_deductions'].get('ESI') if dct_user['json_deductions'].get('ESI') else 0
                lst_data.append(dct_data)

            file_name = 'SalaryReport/ESI_Report_' + datetime.strftime(date.today(), "%d-%m-%Y") + '.xlsx'
            if path.exists(file_name):
                os.remove(file_name)
            if not path.exists(settings.MEDIA_ROOT + '/SalaryReport/'):
                os.mkdir(settings.MEDIA_ROOT + '/SalaryReport/')
            writer = pd.ExcelWriter(settings.MEDIA_ROOT + '/' + file_name, engine ='xlsxwriter')
            workbook = writer.book
            worksheet = workbook.add_worksheet()

            title_style = workbook.add_format({'font_size':14, 'bold':1, 'align': 'center', 'border':1})
            title_style.set_align('vcenter')
            title_style.set_pattern(1)
            title_style.set_bg_color('#ffe0cc')
            worksheet.merge_range('A1:P1', 'ESI Report ('+calendar.month_name[int_month]+' '+str(int_year)+')', title_style)
            worksheet.set_row(0, 30)

            head_style = workbook.add_format({'font_size':11, 'bold':1, 'align': 'center','border':1,'border_color':'#000000'})
            head_style.set_pattern(1)
            head_style.set_bg_color('#bfbfbf')
            head_style.set_align('vcenter')
            worksheet.autofilter('B2:P2')

            row_style = workbook.add_format({'font_size':11})
            row_style.set_align('vcenter')

            worksheet.protect('',{'autofilter':True})

            int_row = 1
            worksheet.write(int_row, 0, 'SL. No', head_style); worksheet.set_column(0, 0, 6)
            worksheet.write(int_row, 1, 'EMP CODE', head_style); worksheet.set_column(1, 1, 13)
            worksheet.write(int_row, 2, 'ESI NO', head_style); worksheet.set_column(2, 2, 20)
            worksheet.write(int_row, 3, 'EMP NAME', head_style); worksheet.set_column(3, 3, 30)
            worksheet.write(int_row, 4, 'BRANCH', head_style); worksheet.set_column(4, 4, 20)
            worksheet.write(int_row, 5, 'DEPARTMENT', head_style); worksheet.set_column(5, 5, 30)
            worksheet.write(int_row, 6, 'DESIGNATION', head_style); worksheet.set_column(6, 6, 35)
            worksheet.write(int_row, 7, 'DOJ', head_style); worksheet.set_column(7, 7, 15)
            worksheet.write(int_row, 8, 'LOP', head_style)
            worksheet.write(int_row, 9, 'ACTUAL', head_style)
            worksheet.write(int_row, 10, 'NWD', head_style)
            worksheet.write(int_row, 11, 'GROSS PAY', head_style)
            worksheet.write(int_row, 12, 'ESI SALARY', head_style)
            worksheet.write(int_row, 13, 'ESI EE', head_style)
            worksheet.write(int_row, 14, 'ESI ER', head_style)
            worksheet.write(int_row, 15, 'TOTAL', head_style); worksheet.set_column(8, 15, 13)
            worksheet.set_row(int_row, 23)

            for ins_data in lst_data:
                int_row += 1
                worksheet.write(int_row, 0, int_row-1, row_style)
                worksheet.write(int_row, 1, ins_data.get('str_emp_code'), row_style)
                worksheet.write(int_row, 2, ins_data.get('str_esi_num'), row_style)
                worksheet.write(int_row, 3, ins_data.get('str_emp_name'), row_style)
                worksheet.write(int_row, 4, ins_data.get('str_branch'), row_style)
                worksheet.write(int_row, 5, ins_data.get('str_department'), row_style)
                worksheet.write(int_row, 6, ins_data.get('str_designation'), row_style)
                worksheet.write(int_row, 7, ins_data.get('dat_joined'), row_style)
                worksheet.write(int_row, 8, ins_data.get('dbl_lop'), row_style)
                worksheet.write(int_row, 9, ins_data.get('int_actual'), row_style)
                worksheet.write(int_row, 10, ins_data.get('dbl_nwd'), row_style)
                worksheet.write(int_row, 11, ins_data.get('dbl_gross'), row_style)
                worksheet.write(int_row, 12, ins_data.get('dbl_esi_salary'), row_style)
                worksheet.write(int_row, 13, ins_data.get('ESI_EE'), row_style)
                worksheet.write(int_row, 14, ins_data.get('ESI_ER'), row_style)
                worksheet.write(int_row, 15, ins_data.get('ESI_EE', 0)+ins_data.get('ESI_ER',0), row_style)
                worksheet.set_row(int_row, 20, row_style)
            writer.save()
            conn.close()
            return Response({'status':1, 'data':request.scheme+'://'+request.get_host()+settings.MEDIA_URL+file_name})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


class PFReportView(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            conn = engine.connect()

            int_cat_id = request.data.get('intCategoryId')
            int_month = int(request.data.get('intMonthYear').split('-')[0])
            int_year = int(request.data.get('intMonthYear').split('-')[1])
            now_date = datetime.now()

            dur_calendar = calendar.monthrange(int_year, int_month)
            str_start_date = str(int_year)+'-'+str(int_month)+'-1'
            str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(dur_calendar[1])

            if not request.user.is_superuser:
                ins_admin = AdminSettings.objects.filter(vchr_code='PAYROLL_PERIOD',bln_enabled=True,fk_company_id=request.user.userdetails.fk_company_id).values('vchr_value', 'int_value').first()
                if ins_admin and ins_admin['int_value'] != 0:
                    str_start_date = datetime.strftime(datetime.strptime(str(int_year)+'-'+str(int_month)+'-'+ins_admin['vchr_value'][0],'%Y-%m-%d')+timedelta(days=int(ins_admin['vchr_value'][0])*ins_admin['int_value']),'%Y-%m-')+ins_admin['vchr_value'][0]
                    str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(int(ins_admin['vchr_value'][0])-1)

            if int_month == now_date.month and int_year == now_date.year and now_date.day <= int(str_end_date.split('-')[2]):
                str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(now_date.day)

            dat_month_last = datetime.strptime(str_end_date, '%Y-%m-%d')
            dat_month_first = datetime.strptime(str_start_date, '%Y-%m-%d')

            str_query = "SELECT ud.user_ptr_id,ud.vchr_employee_code,ud.vchr_uan_no,ud.dat_doj,dept.vchr_name AS str_department, desig.vchr_name AS str_designation, brnch.vchr_name AS str_branch, CONCAT(TRIM(au.first_name), ' ', CASE WHEN ud.vchr_middle_name IS NOT NULL THEN CONCAT(TRIM(ud.vchr_middle_name), ' ', TRIM(au.last_name)) ELSE TRIM(au.last_name) END) AS str_emp_name, slpcd.dbl_bp, slpcd.dbl_da, slpcd.dbl_hra, slpcd.dbl_cca, slpcd.dbl_wa, slpcd.dbl_sa, slpcd.dbl_gross, slpcd.json_allowances, slpcd.json_deductions, slpcd.dbl_net_salary, slpcd.dbl_monthly_ctc, slpcd.json_attendance FROM auth_user au JOIN user_details ud ON ud.user_ptr_id = au.id AND ud.dat_doj <= '{3}'::DATE LEFT JOIN salary_processed slpcd ON slpcd.int_status = 0 AND slpcd.fk_employee_id = ud.user_ptr_id AND int_month={0} AND int_year={1} LEFT JOIN salary_details slydtl ON slydtl.pk_bint_id = slpcd.fk_details_id JOIN category cat ON cat.pk_bint_id = ud.fk_category_id LEFT JOIN department dept ON dept.pk_bint_id = ud.fk_department_id LEFT JOIN job_position desig ON desig.pk_bint_id = ud.fk_desig_id LEFT JOIN branch brnch ON brnch.pk_bint_id = ud.fk_branch_id WHERE (au.is_active = TRUE OR (au.is_active = FALSE AND ud.dat_resignation >= '{2}'::DATE)){4} ORDER BY TRIM(TRIM(TRIM(ud.vchr_employee_code,'MYGC-'),'MYGE-'),'MYGT-')::INT"

            str_filter = ''
            if int_cat_id:
                str_filter += ' AND cat.pk_bint_id = '+str(int_cat_id)
            if request.data.get('lstDesignation'):
                str_filter += ' AND desig.pk_bint_id IN ('+str(request.data.get('lstDesignation'))[1:-1]+')'
            if request.data.get('intDepartmentId'):
                str_filter += ' AND dept.pk_bint_id = '+str(request.data.get('intDepartmentId'))
            if request.data.get('lstBranch'):
                str_filter += ' AND brnch.pk_bint_id IN ('+str(request.data.get('lstBranch'))[1:-1]+')'
            if request.data.get('intSalaryFrom'):
                str_filter += ' AND ud.dbl_gross >= '+str(request.data.get('intSalaryFrom'))
            if request.data.get('intSalaryTo'):
                str_filter += ' AND ud.dbl_gross <= '+str(request.data.get('intSalaryTo'))

            if request.data.get('intPFNumber'):
                str_filter += " AND ud.vchr_uan_no = '"+str(request.data.get('intPFNumber'))+"'"
            str_filter += " AND (ud.json_allowance->>'bln_pf')::BOOLEAN=TRUE"
            str_query = str_query.format(str(int_month), str(int_year), str_start_date, str_end_date, str_filter)

            rst_data = conn.execute(str_query).fetchall()
            if not rst_data:
                conn.close()
                return Response({'status':0,'reason':'No Data'})
            lst_data = []
            for ins_user in rst_data:
                dct_user = dict(ins_user)
                int_days = 30
                dct_data={}
                dct_data['str_emp_code'] = dct_user['vchr_employee_code']
                dct_data['str_emp_name'] = dct_user['str_emp_name']
                dct_data['str_pf_num'] = dct_user['vchr_uan_no']
                dct_data['str_department'] = dct_user['str_department']
                dct_data['str_designation'] = dct_user['str_designation']
                dct_data['str_branch'] = dct_user['str_branch']
                dct_data['dat_joined'] = datetime.strftime(dct_user['dat_doj'], '%d-%m-%Y') if dct_user['dat_doj'] else ''
                dct_user['json_attendance'] = dct_user.get('json_attendance') if dct_user.get('json_attendance') else {}
                dct_data['dbl_lop'] = dct_user.get('json_attendance',{}).get('dbl_tot_lop',0)
                dct_data['int_actual'] = int_days - dct_user.get('json_attendance',{}).get('dbl_tot_lop',0)
                dct_data['dbl_nwd'] = int_days
                dct_data['dbl_gross'] = dct_user['dbl_gross'] if dct_user['dbl_gross'] else 0.0
                dct_data['dbl_bp_da'] = dct_user['dbl_bp'] if dct_user['dbl_bp'] else 0.0
                dct_data['dbl_hra'] = dct_user['dbl_hra'] if dct_user['dbl_hra'] else 0.0
                dct_data['dbl_cca'] = dct_user['dbl_cca'] if dct_user['dbl_cca'] else 0.0
                dct_data['dbl_sa'] = dct_user['dbl_sa'] if dct_user['dbl_sa'] else 0.0
                dct_data['dbl_wa'] = dct_user['dbl_wa'] if dct_user['dbl_wa'] else 0.0

                dct_data['dbl_pf_salary'] = 0
                if dct_user['json_deductions'] and dct_user['json_deductions'].get('PF'):
                    if dct_data['dbl_gross']-dct_data['dbl_hra']>15000:
                        dct_data['dbl_pf_salary'] = 15000
                    else:
                        dct_data['dbl_pf_salary'] = dct_data['dbl_gross']-dct_data['dbl_hra']
                dct_data['PF_ER'] = 0.0
                dct_data['PF_EE'] = 0.0
                dct_user['json_allowances'] = dct_user.get('json_allowances') if dct_user.get('json_allowances') else {}
                dct_user['json_deductions'] = dct_user.get('json_deductions') if dct_user.get('json_deductions') else {}
                dct_data['PF_ER'] = dct_user['json_allowances'].get('PF') if dct_user['json_allowances'].get('PF') else 0
                dct_data['PF_EE'] = dct_user['json_deductions'].get('PF') if dct_user['json_deductions'].get('PF') else 0


                lst_data.append(dct_data)

            file_name = 'SalaryReport/PF_Report_' + datetime.strftime(date.today(), "%d-%m-%Y") + '.xlsx'
            if path.exists(file_name):
                os.remove(file_name)
            if not path.exists(settings.MEDIA_ROOT + '/SalaryReport/'):
                os.mkdir(settings.MEDIA_ROOT + '/SalaryReport/')
            writer = pd.ExcelWriter(settings.MEDIA_ROOT + '/' + file_name, engine ='xlsxwriter')
            workbook = writer.book
            worksheet = workbook.add_worksheet()

            title_style = workbook.add_format({'font_size':14, 'bold':1, 'align': 'center', 'border':1})
            title_style.set_align('vcenter')
            title_style.set_pattern(1)
            title_style.set_bg_color('#ffe0cc')
            worksheet.merge_range('A1:P1', 'PF Report ('+calendar.month_name[int_month]+' '+str(int_year)+')', title_style)
            worksheet.set_row(0, 30)

            head_style = workbook.add_format({'font_size':11, 'bold':1, 'align': 'center','border':1,'border_color':'#000000'})
            head_style.set_pattern(1)
            head_style.set_bg_color('#bfbfbf')
            head_style.set_align('vcenter')
            worksheet.autofilter('B2:P2')

            row_style = workbook.add_format({'font_size':11})
            row_style.set_align('vcenter')

            worksheet.protect('',{'autofilter':True})

            int_row = 1
            worksheet.write(int_row, 0, 'SL. No', head_style); worksheet.set_column(0, 0, 6)
            worksheet.write(int_row, 1, 'EMP CODE', head_style); worksheet.set_column(1, 1, 13)
            worksheet.write(int_row, 2, 'PF NO', head_style); worksheet.set_column(2, 2, 20)
            worksheet.write(int_row, 3, 'EMP NAME', head_style); worksheet.set_column(3, 3, 30)
            worksheet.write(int_row, 4, 'BRANCH', head_style); worksheet.set_column(4, 4, 20)
            worksheet.write(int_row, 5, 'DEPARTMENT', head_style); worksheet.set_column(5, 5, 30)
            worksheet.write(int_row, 6, 'DESIGNATION', head_style); worksheet.set_column(6, 6, 35)
            worksheet.write(int_row, 7, 'DOJ', head_style); worksheet.set_column(7, 7, 15)
            worksheet.write(int_row, 8, 'LOP', head_style)
            worksheet.write(int_row, 9, 'ACTUAL', head_style)
            worksheet.write(int_row, 10, 'NWD', head_style)
            worksheet.write(int_row, 11, 'GROSS PAY', head_style)
            worksheet.write(int_row, 12, 'PF SALARY', head_style)
            worksheet.write(int_row, 13, 'PF EE', head_style)
            worksheet.write(int_row, 14, 'PF ER', head_style)
            worksheet.write(int_row, 15, 'TOTAL', head_style); worksheet.set_column(8, 15, 13)
            worksheet.set_row(int_row, 23)

            for ins_data in lst_data:
                int_row += 1
                worksheet.write(int_row, 0, int_row-1, row_style)
                worksheet.write(int_row, 1, ins_data.get('str_emp_code'), row_style)
                worksheet.write(int_row, 2, ins_data.get('str_pf_num'), row_style)
                worksheet.write(int_row, 3, ins_data.get('str_emp_name'), row_style)
                worksheet.write(int_row, 4, ins_data.get('str_branch'), row_style)
                worksheet.write(int_row, 5, ins_data.get('str_department'), row_style)
                worksheet.write(int_row, 6, ins_data.get('str_designation'), row_style)
                worksheet.write(int_row, 7, ins_data.get('dat_joined'), row_style)
                worksheet.write(int_row, 8, ins_data.get('dbl_lop'), row_style)
                worksheet.write(int_row, 9, ins_data.get('int_actual'), row_style)
                worksheet.write(int_row, 10, ins_data.get('dbl_nwd'), row_style)
                worksheet.write(int_row, 11, ins_data.get('dbl_gross'), row_style)
                worksheet.write(int_row, 12, ins_data.get('dbl_pf_salary'), row_style)
                worksheet.write(int_row, 13, ins_data.get('PF_EE'), row_style)
                worksheet.write(int_row, 14, ins_data.get('PF_ER'), row_style)
                worksheet.write(int_row, 15, ins_data.get('PF_EE',0) + ins_data.get('PF_ER',0), row_style)
                worksheet.set_row(int_row, 20, row_style)
            writer.save()
            conn.close()
            return Response({'status':1, 'data':request.scheme+'://'+request.get_host()+settings.MEDIA_URL+file_name})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


class WWFReportView(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            conn = engine.connect()

            int_cat_id = request.data.get('intCategoryId')
            int_month = int(request.data.get('intMonthYear').split('-')[0])
            int_year = int(request.data.get('intMonthYear').split('-')[1])
            now_date = datetime.now()

            dur_calendar = calendar.monthrange(int_year, int_month)
            str_start_date = str(int_year)+'-'+str(int_month)+'-1'
            str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(dur_calendar[1])

            if not request.user.is_superuser:
                ins_admin = AdminSettings.objects.filter(vchr_code='PAYROLL_PERIOD',bln_enabled=True,fk_company_id=request.user.userdetails.fk_company_id).values('vchr_value', 'int_value').first()
                if ins_admin and ins_admin['int_value'] != 0:
                    str_start_date = datetime.strftime(datetime.strptime(str(int_year)+'-'+str(int_month)+'-'+ins_admin['vchr_value'][0],'%Y-%m-%d')+timedelta(days=int(ins_admin['vchr_value'][0])*ins_admin['int_value']),'%Y-%m-')+ins_admin['vchr_value'][0]
                    str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(int(ins_admin['vchr_value'][0])-1)

            if int_month == now_date.month and int_year == now_date.year and now_date.day <= int(str_end_date.split('-')[2]):
                str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(now_date.day)

            dat_month_last = datetime.strptime(str_end_date, '%Y-%m-%d')
            dat_month_first = datetime.strptime(str_start_date, '%Y-%m-%d')

            str_query = "SELECT ud.user_ptr_id,ud.vchr_employee_code,ud.vchr_wwf_no,dept.vchr_name AS str_department, desig.vchr_name AS str_designation, brnch.vchr_name AS str_branch, CONCAT(TRIM(au.first_name), ' ', CASE WHEN ud.vchr_middle_name IS NOT NULL THEN CONCAT(TRIM(ud.vchr_middle_name), ' ', TRIM(au.last_name)) ELSE TRIM(au.last_name) END) AS str_emp_name, slpcd.json_allowances, slpcd.json_deductions FROM auth_user au JOIN user_details ud ON ud.user_ptr_id = au.id AND ud.dat_doj <= '{3}'::DATE LEFT JOIN salary_processed slpcd ON slpcd.int_status=0 AND slpcd.fk_employee_id = ud.user_ptr_id AND int_month={0} AND int_year={1} LEFT JOIN salary_details slydtl ON slydtl.pk_bint_id = slpcd.fk_details_id JOIN category cat ON cat.pk_bint_id = ud.fk_category_id LEFT JOIN department dept ON dept.pk_bint_id = ud.fk_department_id LEFT JOIN job_position desig ON desig.pk_bint_id = ud.fk_desig_id LEFT JOIN branch brnch ON brnch.pk_bint_id = ud.fk_branch_id WHERE (au.is_active = TRUE OR (au.is_active = FALSE AND ud.dat_resignation >= '{2}'::DATE)){4} ORDER BY TRIM(TRIM(TRIM(ud.vchr_employee_code,'MYGC-'),'MYGE-'),'MYGT-')::INT"

            str_filter = ''
            if int_cat_id:
                str_filter += ' AND cat.pk_bint_id = '+str(int_cat_id)
            if request.data.get('lstDesignation'):
                str_filter += ' AND desig.pk_bint_id IN ('+str(request.data.get('lstDesignation'))[1:-1]+')'
            if request.data.get('intDepartmentId'):
                str_filter += ' AND dept.pk_bint_id = '+str(request.data.get('intDepartmentId'))
            if request.data.get('lstBranch'):
                str_filter += ' AND brnch.pk_bint_id IN ('+str(request.data.get('lstBranch'))[1:-1]+')'
            if request.data.get('intSalaryFrom'):
                str_filter += ' AND slpcd.dbl_gross >= '+str(request.data.get('intSalaryFrom'))
            if request.data.get('intSalaryTo'):
                str_filter += ' AND slpcd.dbl_gross <= '+str(request.data.get('intSalaryTo'))

            str_filter += " AND (ud.json_allowance->>'bln_wwf')::BOOLEAN=TRUE"
            if request.data.get('intWWFNumber'):
                str_filter += " AND ud.vchr_wwf_no = '"+str(request.data.get('intWWFNumber'))+"'"

            str_query = str_query.format(str(int_month), str(int_year), str_start_date, str_end_date, str_filter)

            rst_data = conn.execute(str_query).fetchall()
            if not rst_data:
                conn.close()
                return Response({'status':0,'reason':'No Data'})
            lst_data = []
            for ins_user in rst_data:
                dct_user = dict(ins_user)
                dct_data = {}
                dct_data['str_emp_code'] = dct_user['vchr_employee_code']
                dct_data['str_emp_name'] = dct_user['str_emp_name']
                dct_data['str_wwf_num'] = dct_user['vchr_wwf_no']
                dct_data['str_department'] = dct_user['str_department']
                dct_data['str_designation'] = dct_user['str_designation']
                dct_data['str_branch'] = dct_user['str_branch']
                dct_data['dbl_wwf_er'] = 0.0
                if dct_user['json_allowances']:
                    dct_data['dbl_wwf_er'] = dct_user['json_allowances'].get('WWF') if dct_user['json_allowances'].get('WWF') else 0.0
                dct_data['dbl_wwf_ee'] = 0.0
                if dct_user['json_deductions']:
                    dct_data['dbl_wwf_ee'] = dct_user['json_deductions'].get('WWF') if dct_user['json_deductions'].get('WWF') else 0.0
                lst_data.append(dct_data)

            file_name = 'SalaryReport/WWF_Report_' + datetime.strftime(date.today(), "%d-%m-%Y") + '.xlsx'
            if path.exists(file_name):
                os.remove(file_name)
            if not path.exists(settings.MEDIA_ROOT + '/SalaryReport/'):
                os.mkdir(settings.MEDIA_ROOT + '/SalaryReport/')
            writer = pd.ExcelWriter(settings.MEDIA_ROOT + '/' + file_name, engine ='xlsxwriter')
            workbook = writer.book
            worksheet = workbook.add_worksheet()

            title_style = workbook.add_format({'font_size':14, 'bold':1, 'align': 'center', 'border':1})
            title_style.set_align('vcenter')
            title_style.set_pattern(1)
            title_style.set_bg_color('#ffe0cc')
            worksheet.merge_range('A1:I1', 'WWF Report ('+calendar.month_name[int_month]+' '+str(int_year)+')', title_style)
            worksheet.set_row(0, 30)

            head_style = workbook.add_format({'font_size':11, 'bold':1, 'align': 'center','border':1,'border_color':'#000000'})
            head_style.set_pattern(1)
            head_style.set_bg_color('#bfbfbf')
            head_style.set_align('vcenter')
            worksheet.autofilter('B2:I2')

            row_style = workbook.add_format({'font_size':11})
            row_style.set_align('vcenter')

            worksheet.protect('',{'autofilter':True})

            int_row = 1
            worksheet.write(int_row, 0, 'SL. No', head_style); worksheet.set_column(0, 0, 6)
            worksheet.write(int_row, 1, 'EMP CODE', head_style); worksheet.set_column(1, 1, 13)
            worksheet.write(int_row, 2, 'EMP NAME', head_style); worksheet.set_column(2, 2, 28)
            worksheet.write(int_row, 3, 'WWF NO', head_style); worksheet.set_column(3, 3, 20)
            worksheet.write(int_row, 4, 'BRANCH', head_style); worksheet.set_column(4, 4, 20)
            worksheet.write(int_row, 5, 'DEPARTMENT', head_style); worksheet.set_column(5, 5, 30)
            worksheet.write(int_row, 6, 'WWF EE', head_style)
            worksheet.write(int_row, 7, 'WWF ER', head_style)
            worksheet.write(int_row, 8, 'TOTAL', head_style); worksheet.set_column(6, 8, 12)
            worksheet.set_row(int_row, 23)

            for ins_data in lst_data:
                int_row += 1
                worksheet.write(int_row, 0, int_row-1, row_style)
                worksheet.write(int_row, 1, ins_data.get('str_emp_code'), row_style)
                worksheet.write(int_row, 2, ins_data.get('str_emp_name'), row_style)
                worksheet.write(int_row, 3, ins_data.get('str_wwf_num'), row_style)
                worksheet.write(int_row, 4, ins_data.get('str_branch'), row_style)
                worksheet.write(int_row, 5, ins_data.get('str_department'), row_style)
                worksheet.write(int_row, 6, ins_data.get('dbl_wwf_ee'), row_style)
                worksheet.write(int_row, 7, ins_data.get('dbl_wwf_er'), row_style)
                worksheet.write(int_row, 8, ins_data.get('dbl_wwf_ee', 0) + ins_data.get('dbl_wwf_er', 0), row_style)
                worksheet.set_row(int_row, 20, row_style)
            writer.save()
            conn.close()
            return Response({'status':1, 'data':request.scheme+'://'+request.get_host()+settings.MEDIA_URL+file_name})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


class SalaryPayReportView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            conn = engine.connect()
            int_cat_id = request.data.get('intCategoryId')
            int_month = int(request.data.get('intMonthYear').split('-')[0])
            int_year = int(request.data.get('intMonthYear').split('-')[1])
            now_date = datetime.now()

            dur_calendar = calendar.monthrange(int_year, int_month)
            str_start_date = str(int_year)+'-'+str(int_month)+'-1'
            str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(dur_calendar[1])

            if not request.user.is_superuser:
                ins_admin = AdminSettings.objects.filter(vchr_code='PAYROLL_PERIOD',bln_enabled=True,fk_company_id=request.user.userdetails.fk_company_id).values('vchr_value', 'int_value').first()
                if ins_admin and ins_admin['int_value'] != 0:
                    str_start_date = datetime.strftime(datetime.strptime(str(int_year)+'-'+str(int_month)+'-'+ins_admin['vchr_value'][0],'%Y-%m-%d')+timedelta(days=int(ins_admin['vchr_value'][0])*ins_admin['int_value']),'%Y-%m-')+ins_admin['vchr_value'][0]
                    str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(int(ins_admin['vchr_value'][0])-1)

            if int_month == now_date.month and int_year == now_date.year and now_date.day <= int(str_end_date.split('-')[2]):
                str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(now_date.day)

            dat_month_last = datetime.strptime(str_end_date, '%Y-%m-%d')
            dat_month_first = datetime.strptime(str_start_date, '%Y-%m-%d')

            str_query = "SELECT ud.user_ptr_id, ud.vchr_employee_code AS str_emp_code, CONCAT(TRIM(au.first_name), ' ', CASE WHEN ud.vchr_middle_name IS NOT NULL THEN CONCAT(TRIM(ud.vchr_middle_name), ' ', TRIM(au.last_name)) ELSE TRIM(au.last_name) END) AS str_emp_name, brnch.vchr_name AS str_branch, ud.vchr_acc_no, slpcd.dbl_net_salary FROM auth_user au JOIN user_details ud ON ud.user_ptr_id = au.id AND ud.dat_doj <= '{3}'::DATE JOIN salary_processed slpcd ON slpcd.int_status = 0 AND slpcd.fk_employee_id = ud.user_ptr_id AND int_month={0} AND int_year={1} LEFT JOIN salary_details slydtl ON slydtl.pk_bint_id = slpcd.fk_details_id JOIN category cat ON cat.pk_bint_id = ud.fk_category_id LEFT JOIN department dept ON dept.pk_bint_id = ud.fk_department_id LEFT JOIN job_position desig ON desig.pk_bint_id = ud.fk_desig_id LEFT JOIN branch brnch ON brnch.pk_bint_id = ud.fk_branch_id WHERE (au.is_active = TRUE OR (au.is_active = FALSE AND ud.dat_resignation >= '{2}'::DATE)){4} ORDER BY TRIM(TRIM(TRIM(ud.vchr_employee_code,'MYGC-'),'MYGE-'),'MYGT-')::INT"

            str_filter = ''
            if int_cat_id:
                str_filter += ' AND cat.pk_bint_id = '+str(int_cat_id)
            if request.data.get('lstDesignation'):
                str_filter += ' AND desig.pk_bint_id IN ('+str(request.data.get('lstDesignation'))[1:-1]+')'
            if request.data.get('intDepartmentId'):
                str_filter += ' AND dept.pk_bint_id = '+str(request.data.get('intDepartmentId'))
            if request.data.get('lstBranch'):
                str_filter += ' AND brnch.pk_bint_id IN ('+str(request.data.get('lstBranch'))[1:-1]+')'

            str_query = str_query.format(str(int_month), str(int_year), str_start_date, str_end_date, str_filter)

            rst_data = conn.execute(str_query).fetchall()
            if not rst_data:
                conn.close()
                return Response({'status':0,'reason':'No Data'})


            file_name = 'SalaryReport/Salary_Pay_Report_' + datetime.strftime(date.today(), "%d-%m-%Y") + '.xlsx'
            if path.exists(file_name):
                os.remove(file_name)
            if not path.exists(settings.MEDIA_ROOT + '/SalaryReport/'):
                os.mkdir(settings.MEDIA_ROOT + '/SalaryReport/')
            writer = pd.ExcelWriter(settings.MEDIA_ROOT + '/' + file_name, engine ='xlsxwriter')
            workbook = writer.book
            worksheet = workbook.add_worksheet()

            title_style = workbook.add_format({'font_size':14, 'bold':1, 'align': 'center', 'border':1})
            title_style.set_align('vcenter')
            title_style.set_pattern(1)
            title_style.set_bg_color('#ffe0cc')
            worksheet.merge_range('A1+:F1', 'Salary Pay Report ('+calendar.month_name[int_month]+' '+str(int_year)+')', title_style)
            worksheet.set_row(0, 30)

            head_style = workbook.add_format({'font_size':11, 'bold':1, 'align': 'center','border':1,'border_color':'#000000'})
            head_style.set_pattern(1)
            head_style.set_bg_color('#bfbfbf')
            head_style.set_align('vcenter')
            worksheet.autofilter('B2:F2')

            row_style = workbook.add_format({'font_size':11})
            row_style.set_align('vcenter')

            worksheet.protect('',{'autofilter':True})

            int_row = 1
            worksheet.write(int_row, 0, 'SL. No', head_style); worksheet.set_column(0, 0, 6)
            worksheet.write(int_row, 1, 'EMP CODE', head_style); worksheet.set_column(1, 1, 13)
            worksheet.write(int_row, 2, 'EMP NAME', head_style); worksheet.set_column(2, 2, 30)
            worksheet.write(int_row, 3, 'BRANCH', head_style); worksheet.set_column(3, 3, 20)
            worksheet.write(int_row, 4, 'ACCOUNT NO', head_style); worksheet.set_column(4, 4, 20)
            worksheet.write(int_row, 5, 'AMOUNT', head_style); worksheet.set_column(5, 5, 15)
            worksheet.set_row(int_row, 23)

            for ins_data in rst_data:
                int_row += 1
                dct_user = dict(ins_data)
                worksheet.write(int_row, 0, int_row-1, row_style)
                worksheet.write(int_row, 1, dct_user.get('str_emp_code'), row_style)
                worksheet.write(int_row, 2, dct_user.get('str_emp_name'), row_style)
                worksheet.write(int_row, 3, dct_user.get('str_branch'), row_style)
                worksheet.write(int_row, 4, dct_user.get('vchr_acc_no'), row_style)
                worksheet.write(int_row, 5, dct_user.get('dbl_net_salary'), row_style)

            writer.save()
            conn.close()
            return Response({'status':1, 'data':request.scheme+'://'+request.get_host()+settings.MEDIA_URL+file_name})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


class ESIUploadReport(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            conn = engine.connect()
            int_cat_id = request.data.get('intCategoryId')
            int_month = int(request.data.get('intMonthYear').split('-')[0])
            int_year = int(request.data.get('intMonthYear').split('-')[1])
            now_date = datetime.now()

            dur_calendar = calendar.monthrange(int_year, int_month)
            str_start_date = str(int_year)+'-'+str(int_month)+'-1'
            str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(dur_calendar[1])

            if not request.user.is_superuser:
                ins_admin = AdminSettings.objects.filter(vchr_code='PAYROLL_PERIOD',bln_enabled=True,fk_company_id=request.user.userdetails.fk_company_id).values('vchr_value', 'int_value').first()
                if ins_admin and ins_admin['int_value'] != 0:
                    str_start_date = datetime.strftime(datetime.strptime(str(int_year)+'-'+str(int_month)+'-'+ins_admin['vchr_value'][0],'%Y-%m-%d')+timedelta(days=int(ins_admin['vchr_value'][0])*ins_admin['int_value']),'%Y-%m-')+ins_admin['vchr_value'][0]
                    str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(int(ins_admin['vchr_value'][0])-1)

            if int_month == now_date.month and int_year == now_date.year and now_date.day <= int(str_end_date.split('-')[2]):
                str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(now_date.day)

            dat_month_last = datetime.strptime(str_end_date, '%Y-%m-%d')
            dat_month_first = datetime.strptime(str_start_date, '%Y-%m-%d')

            str_query = "SELECT CASE WHEN NOT au.is_active AND ud.dat_resignation::date >= '{2}'::date THEN TRUE ELSE au.is_active END as bln_active,ud.vchr_esi_no,ud.user_ptr_id AS int_emp_id, ud.vchr_employee_code, CONCAT(TRIM(au.first_name), ' ', CASE WHEN ud.vchr_middle_name IS NOT NULL THEN CONCAT(TRIM(ud.vchr_middle_name), ' ', TRIM(au.last_name)) ELSE TRIM(au.last_name) END) AS str_emp_name,sp.json_attendance,sp.dbl_net_salary,CASE WHEN sp.dbl_gross IS NOT NULL THEN sp.dbl_gross ELSE 0 END as dbl_gross,CASE WHEN sp.dbl_wa IS NOT NULL THEN sp.dbl_wa ELSE 0 END as dbl_wa, ud.dat_resignation FROM auth_user au JOIN user_details ud ON ud.user_ptr_id = au.id AND ud.dat_doj <= '{3}'::DATE JOIN category cat ON cat.pk_bint_id = ud.fk_category_id LEFT JOIN salary_processed sp ON sp.fk_employee_id =ud.user_ptr_id AND sp.int_month={0} AND sp.int_year={1} AND sp.int_status=0 LEFT JOIN department dept ON dept.pk_bint_id = ud.fk_department_id LEFT JOIN job_position desig ON desig.pk_bint_id = ud.fk_desig_id LEFT JOIN branch brnch ON brnch.pk_bint_id = ud.fk_branch_id LEFT JOIN salary_details slrydtl ON slrydtl.fk_employee_id = ud.user_ptr_id AND slrydtl.int_status = 1 WHERE (au.is_active = TRUE OR (au.is_active = FALSE AND ud.dat_resignation::date>=('{2}'::date -interval '1 month'))){4}  GROUP BY ud.vchr_esi_no,au.is_active,int_emp_id,ud.dat_resignation,sp.json_attendance, ud.vchr_employee_code, str_emp_name,sp.dbl_net_salary,sp.dbl_gross,sp.dbl_wa ORDER BY TRIM(TRIM(TRIM(ud.vchr_employee_code,'MYGC-'),'MYGE-'),'MYGT-')::INT"

            str_filter=""
            if int_cat_id:
                str_filter += ' AND cat.pk_bint_id = '+str(int_cat_id)
            if request.data.get('lstDesignation'):
                str_filter += ' AND desig.pk_bint_id IN ('+str(request.data.get('lstDesignation'))[1:-1]+')'
            if request.data.get('intDepartmentId'):
                str_filter += ' AND dept.pk_bint_id = '+str(request.data.get('intDepartmentId'))
            if request.data.get('lstBranch'):
                str_filter += ' AND brnch.pk_bint_id IN ('+str(request.data.get('lstBranch'))[1:-1]+')'
            if request.data.get('intSalaryFrom'):
                str_filter += ' AND ud.dbl_gross >= '+str(request.data.get('intSalaryFrom'))
            if request.data.get('intSalaryTo'):
                str_filter += ' AND ud.dbl_gross <= '+str(request.data.get('intSalaryTo'))

            str_filter += " AND (ud.json_allowance->>'bln_esi')::BOOLEAN=TRUE"
            if request.data.get('intESINumber'):
                str_filter += " AND ud.vchr_esi_no = '"+str(request.data.get('intESINumber'))+"'"
            str_query = str_query.format(str(int_month), str(int_year), str_start_date, str_end_date, str_filter)
            rst_data = conn.execute(str_query).fetchall()
            if not rst_data:
                conn.close()
                return Response({'status':0,'reason':'No Data'})
            lst_data = []

            for ins_user in rst_data:
                dct_data={}
                int_days = 30
                ins_user=dict(ins_user)
                dct_data['NWD']=int_days
                dct_data['vchr_esi_no'] = ins_user.get('vchr_esi_no')
                dct_data['str_emp_name'] = ins_user.get('str_emp_name')
                dct_data['dbl_net_salary'] = ins_user.get('dbl_net_salary') if ins_user.get('dbl_net_salary') else 0
                if ins_user.get('dbl_gross', 0) - ins_user.get('dbl_wa', 0) < 21000:
                    dct_data['dbl_esi_salary'] = ins_user.get('dbl_gross', 0) - ins_user.get('dbl_wa', 0)
                else:
                    dct_data['dbl_esi_salary'] = 0
                if dct_data['dbl_net_salary'] ==0 :
                    dct_data['NWD']=0
                dct_data['dat_punch'] = ''
                dct_data['int_reason']=None
                ins_user['json_attendance'] = ins_user.get('json_attendance') if ins_user.get('json_attendance') else {}
                if ins_user.get('json_attendance',{}).get('dbl_tot_lop'):
                    dct_data['NWD']=int_days-ins_user.get('json_attendance',{}).get('dbl_tot_lop',0)
                if dct_data.get('NWD') <= 0:
                    if not ins_user.get('bln_active'):
                        dct_data['dat_punch'] = ins_user['dat_resignation'].strftime('%d-%m-%Y') if ins_user.get('dat_resignation') else None
                        dct_data['int_reason']=2
                    else:
                        dct_data['int_reason']=1
                        # dct_data['dat_punch'] = PunchLog.objects.filter(fk_punchingemp_id__fk_user_id=ins_user.get('int_emp_id')).aggregate(Max('dat_punch'))['dat_punch__max']
                        # dct_data['dat_punch'] = dct_data['dat_punch'].strftime('%d-%m-%Y') if dct_data.get('dat_punch') else None
                lst_data.append(dct_data)
            file_name = 'SalaryReport/ESI_Upload_Report_' + datetime.strftime(date.today(), "%d-%m-%Y") + '.xlsx'
            if not path.exists(settings.MEDIA_ROOT + '/SalaryReport/'):
                os.mkdir(settings.MEDIA_ROOT + '/SalaryReport/')
            writer = pd.ExcelWriter(settings.MEDIA_ROOT + '/' + file_name, engine ='xlsxwriter')
            workbook = writer.book
            worksheet = workbook.add_worksheet()

            title_style = workbook.add_format({'font_size':14, 'bold':1, 'align': 'center', 'border':1})
            title_style.set_align('vcenter')
            title_style.set_pattern(1)
            title_style.set_bg_color('#ffe0cc')
            worksheet.merge_range('A1+:F1', 'ESI Upload Report ('+calendar.month_name[int_month]+' '+str(int_year)+')', title_style)
            worksheet.set_row(0, 30)

            head_style = workbook.add_format({'font_size':11, 'bold':1, 'align': 'center','border':1,'border_color':'#000000','text_wrap': True})
            head_style.set_pattern(1)
            head_style.set_bg_color('#bfbfbf')
            head_style.set_align('vcenter')
            worksheet.autofilter('B2:F2')

            row_style = workbook.add_format({'font_size':11})
            row_style.set_align('vcenter')

            worksheet.protect('',{'autofilter':True})

            int_row = 1
            worksheet.write(int_row, 0, 'IP No', head_style); worksheet.set_column(0, 0, 15)
            worksheet.write(int_row, 1, 'IP Name', head_style); worksheet.set_column(1, 1, 25)
            worksheet.write(int_row, 2, 'No of Days for which wages paid', head_style); worksheet.set_column(2, 2, 20)
            worksheet.write(int_row, 3, 'Total Monthly Wages', head_style); worksheet.set_column(3, 3, 10)
            worksheet.write(int_row, 4, 'Reason Code for Zero workings days', head_style); worksheet.set_column(4, 4, 20)
            worksheet.write(int_row, 5, 'Last Working Day', head_style); worksheet.set_column(5, 5, 25)
            worksheet.set_row(int_row, 40)

            for ins_data in lst_data:
                int_row += 1
                worksheet.write(int_row, 0, ins_data.get('vchr_esi_no'), row_style)
                worksheet.write(int_row, 1, ins_data.get('str_emp_name'), row_style)
                worksheet.write(int_row, 2, ins_data.get('NWD'), row_style)
                worksheet.write(int_row, 3, ins_data.get('dbl_esi_salary'), row_style)
                worksheet.write(int_row, 4, ins_data.get('int_reason'), row_style)
                worksheet.write(int_row, 5, ins_data.get('dat_punch'), row_style)

            writer.save()
            conn.close()
            return Response({'status':1, 'data':request.scheme+'://'+request.get_host()+settings.MEDIA_URL+file_name})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


class PFUploadReport(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            conn = engine.connect()
            int_cat_id = request.data.get('intCategoryId')
            int_month = int(request.data.get('intMonthYear').split('-')[0])
            int_year = int(request.data.get('intMonthYear').split('-')[1])
            now_date = datetime.now()

            dur_calendar = calendar.monthrange(int_year, int_month)
            str_start_date = str(int_year)+'-'+str(int_month)+'-1'
            str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(dur_calendar[1])

            if not request.user.is_superuser:
                ins_admin = AdminSettings.objects.filter(vchr_code='PAYROLL_PERIOD',bln_enabled=True,fk_company_id=request.user.userdetails.fk_company_id).values('vchr_value', 'int_value').first()
                if ins_admin and ins_admin['int_value'] != 0:
                    str_start_date = datetime.strftime(datetime.strptime(str(int_year)+'-'+str(int_month)+'-'+ins_admin['vchr_value'][0],'%Y-%m-%d')+timedelta(days=int(ins_admin['vchr_value'][0])*ins_admin['int_value']),'%Y-%m-')+ins_admin['vchr_value'][0]
                    str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(int(ins_admin['vchr_value'][0])-1)

            if int_month == now_date.month and int_year == now_date.year and now_date.day <= int(str_end_date.split('-')[2]):
                str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(now_date.day)

            dat_month_last = datetime.strptime(str_end_date, '%Y-%m-%d')
            dat_month_first = datetime.strptime(str_start_date, '%Y-%m-%d')

            str_query = "SELECT ud.vchr_uan_no as str_uan,sp.dbl_gross,sp.dbl_hra,ud.user_ptr_id AS int_emp_id, ud.vchr_employee_code, CONCAT(TRIM(au.first_name), ' ', CASE WHEN ud.vchr_middle_name IS NOT NULL THEN CONCAT(TRIM(ud.vchr_middle_name), ' ', TRIM(au.last_name)) ELSE TRIM(au.last_name) END) AS str_emp_name,sp.json_attendance,sp.dbl_net_salary,sp.json_deductions, struct.json_rules FROM auth_user au JOIN user_details ud ON ud.user_ptr_id = au.id AND ud.dat_doj <= '{3}'::DATE LEFT JOIN salary_processed sp ON sp.fk_employee_id =ud.user_ptr_id AND sp.int_month={0} AND sp.int_year={1} AND int_status=0 JOIN category cat ON cat.pk_bint_id = ud.fk_category_id LEFT JOIN salary_structure struct ON struct.pk_bint_id = ud.fk_salary_struct_id LEFT JOIN department dept ON dept.pk_bint_id = ud.fk_department_id LEFT JOIN job_position desig ON desig.pk_bint_id = ud.fk_desig_id LEFT JOIN branch brnch ON brnch.pk_bint_id = ud.fk_branch_id LEFT JOIN salary_details slrydtl ON slrydtl.fk_employee_id = ud.user_ptr_id AND slrydtl.int_status = 1 WHERE (au.is_active = TRUE OR (au.is_active = FALSE AND ud.dat_resignation::date>='{2}'::date)){4} GROUP BY ud.vchr_uan_no,sp.dbl_gross,sp.dbl_hra,int_emp_id,ud.dat_resignation,sp.json_attendance, ud.vchr_employee_code, str_emp_name,sp.dbl_net_salary,sp.json_deductions, struct.json_rules ORDER BY TRIM(TRIM(TRIM(ud.vchr_employee_code,'MYGC-'),'MYGE-'),'MYGT-')::INT"
            str_filter=""
            if int_cat_id:
                str_filter += ' AND cat.pk_bint_id = '+str(int_cat_id)
            if request.data.get('lstDesignation'):
                str_filter += ' AND desig.pk_bint_id IN ('+str(request.data.get('lstDesignation'))[1:-1]+')'
            if request.data.get('intDepartmentId'):
                str_filter += ' AND dept.pk_bint_id = '+str(request.data.get('intDepartmentId'))
            if request.data.get('lstBranch'):
                str_filter += ' AND brnch.pk_bint_id IN ('+str(request.data.get('lstBranch'))[1:-1]+')'
            if request.data.get('intSalaryFrom'):
                str_filter += ' AND ud.dbl_gross >= '+str(request.data.get('intSalaryFrom'))
            if request.data.get('intSalaryTo'):
                str_filter += ' AND ud.dbl_gross <= '+str(request.data.get('intSalaryTo'))

            str_filter += " AND (ud.json_allowance->>'bln_pf')::BOOLEAN=TRUE"
            if request.data.get('intPFNumber'):
                str_filter += " AND ud.vchr_uan_no = '"+str(request.data.get('intPFNumber'))+"'"

            str_query = str_query.format(str(int_month), str(int_year), str_start_date, str_end_date, str_filter)
            rst_data = conn.execute(str_query).fetchall()
            dct_struct = {data['vchr_type']:{'ER':data['dbl_empr_share'], 'EE':data['dbl_empy_share']} for data in PfandEsiStructure.objects.filter(Q(int_end_month__isnull=True, int_end_year__isnull=True) | Q(int_end_month__gte=int_month, int_end_year__gte=int_year), int_start_month__lte=int_month, int_start_year__lte=int_year).values('vchr_type', 'dbl_empr_share', 'dbl_empy_share')}
            if not rst_data:
                conn.close()
                return Response({'status':0,'reason':'No Data'})
            lst_data = []
            for ins_user in rst_data:
                dct_data={}
                int_days = 30
                ins_user=dict(ins_user)
                ins_user['json_attendance'] = ins_user.get('json_attendance') if ins_user.get('json_attendance') else {}

                dct_data['str_uan'] = ins_user.get('str_uan')
                dct_data['emp_name'] = ins_user.get('str_emp_name')
                dct_data['dbl_gross'] = ins_user.get('dbl_gross')
                dct_data['dbl_epf'] = 0
                dct_data['dbl_eps'] = 0
                dct_data['dbl_edli'] = 0
                if ins_user['json_deductions'] and ins_user['json_deductions'].get('PF'):
                    if ins_user['dbl_gross']-ins_user['dbl_hra'] < 15000:
                        dct_data['dbl_epf'] = ins_user['dbl_gross']-ins_user['dbl_hra']
                        dct_data['dbl_eps'] = ins_user['dbl_gross']-ins_user['dbl_hra']
                        dct_data['dbl_edli'] = ins_user['dbl_gross']-ins_user['dbl_hra']
                    else:
                        dct_data['dbl_epf'] = 15000
                        dct_data['dbl_eps'] = 15000
                        dct_data['dbl_edli'] = 15000

                dct_data['dbl_epf_contri'] = round(dct_data['dbl_epf']*((dct_struct.get('PF', {}).get('EE') if dct_struct.get('PF', {}).get('EE') else ins_user['json_rules'].get('Deductions', {}).get('PF',10))/100),0)
                dct_data['dbl_eps_contri'] = round(dct_data['dbl_eps']*((8.33)/100),0)
                dct_data['dbl_epf_eps_diff'] = dct_data['dbl_epf_contri']-dct_data['dbl_eps_contri']
                dct_data['dbl_ncp'] = ins_user.get('json_attendance',{}).get('dbl_tot_lop',0)
                dct_data['dbl_refund'] = ''
                lst_data.append(dct_data)
            file_name = 'SalaryReport/PF_Upload_Report_' + datetime.strftime(date.today(), "%d-%m-%Y") + '.xlsx'
            if not path.exists(settings.MEDIA_ROOT + '/SalaryReport/'):
                os.mkdir(settings.MEDIA_ROOT + '/SalaryReport/')
            writer = pd.ExcelWriter(settings.MEDIA_ROOT + '/' + file_name, engine ='xlsxwriter')
            workbook = writer.book
            worksheet = workbook.add_worksheet()

            title_style = workbook.add_format({'font_size':14, 'bold':1, 'align': 'center', 'border':1})
            title_style.set_align('vcenter')
            title_style.set_pattern(1)
            title_style.set_bg_color('#ffe0cc')
            worksheet.merge_range('A1+:K1', 'PF Upload Report ('+calendar.month_name[int_month]+' '+str(int_year)+')', title_style)
            worksheet.set_row(0, 30)

            head_style = workbook.add_format({'font_size':11, 'bold':1, 'align': 'center','border':1,'border_color':'#000000','text_wrap':True})
            head_style.set_pattern(1)
            head_style.set_bg_color('#bfbfbf')
            head_style.set_align('vcenter')
            worksheet.autofilter('B2:K2')

            row_style = workbook.add_format({'font_size':11})
            row_style.set_align('vcenter')

            worksheet.protect('',{'autofilter':True})

            int_row = 1
            worksheet.write(int_row, 0, 'UAN', head_style); worksheet.set_column(0, 0, 15)
            worksheet.write(int_row, 1, 'MEMBER NAME', head_style); worksheet.set_column(1, 1, 25)
            worksheet.write(int_row, 2, 'GROSS WAGES', head_style);
            worksheet.write(int_row, 3, 'EPF WAGES', head_style);
            worksheet.write(int_row, 4, 'EPS WAGES', head_style);
            worksheet.write(int_row, 5, 'EDLI WAGES', head_style);
            worksheet.write(int_row, 6, 'EPF CONTRI REMITTED', head_style);
            worksheet.write(int_row, 7, 'EPS CONTRI REMITTED', head_style);
            worksheet.write(int_row, 8, 'EPF EPS DIFF REMITTED', head_style);
            worksheet.write(int_row, 9, 'NCP DAYS', head_style);
            worksheet.write(int_row, 10, 'REFUND OF ADVANCES', head_style); worksheet.set_column(2, 10, 15)
            worksheet.set_row(int_row, 35)

            for ins_data in lst_data:
                int_row += 1
                worksheet.write(int_row, 0, ins_data.get('str_uan'), row_style)
                worksheet.write(int_row, 1, ins_data.get('emp_name'), row_style)
                worksheet.write(int_row, 2, ins_data.get('dbl_gross'), row_style)
                worksheet.write(int_row, 3, ins_data.get('dbl_epf'), row_style)
                worksheet.write(int_row, 4, ins_data.get('dbl_eps'), row_style)
                worksheet.write(int_row, 5, ins_data.get('dbl_edli'), row_style)
                worksheet.write(int_row, 6, ins_data.get('dbl_epf_contri'), row_style)
                worksheet.write(int_row, 7, ins_data.get('dbl_eps_contri'), row_style)
                worksheet.write(int_row, 8, ins_data.get('dbl_epf_eps_diff'), row_style)
                worksheet.write(int_row, 9, ins_data.get('dbl_ncp'), row_style)
                worksheet.write(int_row, 10, ins_data.get('dbl_refund'), row_style)
            writer.save()
            conn.close()
            return Response({'status':1, 'data':request.scheme+'://'+request.get_host()+settings.MEDIA_URL+file_name})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


class WPSReport(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            conn = engine.connect()

            int_month = int(request.data.get('intMonthYear').split('-')[0])
            int_year = int(request.data.get('intMonthYear').split('-')[1])
            now_date = datetime.now()

            dur_calendar = calendar.monthrange(int_year, int_month)
            str_start_date = str(int_year)+'-'+str(int_month)+'-1'
            str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(dur_calendar[1])

            if not request.user.is_superuser:
                ins_admin = AdminSettings.objects.filter(vchr_code='PAYROLL_PERIOD',bln_enabled=True,fk_company_id=request.user.userdetails.fk_company_id).values('vchr_value', 'int_value').first()
                if ins_admin and ins_admin['int_value'] != 0:
                    str_start_date = datetime.strftime(datetime.strptime(str(int_year)+'-'+str(int_month)+'-'+ins_admin['vchr_value'][0],'%Y-%m-%d')+timedelta(days=int(ins_admin['vchr_value'][0])*ins_admin['int_value']),'%Y-%m-')+ins_admin['vchr_value'][0]
                    str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(int(ins_admin['vchr_value'][0])-1)

            if int_month == now_date.month and int_year == now_date.year and now_date.day <= int(str_end_date.split('-')[2]):
                str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(now_date.day)

            dat_month_last = datetime.strptime(str_end_date, '%Y-%m-%d')
            dat_month_first = datetime.strptime(str_start_date, '%Y-%m-%d')

            str_query = "SELECT ud.vchr_employee_code AS emp_code,CONCAT(TRIM(au.first_name), ' ', CASE WHEN ud.vchr_middle_name IS NOT NULL THEN CONCAT(TRIM(ud.vchr_middle_name), ' ', TRIM(au.last_name)) ELSE TRIM(au.last_name) END) AS str_emp_name,ud.vchr_father_name,ud.vchr_gender AS str_gender, to_char(ud.dat_dob :: DATE,'dd-Mon-yyyy') AS emp_dob,jp.vchr_name AS emp_desig,to_char(ud.dat_doj :: DATE,'dd-Mon-yyyy') AS date_of_join ,ud.bint_phone AS emp_phone,CASE WHEN ud.vchr_email IS NOT NULL THEN ud.vchr_email else au.email END AS emp_email,ud.vchr_bank_name, ud.vchr_ifsc, ud.vchr_acc_no, sp.json_attendance->'dbl_tot_lop' AS total_lop,sp.json_attendance->'int_week_off' AS weekly_off_granted,sp.json_attendance->'dbl_casual_leave' AS num_leave_granted,sp.dbl_bp AS basic_pay,sp.dbl_da,sp.dbl_hra,sp.dbl_cca,sp.dbl_wa,sp.dbl_sa,sp.dbl_gross AS gross_wages,sp.dbl_gross AS total_amount,sp.json_deductions->'PF' AS provident_fund,sp.json_deductions->'SalaryAdvance' AS advance_deduction,sp.json_deductions->'WWF' AS welfare_fund,sp.dbl_net_salary AS Net_wages_payed,to_char(sp.dat_approval :: DATE,'dd-Mon-yyyy') AS dat_payment, sp.json_deductions, sp.json_allowances, wp.vchr_name AS str_wps_name FROM auth_user au JOIN user_details ud ON au.id = ud.user_ptr_id AND ud.dat_doj <= '{3}'::DATE LEFT JOIN salary_processed sp ON sp.fk_employee_id = ud.user_ptr_id AND sp.int_status=0 AND sp.int_month = {0} AND sp.int_year = {1} LEFT JOIN job_position jp ON jp.pk_bint_id = ud.fk_desig_id LEFT JOIN wps AS wp ON wp.pk_bint_id = ud.fk_wps_id WHERE (au.is_active = TRUE OR (au.is_active = FALSE AND ud.dat_resignation::date>='{2}'::DATE)){4} ORDER BY TRIM(TRIM(TRIM(ud.vchr_employee_code,'MYGC-'),'MYGE-'),'MYGT-')::INT"

            str_filter = ''
            if request.data.get('intCategoryId'):
                str_filter += ' AND ud.fk_category_id = '+str(request.data.get('intCategoryId'))
            if request.data.get('lstDesignation'):
                str_filter += ' AND jp.pk_bint_id  IN ('+str(request.data.get('lstDesignation'))[1:-1]+')'
            if request.data.get('intDepartmentId'):
                str_filter += ' AND ud.fk_department_id = '+str(request.data.get('intDepartmentId'))
            if request.data.get('lstBranch'):
                str_filter += ' AND ud.fk_branch_id IN ('+str(request.data.get('lstBranch'))[1:-1]+')'
            if request.data.get('lstEmployee'):
                str_filter += ' AND ud.user_ptr_id IN ('+str(request.data.get('lstEmployee'))[1:-1]+')'
            if request.data.get('intWPSGroupId'):
                str_filter += ' AND wp.pk_bint_id = '+str(request.data.get('intWPSGroupId'))

            str_query = str_query.format(str(int_month), str(int_year), str_start_date, str_end_date, str_filter)

            rst_data = conn.execute(str_query).fetchall()
            if not rst_data:
                conn.close()
                return Response({'status':0,'reason':'No Data'})
            lst_data = []
            for ins_user in rst_data:
                dct_data = {}
                dct_user = dict(ins_user)
                int_days = 30
                dct_data['str_emp_code'] = dct_user['emp_code']
                dct_data['str_emp_name'] = dct_user['str_emp_name']
                dct_data['str_father_name'] = dct_user['vchr_father_name']
                dct_data['str_gender'] = dct_user['str_gender']
                dct_data['date_of_birth'] = dct_user['emp_dob']
                dct_data['str_designation'] = dct_user['emp_desig']
                dct_data['date_of_join'] = dct_user['date_of_join']
                dct_data['int_phone'] = dct_user['emp_phone']
                dct_data['str_email'] = dct_user['emp_email']
                dct_data['str_bank_name'] = dct_user['vchr_bank_name']
                dct_data['str_ifsc'] = dct_user['vchr_ifsc']
                dct_data['int_account_no'] = dct_user['vchr_acc_no']
                dct_data['days_of_attendance'] = int_days - (dct_user['total_lop'] if dct_user['total_lop'] else 0)
                dct_data['loss_of_pay'] = dct_user['total_lop']
                dct_data['weekly_off_granted'] = dct_user['weekly_off_granted']
                dct_data['num_leave_granted'] = dct_user['num_leave_granted']
                dct_data['basic_pay'] = dct_user['basic_pay'] - (dct_user['dbl_da'] if dct_user['dbl_da'] else 0)
                dct_data['dbl_da'] = dct_user['dbl_da'] if dct_user['dbl_da'] else 0
                dct_data['dbl_hra'] = dct_user['dbl_hra']
                dct_data['dbl_cca'] = dct_user['dbl_cca']+dct_user['dbl_wa']+dct_user['dbl_sa']
                dct_data['gross_monthly_wages'] = dct_user['gross_wages']
                dct_data['other_allowances'] = dct_user['json_allowances'].get('FixedAllowance', 0.0) + dct_user['json_allowances'].get('VariablePay', 0.0)
                dct_data['total_amount'] = dct_user['total_amount']
                dct_data['provident_fund'] = dct_user['provident_fund']
                dct_data['advance_deduction'] = dct_user['advance_deduction']+dct_user['json_deductions'].get('WorkLoan', 0)+dct_user['json_deductions'].get('MobileLoan', 0)
                dct_data['welfare_fund'] = dct_user['welfare_fund']
                dct_data['professional_tax'] = dct_user['json_deductions']['ProTax']
                dct_data['dbl_esi'] = dct_user['json_deductions'].get('ESI', 0)
                dct_data['dbl_tds'] = dct_user['json_deductions'].get('TDS', 0)
                dct_data['other_deduction'] = dct_user['json_deductions'].get('Charity', 0)
                dct_data['total_deductions'] = dct_user['welfare_fund']+dct_data['advance_deduction']+dct_user['provident_fund']+dct_data['professional_tax']+dct_data['other_deduction']
                dct_data['net_wages_payed'] = dct_user['net_wages_payed']
                dct_data['date_of_payment'] = dct_user['dat_payment']
                dct_data['str_wps_group'] = dct_user['str_wps_name']

                lst_data.append(dct_data)

            file_name = 'SalaryReport/WPS_Report_' + datetime.strftime(date.today(), "%d-%m-%Y") + '.xlsx'
            if not path.exists(settings.MEDIA_ROOT + '/SalaryReport/'):
                os.mkdir(settings.MEDIA_ROOT + '/SalaryReport/')
            writer = pd.ExcelWriter(settings.MEDIA_ROOT + '/' + file_name, engine ='xlsxwriter')
            workbook = writer.book
            worksheet = workbook.add_worksheet()

            title_style = workbook.add_format({'font_size':14, 'bold':1, 'align': 'center', 'border':1})
            title_style.set_align('vcenter')
            title_style.set_pattern(1)
            title_style.set_bg_color('#ffe0cc')
            worksheet.merge_range('A1+:AR1', 'WPS Report ('+calendar.month_name[int_month]+' '+str(int_year)+')', title_style)
            worksheet.set_row(0, 30)

            head_style = workbook.add_format({'font_size':11, 'bold':1, 'align': 'center','border':1,'border_color':'#000000','text_wrap':True})
            head_style.set_pattern(1)
            head_style.set_bg_color('#bfbfbf')
            head_style.set_align('vcenter')
            worksheet.autofilter('B2:AR2')

            row_style = workbook.add_format({'font_size':11})
            row_style.set_align('vcenter')

            worksheet.protect('',{'autofilter':True})

            int_row = 1
            worksheet.write(int_row, 0, 'Employee Code', head_style); worksheet.set_column(0, 0, 13)
            worksheet.write(int_row, 1, 'Employee Name', head_style)
            worksheet.write(int_row, 2, 'Name of Father/Husband', head_style); worksheet.set_column(1, 2, 30)
            worksheet.write(int_row, 3, 'Sex', head_style); worksheet.set_column(3, 3, 10)
            worksheet.write(int_row, 4, 'Date of Birth', head_style); worksheet.set_column(4, 4, 15)
            worksheet.write(int_row, 5, 'Designation', head_style); worksheet.set_column(5, 5, 30)
            worksheet.write(int_row, 6, 'Designation Code/Grade as in Government Order', head_style); worksheet.set_column(6, 6, 20)
            worksheet.write(int_row, 7, 'Date of Joining', head_style); worksheet.set_column(7, 7, 15)
            worksheet.write(int_row, 8, 'Mobile Number', head_style); worksheet.set_column(8, 8, 17)
            worksheet.write(int_row, 9, 'E-mail ID', head_style)
            worksheet.write(int_row, 10, 'Bank Name', head_style); worksheet.set_column(9, 10, 25)
            worksheet.write(int_row, 11, 'IFSC Code', head_style); worksheet.set_column(11, 11, 15)
            worksheet.write(int_row, 12, 'Bank Account Number', head_style); worksheet.set_column(12, 12, 22)
            worksheet.write(int_row, 13, 'Days of Attendance', head_style)
            worksheet.write(int_row, 14, 'Loss of Pay Days', head_style)
            worksheet.write(int_row, 15, 'Number of Weekly Off Granted', head_style)
            worksheet.write(int_row, 16, 'Number of Leave Granted', head_style)
            worksheet.write(int_row, 17, 'Basic', head_style)
            worksheet.write(int_row, 18, 'DA', head_style)
            worksheet.write(int_row, 19, 'HRA', head_style)
            worksheet.write(int_row, 20, 'City Compensation Allowances', head_style)
            worksheet.write(int_row, 21, 'Gross Monthly Wages', head_style)
            worksheet.write(int_row, 22, 'Overtime Wages', head_style)
            worksheet.write(int_row, 23, 'Leave Wages', head_style)
            worksheet.write(int_row, 24, 'National & Festival Holidays Wages', head_style)
            worksheet.write(int_row, 25, 'Arrear Paid', head_style)
            worksheet.write(int_row, 26, 'Bonus', head_style)
            worksheet.write(int_row, 27, 'Maternity Benefit', head_style)
            worksheet.write(int_row, 28, 'Other Allowances', head_style)
            worksheet.write(int_row, 29, 'Advance', head_style)
            worksheet.write(int_row, 30, 'Total Amount', head_style)
            worksheet.write(int_row, 31, 'Employees Provident Fund', head_style)
            worksheet.write(int_row, 32, 'Employees State Insurance', head_style)
            worksheet.write(int_row, 33, 'Advances', head_style)
            worksheet.write(int_row, 34, 'Welfare Fund', head_style)
            worksheet.write(int_row, 35, 'Professional Tax', head_style)
            worksheet.write(int_row, 36, 'Tax Deducted at Source', head_style)
            worksheet.write(int_row, 37, 'Deduction of Fine', head_style)
            worksheet.write(int_row, 38, 'Deduction for Loss & Damages', head_style)
            worksheet.write(int_row, 39, 'Other Deduction', head_style)
            worksheet.write(int_row, 40, 'Total Deduction', head_style)
            worksheet.write(int_row, 41, 'Net Wages Paid', head_style)
            worksheet.write(int_row, 42, 'Date of Payment', head_style); worksheet.set_column(13, 42, 17)
            worksheet.write(int_row, 43, 'Remarks', head_style); worksheet.set_column(43, 43, 17)
            worksheet.set_row(int_row, 43)

            for ins_data in lst_data:
                int_row += 1
                worksheet.write(int_row, 0, ins_data.get('str_emp_code'), row_style)
                worksheet.write(int_row, 1, ins_data.get('str_emp_name'), row_style)
                worksheet.write(int_row, 2, ins_data.get('str_father_name'), row_style)
                worksheet.write(int_row, 3, ins_data.get('str_gender'), row_style)
                worksheet.write(int_row, 4, ins_data.get('date_of_birth'), row_style)
                worksheet.write(int_row, 5, ins_data.get('str_designation'), row_style)
                worksheet.write(int_row, 6, ' ', row_style)
                worksheet.write(int_row, 7, ins_data.get('date_of_join'), row_style)
                worksheet.write(int_row, 8, ins_data.get('int_phone'), row_style)
                worksheet.write(int_row, 9, ins_data.get('str_email'), row_style)
                worksheet.write(int_row, 10, ins_data.get('str_bank_name'), row_style)
                worksheet.write(int_row, 11, ins_data.get('str_ifsc'), row_style)
                worksheet.write(int_row, 12, ins_data.get('int_account_no'), row_style)
                worksheet.write(int_row, 13, ins_data.get('days_of_attendance'), row_style)
                worksheet.write(int_row, 14, ins_data.get('loss_of_pay'), row_style)
                worksheet.write(int_row, 15, ins_data.get('weekly_off_granted'), row_style)
                worksheet.write(int_row, 16, ins_data.get('num_leave_granted'), row_style)
                worksheet.write(int_row, 17, ins_data.get('basic_pay'), row_style)
                worksheet.write(int_row, 18, ins_data.get('dbl_da'), row_style)
                worksheet.write(int_row, 19, ins_data.get('dbl_hra'), row_style)
                worksheet.write(int_row, 20, ins_data.get('dbl_cca'), row_style)
                worksheet.write(int_row, 21, ins_data.get('gross_monthly_wages'), row_style)
                worksheet.write(int_row, 22, 0, row_style)
                worksheet.write(int_row, 23, 0, row_style)
                worksheet.write(int_row, 24, 0, row_style)
                worksheet.write(int_row, 25, 0, row_style)
                worksheet.write(int_row, 26, 0, row_style)
                worksheet.write(int_row, 27, 0, row_style)
                worksheet.write(int_row, 28, ins_data.get('other_allowances'), row_style)
                worksheet.write(int_row, 29, 0, row_style)
                worksheet.write(int_row, 30, ins_data.get('total_amount'), row_style)
                worksheet.write(int_row, 31, ins_data.get('provident_fund'), row_style)
                worksheet.write(int_row, 32, ins_data.get('dbl_esi'), row_style)
                worksheet.write(int_row, 33, ins_data.get('advance_deduction'), row_style)
                worksheet.write(int_row, 34, ins_data.get('welfare_fund'), row_style)
                worksheet.write(int_row, 35, ins_data.get('professional_tax'), row_style)
                worksheet.write(int_row, 36, ins_data.get('dbl_tds'), row_style)
                worksheet.write(int_row, 37, 0, row_style)
                worksheet.write(int_row, 38, 0, row_style)
                worksheet.write(int_row, 39, ins_data.get('other_deduction'), row_style)
                worksheet.write(int_row, 40, ins_data.get('total_deductions'), row_style)
                worksheet.write(int_row, 41, ins_data.get('net_wages_payed'), row_style)
                worksheet.write(int_row, 42, ins_data.get('date_of_payment'), row_style)
                worksheet.write(int_row, 43, ins_data.get('str_wps_group'), row_style)
            writer.save()
            conn.close()
            return Response({'status':1, 'data':request.scheme+'://'+request.get_host()+settings.MEDIA_URL+file_name})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


def AllSalaryDetails(request, str_month_year, str_start_date, str_end_date, str_filter = '', int_max_days = 30):
    try:
        conn = engine.connect()
        int_month = int(str_month_year.split('-')[0])
        int_year = int(str_month_year.split('-')[1])

        str_select_part = "SELECT ud.user_ptr_id AS int_emp_id, ud.vchr_employee_code, CONCAT(TRIM(au.first_name), ' ', CASE WHEN ud.vchr_middle_name IS NOT NULL THEN CONCAT(TRIM(ud.vchr_middle_name), ' ', TRIM(au.last_name)) ELSE TRIM(au.last_name) END) AS str_emp_name, dept.vchr_name AS str_department, desig.vchr_name AS str_designation, brnch.vchr_name AS str_branch, ud.dat_doj AS dat_joined, cat.vchr_name AS str_category_name, JSON_BUILD_OBJECT('int_struct_id', struct.pk_bint_id, 'str_struct_name', struct.vchr_name, 'dbl_bp_da', struct.dbl_bp_da, 'dbl_bp_da_per', struct.dbl_bp_da_per, 'dbl_da', struct.dbl_da, 'json_rules', struct.json_rules) AS json_structure, JSON_BUILD_OBJECT('int_details_id', slrydtl.pk_bint_id, 'dbl_bp', slrydtl.dbl_bp, 'dbl_da', slrydtl.dbl_da, 'dbl_hra', slrydtl.dbl_hra, 'dbl_cca', slrydtl.dbl_cca, 'dbl_sa', slrydtl.dbl_sa, 'dbl_wa', slrydtl.dbl_wa, 'dbl_gross', (CASE WHEN ud.dbl_gross IS NOT NULL THEN ud.dbl_gross ELSE 0 END), 'json_deduction', slrydtl.json_deduction, 'json_allowance', slrydtl.json_allowance, 'dbl_variable_pay', (CASE WHEN vrblpy.dbl_amount IS NOT NULL THEN vrblpy.dbl_amount ELSE 0 END), 'dbl_fixed_allowance', (CASE WHEN fxalwc.dbl_amount IS NOT NULL THEN fxalwc.dbl_amount ELSE 0 END), 'dbl_adv_amount', (CASE WHEN slryadv.dbl_amount IS NOT NULL THEN slryadv.dbl_amount ELSE 0 END), 'json_rules', ud.json_allowance, 'json_loan', JSON_BUILD_OBJECT('json_mobile_loan', JSON_BUILD_OBJECT('int_loan_id', londtlsm.pk_bint_id, 'dbl_loan_amount', (CASE WHEN londtlsm.dbl_amount IS NOT NULL THEN londtlsm.dbl_amount ELSE 0 END), 'bln_mob_loan', lonrqstm.bln_mob_loan), 'json_work_loan', JSON_BUILD_OBJECT('int_loan_id', londtlsw.pk_bint_id, 'dbl_loan_amount', (CASE WHEN londtlsw.dbl_amount IS NOT NULL THEN londtlsw.dbl_amount ELSE 0 END), 'bln_mob_loan', lonrqstw.bln_mob_loan))) AS json_salary_details, JSONB_AGG(JSON_BUILD_OBJECT(to_char(sris.dat_series, 'DD-MM-YYYY'), INITCAP(CASE WHEN au.is_active = FALSE AND ud.dat_resignation < sris.dat_series THEN 'Resigned' WHEN plog.dat_punch IS NULL AND ud.dat_doj > sris.dat_series THEN 'Absent' WHEN wkoff.pk_bint_id IS NOT NULL OR TRIM(ud.vchr_weekoff_day) ILIKE TRIM(TO_CHAR(sris.dat_series, 'Day')) THEN CASE WHEN plog.vchr_direction = 'OUT' THEN CONCAT('Worked on Week Off ', to_char(plog.dat_start, 'HH:MI AM'),' - ' ,to_char(plog.dat_end, 'HH:MI AM')) ELSE 'Week Off' END WHEN hldy.pk_bint_id IS NOT NULL THEN CASE WHEN plog.vchr_direction = 'OUT' THEN CONCAT('Worked on ', INITCAP(hldy.vchr_name), ' ', to_char(plog.dat_start, 'HH:MI AM'),' - ' ,to_char(plog.dat_end, 'HH:MI AM')) ELSE INITCAP(hldy.vchr_name) END WHEN wklv.int_status IS NOT NULL THEN CONCAT('Week Off', CASE WHEN wklv.int_status = 1 THEN ' Pending Approval' WHEN wklv.int_status = 2 THEN ' Pending Verification' END) WHEN lev.int_status IN (1, 2) THEN CONCAT(CASE WHEN lev.chr_leave_mode='F' THEN 'Full Day' ELSE 'Half Day' END, ' ', levtyp.vchr_name, CASE WHEN lev.int_status = 1 THEN ' Pending Approval' END) WHEN odr.int_status != -1 THEN CONCAT(CASE WHEN odr.chr_day_type='F' THEN 'Full Day' ELSE 'Half Day' END, ' On-Duty', CASE WHEN odr.int_status = 0 THEN ' Pending Approval' WHEN odr.int_status = 1 THEN ' Pending Verification' END) WHEN cofu.int_status IN (1, 2) THEN CONCAT(CASE WHEN cofu.chr_leave_mode='F' THEN 'Full Day' ELSE 'Half Day' END, ' Combo Off', CASE WHEN cofu.int_status = 1 THEN ' Pending Approval' END) WHEN eshft.int_shift_type = 2 THEN 'Present - Shift Exempted' WHEN shftex.pk_bint_id IS NOT NULL AND plog.vchr_direction = 'OUT' THEN CONCAT('Free Shift ', to_char(plog.dat_start, 'HH:MI AM'),' - ' ,to_char(plog.dat_end, 'HH:MI AM')) WHEN plog.vchr_direction = 'OUT' AND ((CASE WHEN lev.int_status = 2 AND lev.chr_leave_mode != 'F' THEN 0.5 ELSE 0 END) + (CASE WHEN odr.int_status = 2 AND odr.chr_day_type != 'F' THEN 0.5 ELSE 0 END) + (CASE WHEN cofu.int_status = 2 AND cofu.chr_leave_mode != 'F' THEN 0.5 ELSE 0 END)) < 1 THEN (CASE WHEN (plog.dat_end - plog.dat_start) + (CASE WHEN ltrqst.int_status IN (1, 2) THEN ('01:00:00'::INTERVAL)*ltplcy.dbl_hours ELSE '00:00:00'::INTERVAL END) + admnst.tim_punch_cool < (CASE WHEN shft.time_half_day IS NOT NULL THEN shft.time_half_day::INTERVAL WHEN shft.time_full_day IS NOT NULL THEN (shft.time_full_day::INTERVAL)/2 WHEN shft.time_shed_hrs IS NOT NULL THEN (shft.time_shed_hrs::INTERVAL)/2 ELSE (shft.time_shift_to-shft.time_shift_from)/2 END) THEN CONCAT('Absent ', to_char(plog.dat_start, 'HH:MI AM'),' - ' ,to_char(plog.dat_end, 'HH:MI AM')) WHEN (TRIM(TO_CHAR(sris.dat_series::DATE,'Day')) ILIKE 'saturday' AND TO_CHAR(sris.dat_series::DATE,'W')::INT = 2 AND brnch.vchr_name ILIKE 'head office') AND (plog.dat_end - plog.dat_start) + (CASE WHEN ltrqst.int_status IN (1, 2) THEN ('01:00:00'::INTERVAL)*ltplcy.dbl_hours ELSE '00:00:00'::INTERVAL END) + admnst.tim_punch_cool > (CASE WHEN shft.time_half_day IS NOT NULL THEN shft.time_half_day::INTERVAL WHEN shft.time_full_day IS NOT NULL THEN (shft.time_full_day::INTERVAL)/2 WHEN shft.time_shed_hrs IS NOT NULL THEN (shft.time_shed_hrs::INTERVAL)/2 ELSE (shft.time_shift_to-shft.time_shift_from)/2 END) THEN CONCAT('Present ', to_char(plog.dat_start, 'HH:MI AM'),' - ' ,to_char(plog.dat_end, 'HH:MI AM')) WHEN (plog.dat_end - plog.dat_start) + (CASE WHEN ltrqst.int_status IN (1, 2) THEN ('01:00:00'::INTERVAL)*ltplcy.dbl_hours ELSE '00:00:00'::INTERVAL END) + admnst.tim_punch_cool < (CASE WHEN shft.time_full_day IS NOT NULL THEN shft.time_full_day::INTERVAL WHEN shft.time_shed_hrs IS NOT NULL THEN shft.time_shed_hrs::INTERVAL ELSE (shft.time_shift_to-shft.time_shift_from) END) THEN CONCAT('Half Day ', to_char(plog.dat_start, 'HH:MI AM'),' - ' ,to_char(plog.dat_end, 'HH:MI AM')) ELSE CONCAT('Present ', to_char(plog.dat_start, 'HH:MI AM'),' - ' ,to_char(plog.dat_end, 'HH:MI AM')) END) WHEN plog.vchr_direction = 'IN' THEN CONCAT('Punch-Out Missing - ', to_char(plog.dat_start, 'HH:MI AM')) WHEN ((CASE WHEN lev.int_status = 2 AND lev.chr_leave_mode != 'F' THEN 0.5 ELSE 0 END) + (CASE WHEN odr.int_status = 2 AND odr.chr_day_type != 'F' THEN 0.5 ELSE 0 END) + (CASE WHEN cofu.int_status = 2 AND cofu.chr_leave_mode != 'F' THEN 0.5 ELSE 0 END)) >= 1 THEN (CASE WHEN lev.int_status = 2 AND lev.chr_leave_mode = 'F' THEN INITCAP(levtyp.vchr_name) WHEN odr.int_status = 2 AND odr.chr_day_type = 'F' THEN 'On Duty' WHEN cofu.int_status = 2 AND cofu.chr_leave_mode = 'F' THEN 'Comp Off' ELSE CONCAT(CASE WHEN lev.int_status = 2 THEN CONCAT('Half Day ', INITCAP(levtyp.vchr_name)) ELSE '' END, CASE WHEN lev.int_status = 2 AND odr.int_status = 2 THEN ' - Half Day On Duty' WHEN odr.int_status = 2 THEN 'Half Day On Duty' ELSE '' END, CASE WHEN (lev.int_status = 2 OR odr.int_status = 2) AND cofu.int_status = 2 THEN ' - Half Day Comp Off' WHEN cofu.int_status = 2 THEN 'Half Day Comp Off' ELSE '' END) END) ELSE 'Absent' END))) AS json_attendance, SUM(CASE WHEN plog.dat_start IS NOT NULL AND plog.dat_end IS NOT NULL THEN (plog.dat_end::TIME - plog.dat_start::TIME)::TIME END) AS dur_worked_hour, (CASE WHEN eshft.int_shift_type = 2 THEN '00:00:00'::INTERVAL WHEN lshrde.dur_aftr_deduct IS NOT NULL THEN lshrde.dur_aftr_deduct WHEN tmshft.time_full_day IS NOT NULL AND tmshft.time_full_day > (SUM(plog.dat_end-plog.dat_start) + SUM(CASE WHEN ltrqst.int_status IN (1, 2) THEN ('01:00:00'::INTERVAL)*ltplcy.dbl_hours ELSE '00:00:00'::INTERVAL END) + (tmshft.time_full_day/{5} * SUM((CASE WHEN lev.int_status = 2 AND lev.chr_leave_mode = 'F' THEN 1 WHEN lev.int_status = 2 AND lev.chr_leave_mode != 'F' THEN 0.5 ELSE 0 END) + (CASE WHEN odr.int_status = 2 AND odr.chr_day_type = 'F' THEN 1 WHEN odr.int_status = 2 AND odr.chr_day_type != 'F' THEN 0.5 ELSE 0 END) + (CASE WHEN cofu.int_status = 2 AND cofu.chr_leave_mode = 'F' THEN 1 WHEN cofu.int_status = 2 AND cofu.chr_leave_mode != 'F' THEN 0.5 ELSE 0 END)))) THEN tmshft.time_full_day - (SUM(plog.dat_end-plog.dat_start) + SUM(CASE WHEN ltrqst.int_status IN (1, 2) THEN ('01:00:00'::INTERVAL)*ltplcy.dbl_hours ELSE '00:00:00'::INTERVAL END) + (tmshft.time_full_day/{5} * SUM((CASE WHEN lev.int_status = 2 AND lev.chr_leave_mode = 'F' THEN 1 WHEN lev.int_status = 2 AND lev.chr_leave_mode != 'F' THEN 0.5 ELSE 0 END) + (CASE WHEN odr.int_status = 2 AND odr.chr_day_type = 'F' THEN 1 WHEN odr.int_status = 2 AND odr.chr_day_type != 'F' THEN 0.5 ELSE 0 END) + (CASE WHEN cofu.int_status = 2 AND cofu.chr_leave_mode = 'F' THEN 1 WHEN cofu.int_status = 2 AND cofu.chr_leave_mode != 'F' THEN 0.5 ELSE 0 END)))) WHEN lshrde.dur_time IS NOT NULL THEN lshrde.dur_time ELSE '00:00:00'::INTERVAL END) AS less_hours, (CASE WHEN eshft.int_shift_type = 2 THEN 0 WHEN lshrplcy.dbl_days IS NULL AND lshrde.dur_time IS NOT NULL THEN (SELECT CEIL(DATE_PART('EPOCH',(CASE WHEN lshrde.dur_aftr_deduct IS NOT NULL THEN lshrde.dur_aftr_deduct ELSE lshrde.dur_time END)-(SELECT MAX(dur_to) FROM less_hour_policy))/DATE_PART('EPOCH',dur_to)) * dbl_days FROM less_hour_policy WHERE bln_auto=TRUE ORDER BY pk_bint_id DESC LIMIT 1) WHEN tmshft.time_full_day IS NOT NULL AND (tmshft.time_full_day/{5}) > (SUM(plog.dat_end-plog.dat_start) + SUM(CASE WHEN ltrqst.int_status IN (1, 2) THEN ('01:00:00'::INTERVAL)*ltplcy.dbl_hours ELSE '00:00:00'::INTERVAL END) + ((tmshft.time_full_day/{5}) * SUM((CASE WHEN lev.int_status = 2 AND lev.chr_leave_mode = 'F' THEN 1 WHEN lev.int_status = 2 AND lev.chr_leave_mode != 'F' THEN 0.5 ELSE 0 END) + (CASE WHEN odr.int_status = 2 AND odr.chr_day_type = 'F' THEN 1 WHEN odr.int_status = 2 AND odr.chr_day_type != 'F' THEN 0.5 ELSE 0 END) + (CASE WHEN cofu.int_status = 2 AND cofu.chr_leave_mode = 'F' THEN 1 WHEN cofu.int_status = 2 AND cofu.chr_leave_mode != 'F' THEN 0.5 ELSE 0 END)))) THEN (SELECT CEIL(DATE_PART('EPOCH',(tmshft.time_full_day/{5})-(SUM(plog.dat_end-plog.dat_start) + SUM(CASE WHEN ltrqst.int_status IN (1, 2) THEN ('01:00:00'::INTERVAL)*ltplcy.dbl_hours ELSE '00:00:00'::INTERVAL END) + ((tmshft.time_full_day/{5}) * SUM((CASE WHEN lev.int_status = 2 AND lev.chr_leave_mode = 'F' THEN 1 WHEN lev.int_status = 2 AND lev.chr_leave_mode != 'F' THEN 0.5 ELSE 0 END) + (CASE WHEN odr.int_status = 2 AND odr.chr_day_type = 'F' THEN 1 WHEN odr.int_status = 2 AND odr.chr_day_type != 'F' THEN 0.5 ELSE 0 END) + (CASE WHEN cofu.int_status = 2 AND cofu.chr_leave_mode = 'F' THEN 1 WHEN cofu.int_status = 2 AND cofu.chr_leave_mode != 'F' THEN 0.5 ELSE 0 END))))-(SELECT MAX(dur_to) FROM less_hour_policy))/DATE_PART('EPOCH',dur_to)) * dbl_days FROM less_hour_policy WHERE bln_auto=TRUE ORDER BY pk_bint_id DESC LIMIT 1) WHEN lshrplcy.dbl_days IS NOT NULL THEN lshrplcy.dbl_days ELSE 0 END) AS less_hour_days, SUM(CASE WHEN (lev.int_status = 2 AND levtyp.vchr_name IN ({0})) THEN (CASE WHEN lev.chr_leave_mode = 'F' THEN 1 ELSE 0.5 END) ELSE 0 END) AS leave_lop, SUM(CASE WHEN (au.is_active = FALSE AND ud.dat_resignation < sris.dat_series) OR (plog.dat_punch IS NULL AND ud.dat_doj > sris.dat_series) THEN 1 WHEN wkoff.pk_bint_id IS NOT NULL OR TRIM(ud.vchr_weekoff_day) ILIKE TRIM(TO_CHAR(sris.dat_series, 'Day')) OR hldy.pk_bint_id IS NOT NULL OR eshft.int_shift_type = 2 THEN 0 WHEN (lev.int_status IS NULL OR lev.int_status != 2) AND (cofu.int_status IS NULL OR cofu.int_status != 2) AND (odr.int_status IS NULL OR odr.int_status != 2) AND (plog.dat_punch IS NULL OR plog.vchr_direction = 'IN') AND lshrdtl.pk_bint_id IS NULL THEN 1 WHEN (((CASE WHEN lev.int_status = 2 AND lev.chr_leave_mode = 'F' THEN 1 WHEN lev.int_status = 2 AND lev.chr_leave_mode != 'F' THEN 0.5 ELSE 0 END) + (CASE WHEN odr.int_status = 2 AND odr.chr_day_type = 'F' THEN 1 WHEN odr.int_status = 2 AND odr.chr_day_type != 'F' THEN 0.5 ELSE 0 END) + (CASE WHEN cofu.int_status = 2 AND cofu.chr_leave_mode = 'F' THEN 1 WHEN cofu.int_status = 2 AND cofu.chr_leave_mode != 'F' THEN 0.5 ELSE 0 END)) >= 1) THEN 0 WHEN (((CASE WHEN lev.int_status = 2 AND lev.chr_leave_mode = 'F' THEN 1 WHEN lev.int_status = 2 AND lev.chr_leave_mode != 'F' THEN 0.5 ELSE 0 END) + (CASE WHEN odr.int_status = 2 AND odr.chr_day_type = 'F' THEN 1 WHEN odr.int_status = 2 AND odr.chr_day_type != 'F' THEN 0.5 ELSE 0 END) + (CASE WHEN cofu.int_status = 2 AND cofu.chr_leave_mode = 'F' THEN 1 WHEN cofu.int_status = 2 AND cofu.chr_leave_mode != 'F' THEN 0.5 ELSE 0 END)) BETWEEN 0.5 AND 1) AND (plog.dat_punch IS NULL OR plog.vchr_direction = 'IN') AND lshrdtl.pk_bint_id IS NULL THEN 0.5 ELSE 0 END) AS dbl_absent, ((CASE WHEN emplv.dbl_number IS NOT NULL THEN emplv.dbl_number ELSE 0 END) + (CASE WHEN eshft.int_shift_type = 2 THEN 0 WHEN lshrplcy.dbl_days IS NULL AND lshrde.dur_time IS NOT NULL THEN (SELECT CEIL(DATE_PART('EPOCH',(CASE WHEN lshrde.dur_aftr_deduct IS NOT NULL THEN lshrde.dur_aftr_deduct ELSE lshrde.dur_time END)-(SELECT MAX(dur_to) FROM less_hour_policy))/DATE_PART('EPOCH',dur_to)) * dbl_days FROM less_hour_policy WHERE bln_auto=TRUE ORDER BY pk_bint_id DESC LIMIT 1) WHEN tmshft.time_full_day IS NOT NULL AND (tmshft.time_full_day/{5}) > (SUM(plog.dat_end-plog.dat_start) + SUM(CASE WHEN ltrqst.int_status IN (1, 2) THEN ('01:00:00'::INTERVAL)*ltplcy.dbl_hours ELSE '00:00:00'::INTERVAL END) + ((tmshft.time_full_day/{5}) * SUM((CASE WHEN lev.int_status = 2 AND lev.chr_leave_mode = 'F' THEN 1 WHEN lev.int_status = 2 AND lev.chr_leave_mode != 'F' THEN 0.5 ELSE 0 END) + (CASE WHEN odr.int_status = 2 AND odr.chr_day_type = 'F' THEN 1 WHEN odr.int_status = 2 AND odr.chr_day_type != 'F' THEN 0.5 ELSE 0 END) + (CASE WHEN cofu.int_status = 2 AND cofu.chr_leave_mode = 'F' THEN 1 WHEN cofu.int_status = 2 AND cofu.chr_leave_mode != 'F' THEN 0.5 ELSE 0 END)))) THEN (SELECT CEIL(DATE_PART('EPOCH',(tmshft.time_full_day/{5})-(SUM(plog.dat_end-plog.dat_start) + SUM(CASE WHEN ltrqst.int_status IN (1, 2) THEN ('01:00:00'::INTERVAL)*ltplcy.dbl_hours ELSE '00:00:00'::INTERVAL END) + ((tmshft.time_full_day/{5}) * SUM((CASE WHEN lev.int_status = 2 AND lev.chr_leave_mode = 'F' THEN 1 WHEN lev.int_status = 2 AND lev.chr_leave_mode != 'F' THEN 0.5 ELSE 0 END) + (CASE WHEN odr.int_status = 2 AND odr.chr_day_type = 'F' THEN 1 WHEN odr.int_status = 2 AND odr.chr_day_type != 'F' THEN 0.5 ELSE 0 END) + (CASE WHEN cofu.int_status = 2 AND cofu.chr_leave_mode = 'F' THEN 1 WHEN cofu.int_status = 2 AND cofu.chr_leave_mode != 'F' THEN 0.5 ELSE 0 END))))-(SELECT MAX(dur_to) FROM less_hour_policy))/DATE_PART('EPOCH',dur_to)) * dbl_days FROM less_hour_policy WHERE bln_auto=TRUE ORDER BY pk_bint_id DESC LIMIT 1) WHEN lshrplcy.dbl_days IS NOT NULL THEN lshrplcy.dbl_days ELSE 0 END) + SUM(CASE WHEN (au.is_active = FALSE AND ud.dat_resignation < sris.dat_series) OR (plog.dat_punch IS NULL AND ud.dat_doj > sris.dat_series) THEN 1 WHEN eshft.int_shift_type = 2 THEN 0 WHEN lev.int_status = 2 AND levtyp.vchr_name IN ('LOP') THEN (CASE WHEN lev.chr_leave_mode = 'F' THEN 1 ELSE 0.5 END) WHEN lshrdtl.pk_bint_id IS NULL AND wkoff.pk_bint_id IS NULL AND (ud.vchr_weekoff_day IS NULL OR TRIM(ud.vchr_weekoff_day) NOT ILIKE TRIM(TO_CHAR(sris.dat_series, 'Day'))) AND hldy.pk_bint_id IS NULL THEN (CASE WHEN ((lev.int_status IS NULL OR lev.int_status != 2) AND (cofu.int_status IS NULL OR cofu.int_status != 2) AND (odr.int_status IS NULL OR odr.int_status != 2) AND (plog.dat_punch IS NULL OR plog.vchr_direction = 'IN')) AND (plog.dat_punch IS NULL OR plog.vchr_direction = 'IN') AND lshrdtl.pk_bint_id IS NULL THEN 1 WHEN (((CASE WHEN lev.int_status = 2 AND lev.chr_leave_mode = 'F' THEN 1 WHEN lev.int_status = 2 AND lev.chr_leave_mode != 'F' THEN 0.5 ELSE 0 END) + (CASE WHEN odr.int_status = 2 AND odr.chr_day_type = 'F' THEN 1 WHEN odr.int_status = 2 AND odr.chr_day_type != 'F' THEN 0.5 ELSE 0 END) + (CASE WHEN cofu.int_status = 2 AND cofu.chr_leave_mode = 'F' THEN 1 WHEN cofu.int_status = 2 AND cofu.chr_leave_mode != 'F' THEN 0.5 ELSE 0 END)) >= 1) THEN 0 WHEN (((CASE WHEN lev.int_status = 2 AND lev.chr_leave_mode = 'F' THEN 1 WHEN lev.int_status = 2 AND lev.chr_leave_mode != 'F' THEN 0.5 ELSE 0 END) + (CASE WHEN odr.int_status = 2 AND odr.chr_day_type = 'F' THEN 1 WHEN odr.int_status = 2 AND odr.chr_day_type != 'F' THEN 0.5 ELSE 0 END) + (CASE WHEN cofu.int_status = 2 AND cofu.chr_leave_mode = 'F' THEN 1 WHEN cofu.int_status = 2 AND cofu.chr_leave_mode != 'F' THEN 0.5 ELSE 0 END)) BETWEEN 0.5 AND 1) AND (plog.dat_punch IS NULL OR plog.vchr_direction = 'IN') AND lshrdtl.pk_bint_id IS NULL THEN 0.5 ELSE 0 END) ELSE 0 END)) AS dbl_lop, SUM(CASE WHEN wkoff.pk_bint_id IS NULL AND (ud.vchr_weekoff_day IS NULL OR TRIM(ud.vchr_weekoff_day) NOT ILIKE TRIM(TO_CHAR(sris.dat_series, 'Day'))) AND hldy.pk_bint_id IS NULL THEN (CASE WHEN eshft.int_shift_type = 2 THEN 1 WHEN (plog.dat_end - plog.dat_start) + admnst.tim_punch_cool >= (CASE WHEN shft.time_full_day IS NOT NULL THEN shft.time_full_day::INTERVAL WHEN shft.time_shed_hrs IS NOT NULL THEN shft.time_shed_hrs::INTERVAL ELSE (shft.time_shift_to-shft.time_shift_from) END) THEN 1 WHEN (TRIM(TO_CHAR(sris.dat_series::DATE,'Day')) ILIKE 'saturday' AND TO_CHAR(sris.dat_series::DATE,'W')::INT = 2 AND brnch.vchr_name ILIKE 'head office') AND (plog.dat_end - plog.dat_start) + (CASE WHEN ltrqst.int_status IN (1, 2) THEN ('01:00:00'::INTERVAL)*ltplcy.dbl_hours ELSE '00:00:00'::INTERVAL END) + admnst.tim_punch_cool >= (CASE WHEN shft.time_half_day IS NOT NULL THEN shft.time_half_day::INTERVAL WHEN shft.time_full_day IS NOT NULL THEN (shft.time_full_day::INTERVAL)/2 WHEN shft.time_shed_hrs IS NOT NULL THEN (shft.time_shed_hrs::INTERVAL)/2 ELSE (shft.time_shift_to-shft.time_shift_from)/2 END) THEN 1 WHEN (plog.dat_end - plog.dat_start) + (CASE WHEN ltrqst.int_status IN (1, 2) THEN ('01:00:00'::INTERVAL)*ltplcy.dbl_hours ELSE '00:00:00'::INTERVAL END) + admnst.tim_punch_cool >= (CASE WHEN shft.time_half_day IS NOT NULL THEN shft.time_half_day::INTERVAL WHEN shft.time_full_day IS NOT NULL THEN (shft.time_full_day::INTERVAL)/2 WHEN shft.time_shed_hrs IS NOT NULL THEN (shft.time_shed_hrs::INTERVAL)/2 ELSE (shft.time_shift_to-shft.time_shift_from)/2 END) THEN 0.5 ELSE 0 END) ELSE 0 END) AS dbl_present, SUM(CASE WHEN (lev.int_status = 2 AND levtyp.vchr_name NOT IN ({0})) THEN (CASE WHEN lev.chr_leave_mode = 'F' THEN 1 ELSE 0.5 END) ELSE 0 END)::FLOAT AS dbl_leave, SUM(CASE WHEN odr.int_status = 2 THEN (CASE WHEN odr.chr_day_type = 'F' THEN 1 ELSE 0.5 END) ELSE 0 END)::FLOAT AS dbl_on_duty, SUM(CASE WHEN cofu.int_status = 2 THEN (CASE WHEN cofu.chr_leave_mode = 'F' THEN 1 ELSE 0.5 END) ELSE 0 END)::FLOAT AS dbl_combo, SUM(CASE WHEN (wkoff.pk_bint_id IS NOT NULL OR TRIM(ud.vchr_weekoff_day) ILIKE TRIM(TO_CHAR(sris.dat_series, 'Day'))) AND ud.dat_doj < sris.dat_series THEN 1 ELSE 0 END)::INT AS int_week_off, SUM(CASE WHEN hldy.pk_bint_id IS NOT NULL AND ud.dat_doj < sris.dat_series THEN 1 ELSE 0 END)::INT AS int_holiday, CASE WHEN ud.vchr_employee_code IN ('MYGE-1', 'MYGE-69') THEN 0 WHEN ptax.dbl_tax IS NOT NULL THEN dbl_tax / DATE_PART('MONTH', AGE(DATE_TRUNC('MONTH', ptax.dat_deduction+'1MONTH'::INTERVAL), DATE_TRUNC('MONTH', ptax.dat_start)))::INT ELSE 0 END AS dbl_ptax_amt"

        str_table_part = " FROM auth_user au JOIN user_details ud ON ud.user_ptr_id = au.id AND ud.dat_doj <= '{4}'::DATE JOIN category cat ON cat.pk_bint_id = ud.fk_category_id JOIN company cmpny ON cmpny.pk_bint_id = ud.fk_company_id JOIN document doc ON doc.fk_company_id = cmpny.pk_bint_id AND doc.vchr_module_name = 'EMPLOYEE CODE' JOIN salary_structure struct ON struct.pk_bint_id = ud.fk_salary_struct_id AND struct.bln_active = TRUE LEFT JOIN department dept ON dept.pk_bint_id = ud.fk_department_id LEFT JOIN job_position desig ON desig.pk_bint_id = ud.fk_desig_id LEFT JOIN branch brnch ON brnch.pk_bint_id = ud.fk_branch_id LEFT JOIN admin_settings admnst ON admnst.fk_company_id = ud.fk_company_id AND admnst.bln_enabled = TRUE AND admnst.vchr_code = 'COOL_TIME' LEFT JOIN salary_details slrydtl ON slrydtl.fk_employee_id = ud.user_ptr_id AND slrydtl.int_status = 1 LEFT JOIN salary_advance slryadv ON slryadv.fk_employee_id = ud.user_ptr_id AND slryadv.int_month = {1} AND slryadv.int_year = {2} AND slryadv.int_status = 2 LEFT JOIN variable_pay vrblpy ON vrblpy.fk_employee_id = ud.user_ptr_id AND (vrblpy.int_status = 1 OR (date_part('MONTH', vrblpy.dat_stoped)::INT > {1} AND date_part('YEAR', vrblpy.dat_stoped)::INT >= {2} AND vrblpy.int_status = 2)) LEFT JOIN fixed_allowance fxalwc ON fxalwc.fk_employee_id = ud.user_ptr_id AND (fxalwc.int_status = 1 OR (date_part('MONTH', fxalwc.dat_stoped)::INT > {1} AND date_part('YEAR', fxalwc.dat_stoped)::INT >= {2} AND fxalwc.int_status = 2)) LEFT JOIN (loan_request lonrqstm JOIN loan_details londtlsm ON lonrqstm.int_status = 1 AND londtlsm.fk_request_id = lonrqstm.pk_bint_id) ON lonrqstm.bln_mob_loan = TRUE AND lonrqstm.fk_employee_id = ud.user_ptr_id AND londtlsm.int_month = {1} AND londtlsm.int_year = {2} AND londtlsm.int_status IN (0, 1) LEFT JOIN (loan_request lonrqstw JOIN loan_details londtlsw ON lonrqstw.int_status = 1 AND londtlsw.fk_request_id = lonrqstw.pk_bint_id) ON (lonrqstw.bln_mob_loan IS NULL OR lonrqstw.bln_mob_loan = FALSE) AND lonrqstw.fk_employee_id = ud.user_ptr_id AND londtlsw.int_month = {1} AND londtlsw.int_year = {2} AND londtlsw.int_status IN (0, 1) RIGHT JOIN (SELECT (GENERATE_SERIES('{3}'::DATE, '{4}'::DATE, '1 day'::INTERVAL)::DATE) AS dat_series) AS sris ON TRUE LEFT JOIN punching_emp pemp ON pemp.fk_user_id = ud.user_ptr_id LEFT JOIN punch_log plog ON plog.fk_punchingemp_id = pemp.pk_bint_id AND plog.dat_punch = sris.dat_series LEFT JOIN employee_shift eshft ON eshft.fk_employee_id = ud.user_ptr_id AND eshft.bln_active = TRUE LEFT JOIN shift_exemption shftex ON shftex.int_status = 1 AND shftex.dat_start <= plog.dat_punch::DATE AND shftex.dat_end >= plog.dat_punch::DATE AND ((CASE WHEN shftex.int_type = 0 OR (shftex.int_type IN (1, 2, 3) AND (shftex.json_type_ids->>'int_type')::INT = 1) THEN ud.user_ptr_id IN (SELECT JSONB_ARRAY_ELEMENTS_TEXT((shftex.json_type_ids->>'lst_emp_id')::JSONB)::INT) WHEN shftex.int_type = 1 AND (shftex.json_type_ids->>'int_type')::INT = 0 THEN ud.fk_department_id IN (SELECT JSONB_ARRAY_ELEMENTS_TEXT((shftex.json_type_ids->>'lst_type_ids')::JSONB)::INT) WHEN shftex.int_type = 2 AND (shftex.json_type_ids->>'int_type')::INT = 0 THEN ud.fk_desig_id IN (SELECT JSONB_ARRAY_ELEMENTS_TEXT((shftex.json_type_ids->>'lst_type_ids')::JSONB)::INT) WHEN shftex.int_type = 3 AND (shftex.json_type_ids->>'int_type')::INT = 0 THEN ud.fk_branch_id IN (SELECT JSONB_ARRAY_ELEMENTS_TEXT((shftex.json_type_ids->>'lst_type_ids')::JSONB)::INT) END) AND (CASE WHEN (shftex.json_type_ids->>'lst_exclude_ids')::JSONB IS NOT NULL THEN ud.user_ptr_id NOT IN (SELECT JSONB_ARRAY_ELEMENTS_TEXT((shftex.json_type_ids->>'lst_exclude_ids')::JSONB)::INT) END)) LEFT JOIN shift_allocation salloc ON salloc.fk_employee_id = ud.user_ptr_id AND salloc.int_status IN (0, 2) AND salloc.dat_shift = sris.dat_series LEFT JOIN shift_schedule shft ON shft.pk_bint_id = (CASE WHEN plog.fk_shift_id IS NOT NULL THEN plog.fk_shift_id WHEN eshft.int_shift_type = 0 THEN (eshft.json_shift#>>'{7}')::INT WHEN eshft.int_shift_type = 1 THEN salloc.fk_shift_id END) LEFT JOIN shift_schedule tmshft ON tmshft.pk_bint_id = (CASE WHEN plog.fk_shift_id IS NOT NULL THEN plog.fk_shift_id WHEN eshft.int_shift_type = 0 THEN (eshft.json_shift#>>'{7}')::INT WHEN eshft.int_shift_type = 1 THEN salloc.fk_shift_id END) AND tmshft.bln_time_shift = TRUE LEFT JOIN (SELECT fk_user_id, dat_from, dat_to, fk_leave_type_id, (CASE SUM(CASE WHEN chr_leave_mode = 'F' THEN 1 WHEN chr_leave_mode in ('M', 'E') THEN 0.5 ELSE 0 END) WHEN 0.5 THEN 'H' WHEN 0 THEN NULL WHEN NULL THEN NULL ELSE 'F' END) AS chr_leave_mode, int_status FROM leave GROUP BY fk_user_id, dat_from, dat_to, fk_leave_type_id, int_status) lev ON lev.fk_user_id = ud.user_ptr_id AND lev.dat_from <= sris.dat_series and lev.dat_to >= sris.dat_series AND lev.int_status NOT IN (3, 4) LEFT JOIN leave_type levtyp ON levtyp.pk_bint_id = lev.fk_leave_type_id LEFT JOIN emp_leave_data emplv ON emplv.fk_employee_id = ud.user_ptr_id AND emplv.int_status = 1 AND emplv.int_month = {1} AND emplv.int_year = {2} LEFT JOIN less_hour_leave lshrlv ON lshrlv.fk_employee_id = ud.user_ptr_id AND lshrlv.dat_leave = sris.dat_series LEFT JOIN less_hour_deduction lshrde ON lshrde.fk_employee_id = ud.user_ptr_id AND lshrde.int_month = {1} AND lshrde.int_year = {2} LEFT JOIN less_hour_details lshrdtl ON lshrdtl.fk_master_id = lshrde.pk_bint_id AND lshrdtl.dat_less_hour = sris.dat_series LEFT JOIN less_hour_policy lshrplcy ON lshrplcy.dur_from <= (CASE WHEN lshrde.dur_aftr_deduct IS NOT NULL THEN lshrde.dur_aftr_deduct ELSE lshrde.dur_time END) AND lshrplcy.dur_to >= (CASE WHEN lshrde.dur_aftr_deduct IS NOT NULL THEN lshrde.dur_aftr_deduct ELSE lshrde.dur_time END) AND lshrplcy.bln_auto = FALSE LEFT JOIN less_hour_rules lsrls ON lsrls.bln_active = TRUE AND CASE WHEN lsrls.fk_department_id IS NOT NULL AND lsrls.fk_desig_id IS NOT NULL THEN lsrls.fk_department_id = ud.fk_department_id AND lsrls.fk_desig_id = ud.fk_desig_id WHEN lsrls.fk_department_id IS NOT NULL THEN lsrls.fk_department_id = ud.fk_department_id WHEN lsrls.fk_desig_id IS NOT NULL THEN lsrls.fk_desig_id = ud.fk_desig_id ELSE FALSE END LEFT JOIN (SELECT fk_user_id, dat_leave, (CASE SUM(CASE WHEN chr_leave_mode = 'F' THEN 1 WHEN chr_leave_mode in ('M', 'E') THEN 0.5 ELSE 0 END) WHEN 0.5 THEN 'H' WHEN 0 THEN NULL WHEN NULL THEN NULL ELSE 'F' END) AS chr_leave_mode, int_status FROM combo_off_users GROUP BY fk_user_id, dat_leave, int_status) cofu ON cofu.fk_user_id = ud.user_ptr_id AND cofu.dat_leave = sris.dat_series AND cofu.int_status IN (1, 2) LEFT JOIN (SELECT fk_requested_id, dat_request, (CASE SUM(CASE WHEN chr_day_type = 'F' THEN 1 WHEN chr_day_type in ('M', 'E') THEN 0.5 ELSE 0 END) WHEN 0.5 THEN 'H' WHEN 0 THEN NULL WHEN NULL THEN NULL ELSE 'F' END) AS chr_day_type, int_status FROM on_duty_request GROUP BY fk_requested_id, dat_request, int_status) odr ON odr.fk_requested_id=ud.user_ptr_id AND odr.dat_request=sris.dat_series AND odr.int_status != -1 LEFT JOIN duty_roster wkoff ON (ud.int_weekoff_type = 1 OR shftex.pk_bint_id IS NOT NULL) AND wkoff.fk_employee_id = ud.user_ptr_id AND wkoff.bln_active=TRUE AND wkoff.json_dates ? sris.dat_series::TEXT LEFT JOIN weekoff_leave wklv ON wklv.fk_employee_id = ud.user_ptr_id AND wklv.dat_from <= sris.dat_series AND wklv.dat_to >= sris.dat_series AND wklv.int_status IN (1, 2) LEFT JOIN holiday hldy ON hldy.dat_holiday = sris.dat_series AND hldy.bln_active = TRUE LEFT JOIN (late_hours_request ltrqst JOIN late_hours_policy ltplcy ON ltplcy.pk_bint_id = ltrqst.fk_late_hours_policy_id) ON ltrqst.dat_requested::DATE = sris.dat_series::DATE AND ltrqst.fk_employee_id = ud.user_ptr_id AND ltrqst.int_status != -1 LEFT JOIN (SELECT ptax.dbl_from_amt, ptax.dbl_to_amt, ptax.dbl_tax, CONCAT(CASE WHEN EXTRACT(YEAR FROM NOW()) = {2} THEN {2} WHEN ptprd.int_month_from <= ptprd.int_month_to THEN {2} ELSE {2}-1 END, '-', ptprd.int_month_from::TEXT, '-01')::DATE dat_start, CONCAT(CASE WHEN (ptprd.int_month_from <= ptprd.int_month_to OR EXTRACT(YEAR FROM NOW()) != {2}) THEN {2} ELSE {2}+1 END, '-', ptprd.int_month_to::TEXT, '-01')::DATE dat_end, CONCAT(CASE WHEN (ptprd.int_month_from <= ptprd.int_deduct_month OR EXTRACT(YEAR FROM NOW()) != {2}) THEN {2} ELSE {2}+1 END, '-', ptprd.int_deduct_month::TEXT, '-01')::DATE dat_deduction, ptax.bln_active FROM professional_tax ptax JOIN pt_period ptprd ON ptprd.pk_bint_id = ptax.fk_period_id) ptax ON ptax.dat_start <= CONCAT('{2}', '-', '{1}', '-01')::DATE AND ptax.dat_deduction >= CONCAT('{2}', '-', '{1}', '-01')::DATE AND (CASE WHEN ptax.dbl_from_amt IS NULL THEN ptax.dbl_to_amt >= (ud.dbl_gross * DATE_PART('MONTH', AGE(DATE_TRUNC('MONTH', ptax.dat_end+'1MONTH'::INTERVAL), DATE_TRUNC('MONTH', CASE WHEN ptax.dat_start <= CONCAT(EXTRACT(YEAR FROM ud.dat_doj), '-', EXTRACT(MONTH FROM ud.dat_doj), '-01')::DATE THEN CONCAT(EXTRACT(YEAR FROM ud.dat_doj), '-', EXTRACT(MONTH FROM ud.dat_doj), '-01')::DATE ELSE ptax.dat_start END)))::INT) WHEN ptax.dbl_to_amt IS NULL THEN ptax.dbl_from_amt <= (ud.dbl_gross * DATE_PART('MONTH', AGE(DATE_TRUNC('MONTH', ptax.dat_end+'1MONTH'::INTERVAL), DATE_TRUNC('MONTH', CASE WHEN ptax.dat_start <= CONCAT(EXTRACT(YEAR FROM ud.dat_doj), '-', EXTRACT(MONTH FROM ud.dat_doj), '-01')::DATE THEN CONCAT(EXTRACT(YEAR FROM ud.dat_doj), '-', EXTRACT(MONTH FROM ud.dat_doj), '-01')::DATE ELSE ptax.dat_start END)))::INT) ELSE ptax.dbl_from_amt <= (ud.dbl_gross * DATE_PART('MONTH', AGE(DATE_TRUNC('MONTH', ptax.dat_end+'1MONTH'::INTERVAL), DATE_TRUNC('MONTH', CASE WHEN ptax.dat_start <= CONCAT(EXTRACT(YEAR FROM ud.dat_doj), '-', EXTRACT(MONTH FROM ud.dat_doj), '-01')::DATE THEN CONCAT(EXTRACT(YEAR FROM ud.dat_doj), '-', EXTRACT(MONTH FROM ud.dat_doj), '-01')::DATE ELSE ptax.dat_start END)))::INT) AND ptax.dbl_to_amt >= (ud.dbl_gross * DATE_PART('MONTH', AGE(DATE_TRUNC('MONTH', ptax.dat_end+'1MONTH'::INTERVAL), DATE_TRUNC('MONTH', CASE WHEN ptax.dat_start <= CONCAT(EXTRACT(YEAR FROM ud.dat_doj), '-', EXTRACT(MONTH FROM ud.dat_doj), '-01')::DATE THEN CONCAT(EXTRACT(YEAR FROM ud.dat_doj), '-', EXTRACT(MONTH FROM ud.dat_doj), '-01')::DATE ELSE ptax.dat_start END)))::INT) END)"

        str_conditional_part = " WHERE (au.is_active = TRUE OR (au.is_active = FALSE AND ud.dat_resignation>='{3}'::DATE)){6}"

        str_grouping_part = " GROUP BY ud.user_ptr_id, ud.vchr_employee_code, au.first_name, ud.vchr_middle_name, au.last_name, dept.vchr_name, desig.vchr_name, brnch.vchr_name, ud.dat_doj, cat.vchr_name, struct.pk_bint_id, struct.vchr_name, struct.dbl_bp_da, struct.dbl_bp_da_per, struct.dbl_da, struct.json_rules, slrydtl.pk_bint_id, slrydtl.dbl_bp, slrydtl.dbl_da, slrydtl.dbl_hra, slrydtl.dbl_cca, slrydtl.dbl_sa, slrydtl.dbl_wa, ud.dbl_gross, slrydtl.json_deduction, slrydtl.json_allowance, vrblpy.dbl_amount, fxalwc.dbl_amount, slryadv.dbl_amount, londtlsm.pk_bint_id, londtlsm.dbl_amount, lonrqstm.bln_mob_loan, londtlsw.pk_bint_id, londtlsw.dbl_amount, lonrqstw.bln_mob_loan, ud.json_allowance, lshrplcy.dbl_days, lshrde.dur_time, lsrls.dur_min_hours, lshrde.dur_aftr_deduct, emplv.dbl_number, ptax.dat_deduction, ptax.dat_start, ptax.dbl_tax, eshft.int_shift_type, tmshft.time_full_day, cmpny.vchr_code, cat.vchr_code, doc.chr_num_separate"

        str_ordering_part = " ORDER BY TRIM(TRIM(ud.vchr_employee_code, CONCAT(cmpny.vchr_code, cat.vchr_code)), CASE WHEN doc.chr_num_separate IS NOT NULL THEN doc.chr_num_separate ELSE '' END)::INT"

        str_query = str_select_part + str_table_part + str_conditional_part + str_grouping_part + str_ordering_part
        lst_leave_type = ['LOP']
        # 0.str(lst_leave_type)[1:-1], str_month, str_year, 3. str_date_from, 4. str_date_to, 5. int_max_days, 6. string where conditions

        str_query = str_query.format(str(lst_leave_type)[1:-1], str(int_month), str(int_year), str_start_date, str_end_date, int_max_days, str_filter, '{lstShift,0}')
        rst_data = conn.execute(str_query).fetchall()
        conn.close()
        dct_pro_tax = ProfessionalTaxCalculation(int_month, int_year)
        dct_struct = {data['vchr_type']:{'ER':data['dbl_empr_share'], 'EE':data['dbl_empy_share']} for data in PfandEsiStructure.objects.filter(Q(int_end_month__isnull=True, int_end_year__isnull=True) | Q(int_end_month__gte=int_month, int_end_year__gte=int_year), int_start_month__lte=int_month, int_start_year__lte=int_year).values('vchr_type', 'dbl_empr_share', 'dbl_empy_share')}
        lst_data = []
        for ins_data in rst_data:
            ins_data = dict(ins_data)
            dct_copy = copy.deepcopy(ins_data)
            dct_data = {}
            # --- Emp Details ---
            dct_data['int_emp_id'] = ins_data['int_emp_id']
            dct_data['str_employee_code'] = ins_data['vchr_employee_code']
            dct_data['str_emp_name'] = ins_data['str_emp_name']
            dct_data['str_designation'] = ins_data['str_designation']
            dct_data['str_department'] = ins_data['str_department']
            dct_data['str_branch'] = ins_data['str_branch']
            dct_data['dat_joined'] = ins_data['dat_joined']
            dct_data['str_category_name'] = ins_data['str_category_name']
            dct_data['str_salary_slab'] = ins_data['json_structure']['str_struct_name']
            dct_data['int_mobile_loan_id'] = ins_data['json_salary_details']['json_loan']['json_mobile_loan']['int_loan_id']
            dct_data['int_work_loan_id'] = ins_data['json_salary_details']['json_loan']['json_work_loan']['int_loan_id']
            # --- Actual Salary ---
            dct_data['int_slry_dtls_id'] = ins_data['json_salary_details']['int_details_id']
            dct_data['dbl_bp'] = ins_data['json_salary_details']['dbl_bp']
            dct_data['dbl_da'] = ins_data['json_salary_details']['dbl_da']
            dct_data['dbl_hra'] = ins_data['json_salary_details']['dbl_hra']
            dct_data['dbl_cca'] = ins_data['json_salary_details']['dbl_cca']
            dct_data['dbl_wa'] = ins_data['json_salary_details']['dbl_wa']
            dct_data['dbl_sa'] = ins_data['json_salary_details']['dbl_sa']
            dct_data['dbl_gross'] = ins_data['json_salary_details']['dbl_gross']
            # dct_data['dbl_pt_amt'] = ins_data['dbl_ptax_amt']
            dct_data['dbl_pt_amt'] = dct_pro_tax.get(ins_data['int_emp_id'], 0)
            if dct_data['dbl_gross'] - dct_data['dbl_hra'] < 15000 and ins_data['json_salary_details'].get('json_rules',{}).get('bln_pf'):
                dct_data['dbl_pf_salary'] = dct_data['dbl_gross']-dct_data['dbl_hra']
            elif ins_data['json_salary_details'].get('json_rules',{}).get('bln_pf'):
                dct_data['dbl_pf_salary'] = 15000
            if ins_data['json_salary_details'].get('json_rules',{}).get('bln_pf'):
                if dct_struct.get('PF', {}).get('EE'):
                    ins_data['json_salary_details']['json_deduction']['PF'] = round(dct_data['dbl_pf_salary']*(dct_struct.get('PF', {}).get('EE')/100), 0)
                if dct_struct.get('PF', {}).get('ER'):
                    ins_data['json_salary_details']['json_allowance']['PF'] = round(dct_data['dbl_pf_salary']*(dct_struct.get('PF', {}).get('ER')/100), 0)
            else:
                dct_data['dbl_pf_salary'] = 0
            if dct_data['dbl_gross'] - dct_data['dbl_wa'] < 21000 and ins_data['json_salary_details'].get('json_rules',{}).get('bln_esi'):
                dct_data['dbl_esi_salary'] = dct_data['dbl_gross'] - dct_data['dbl_wa']
            else:
                dct_data['dbl_esi_salary'] = 0
            if ins_data['json_salary_details'].get('json_rules',{}).get('bln_esi'):
                if dct_struct.get('ESI', {}).get('EE'):
                    ins_data['json_salary_details']['json_deduction']['ESI'] = math.ceil(dct_data['dbl_esi_salary']*(dct_struct.get('ESI', {}).get('EE')/100))
                if dct_struct.get('ESI', {}).get('ER'):
                    ins_data['json_salary_details']['json_allowance']['ESI'] = math.ceil(dct_data['dbl_esi_salary']*(dct_struct.get('ESI', {}).get('ER')/100))
            dct_data['json_deductions'] = ins_data['json_salary_details']['json_deduction']
            dct_data['json_allowance'] = ins_data['json_salary_details']['json_allowance']
            dct_data['dbl_tot_allowances'] = ins_data['json_salary_details']['json_allowance'].get('PF',0) + ins_data['json_salary_details']['json_allowance'].get('ESI',0) + ins_data['json_salary_details']['json_allowance'].get('WWF',0) + ins_data['json_salary_details']['json_allowance'].get('Gratuity',0)
            dct_data['dbl_tot_deductions'] = ins_data['json_salary_details']['json_deduction'].get('PF', 0) + ins_data['json_salary_details']['json_deduction'].get('ESI', 0) + ins_data['json_salary_details']['json_deduction'].get('WWF', 0) + ins_data['json_salary_details']['json_loan']['json_mobile_loan']['dbl_loan_amount'] + ins_data['json_salary_details']['json_loan']['json_work_loan']['dbl_loan_amount'] + ins_data['json_salary_details']['dbl_adv_amount'] + ins_data['json_salary_details']['json_deduction'].get('Charity', 0) + ins_data['json_salary_details']['json_deduction'].get('TDS', 0) + dct_pro_tax.get(ins_data['int_emp_id'], 0)
            dct_data['dbl_variable_pay'] = ins_data['json_salary_details']['dbl_variable_pay'] if ins_data['json_salary_details']['dbl_variable_pay'] else 0
            dct_data['dbl_fixed_allowance'] = ins_data['json_salary_details']['dbl_fixed_allowance'] if ins_data['json_salary_details']['dbl_fixed_allowance'] else 0
            dct_data['json_allowance']['dbl_variable_pay'] = ins_data['json_salary_details']['dbl_variable_pay'] if ins_data['json_salary_details']['dbl_variable_pay'] else 0
            dct_data['json_allowance']['dbl_fixed_allowance'] = ins_data['json_salary_details']['dbl_fixed_allowance'] if ins_data['json_salary_details']['dbl_fixed_allowance'] else 0
            dct_data['dbl_net_salary'] = round(dct_data['dbl_gross'] + dct_data['dbl_variable_pay'] + dct_data['dbl_fixed_allowance'] - dct_data['dbl_tot_deductions'], 0)
            dct_data['dbl_monthly_ctc'] = round(dct_data['dbl_gross'] + dct_data['dbl_variable_pay'] + dct_data['dbl_fixed_allowance'] + dct_data['dbl_tot_allowances'], 0)
            # --- Attendance ---
            dct_data['json_attendance'] = {}
            for dct_attendace in ins_data['json_attendance']:
                dct_data['json_attendance'].update(dct_attendace)
            dct_data['dur_worked_hour'] = ins_data['dur_worked_hour']
            dct_data['dur_less_hours'] = ins_data['less_hours']
            dct_data['dbl_less_hour_days'] = ins_data['less_hour_days']
            dct_data['dbl_absent'] = float(ins_data['dbl_absent'])
            dct_data['dbl_lop_leave'] = float(ins_data['leave_lop'])
            dct_data['dbl_tot_lop'] = ins_data['dbl_lop']
            dct_data['dbl_present'] = float(ins_data['dbl_present'])
            dct_data['dbl_combo'] = ins_data['dbl_combo']
            dct_data['dbl_on_duty'] = ins_data['dbl_on_duty']
            dct_data['dbl_leave'] = ins_data['dbl_leave']
            dct_data['int_week_off'] = ins_data['int_week_off']
            dct_data['int_holiday'] = ins_data['int_holiday']
            # --- Calculated ---
            dct_data['BP_DA'] = round((dct_copy['json_salary_details']['dbl_bp'] if dct_copy['json_salary_details']['dbl_bp'] else 0) * ((int_max_days - dct_copy['dbl_lop'])/int_max_days), 0)
            dct_data['BP'] = round((dct_copy['json_salary_details']['dbl_bp'] if dct_copy['json_salary_details']['dbl_bp'] else 0) * ((int_max_days - dct_copy['dbl_lop'])/int_max_days), 0)
            dct_data['DA'] = round((dct_copy['json_salary_details']['dbl_da'] if dct_copy['json_salary_details']['dbl_da'] else 0) * ((int_max_days - dct_copy['dbl_lop'])/int_max_days), 0)
            dct_data['HRA'] = round((dct_copy['json_salary_details']['dbl_hra'] if dct_copy['json_salary_details']['dbl_hra'] else 0) * ((int_max_days - dct_copy['dbl_lop'])/int_max_days), 0)
            dct_data['CCA'] = round((dct_copy['json_salary_details']['dbl_cca'] if dct_copy['json_salary_details']['dbl_cca'] else 0) * ((int_max_days - dct_copy['dbl_lop'])/int_max_days), 0)
            dct_data['WA'] = round((dct_copy['json_salary_details']['dbl_wa'] if dct_copy['json_salary_details']['dbl_wa'] else 0) * ((int_max_days - dct_copy['dbl_lop'])/int_max_days), 0)
            dct_data['SA'] = round((dct_copy['json_salary_details']['dbl_sa'] if dct_copy['json_salary_details']['dbl_sa'] else 0) * ((int_max_days - dct_copy['dbl_lop'])/int_max_days), 0)
            dct_data['GROSS'] = round(dct_copy['json_salary_details']['dbl_gross'] * ((int_max_days - dct_copy['dbl_lop'])/int_max_days), 0)
            dct_data['Deductions'] = dct_copy['json_salary_details']['json_deduction'] if dct_copy['json_salary_details']['json_deduction'] else {}
            if dct_data['GROSS'] - dct_data['HRA'] < 15000 and dct_copy['json_salary_details'].get('json_rules',{}).get('bln_pf'):
                dct_data['Deductions']['PF'] = round((dct_data['GROSS'] - dct_data['HRA']) * ((dct_struct.get('PF', {}).get('EE') if dct_struct.get('PF', {}).get('EE') else dct_copy['json_structure']['json_rules']['Deductions']['PF'])/100), 0)
                dct_data['PF_SALARY'] = dct_data['GROSS'] - dct_data['HRA']
            elif dct_copy['json_salary_details'].get('json_rules',{}).get('bln_pf'):
                dct_data['Deductions']['PF'] = round(15000 * ((dct_struct.get('PF', {}).get('EE') if dct_struct.get('PF', {}).get('EE') else dct_copy['json_structure']['json_rules']['Deductions']['PF'])/100), 0)
                dct_data['PF_SALARY'] = 15000
            else:
                dct_data['Deductions']['PF'] = 0
                dct_data['PF_SALARY'] = 0
            if dct_data['GROSS'] - dct_data['WA'] < 21000 and dct_copy['json_salary_details'].get('json_rules',{}).get('bln_esi'):
                dct_data['Deductions']['ESI'] = math.ceil((dct_data['GROSS'] - dct_data['WA']) * ((dct_struct.get('ESI', {}).get('EE') if dct_struct.get('ESI', {}).get('EE') else dct_copy['json_structure']['json_rules']['Deductions']['ESI'])/100))
                dct_data['ESI_SALARY'] = dct_data['GROSS'] - dct_data['WA']
            else:
                dct_data['Deductions']['ESI'] = 0
                dct_data['ESI_SALARY'] = 0
            dct_data['Deductions']['SalaryAdvance'] = dct_copy['json_salary_details']['dbl_adv_amount'] if dct_copy['json_salary_details']['dbl_adv_amount'] else 0
            dct_data['Deductions']['ProTax'] = dct_pro_tax.get(ins_data['int_emp_id'], 0) if (int_max_days - dct_copy['dbl_lop'])>0 else 0
            if dct_copy['json_salary_details']['json_loan']['json_mobile_loan']:
                dct_data['Deductions']['MobileLoan'] = dct_copy['json_salary_details']['json_loan']['json_mobile_loan']['dbl_loan_amount'] if dct_copy['json_salary_details']['json_loan']['json_mobile_loan']['dbl_loan_amount'] else 0
            if dct_copy['json_salary_details']['json_loan']['json_work_loan']:
                dct_data['Deductions']['WorkLoan'] = dct_copy['json_salary_details']['json_loan']['json_work_loan']['dbl_loan_amount'] if dct_copy['json_salary_details']['json_loan']['json_work_loan']['dbl_loan_amount'] else 0
            dct_data['Tot_Deduction'] = dct_data.get('Deductions',{}).get('PF', 0) + dct_data.get('Deductions', {}).get('ESI', 0) + dct_data.get('Deductions', {}).get('WWF', 0) + dct_data.get('Deductions', {}).get('SalaryAdvance', 0) + dct_data.get('Deductions', {}).get('MobileLoan', 0) + dct_data.get('Deductions', {}).get('WorkLoan', 0) + dct_data.get('Deductions', {}).get('Charity', 0) + dct_data.get('Deductions', {}).get('TDS', 0) + (dct_pro_tax.get(ins_data['int_emp_id'], 0) if (int_max_days - dct_copy['dbl_lop'])>0 else 0)

            dct_data['Allowances'] = dct_copy['json_salary_details']['json_allowance'] if dct_copy['json_salary_details']['json_allowance'] else {}
            if dct_data['GROSS'] - dct_data['HRA'] < 15000 and dct_copy['json_salary_details'].get('json_rules',{}).get('bln_pf'):
                dct_data['Allowances']['PF'] = round((dct_data['GROSS'] - dct_data['HRA']) * ((dct_struct.get('PF', {}).get('ER') if dct_struct.get('PF', {}).get('ER') else dct_copy['json_structure']['json_rules']['Allowances']['PF'])/100), 0)
            elif dct_copy['json_salary_details'].get('json_rules',{}).get('bln_pf'):
                dct_data['Allowances']['PF'] = round(15000 * ((dct_struct.get('PF', {}).get('ER') if dct_struct.get('PF', {}).get('ER') else dct_copy['json_structure']['json_rules']['Allowances']['PF'])/100), 0)
            else:
                dct_data['Allowances']['PF'] = 0
            if dct_data['GROSS'] - dct_data['WA'] < 21000 and dct_copy['json_salary_details'].get('json_rules',{}).get('bln_esi'):
                dct_data['Allowances']['ESI'] = round((dct_data['GROSS'] - dct_data['WA']) * ((dct_struct.get('ESI', {}).get('ER') if dct_struct.get('ESI', {}).get('ER') else dct_copy['json_structure']['json_rules']['Allowances']['ESI'])/100), 0)
            else:
                dct_data['Allowances']['ESI'] = 0
            dct_data['Tot_Allowance'] = dct_data.get('Allowances', {}).get('PF', 0) + dct_data.get('Allowances', {}).get('ESI', 0) + dct_data.get('Allowances', {}).get('WWF', 0) + dct_data.get('Allowances', {}).get('Gratuity', 0)

            dct_data['VariablePay'] = round((dct_copy['json_salary_details']['dbl_variable_pay']/int_max_days) * (int_max_days - dct_copy['dbl_lop']), 0) if dct_copy['json_salary_details']['dbl_variable_pay'] else 0
            dct_data['FixedAllowance'] = round(dct_copy['json_salary_details']['dbl_fixed_allowance']) if dct_copy['json_salary_details']['dbl_fixed_allowance'] else 0
            dct_data['Allowances']['VariablePay'] = round((dct_copy['json_salary_details']['dbl_variable_pay']/int_max_days) * (int_max_days - dct_copy['dbl_lop']), 0) if dct_copy['json_salary_details']['dbl_variable_pay'] else 0
            dct_data['Allowances']['FixedAllowance'] = round(dct_copy['json_salary_details']['dbl_fixed_allowance']) if dct_copy['json_salary_details']['dbl_fixed_allowance'] else 0
            dct_data['Net_Salary'] = round((dct_data['GROSS'] + dct_data['VariablePay'] + dct_data['FixedAllowance']) - dct_data['Tot_Deduction'], 0)
            dct_data['Monthly_CTC'] = round(dct_data['GROSS'] + dct_data['VariablePay'] + dct_data['FixedAllowance'] + dct_data['Tot_Allowance'], 0)
            lst_data.append(dct_data)
        return lst_data
    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
        return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


class SaleryProcessApproval(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            int_month = int(request.data.get('intMonthYear').split('-')[0])
            int_year = int(request.data.get('intMonthYear').split('-')[1])
            rst_salary_processed = SalaryProcessed.objects.filter(int_month = int_month,int_year = int_year,int_status = 0).extra(select={'lop':"json_attendance->>'dbl_tot_lop'"}).annotate(strFullName=Concat('fk_employee_id__first_name', Value(' '), Case(When(fk_employee_id__vchr_middle_name = None, then=F('fk_employee_id__last_name')), default=Concat('fk_employee_id__vchr_middle_name', Value(' '), 'fk_employee_id__last_name'), output_field = CharField()), output_field =  CharField())).values('fk_employee_id__vchr_employee_code','strFullName','lop','dbl_gross','dbl_net_salary','pk_bint_id')

            return Response({'status':1,'data':rst_salary_processed})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})

    def put(self,request):
        try:
            lst_approved = request.data.get('lst_approved')
            lst_deleted = request.data.get('lst_deleted')
            SalaryProcessed.objects.filter(pk_bint_id__in = lst_approved).update(int_status = 1,dat_approval = datetime.now(),fk_approved_id = request.user.id)
            SalaryProcessed.objects.filter(pk_bint_id__in = lst_deleted).update(int_status = -1,dat_approval = datetime.now(),fk_approved_id = request.user.id)
            return Response({"status":1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


class HoldSalary(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            int_month = int(request.data.get('intMonthYear').split('-')[0])
            int_year = int(request.data.get('intMonthYear').split('-')[1])
            int_emp_id = int(request.data.get('intEmpId'))
            rst_salary_processed= SalaryProcessed.objects.filter(int_month=int_month,int_year=int_year,fk_employee_id=int_emp_id,int_status=1,bln_hold=False).values('dbl_net_salary')
            if rst_salary_processed:
                return Response({"status":1,'dbl_net_salary':rst_salary_processed[0]['dbl_net_salary']})
            else:
                return Response({"status":0})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})
    def put(self,request):
        try:
            int_month = int(request.data.get('intMonthYear').split('-')[0])
            int_year = int(request.data.get('intMonthYear').split('-')[1])
            int_emp_id = int(request.data.get('intEmpId'))
            vchr_remarks = request.data.get('strRemarks')
            rst_salary_processed = SalaryProcessed.objects.filter(int_month=int_month,int_year=int_year,fk_employee_id=int_emp_id,int_status=1,bln_hold=False).update(int_status=2,vchr_remarks=vchr_remarks,dat_hold=datetime.now(),fk_hold_id=request.user.id,bln_hold=True)
            if rst_salary_processed:
                return Response({"status":1})
            else:
                return Response({"status":0})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


class ReleaseHoldSalary(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            int_month = int(request.GET.get('intMonthYear').split('-')[0])
            int_year = int(request.GET.get('intMonthYear').split('-')[1])
            lst_salary_processed= list(SalaryProcessed.objects.filter(int_month=int_month,int_year=int_year,bln_hold=True).annotate(fullname=Concat('fk_employee__first_name', Value(' '),'fk_employee__vchr_middle_name', Value(' ') ,'fk_employee__last_name')).values('pk_bint_id','fk_employee__vchr_employee_code','fullname','fk_employee_id','fk_employee__fk_branch__vchr_name','fk_employee__fk_desig__vchr_name','dbl_net_salary','vchr_remarks'))
            if lst_salary_processed:
                return Response({"status":1,'data':lst_salary_processed})
            else:
                return Response({"status":0})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})
    def post(self,request):
        try:
            int_id = int(request.data.get('intSalaryProcessId'))
            dct_salary_processed = SalaryProcessed.objects.filter(pk_bint_id=int_id).values().first()
            if dct_salary_processed:
                SalaryProcessed.objects.filter(pk_bint_id=int_id).update(int_status=-1)
                ins_salary_processed = SalaryProcessed(
                                    fk_employee_id = dct_salary_processed['fk_employee_id'],
                                    fk_details_id = dct_salary_processed['fk_details_id'],
                                    int_month = dct_salary_processed['int_month'],
                                    int_year = dct_salary_processed['int_year'],
                                    json_attendance =  dct_salary_processed['json_attendance'],
                                    dbl_bp = dct_salary_processed['dbl_bp'],
                                    dbl_da = dct_salary_processed['dbl_da'],
                                    dbl_hra = dct_salary_processed['dbl_hra'],
                                    dbl_cca = dct_salary_processed['dbl_cca'],
                                    dbl_wa = dct_salary_processed['dbl_wa'],
                                    dbl_sa = dct_salary_processed['dbl_sa'],
                                    dbl_gross = dct_salary_processed['dbl_gross'],
                                    json_allowances = dct_salary_processed['json_allowances'],
                                    json_deductions = dct_salary_processed['json_deductions'],
                                    dbl_net_salary = dct_salary_processed['dbl_net_salary'],
                                    dbl_monthly_ctc = dct_salary_processed['dbl_monthly_ctc'],
                                    fk_created_id = dct_salary_processed['fk_created_id'],
                                    dat_created = dct_salary_processed['dat_created'],
                                    fk_approved_id = request.user.id,
                                    dat_approval = datetime.now(),
                                    int_status = dct_salary_processed['int_status'],
                                    bln_hold = False)
                ins_salary_processed.save()
                return Response({"status":1})
            else:
                return Response({"status":0})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})




class ProfessionalTaxReport(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            ins_pt_period = PtPeriod.objects.filter(pk_bint_id = request.data.get('intHalfPeriod', 1)).values().first()
            int_year = date.today().year if ins_pt_period['int_month_from'] < ins_pt_period['int_month_to'] else date.today().year - 1
            int_month = ins_pt_period['int_month_to']
            dur_calendar = calendar.monthrange(int_year, int_month)
            str_start_date = str(int_year)+'-'+str(ins_pt_period['int_month_from'])+'-1'
            str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(dur_calendar[1])
            str_deduct_date = str(int_year)+'-'+str(ins_pt_period['int_deduct_month'])+'-'+str(dur_calendar[1])
            if not request.user.is_superuser:
                ins_admin = AdminSettings.objects.filter(vchr_code='PAYROLL_PERIOD',bln_enabled=True,fk_company_id=request.user.userdetails.fk_company_id).values('vchr_value', 'int_value').first()
                if ins_admin and ins_admin['int_value'] != 0:
                    str_start_date = datetime.strftime(datetime.strptime(str(int_year)+'-'+str(ins_pt_period['int_month_from'])+'-'+ins_admin['vchr_value'][0],'%Y-%m-%d')+timedelta(days=int(ins_admin['vchr_value'][0])*ins_admin['int_value']),'%Y-%m-')+ins_admin['vchr_value'][0]
                    str_end_date = str(date.today().year)+'-'+str(ins_pt_period['int_month_to'])+'-'+str(int(ins_admin['vchr_value'][0])-1)
                    str_deduct_date = str(date.today().year)+'-'+str(ins_pt_period['int_deduct_month'])+'-'+str(int(ins_admin['vchr_value'][0])-1)
            dat_start = datetime.strptime(str_start_date, '%Y-%m-%d')
            dat_end = datetime.strptime(str_end_date, '%Y-%m-%d')
            dat_deduct =  datetime.strptime(str_deduct_date, '%Y-%m-%d')
            ins_pro_tax = ProfessionalTax.objects.filter(fk_period_id = ins_pt_period['pk_bint_id'], bln_active = True).annotate(int_month_from = F('fk_period__int_month_from'), int_month_to = F('fk_period__int_month_to')).values('int_month_from', 'int_month_to', 'dbl_from_amt', 'dbl_to_amt', 'dbl_tax')
            # ins_salary = SalaryDetails.objects.values('fk_employee_id', 'dbl_gross').annotate(
            #                                         dat_created = Min('dat_created'),
            #                                         full_name = Concat('fk_employee__first_name', Value(' '),
            #                                         Case(When(fk_employee__vchr_middle_name = None, then = F('fk_employee__last_name')),
            #                                         default = Concat('fk_employee__vchr_middle_name', Value(' '), 'fk_employee__last_name'),
            #                                         output_field = CharField()), output_field = CharField()),
            #                                         int_emp_id = Cast(Substr('fk_employee__vchr_employee_code',6), IntegerField()),
            #                                         str_emp_code = F('fk_employee__vchr_employee_code'),
            #                                         str_department = F('fk_employee__fk_department__vchr_name'),
            #                                         str_designation = F('fk_employee__fk_desig__vchr_name')).filter(
            #                                         dat_created__gte = str_start_date, dat_created__lte = str_end_date).order_by('int_emp_id','dat_created')
            ins_salary =  SalaryDetails.objects.filter(Q(fk_employee__is_active = True)|Q(fk_employee__is_active = False,
                                                    fk_employee__dat_resignation__gte = dat_start),int_status = 1).annotate(
                                                    int_emp_code = Cast(Substr('fk_employee__vchr_employee_code', 6), IntegerField()),
                                                    str_emp_code = F('fk_employee__vchr_employee_code'), str_full_name = Concat(
                                                    'fk_employee__first_name', Value(' '), Case(When(fk_employee__vchr_middle_name = None,
                                                    then = F('fk_employee__last_name')), default = Concat('fk_employee__vchr_middle_name',
                                                    Value(' '), 'fk_employee__last_name'), output_field = CharField()), output_field = CharField()),
                                                    str_department = F('fk_employee__fk_department__vchr_name'), str_designation = F('fk_employee__fk_desig__vchr_name'),
                                                    str_branch = F('fk_employee__fk_branch__vchr_name'), int_emp_id = F('fk_employee_id'), dat_doj = F('fk_employee__dat_doj'),
                                                    dat_resignation = F('fk_employee__dat_resignation'), is_active = F('fk_employee__is_active')).values('int_emp_id',
                                                    'str_emp_code','str_full_name', 'str_department', 'str_designation', 'str_branch', 'dbl_gross', 'dbl_bp', 'dbl_hra', 'dbl_cca', 'dbl_sa',
                                                    'dbl_wa', 'dat_created','dat_doj', 'dat_resignation', 'is_active').order_by('int_emp_code', 'dat_created')
            if request.data.get('lstDesignation'):
                ins_salary = ins_salary.filter(fk_employee__fk_desig_id__in=request.data.get('lstDesignation'))
            if request.data.get('lstEmployee'):
                ins_salary = ins_salary.filter(fk_employee_id__in=request.data.get('lstEmployee'))
            if request.data.get('lstDepartmentId'):
                ins_salary = ins_salary.filter(fk_employee__fk_department_id__in=request.data.get('lstDepartmentId'))
            if request.data.get('lstBranch'):
                ins_salary = ins_salary.filter(fk_employee__fk_branch_id__in=request.data.get('lstBranch'))

            rst_bonus = BonusPaid.objects.filter(dat_paid__gte = dat_start, dat_paid__lte = dat_end).values('json_paid')
            dct_bonus = {}
            for ins_bonus in rst_bonus:
                for dct_emp_bonus in ins_bonus['json_paid']:
                    for emp_id in dct_emp_bonus:
                        if emp_id not in dct_bonus:
                            dct_bonus[emp_id] = dct_emp_bonus[emp_id]
                        else:
                            dct_bonus[emp_id] += dct_emp_bonus[emp_id]

            if not ins_salary:
                return Response({'status':0,'reason':'No data', 'message': 'No Data'})
            # ins_salary = ins_salary.filter(fk_employee_id=1988)
            dct_data = OrderedDict()
            dat_temp = dat_start
            while dat_temp < dat_deduct:
                num_months = (dat_end.year - dat_temp.year) * 12 + (dat_end.month - dat_temp.month)
                for ins_data in ins_salary:
                    if ins_data['str_emp_code'] not in dct_data:
                        dct_data[ins_data['str_emp_code']] = {}
                        dct_data[ins_data['str_emp_code']]['int_emp_id'] = ins_data['int_emp_id']
                        dct_data[ins_data['str_emp_code']]['str_emp_code'] = ins_data['str_emp_code']
                        dct_data[ins_data['str_emp_code']]['str_full_name'] = ins_data['str_full_name']
                        dct_data[ins_data['str_emp_code']]['str_department'] = ins_data['str_department']
                        dct_data[ins_data['str_emp_code']]['str_designation'] = ins_data['str_designation']
                        dct_data[ins_data['str_emp_code']]['str_branch'] = ins_data['str_branch']
                        dct_data[ins_data['str_emp_code']]['dbl_bp_da'] = 0
                        dct_data[ins_data['str_emp_code']]['dbl_hra'] = 0
                        dct_data[ins_data['str_emp_code']]['dbl_others'] = 0
                        dct_data[ins_data['str_emp_code']]['dbl_gross'] = 0
                        dct_data[ins_data['str_emp_code']]['dbl_gross_6'] = 0
                        dct_data[ins_data['str_emp_code']]['dat_doj'] = None
                        dct_data[ins_data['str_emp_code']]['dat_doj_start'] = None
                    if ins_data['dat_doj'] <= dat_temp and (ins_data['is_active'] or not ins_data['dat_resignation'] or ins_data['dat_resignation'] >= dat_end.date()):
                        dct_data[ins_data['str_emp_code']]['dbl_bp_da'] = ins_data['dbl_bp']
                        dct_data[ins_data['str_emp_code']]['dbl_hra'] = ins_data['dbl_hra']
                        dct_data[ins_data['str_emp_code']]['dbl_others'] = ins_data['dbl_gross'] - ins_data['dbl_bp'] - ins_data['dbl_hra']
                        dct_data[ins_data['str_emp_code']]['dbl_gross'] = ins_data['dbl_gross']
                        if dct_data[ins_data['str_emp_code']]['dat_doj_start']:
                            dct_data[ins_data['str_emp_code']]['dbl_gross_6'] += (ins_data['dbl_gross'] * ((dat_end.year - dct_data[ins_data['str_emp_code']]['dat_doj_start'].year) * 12 + (dat_end.month - dct_data[ins_data['str_emp_code']]['dat_doj_start'].month)))/((dat_deduct.year - dct_data[ins_data['str_emp_code']]['dat_doj_start'].year) * 12 + (dat_deduct.month - dct_data[ins_data['str_emp_code']]['dat_doj_start'].month))
                        else:
                            dct_data[ins_data['str_emp_code']]['dbl_gross_6'] += (ins_data['dbl_gross'] * ((dat_end.year - dat_start.year) * 12 + (dat_end.month - dat_start.month)))/((dat_deduct.year - dat_start.year) * 12 + (dat_deduct.month - dat_start.month))

                    elif ins_data['dat_doj'] >= dat_temp and ins_data['dat_doj'] <= (dat_temp + relativedelta(months=1, days=-1)) and not dct_data[ins_data['str_emp_code']]['dat_doj']:
                        dct_data[ins_data['str_emp_code']]['dat_doj'] = ins_data['dat_doj']
                        dct_data[ins_data['str_emp_code']]['dat_doj_start'] = dat_temp
                        dct_data[ins_data['str_emp_code']]['dbl_bp_da'] = ins_data['dbl_bp']
                        dct_data[ins_data['str_emp_code']]['dbl_hra'] = ins_data['dbl_hra']
                        dct_data[ins_data['str_emp_code']]['dbl_others'] = ins_data['dbl_gross'] - ins_data['dbl_bp'] - ins_data['dbl_hra']
                        dct_data[ins_data['str_emp_code']]['dbl_gross'] = ins_data['dbl_gross']
                        dct_data[ins_data['str_emp_code']]['dbl_gross_6'] += (ins_data['dbl_gross'] * ((dat_end.year - dat_temp.year) * 12 + (dat_end.month - dat_temp.month)))/((dat_deduct.year - dat_temp.year) * 12 + (dat_deduct.month - dat_temp.month))
                        dct_data[ins_data['str_emp_code']]['dbl_gross_6'] -= ins_data['dbl_gross'] - (ins_data['dbl_gross']/30)*(((dat_temp + relativedelta(months=1, days=-1)) - ins_data['dat_doj']).days+1)

                    elif not ins_data['is_active'] and ins_data['dat_resignation'] and ins_data['dat_resignation'] >= dat_temp.date() and ins_data['dat_resignation'] <= dat_end.date():
                        dct_data[ins_data['str_emp_code']]['dbl_bp_da'] = ins_data['dbl_bp']
                        dct_data[ins_data['str_emp_code']]['dbl_hra'] = ins_data['dbl_hra']
                        dct_data[ins_data['str_emp_code']]['dbl_others'] = ins_data['dbl_gross'] - ins_data['dbl_bp'] - ins_data['dbl_hra']
                        dct_data[ins_data['str_emp_code']]['dbl_gross'] = ins_data['dbl_gross']
                        if ins_data['dat_resignation'] >= dat_temp.date() and ins_data['dat_resignation'] <= (dat_temp + relativedelta(months=1, days=-1)).date():
                            dct_data[ins_data['str_emp_code']]['dbl_gross_6'] += (ins_data['dbl_gross']/30)*((ins_data['dat_resignation']-dat_temp.date()).days+1 if (ins_data['dat_resignation']-dat_temp.date()).days+1 < 30 else 30)
                        else:
                            dct_data[ins_data['str_emp_code']]['dbl_gross_6'] += (ins_data['dbl_gross'] * ((ins_data['dat_resignation'].year - dat_start.year) * 12 + (ins_data['dat_resignation'].month - dat_start.month)))/((ins_data['dat_resignation'].year - dat_start.year) * 12 + (ins_data['dat_resignation'].month - dat_start.month))

                #     if ins_data['int_emp_id'] not in dct_data:
                #         dct_data[ins_data['int_emp_id']] = {}
                #         dct_data[ins_data['int_emp_id']]['dat_created'] = None
                #         dct_data[ins_data['int_emp_id']]['dat_month'] = None
                #         dct_data[ins_data['int_emp_id']]['dbl_gross'] = None
                #         dct_data[ins_data['int_emp_id']]['dbl_count'] = None
                #         dct_data[ins_data['int_emp_id']]['int_month'] = None
                #     if ins_data['dat_created'] < dat_temp or (ins_data['dat_created'] > dat_temp and ins_data['dat_created'] < dat_temp+relativedelta(months=1,days=-1)):
                #         if ins_data['dat_created'] not in dct_data[ins_data['int_emp_id']]['dat_created']:
                #             dct_data[ins_data['int_emp_id']]['dat_created'] = ins_data['dat_created']
                #             dct_data[ins_data['int_emp_id']]['dat_month'] = dat_temp
                #             dct_data[ins_data['int_emp_id']]['dbl_gross'] = ins_data['dbl_gross']
                #             dct_data[ins_data['int_emp_id']]['dbl_count'] = 1
                #             dct_data[ins_data['int_emp_id']]['int_month'] = num_months
                #
                #
                #         # if ins_data['dat_created'] not in dct_data[ins_data['int_emp_id']]:
                #         #     dct_data[ins_data['int_emp_id']][ins_data['dat_created']] = {}
                #         #     dct_data[ins_data['int_emp_id']][ins_data['dat_created']]['dbl_gross'] = ins_data['dbl_gross']
                #         #     dct_data[ins_data['int_emp_id']][ins_data['dat_created']]['int_count'] = num_months
                #         #     dct_data[ins_data['int_emp_id']][ins_data['dat_created']]['dat_month'] = dat_temp
                #         #     elif
                #         print(ins_data['dat_created'])
                #
                #         # if num_months not in dct_data[ins_data['int_emp_id']]:
                #         #     dct_data[ins_data['int_emp_id']][num_months] = {}
                #         #     dct_data[ins_data['int_emp_id']][num_months]['dat_created'] = ins_data['dat_created']
                #         #     dct_data[ins_data['int_emp_id']][num_months]['dbl_gross'] = ins_data['dbl_gross']
                #         #     dct_data[ins_data['int_emp_id']][num_months]['dat_month'] = dat_temp
                #         # elif ins_data['dat_created'] > dct_data[ins_data['int_emp_id']][num_months]['dat_created']:
                #         #     dct_data[ins_data['int_emp_id']][num_months]['dat_created'] = ins_data['dat_created']
                #         #     dct_data[ins_data['int_emp_id']][num_months]['dbl_gross'] = ins_data['dbl_gross']
                #         #     dct_data[ins_data['int_emp_id']][num_months]['dat_month'] = dat_temp

                dat_temp += relativedelta(months=1)

            file_name = 'SalaryReport/Professional_Tax_Report_' + datetime.strftime(date.today(), "%d-%m-%Y") + '.xlsx'
            if not path.exists(settings.MEDIA_ROOT + '/SalaryReport/'):
                os.mkdir(settings.MEDIA_ROOT + '/SalaryReport/')
            writer = pd.ExcelWriter(settings.MEDIA_ROOT + '/' + file_name, engine ='xlsxwriter')
            workbook = writer.book
            worksheet = workbook.add_worksheet()

            # title_style = workbook.add_format({'font_size':14, 'bold':1, 'align': 'center', 'border':1})
            # title_style.set_align('vcenter')
            # title_style.set_pattern(1)
            # title_style.set_bg_color('#ffe0cc')
            # worksheet.merge_range('A1+:K1', 'Professional Tax Report ('+calendar.month_name[int_month]+' '+str(int_year)+')', title_style)
            # worksheet.set_row(0, 30)

            head_style = workbook.add_format({'font_size':11, 'bold':1, 'align': 'center','border':1,'border_color':'#000000','text_wrap':True})
            head_style.set_pattern(1)
            head_style.set_bg_color('#bfbfbf')
            head_style.set_align('vcenter')
            worksheet.autofilter('A1:N1')

            row_style = workbook.add_format({'font_size':11})
            row_style.set_align('vcenter')

            worksheet.protect('',{'autofilter':True})

            int_row = 0
            worksheet.write(int_row, 0, 'ID', head_style); worksheet.set_column(0, 0, 13)
            worksheet.write(int_row, 1, 'Name', head_style);
            worksheet.write(int_row, 2, 'Branch', head_style);
            worksheet.write(int_row, 3, 'Department', head_style);
            worksheet.write(int_row, 4, 'Designation', head_style);worksheet.set_column(1, 4, 35)
            worksheet.write(int_row, 5, 'Basic + DA', head_style);
            worksheet.write(int_row, 6, 'HRA', head_style);
            worksheet.write(int_row, 7, 'Others', head_style);
            worksheet.write(int_row, 8, 'Gross Salary', head_style); worksheet.set_column(5, 8, 15)
            worksheet.write(int_row, 9, 'Gross Salary for six Month', head_style); worksheet.set_column(9, 9, 20)
            worksheet.write(int_row, 10, 'Bonus', head_style);
            worksheet.write(int_row, 11, 'Total', head_style); worksheet.set_column(10, 11, 15)
            worksheet.write(int_row, 12, 'Professional Tax Amonut', head_style); worksheet.set_column(12, 12, 20)
            worksheet.write(int_row, 13, 'DOJ', head_style); worksheet.set_column(13, 13, 18)
            worksheet.set_row(int_row, 35)

            for ins_data in dct_data:
                int_row += 1
                worksheet.write(int_row, 0, dct_data[ins_data].get('str_emp_code'), row_style)
                worksheet.write(int_row, 1, dct_data[ins_data].get('str_full_name'), row_style)
                worksheet.write(int_row, 2, dct_data[ins_data].get('str_branch'), row_style)
                worksheet.write(int_row, 3, dct_data[ins_data].get('str_department'), row_style)
                worksheet.write(int_row, 4, dct_data[ins_data].get('str_designation'), row_style)
                worksheet.write(int_row, 5, dct_data[ins_data].get('dbl_bp_da'), row_style)
                worksheet.write(int_row, 6, dct_data[ins_data].get('dbl_hra'), row_style)
                worksheet.write(int_row, 7, dct_data[ins_data].get('dbl_others'), row_style)
                worksheet.write(int_row, 8, round(dct_data[ins_data].get('dbl_gross')), row_style)
                worksheet.write(int_row, 9, round(dct_data[ins_data].get('dbl_gross_6')), row_style)
                worksheet.write(int_row, 10, dct_bonus.get(str(dct_data[ins_data]['int_emp_id']), 0), row_style)
                dbl_total = dct_data[ins_data].get('dbl_gross_6') + dct_bonus.get(str(dct_data[ins_data]['int_emp_id']), 0)
                worksheet.write(int_row, 11, round(dbl_total), row_style)
                ins_tax = ins_pro_tax.filter(Q(dbl_from_amt__isnull=True, dbl_to_amt__gte=dbl_total) | Q(dbl_from_amt__lte=dbl_total, dbl_to_amt__isnull=True) | Q(dbl_from_amt__lte = dbl_total, dbl_to_amt__gte=dbl_total)).values('dbl_tax').first()
                worksheet.write(int_row, 12, ins_tax['dbl_tax'] if ins_tax and ins_tax['dbl_tax'] else 0, row_style)
                worksheet.write(int_row, 13, dct_data[ins_data].get('dat_doj').strftime('%d-%m-%Y') if dct_data[ins_data].get('dat_doj') else '', row_style)
            writer.save()
            return Response({'status':1, 'data':request.scheme+'://'+request.get_host()+settings.MEDIA_URL+file_name})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno), 'message': 'Something Went Wrong'})

class FixedAllowanceAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            if request.GET.get('intFixedId'):
                FixedAllowance.objects.filter(pk_bint_id = request.GET.get('intFixedId')).update(int_status = 2, dat_stoped = datetime.now())
                return Response({'status':1})
            else:
                return Response({'status':0})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})
    def post(self,request):
        try:
            int_month = int(request.data['intMonthYear'].split('-')[0])
            int_year = int(request.data['intMonthYear'].split('-')[1])
            int_emp_id = request.data['intEmpId']
            if int_emp_id:
                if request.data['blnFixed'] and not FixedAllowance.objects.filter(fk_employee_id = int_emp_id, int_month = int_month, int_year = int_year):
                    FixedAllowance.objects.create(fk_employee_id = int_emp_id, dbl_amount = request.data['intAmount'], int_month = int_month, int_year = int_year,txt_remarks = request.data.get('strRemarks'))
                elif request.data['blnFixed']:
                    return Response({'status':0, 'message': 'Fixed Allowance Already added'})
            else:
                return Response({'status':0, 'message': 'No Employee'})
            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})
    def put(self, request):
        try:
            session = Connection()
            int_month = int(request.data['intMonthYear'].split('-')[0])
            int_year = int(request.data['intMonthYear'].split('-')[1])
            rst_fixed = session.query(UserDetailsSA.user_ptr_id, FixedAllowanceSA.pk_bint_id.label('int_fixed_all_id'), UserDetailsSA.vchr_employee_code, func.concat(AuthUserSA.first_name, ' ',AuthUserSA.last_name).label('strName'), FixedAllowanceSA.dbl_amount,FixedAllowanceSA.int_month,FixedAllowanceSA.int_year,FixedAllowanceSA.txt_remarks)\
                                .join(AuthUserSA, AuthUserSA.id == UserDetailsSA.user_ptr_id)\
                                .outerjoin(FixedAllowanceSA, or_(and_(FixedAllowanceSA.fk_employee_id == UserDetailsSA.user_ptr_id, FixedAllowanceSA.int_month <= int_month, FixedAllowanceSA.int_year <= int_year, FixedAllowanceSA.int_status == 1), and_(FixedAllowanceSA.fk_employee_id == UserDetailsSA.user_ptr_id, FixedAllowanceSA.int_status == 2, extract('month', FixedAllowanceSA.dat_stoped) > int_month, extract('year', FixedAllowanceSA.dat_stoped) >= int_year)))\
                                .group_by(UserDetailsSA.user_ptr_id, FixedAllowanceSA.pk_bint_id, UserDetailsSA.vchr_employee_code, func.concat(AuthUserSA.first_name, ' ',AuthUserSA.last_name), FixedAllowanceSA.dbl_amount)\
                                .filter(FixedAllowanceSA.dbl_amount != None)

            if request.data.get('intId'):
                rst_fixed = rst_fixed.filter(UserDetailsSA.user_ptr_id == request.data['intId'])
            int_user_id  = request.user.userdetails.user_ptr_id
            int_desig_id = request.user.userdetails.fk_desig_id
            int_dpt_name = request.user.userdetails.fk_department.vchr_name
            ins_hierarchy = HierarchyLevel.objects.filter(int_status=1, fk_reporting_to=int_desig_id).values('fk_designation_id')

            lst_desig = []
            for item in ins_hierarchy:
                lst_desig.append(item['fk_designation_id'])
            if int_dpt_name != 'HR & ADMIN':
                if lst_desig:
                    rst_fixed = rst_fixed.filter(UserDetailsSA.fk_desig_id.in_(lst_desig))
            lst_data = []
            for rst_data in rst_fixed.all():
                dct_data = {}
                dct_data['intEMPId'] = rst_data.user_ptr_id
                dct_data['strEMPCode']  = rst_data.vchr_employee_code
                dct_data['strEMPName'] = rst_data.strName
                dct_data['intFixedId'] = rst_data.int_fixed_all_id
                dct_data['blnFixed'] = False
                dct_data['intMonthYear'] = str(calendar.month_abbr[rst_data.int_month])+"' "+str(rst_data.int_year)
                if rst_data.dbl_amount:
                    dct_data['blnFixed'] = True
                dct_data['dblAmount'] = rst_data.dbl_amount
                if rst_data.txt_remarks:
                    dct_data['strRemarks'] = rst_data.txt_remarks
                lst_data.append(dct_data)
            if lst_data == []:
                return Response({'status':1, 'data':lst_data})
            file_name = 'FixedAllowanceReport/Fixed_allowance_report' + datetime.strftime(date.today(), "%d-%m-%Y") + '.xlsx'
            if path.exists(file_name):
                os.remove(file_name)
            if not path.exists(settings.MEDIA_ROOT + '/FixedAllowanceReport/'):
                os.mkdir(settings.MEDIA_ROOT + '/FixedAllowanceReport/')
            writer = pd.ExcelWriter(settings.MEDIA_ROOT + '/' + file_name, engine ='xlsxwriter')
            workbook = writer.book
            worksheet = workbook.add_worksheet()

            title_style = workbook.add_format({'font_size':14, 'bold':1, 'align': 'center', 'border':1})
            title_style.set_align('vcenter')
            title_style.set_pattern(1)
            title_style.set_bg_color('#ffe0cc')
            worksheet.set_row(0, 30)

            head_style = workbook.add_format({'font_size':11, 'bold':1, 'align': 'center','border':1,'border_color':'#000000'})
            head_style.set_pattern(1)
            head_style.set_bg_color('#bfbfbf')
            head_style.set_align('vcenter')
            worksheet.autofilter('B2:E2')
            row_style = workbook.add_format({'font_size':11})
            row_style.set_align('vcenter')
            worksheet.protect('',{'autofilter':True})

            int_row = 1
            worksheet.write(int_row, 0, 'SL. No', head_style); worksheet.set_column(0, 0, 6)
            worksheet.write(int_row, 1, 'EMP CODE', head_style); worksheet.set_column(1, 1, 13)
            worksheet.write(int_row, 2, 'EMP NAME', head_style); worksheet.set_column(2, 2, 30)
            worksheet.write(int_row, 3, 'AMOUNT', head_style); worksheet.set_column(3, 3, 15)
            worksheet.write(int_row, 4, 'START DATE', head_style); worksheet.set_column(4, 4, 20)
            worksheet.set_row(int_row, 33)

            for ins_data in lst_data:
                int_row += 1
                worksheet.write(int_row, 0, int_row-1, row_style)
                worksheet.write(int_row, 1, ins_data.get('strEMPCode'), row_style)
                worksheet.write(int_row, 2, ins_data.get('strEMPName'), row_style)
                worksheet.write(int_row, 3, ins_data.get('dblAmount'), row_style)
                worksheet.write(int_row, 4, ins_data.get('intMonthYear'), row_style)
                worksheet.set_row(int_row, 25, row_style)
            writer.save()
            return Response({'status':1, 'data':lst_data,'report':request.scheme+'://'+request.get_host()+settings.MEDIA_URL+file_name})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})
    def patch(self, request):
        try:
            int_month = 0
            int_year = 0
            int_emp_id = 0
            if request.data.get('intMonthYear'):
                int_month = int(request.data['intMonthYear'].split('-')[0])
                int_year = int(request.data['intMonthYear'].split('-')[1])
                int_emp_id = request.data['intEmpId']

            if request.data.get('blnFixed') and FixedAllowance.objects.filter(pk_bint_id = request.data['intFixedId']):
                FixedAllowance.objects.filter(pk_bint_id = request.data['intFixedId']).update(dbl_amount = request.data['intAmount'], int_month = int_month, int_year = int_year,txt_remarks = request.data.get('strRemarks'))
            elif request.data.get('blnFixed'):
                FixedAllowance.objects.create(fk_employee_id = int_emp_id, dbl_amount = request.data['intAmount'], int_month = int_month, int_year = int_year)
            else:
                FixedAllowance.objects.filter(pk_bint_id = request.data['intFixedId']).update(int_status = 0)
            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


class PaySlipDownload(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            conn = engine.connect()
            int_month = int(request.data['intMonthYear'].split('-')[0])
            int_year = int(request.data['intMonthYear'].split('-')[1])
            int_emp_id = request.data['intEmployeeId']
            if request.user.userdetails.fk_department.vchr_name != 'HR & ADMIN':
                return Response({"status":0,"message":"Permission Denied"})
            # int_month = 10
            # int_year = 2020
            str_month = date(1900, int_month ,1).strftime('%B')
            now_date = datetime.now()

            dur_calendar = calendar.monthrange(int_year, int_month)
            str_start_date = str(int_year)+'-'+str(int_month)+'-1'
            str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(dur_calendar[1])

            if not request.user.is_superuser:
                ins_admin = AdminSettings.objects.filter(vchr_code='PAYROLL_PERIOD',bln_enabled=True,fk_company_id=request.user.userdetails.fk_company_id).values('vchr_value', 'int_value').first()
                # ins_admin = AdminSettings.objects.filter(vchr_code='PAYROLL_PERIOD',bln_enabled=True,fk_company_id='1').values('vchr_value', 'int_value').first()
                if ins_admin and ins_admin['int_value'] != 0:
                    str_start_date = datetime.strftime(datetime.strptime(str(int_year)+'-'+str(int_month)+'-'+ins_admin['vchr_value'][0],'%Y-%m-%d')+timedelta(days=int(ins_admin['vchr_value'][0])*ins_admin['int_value']),'%Y-%m-')+ins_admin['vchr_value'][0]
                    str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(int(ins_admin['vchr_value'][0])-1)

            if int_month == now_date.month and int_year == now_date.year and now_date.day <= int(str_end_date.split('-')[2]):
                str_end_date = str(int_year)+'-'+str(int_month)+'-'+str(now_date.day)

            dat_month_last = datetime.strptime(str_end_date, '%Y-%m-%d')
            dat_month_first = datetime.strptime(str_start_date, '%Y-%m-%d')
            lst_leave_type = ['LOP']

            if (int_year == 2020 and int_month < 9) or int_year < 2020:
                return Response({"status":0,"message":"No Data"})

            str_query = "SELECT ud.user_ptr_id AS int_emp_id, ud.vchr_employee_code, CONCAT(au.first_name, ' ', CASE WHEN ud.vchr_middle_name IS NOT NULL THEN CONCAT(ud.vchr_middle_name, ' ', au.last_name) ELSE au.last_name END) AS str_emp_name, cat.vchr_name AS str_category_name, struct.vchr_name AS str_structure, slprcd.dbl_gross, (CASE WHEN vrblpy.dbl_amount IS NOT NULL THEN vrblpy.dbl_amount ELSE 0 END) AS dbl_variable_pay, ud.json_allowance, struct.dbl_bp_da, struct.dbl_bp_da_per, struct.dbl_da, struct.json_rules, (CASE WHEN slryadv.dbl_amount IS NOT NULL THEN slryadv.dbl_amount ELSE 0 END) AS dbl_adv_amount, londtls.pk_bint_id AS int_loan_details_id, (CASE WHEN londtls.dbl_amount IS NOT NULL THEN londtls.dbl_amount ELSE 0 END) AS dbl_work_amount, (CASE WHEN mlondtls.dbl_amount IS NOT NULL THEN mlondtls.dbl_amount ELSE 0 END) AS dbl_mobile_loan, lonrqst.bln_mob_loan AS bln_mob_loan, slprcd.dbl_bp, slprcd.dbl_da, slprcd.dbl_hra, slprcd.dbl_cca, slprcd.dbl_sa, slprcd.dbl_wa, slprcd.json_deductions, slprcd.json_allowances, slprcd.dbl_net_salary, slprcd.dbl_monthly_ctc, json_attendance->>'dbl_tot_lop' AS leave, br.vchr_name str_branch, dept.vchr_name str_department, desg.vchr_name str_designation, ud.dat_doj, ud.vchr_esi_no,ud.vchr_acc_no, ud.vchr_pf_no,ud.vchr_esi_no, ud.vchr_uan_no, ud.vchr_wwf_no, ud.vchr_grade,(CASE WHEN fixed.dbl_amount IS NOT NULL THEN fixed.dbl_amount ELSE 0 END) AS dbl_fixed_alnc,json_attendance->>'dbl_casual_leave' as dbl_casual  FROM salary_processed AS slprcd JOIN user_details ud ON ud.user_ptr_id = slprcd.fk_employee_id JOIN auth_user au ON au.id = ud.user_ptr_id JOIN category cat ON cat.pk_bint_id = ud.fk_category_id JOIN salary_structure struct ON struct.pk_bint_id = ud.fk_salary_struct_id LEFT JOIN variable_pay vrblpy ON vrblpy.fk_employee_id = ud.user_ptr_id AND vrblpy.int_month = slprcd.int_month AND vrblpy.int_year = slprcd.int_year AND vrblpy.int_status = 1  LEFT JOIN fixed_allowance fixed ON fixed.fk_employee_id = ud.user_ptr_id AND fixed.int_month = slprcd.int_month AND fixed.int_year = slprcd.int_year AND fixed.int_status = 1 LEFT JOIN loan_request lonrqst ON lonrqst.fk_employee_id = ud.user_ptr_id AND lonrqst.int_status = 1 AND lonrqst.bln_mob_loan = False LEFT JOIN loan_details londtls ON londtls.fk_request_id = lonrqst.pk_bint_id AND londtls.int_month = slprcd.int_month AND londtls.int_year = slprcd.int_year AND londtls.int_status = 0 LEFT JOIN loan_request AS mlonrqst ON mlonrqst.fk_employee_id = ud.user_ptr_id AND mlonrqst.int_status = 1 AND mlonrqst.bln_mob_loan = True LEFT JOIN loan_details mlondtls ON mlondtls.fk_request_id = mlonrqst.pk_bint_id AND mlondtls.int_month = slprcd.int_month AND mlondtls.int_year = slprcd.int_year AND mlondtls.int_status = 0 LEFT JOIN salary_advance slryadv ON slryadv.fk_employee_id = ud.user_ptr_id AND slryadv.int_month = slprcd.int_month AND slryadv.int_year = slprcd.int_year AND slryadv.int_status = 2 LEFT JOIN department dept ON ud.fk_department_id = dept.pk_bint_id LEFT JOIN job_position desg ON ud.fk_desig_id = desg.pk_bint_id LEFT JOIN branch br ON ud.fk_branch_id = br.pk_bint_id WHERE slprcd.int_status = 0 AND ud.user_ptr_id = {0} AND slprcd.int_month = {1} AND slprcd.int_year = {2} GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41"
            str_query = str_query.format(str(int_emp_id), str(int_month), str(int_year))

            # str_query = str_query.format(str(2045), str(11), str(2020))

            # str_query = str_query.format(str(lst_leave_type)[1:-1], str(int_month), str(int_year), str_start_date, str_end_date, ' AND ud.user_ptr_id='+str(request.user.userdetails.user_ptr_id))
            # str_query = str_query.format(str(lst_leave_type)[1:-1], str(int_month), str(int_year), str_start_date, str_end_date, ' AND ud.user_ptr_id='+str(2258))
            rst_data = conn.execute(str_query).fetchall()
            conn.close()

            if rst_data:
                int_days = 30
                if len(rst_data)!=1:
                    return Response({'status':0, 'reason':'Multiple Data', 'message':'Something went wrong'})
                # dct_data = EmployeeSalaryProcessNew(rst_data[0])
                dct_data = dict(rst_data[0])
                str_amount_words = num2words.num2words(dct_data['dbl_net_salary']).title().split("Point")
                if len(str_amount_words)==2:
                    str_amount_words=str_amount_words[0]+" Rupees and "+str_amount_words[1]+" Paise only/-"
                else:
                    str_amount_words=str_amount_words[0] +" Rupees only/-"


                # if request.data.get("bln_print") == None:
                dct_summary = {}
                dct_summary['str_emp_code'] = dct_data['vchr_employee_code']
                dct_summary['str_emp_name'] = dct_data['str_emp_name']
                dct_summary['str_location'] = dct_data['str_branch']
                dct_summary['str_department'] = dct_data['str_department']
                dct_summary['str_designation'] = dct_data['str_designation']
                dct_summary['dat_doj'] = datetime.strftime(dct_data['dat_doj'],'%d-%m-%Y')
                dct_summary['str_esi_no'] = dct_data['vchr_esi_no']
                dct_summary['ba_da'] = dct_data['dbl_bp'] + dct_data['dbl_da']
                dct_summary['hra'] = dct_data['dbl_hra']
                dct_summary['cca'] = dct_data['dbl_cca']
                dct_summary['wa'] = dct_data['dbl_wa']
                dct_summary['sa'] = dct_data['dbl_sa']
                dct_summary['wwf'] = dct_data['json_deductions'].get('WWF', 0)
                dct_summary['pf'] = dct_data['json_deductions'].get('PF', 0)
                dct_summary['esi'] = dct_data['json_deductions'].get('ESI', 0)
                dct_summary['charity'] = dct_data['json_deductions'].get('Charity', 0)
                # dct_summary['pt'] = dct_data['Deductions']['pt']
                dct_summary['gross_allowance'] = dct_data['dbl_bp'] + dct_data['dbl_da'] + dct_data['dbl_hra'] + dct_data['dbl_cca'] + dct_data['dbl_wa'] + dct_data['dbl_sa']
                dct_summary['gross_deduction'] = dct_data['json_deductions'].get('WWF', 0) + dct_data['json_deductions'].get('PF', 0) + dct_data['json_deductions'].get('ESI', 0) + dct_data['json_deductions'].get('Charity', 0) + dct_data['json_deductions'].get('ProTax', 0) + dct_data['json_deductions'].get('TDS', 0) + dct_data['json_deductions'].get('SalaryAdvance', 0) + dct_data['json_deductions'].get('WorkLoan', 0) + dct_data['json_deductions'].get('MobileLoan', 0)
                dct_summary['dbl_other_deduction']  = dct_data['json_deductions'].get('WorkLoan', 0) + dct_data['json_deductions'].get('MobileLoan', 0)
                dct_summary['net_salary'] = dct_summary['gross_allowance'] - dct_summary['gross_deduction']
                    # return Response({"status":"success","data":dct_summary})

                str_html = """<!doctype html>
                                                <html>
                                                <head>
                                                <meta charset="utf-8">
                                                <title>Untitled Document</title>
                                                	<style>
                                                	    .container{
                                                			         width:1170px;
                                                			         margin:auto;
                                                		          }
                                                		    .clear{
                                                			         clear:both;
                                                			      }
                                                				 p{
                                                					margin-bottom: 5px;
                                                					margin-top: 0px;

                                                				  }
                                                		li{
                                                			font-size: 17px;
                                                		}
                                                		.imagebox{
                                                			         width:100%;
                                                			         float: left;
                                                			         border-bottom: 1px solid #c7c2c2;
                                                		          }
                                                		    .ibox1{
                                                				    width: 20%;
                                                				    float: left;

                                                		          }
                                                		    .ibox2{
                                                				    width: 80%;
                                                				    float: left;
                                                		          }
                                                		 .ibox2 h6{
                                                			       margin-bottom: 0;
                                                                   margin-top: 10px;
                                                			       padding-left: 0 !important;
                                                		          }
                                                		  .ibox2 p{
                                                			       margin-bottom: 0;
                                                                   margin-top: 5px;
                                                			       padding-right: 0;
                                                                   padding-left: 0;
                                                		          }
                                                		    .ibox3{
                                                				    width:20%;
                                                				    float: left;
                                                		          }
                                                		#s {
                                                					  font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;
                                                					  border-collapse: collapse;
                                                					  width: 100%;
                                                					}

                                                		#s td, #s th {
                                                		  border: 1px solid #ddd;
                                                		  padding: 8px;
                                                		}

                                                /*		#s tr:nth-child(even){background-color: #f2f2f2;}*/

                                                		#s tr:hover {background-color: aliceblue;}

                                                		#s th {
                                                		  padding-top: 22px;
                                                		  padding-bottom: 22px;
                                                		  text-align: left;
                                                		  background-color:#ffeae0;
                                                          color: #360986;
                                                		}

                                                	</style>
                                                </head>

                                                <body>

                                                <div style="width:100%;float: left;border-top: 1px solid #c0bebe;border-bottom: 1px solid #c0bebe;border-left: 1px solid #c0bebe;border-right: 1px solid #c0bebe";>
                                                  <div class="container">
                                                    <div class="imagebox">
                                                           <div class="ibox1">
                                                           <img src='"""+settings.MEDIA_ROOT+"""/mygpaylogo.jpeg' style="width:220px;hight:220px">
                                                         </div>
                                                         <div class="ibox2">
                                                            <div style="width:100%;float:left;">

                                                            <p style="font-size: 18px;">  Form XIII- See Rule  29(2)   <br><br>

                                                            		<p style="font-weight: 600; font-size:22px; text-align: center;">MYG</p><br>
                                                              </div>
                                                            <p style="font-size: 18px; text-align: center;"> myG Corporate Office, 27/1288, Puthiyara, Mini Bypass, Calicut Pin : 673004.<br><br><br>
                                                            </p>
                                                           </div>
                                                         </div>
                                                      </div>
                                                    <div class="clear"></div>
                                                      <p style="text-align: center;font-weight:600;font-size:22px;margin-top: 10px;margin-bottom:10px;">Pay Slip - For the Month of – """+str(str_month)+""" """+str(int_year)+"""</p>
                                                      <div style="width:100%;float: left;border-top: 1px solid #c0bebe;padding:10px 0px 10px 0px;border-bottom: 1px solid #c0bebe;">
                                                    		<p style="font-weight: 600; text-align: center;">Basic Details</p>
                                                    		</div>
                                                    <div style="margin-top: 90px;margin-left: 10px;">
                                                      <div style="width: 33%;float: left;">
                                                        <div style="width:30%;float: left">
                                                          <p>EMP Code<span style="float: right">:</span></p>
                                                        </div>
                                                        <div style="width:70%;float: right;text-align: left">
                                                           <p style="font-weight: 600">"""+str(dct_data['vchr_employee_code'])+"""</p>
                                                        </div>
                                                      <div class="clear"></div>

                                                        <div style="width:30%;float: left">
                                                          <p>Name<span style="float: right">:</span></p>
                                                        </div>
                                                        <div style="width:70%;float: right;text-align: left">
                                                           <p style="font-weight: 600">"""+str(dct_data['str_emp_name'])+"""</p>
                                                        </div>
                                                      <div class="clear"></div>

                                                        <div style="width:30%;float: left">
                                                          <p>DOJ<span style="float: right">:</span></p>
                                                        </div>
                                                        <div style="width:70%;float: right;text-align: left">
                                                           <p style="font-weight: 600">"""+str(datetime.strftime(dct_data['dat_doj'],'%d-%m-%Y'))+"""</p>
                                                        </div>
                                                      <div class="clear"></div>
                                                      <div style="width:30%;float: left">
                                                          <p>Grade<span style="float: right">:</span></p>
                                                        </div>
                                                        <div style="width:70%;float: right;text-align: left">
                                                           <p style="font-weight: 600">"""+str(dct_data['vchr_grade'])+"""</p>
                                                        </div>
                                                        <div class="clear"></div>
                                                      <div style="width:30%;float: left">
                                                          <p>PF NO<span style="float: right">:</span></p>
                                                        </div>
                                                        <div style="width:70%;float: right;text-align: left">
                                                           <p style="font-weight: 600">"""+(str(dct_data.get('vchr_pf_no'," ")) if dct_data.get('vchr_pf_no')  else '&nbsp;')+"""</p>
                                                        </div>
                                                        <div style="width:30%;float: left">
                                                          <p>UAN<span style="float: right">:</span></p>
                                                        </div>
                                                        <div style="width:70%;float: right;text-align: left">
                                                           <p style="font-weight: 600">"""+(str(dct_data.get('vchr_uan_no'," ")) if dct_data.get('vchr_uan_no') else '&nbsp;')+"""</p>
                                                        </div>

                                                    </div>
                                                    <div style="width: 33%;float: left"></div>
                                                    <div style="width: 50%;float: right;">
                                                        <div style="width:30%;float: left">
                                                          <p>Department<span style="float: right">:</span></p>
                                                        </div>
                                                        <div style="width:70%;float: right;text-align: left">
                                                           <p style="font-weight: 600">"""+(str(dct_data['str_department']) if dct_data['str_department'] else '&nbsp;')+"""</p>
                                                        </div>
                                                      <div class="clear"></div>

                                                       <div style="width:30%;float: left">
                                                          <p>Designation<span style="float: right">:</span></p>
                                                        </div>
                                                        <div style="width:70%;float: right;text-align: left">
                                                           <p style="font-weight: 600">"""+(str(dct_data['str_designation']) if dct_data['str_designation'] else '&nbsp;')+"""</p>
                                                        </div>
                                                      <div class="clear"></div>

                                                      <div style="width:30%;float: left">
                                                          <p>Location<span style="float: right">:</span></p>
                                                        </div>
                                                        <div style="width:70%;float: right;text-align: left">
                                                           <p style="font-weight: 600">"""+(str(dct_data['str_branch']) if dct_data['str_branch'] else '&nbsp;')+"""</p>
                                                        </div>
                                                      <div class="clear"></div>

                                                      <div style="width:30%;float: left">
                                                          <p>ESIC NO<span style="float: right">:</span></p>
                                                        </div>
                                                        <div style="width:70%;float: right;text-align: left">
                                                           <p style="font-weight: 600">"""+(str(dct_data.get('vchr_esi_no')) if dct_data.get('vchr_esi_no') else '&nbsp;')+"""</p>
                                                        </div>
                                                          <div class="clear"></div>

                                                      <div style="width:30%;float: left">
                                                          <p>WWF NO<span style="float: right">:</span></p>
                                                        </div>
                                                        <div style="width:70%;float: right;text-align: left">
                                                           <p style="font-weight: 600">"""+(str(dct_data.get('vchr_wwf_no')) if str(dct_data.get('vchr_wwf_no')) else '&nbsp;')+"""</p>
                                                        </div>
                                                          <div class="clear"></div>

                                                      <div style="width:30%;float: left">
                                                          <p>BANK ACCOUNT NO<span style="float: right">:</span></p>
                                                        </div>
                                                        <div style="width:70%;float: right;text-align: left">
                                                           <p style="font-weight: 600">"""+(str(dct_data.get('vchr_acc_no')) if dct_data.get('vchr_acc_no') else '&nbsp;')+"""</p>
                                                        </div>
                                                      <div class="clear"></div>
                                                    </div></div>
                                                    <div class="clear"></div>
                                                    <br>
                                                    <div style="width:100%;float: left;border-top: 1px solid #c0bebe;padding:10px 0px 10px 0px;border-bottom: 1px solid #c0bebe;">
                                                  <p style="font-weight: 600; text-align: center;">Attendance Details</p>
                                                  <table id="s" style="margin-top: 27px;">
                                                  <tr>
                                    				<td>Days in Month</td>
                                    				<td style="text-align: right">30.0</td>
                                    				<td>LOP Days</td>
                                    				<td style="text-align: right">"""+str(dct_data['leave'])+"""</td>
                                    			  </tr>
                                                   <tr>
                                    				<td>Payable Days</td>
                                    				<td style="text-align: right">"""+str(30 - float(dct_data['leave']))+"""</td>
                                    				<td>CL</td>
                                    				<td style="text-align: right">"""+str(dct_data['dbl_casual'])+"""</td>
                                    			  </tr>
                                                  </table>
                                                		<p style="font-weight: 600; text-align: center;margin-top: 27px;">Payment Details</p>
                                                		</div>
                                                		<div class="clear"></div>


                                                			<table id="s" style="margin-top: 27px;">
                                                			  <tr>
                                                				<th>Earnings</th>
                                                				<th style="text-align: right">Amount</th>
                                                				<th>Deductions</th>
                                                				<th style="text-align: right">Amount</th>
                                                			  </tr>
                                                			  <tr>
                                                				<td>Basic + Da</td>
                                                				<td style="text-align: right">"""+str(dct_data['dbl_bp'] + dct_data['dbl_da'])+"""</td>
                                                				<td>EPF</td>
                                                				<td style="text-align: right">"""+str(dct_data['json_deductions'].get('PF', 0.0))+"""</td>
                                                			  </tr>
                                                			  <tr>
                                                				<td>House Rent Allowance</td>
                                                				<td style="text-align: right">"""+str(dct_data['dbl_hra'])+"""</td>
                                                        <td>ESI</td>
                                                        <td style="text-align: right">"""+str(dct_data['json_deductions'].get('ESI', 0.0))+"""</td>
                                                			  </tr>
                                                			  <tr>
                                                				<td>City Compensatory Allowance</td>
                                                				<td style="text-align: right">"""+str(dct_data['dbl_cca'])+"""</td>
                                                        <td>WWF</td>
                                                        <td style="text-align: right">"""+str(dct_data['json_deductions'].get('WWF', 0.0))+"""</td>
                                                			  </tr>
                                                			  <tr>
                                                				<td>Washing Allowance</td>
                                                				<td style="text-align: right">"""+str(dct_data['dbl_wa'])+"""</td>
                                                        <td>Profession Tax</td>
                                                        <td style="text-align: right">"""+str(dct_data['json_deductions'].get('ProTax', 0.0))+"""</td>
                                                			  </tr>
                                                			  <tr>
                                                				<td>Special Allowance</td>
                                                				<td style="text-align: right">"""+str(dct_data['dbl_sa'])+"""</td>
                                                        <td>Advance</td>
                                                        <td style="text-align: right">"""+str(dct_data['dbl_adv_amount'])+"""</td>
                                                			  </tr>
                                                			  <tr>
                                                				<td>Variable Allowance</td>
                                                				<td style="text-align: right">"""+(str(dct_data['dbl_variable_pay']) if dct_data['dbl_variable_pay'] else str(0.0))+"""</td>
                                                        <td>TDS</td>
                                                        <td style="text-align: right">"""+(str(dct_data['json_deductions'].get('TDS',0.0) if dct_data['json_deductions'].get('TDS',0.0) != 0 else 0.0) )+"""</td>
                                                				</tr>
                                                        <tr>
                                                       <td>Out Station Allowance</td>
                                                       <td style="text-align: right">"""+(str(dct_data['dbl_fixed_alnc']) if dct_data['dbl_fixed_alnc'] else str(0.0))+"""</td>
                                                       <td>Other Deductions</td>
                                                       <td style="text-align: right">"""+(str(dct_summary['dbl_other_deduction']) if dct_summary['dbl_other_deduction'] else str(0.0))+"""</td>
                                                     </tr>

                                                			  <tr style="background-color:#ffeae0;color: #360986;">
                                                				<td style="font-weight: 600;font-size: 18px;">Total Earnings</td>
                                                				<td style="text-align: right; font-weight: 600;font-size: 18px;">"""+str(dct_summary['gross_allowance'])+"""</td>
                                                        <td style="font-weight: 600;font-size: 18px;">Total deduction</td>
                                                				<td style="text-align: right; font-weight: 600;font-size: 18px;">"""+str(dct_summary['gross_deduction'])+"""</td>
                                                			  </tr>
                                                       </tr>
                                                			  <tr style="background-color:#ffeae0;color: #360986;">
                                                				<td colspan="3" style="text-align: right;font-weight: 600;font-size: 18px;">Net Pay (Total Earnings - Total deductions)</td>
                                                				<td style="text-align: right;font-weight: 600;font-size: 18px;">"""+str(dct_data['dbl_net_salary'])+"""</td>
                                                			  </tr>


                                                			</table><br>
                                                		    <p style="margin-left: 10px">Amount in Words:&nbsp&nbsp<span style="color: green">"""+str_amount_words+""" </span></p>
                                                		<br>
                                                	</div>This is a computer generated salary slip hence dosen't require signature
                                                    </div>

                                                </body>
                                                </html>"""

                """Salary Slip"""
                pdf_name ='Salary_Slip_'+dct_data['vchr_employee_code']+'_'+date.today().strftime('%Y%m%d')+'.pdf'
                filename = settings.MEDIA_ROOT+'/PaySlip/'+pdf_name
                if path.exists(pdf_name):
                    os.remove(pdf_name)
                if not path.exists(settings.MEDIA_ROOT + '/PaySlip/'):
                    os.mkdir(settings.MEDIA_ROOT + '/PaySlip/')
                file_url = request.scheme+'://'+request.get_host()+settings.MEDIA_URL+'PaySlip/'+pdf_name
                pdfkit.from_string(str_html,filename)
                return Response({"status":1,"data":file_url})
            else:
                return Response({"status":0,"message":"Salary not processed"})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


def ProfessionalTaxCalculation(int_month, int_year):
    try:
        conn = engine.connect()
        str_query = ("SELECT * FROM (SELECT pk_bint_id, CONCAT(CASE WHEN EXTRACT(YEAR FROM NOW()) = {1} THEN {1} WHEN int_month_from <= int_month_to THEN {1} ELSE {1}-1 END, '-', int_month_from::TEXT, '-01')::DATE dat_start, CONCAT(CASE WHEN (int_month_from <= int_month_to OR EXTRACT(YEAR FROM NOW()) != {1}) THEN {1} ELSE {1}+1 END, '-', int_month_to::TEXT, '-01')::DATE dat_end, CONCAT(CASE WHEN (int_month_from <= int_deduct_month OR EXTRACT(YEAR FROM NOW()) != {1}) THEN {1} ELSE {1}+1 END, '-', int_deduct_month::TEXT, '-01')::DATE dat_deduction FROM pt_period) ptprd WHERE dat_start <= CONCAT('{1}','-','{0}','-01')::DATE AND dat_end >= CONCAT('{1}','-','{0}','-01')::DATE").format(int_month, int_year);

        rst_data = conn.execute(str_query).fetchall()
        conn.close()
        lst_months = []
        lst_years = []

        dct_pro_tax = {}
        if rst_data:
            dct_pt_period = dict(rst_data[0])
            dat_tmp = dct_pt_period['dat_start']
            while dat_tmp <= dct_pt_period['dat_end']:
                if dat_tmp > datetime.strptime(str(int_year)+'-'+str(int_month)+'-01', "%Y-%m-%d").date():
                    break
                lst_months.append(dat_tmp.month)
                lst_years.append(dat_tmp.year)
                dat_tmp = dat_tmp + relativedelta(months = 1)
            ins_process = SalaryProcessed.objects.filter(int_month__in = lst_months, int_year__in = list(set(lst_years)), int_status = 0).values('fk_employee_id').annotate(dbl_pro_tax = Cast(KeyTextTransform('ProTax', 'json_deductions'), FloatField()), dbl_actual_gross = F('fk_details__dbl_gross')).annotate(dbl_tot_pro_tax = Sum('dbl_pro_tax'), dbl_tot_gross = Sum(Case(When(dbl_pro_tax__gt=0, then=F('dbl_actual_gross')), default = 0, output_field = FloatField()))).values('fk_employee_id', 'dbl_tot_pro_tax', 'dbl_tot_gross')
            ins_details = SalaryDetails.objects.filter(int_status = 1).exclude(fk_employee__vchr_employee_code__in=['MYGE-1', 'MYGE-69']).values('fk_employee_id', 'dbl_gross')
            dct_gross = {}
            int_count = ((dct_pt_period['dat_end'].year - datetime.strptime(str(int_year)+'-'+str(int_month)+'-01', "%Y-%m-%d").year) * 12 + dct_pt_period['dat_end'].month - datetime.strptime(str(int_year)+'-'+str(int_month)+'-01', "%Y-%m-%d").month)+1
            for ins_data in ins_details:
                dct_gross[ins_data['fk_employee_id']] = ins_data['dbl_gross']
            for ins_data in ins_process:
                if dct_gross.get(ins_data['fk_employee_id']):
                    ins_pro_tax = ProfessionalTax.objects.filter(Q(dbl_from_amt__lte=ins_data['dbl_tot_gross']+(dct_gross[ins_data['fk_employee_id']]*int_count), dbl_to_amt = None)| Q(dbl_from_amt=None, dbl_to_amt__gte=ins_data['dbl_tot_gross']+(dct_gross[ins_data['fk_employee_id']]*int_count)) | Q(dbl_from_amt__lte=ins_data['dbl_tot_gross']+(dct_gross[ins_data['fk_employee_id']]*int_count), dbl_to_amt__gte=ins_data['dbl_tot_gross']+(dct_gross[ins_data['fk_employee_id']]*int_count)), fk_period_id = dct_pt_period['pk_bint_id'], bln_active = True).values('dbl_tax').last()
                    dct_pro_tax[ins_data['fk_employee_id']] = round((ins_pro_tax['dbl_tax']-ins_data['dbl_tot_pro_tax'])/((dct_pt_period['dat_deduction'].year - datetime.strptime(str(int_year)+'-'+str(int_month)+'-01', "%Y-%m-%d").year) * 12 + dct_pt_period['dat_deduction'].month - datetime.strptime(str(int_year)+'-'+str(int_month)+'-01', "%Y-%m-%d").month)+1)
        return dct_pro_tax
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
        return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})
