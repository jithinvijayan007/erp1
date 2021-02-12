from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models.fields import BooleanField
from hierarchy.models import *
from userdetails.models import UserDetails
import sys, os
from django.db.models import Q, F, Case, When, BooleanField
from POS import ins_logger
import traceback
from django.db.models.functions import Concat
from django.db.models import F, Q, Value, Case, When, IntegerField, CharField, DateField,BooleanField, Count, ExpressionWrapper, Func
from datetime import datetime, date, timedelta
from os import path
from django.conf import settings
import pandas as pd
# Create your views here.


def get_data(int_department_id, int_designation_id,lst_data=[]):
    ins_hierarchy = HierarchyLevel.objects.filter(int_status=1, fk_department_id = int_department_id, fk_reporting_to=int_designation_id).values('fk_designation_id')
    for int_desig_id in ins_hierarchy:
        lst_data.append(int_desig_id['fk_designation_id'])
        get_data(int_department_id, int_desig_id['fk_designation_id'],lst_data)
    return lst_data

def get_hierarchy(lst_department,int_designation_id,lst_mode=[0,1,2],lst_data=[]):
    if lst_department:
        ins_hierarchy = HierarchyLevel.objects.filter(int_status=1, fk_department_id__in=lst_department, fk_reporting_to=int_designation_id,int_mode__in=lst_mode).values('fk_designation_id')
    else:
        ins_hierarchy = HierarchyLevel.objects.filter(int_status=1, fk_reporting_to=int_designation_id,int_mode__in=lst_mode).values('fk_designation_id')
    for int_desig_id in ins_hierarchy:
        lst_data.append(int_desig_id['fk_designation_id'])
        get_hierarchy(lst_department,int_desig_id['fk_designation_id'],lst_mode,lst_data)
    return lst_data


class ReportingHierarchy(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            int_dept_id = request.GET.get('intDeptId')
            int_hirarchy_id = request.GET.get('intHierarchyId')
            if int_dept_id:
                ins_hierarchy = HierarchyLevel.objects.filter(fk_department_id = int_dept_id, int_status = 1).annotate(intId = F('pk_bint_id'), strDepartment = F('fk_department__vchr_name'), strDesignation = F('fk_designation__vchr_name'), strReportingTo = F('fk_reporting_to__vchr_name'), blnAttendance = Case(When(Q(int_mode = 0)|Q(int_mode = 1), then=True), default = False, output_field=BooleanField()), blnOthers = Case(When(Q(int_mode = 0)|Q(int_mode = 2), then=True), default = False, output_field=BooleanField())).values('intId', 'strDepartment', 'strDesignation', 'strReportingTo', 'blnAttendance', 'blnOthers')
            elif int_hirarchy_id:
                ins_hierarchy = HierarchyLevel.objects.filter(pk_bint_id = int_hirarchy_id).annotate(intHierarchyId = F('pk_bint_id'), intDeptId = F('fk_department_id'), strDepartment = F('fk_department__vchr_name'), intDesigId = F('fk_designation_id'), strDesignation = F('fk_designation__vchr_name'), intReportingId = F('fk_reporting_to_id'), strReportingTo = F('fk_reporting_to__vchr_name'), blnAttendance = Case(When(Q(int_mode = 0)|Q(int_mode = 1), then=True), default = False, output_field=BooleanField()), blnOthers = Case(When(Q(int_mode = 0)|Q(int_mode = 2), then=True), default = False, output_field=BooleanField())).values('intHierarchyId', 'intDeptId', 'intDesigId', 'intReportingId', 'strDepartment', 'strDesignation', 'strReportingTo', 'blnAttendance', 'blnOthers')

            return Response({'status':1, 'data':ins_hierarchy})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


    def post(self, request):
        try:
            int_dept_id = request.data.get('intDeptId')
            int_desig_id = request.data.get('intDesigId')
            int_report_to_id = request.data.get('intReportToId')
            int_mode = 0
            if request.data.get('blnAttendance') and not request.data.get('blnOthers'):
                int_mode = 1
            elif not request.data.get('blnAttendance') and request.data.get('blnOthers'):
                int_mode = 2

            if HierarchyLevel.objects.filter(fk_department_id = int_dept_id, fk_designation_id = int_desig_id, fk_reporting_to_id = int_report_to_id, int_mode__in = [0, int_mode], int_status = 1):
                return Response({'status':0, 'reason':'Already Exist'})
            else:
                HierarchyLevel.objects.create(fk_department_id = int_dept_id, fk_designation_id = int_desig_id, fk_reporting_to_id = int_report_to_id, int_mode = int_mode, fk_created_id = request.user.id)
            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


    def patch(self, request):
        try:
            int_hierarchy_id = request.data.get('intHierarchyId')
            int_dept_id = request.data.get('intDeptId')
            int_desig_id = request.data.get('intDesigId')
            int_report_to_id = request.data.get('intReportToId')
            int_report_to_id = request.data.get('intReportToId')
            int_mode = 0
            if request.data.get('blnAttendance') and not request.data.get('blnOthers'):
                int_mode = 1
            elif not request.data.get('blnAttendance') and request.data.get('blnOthers'):
                int_mode = 2
            if HierarchyLevel.objects.filter(fk_department_id = int_dept_id, fk_designation_id = int_desig_id, fk_reporting_to_id = int_report_to_id, int_mode__in = [0, int_mode], int_status = 1).exclude(pk_bint_id=int_hierarchy_id):
                return Response({'status':0, 'reason':'Already Exist or No Changes'})
            else:
                HierarchyLevel.objects.filter(pk_bint_id = int_hierarchy_id).update(fk_department_id = int_dept_id, fk_designation_id = int_desig_id, fk_reporting_to_id = int_report_to_id, int_mode = int_mode, fk_updated_id = request.user.id)
            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


    def put(self, request):
        try:
            int_hierarchy_id = request.data.get('intHierarchyId')
            HierarchyLevel.objects.filter(pk_bint_id = int_hierarchy_id).update(int_status=0)
            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})

class HierarchyReport(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            lst_data = []
            int_desgn_id = request.data.get('intDesigId')
            int_mode = request.data.get('blnMode')
            if request.data.get('intDesigId'):
                ins_hierarchy = HierarchyLevel.objects.filter(fk_designation_id = int_desgn_id, int_status = 1).values('fk_reporting_to_id','fk_reporting_to__vchr_name','fk_designation__vchr_name').first()
                while 1:
                    if ins_hierarchy:
                        dct_data = {}
                        dct_data['strDesignation'] = ins_hierarchy['fk_designation__vchr_name']
                        dct_data['strReportingToDesig'] = ins_hierarchy['fk_reporting_to__vchr_name']
                        lst_data.append(dct_data)
                        int_hierarchy_id = ins_hierarchy['fk_reporting_to_id']
                        ins_hierarchy = HierarchyLevel.objects.filter(fk_designation_id = int_hierarchy_id, int_status = 1).values('fk_reporting_to_id','fk_reporting_to__vchr_name','fk_designation__vchr_name').first()
                    else:
                        break
                file_name = 'HierarchyLevelReport/Hierarchy_Level_Report' + datetime.strftime(date.today(), "%d-%m-%Y") + '.xlsx'
                if path.exists(file_name):
                    os.remove(file_name)
                if not path.exists(settings.MEDIA_ROOT + '/HierarchyLevelReport/'):
                    os.mkdir(settings.MEDIA_ROOT + '/HierarchyLevelReport/')
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
                worksheet.autofilter('B2:C2')
                row_style = workbook.add_format({'font_size':11})
                row_style.set_align('vcenter')
                worksheet.protect('',{'autofilter':True})

                int_row = 1
                worksheet.write(int_row, 0, 'SL. No', head_style); worksheet.set_column(0, 0, 6)
                worksheet.write(int_row, 1, 'Designation', head_style); worksheet.set_column(1, 1, 35)
                worksheet.write(int_row, 2, 'ReportingTo Designation', head_style); worksheet.set_column(2, 2, 35)
                worksheet.set_row(int_row, 33)

                for ins_data in lst_data:
                    int_row += 1
                    worksheet.write(int_row, 0, int_row-1, row_style)
                    worksheet.write(int_row, 1, ins_data.get('strDesignation'), row_style)
                    worksheet.write(int_row, 2, ins_data.get('strReportingToDesig'), row_style)
                    worksheet.set_row(int_row, 25, row_style)
                writer.save()

            else:
                int_emp_id = request.data.get('intEMPId')
                ins_emp_desgn = UserDetails.objects.filter(user_ptr_id = int_emp_id).annotate(strFullName=Concat('first_name', Value(' '), Case(When(vchr_middle_name = None, then=F('last_name')), default=Concat('vchr_middle_name', Value(' '), 'last_name'), output_field = CharField()), output_field = CharField())).values('fk_desig_id','json_physical_loc','int_hierarchy_type','strFullName').first()
                if ins_emp_desgn['fk_desig_id']:
                    ins_hierarchy = HierarchyLevel.objects.filter(fk_designation_id = ins_emp_desgn['fk_desig_id'], int_status = 1).values('fk_reporting_to_id','fk_reporting_to__vchr_name','fk_designation__vchr_name').first()
                    if ins_emp_desgn['int_hierarchy_type'] in (2,3):
                        ins_user = UserDetails.objects.filter(fk_desig_id = ins_hierarchy['fk_reporting_to_id'],is_active = True).annotate(strFullName=Concat('first_name', Value(' '), Case(When(vchr_middle_name = None, then=F('last_name')), default=Concat('vchr_middle_name', Value(' '), 'last_name'), output_field = CharField()), output_field = CharField())).values('strFullName','user_ptr_id')
                    else:
                        ins_user = UserDetails.objects.filter(fk_desig_id = ins_hierarchy['fk_reporting_to_id'],json_physical_loc__has_any_keys = ins_emp_desgn['json_physical_loc'],is_active = True).annotate(strFullName=Concat('first_name', Value(' '), Case(When(vchr_middle_name = None, then=F('last_name')), default=Concat('vchr_middle_name', Value(' '), 'last_name'), output_field = CharField()), output_field = CharField())).values('strFullName','user_ptr_id')
                    while 1:
                        if ins_hierarchy:
                            dct_data = {}
                            dct_data['strDesignation'] = ins_hierarchy['fk_designation__vchr_name']
                            dct_data['strName'] = ins_emp_desgn['strFullName']
                            dct_data['strReportingToDesig'] = ins_hierarchy['fk_reporting_to__vchr_name']
                            lst_degn = []
                            for data in ins_user:
                                lst_degn.append(data['strFullName'])
                            dct_data['lstReporting'] = lst_degn
                            lst_data.append(dct_data)
                            if ins_user:
                                ins_emp_desgn = UserDetails.objects.filter(user_ptr_id = ins_user[0]['user_ptr_id']).annotate(strFullName=Concat('first_name', Value(' '), Case(When(vchr_middle_name = None, then=F('last_name')), default=Concat('vchr_middle_name', Value(' '), 'last_name'), output_field = CharField()), output_field = CharField())).values('fk_desig_id','json_physical_loc','int_hierarchy_type','strFullName').first()
                                ins_hierarchy = HierarchyLevel.objects.filter(fk_designation_id = ins_emp_desgn['fk_desig_id'], int_status = 1).values('fk_reporting_to_id','fk_reporting_to__vchr_name','fk_designation__vchr_name').first()
                                if ins_hierarchy:
                                    if ins_emp_desgn['int_hierarchy_type'] in (2,3):
                                        ins_user = UserDetails.objects.filter(fk_desig_id = ins_hierarchy['fk_reporting_to_id'],is_active = True).annotate(strFullName=Concat('first_name', Value(' '), Case(When(vchr_middle_name = None, then=F('last_name')), default=Concat('vchr_middle_name', Value(' '), 'last_name'), output_field = CharField()), output_field = CharField())).values('strFullName','user_ptr_id')
                                    else:
                                        ins_user = UserDetails.objects.filter(fk_desig_id = ins_hierarchy['fk_reporting_to_id'],json_physical_loc__has_any_keys = ins_emp_desgn['json_physical_loc'],is_active = True).annotate(strFullName=Concat('first_name', Value(' '), Case(When(vchr_middle_name = None, then=F('last_name')), default=Concat('vchr_middle_name', Value(' '), 'last_name'), output_field = CharField()), output_field = CharField())).values('strFullName','user_ptr_id')
                            else:

                                ins_hierarchy = HierarchyLevel.objects.filter(fk_designation_id = ins_hierarchy['fk_reporting_to_id'], int_status = 1).values('fk_reporting_to_id','fk_reporting_to__vchr_name','fk_designation__vchr_name').first()
                                if ins_hierarchy:
                                    if ins_emp_desgn['int_hierarchy_type'] in (2,3):
                                        ins_user = UserDetails.objects.filter(fk_desig_id = ins_hierarchy['fk_reporting_to_id'],is_active = True).annotate(strFullName=Concat('first_name', Value(' '), Case(When(vchr_middle_name = None, then=F('last_name')), default=Concat('vchr_middle_name', Value(' '), 'last_name'), output_field = CharField()), output_field = CharField())).values('strFullName','user_ptr_id')
                                    else:
                                        ins_user = UserDetails.objects.filter(fk_desig_id = ins_hierarchy['fk_reporting_to_id'],json_physical_loc__has_any_keys = ins_emp_desgn['json_physical_loc'],is_active = True).annotate(strFullName=Concat('first_name', Value(' '), Case(When(vchr_middle_name = None, then=F('last_name')), default=Concat('vchr_middle_name', Value(' '), 'last_name'), output_field = CharField()), output_field = CharField())).values('strFullName','user_ptr_id')
                            ins_emp_desgn['strFullName'] = lst_degn
                        else:
                            break
                    else:
                        return Response({'status':1,'lstData':lst_data})

                file_name = 'HierarchyLevelReport/Hierarchy_Level_Report' + datetime.strftime(date.today(), "%d-%m-%Y") + '.xlsx'
                if path.exists(file_name):
                    os.remove(file_name)
                if not path.exists(settings.MEDIA_ROOT + '/HierarchyLevelReport/'):
                    os.mkdir(settings.MEDIA_ROOT + '/HierarchyLevelReport/')
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
                worksheet.autofilter('B2:C2')
                row_style = workbook.add_format({'font_size':11})
                row_style.set_align('vcenter')
                worksheet.protect('',{'autofilter':True})

                int_row = 1
                worksheet.write(int_row, 0, 'SL. No', head_style); worksheet.set_column(0, 0, 6)
                worksheet.write(int_row, 1, 'Employee Name', head_style); worksheet.set_column(1, 1, 20)
                worksheet.write(int_row, 2, 'Designation', head_style); worksheet.set_column(2, 2, 35)
                worksheet.write(int_row, 3, 'ReportingTo Name', head_style); worksheet.set_column(3, 3, 35)
                worksheet.write(int_row, 4, 'ReportingTo Designation', head_style); worksheet.set_column(4, 4, 35)

                worksheet.set_row(int_row, 33)
                for ins_data in lst_data:
                    int_row += 1
                    worksheet.write(int_row, 0, int_row-1, row_style)
                    if type(ins_data.get('strName')) is str:
                        worksheet.write(int_row, 1, ins_data.get('strName'), row_style)
                    else:
                        sent_str = ""
                        for i in ins_data.get('strName'):
                            if sent_str:
                                sent_str += " , " + str(i)
                            else:
                                sent_str += str(i)
                        sent_str = sent_str[:-1]
                        worksheet.write(int_row, 1, sent_str, row_style)
                    worksheet.write(int_row, 2, ins_data.get('strDesignation'), row_style)
                    sent_str = ""
                    for i in ins_data.get('lstReporting'):
                        if sent_str:
                            sent_str += " , " + str(i)
                        else:
                            sent_str += str(i)
                    sent_str = sent_str[:-1]
                    worksheet.write(int_row, 3, sent_str, row_style)
                    worksheet.write(int_row, 4, ins_data.get('strReportingToDesig'), row_style)
                    worksheet.set_row(int_row, 25, row_style)

                writer.save()
            return Response({'status':1,'lstData':lst_data,'report':request.scheme+'://'+request.get_host()+settings.MEDIA_URL+file_name})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})
