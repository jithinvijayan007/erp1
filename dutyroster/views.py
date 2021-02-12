from django.shortcuts import render
import calendar
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.views import APIView
from dutyroster.models import DutyRoster, WeekoffLeave
from hierarchy.views import get_data
from user_model.models import UserDetails
from django.db.models import F, Q, Case, When, Value, Func, IntegerField, CharField
from django.db.models.functions import Concat, Substr, Cast
from hierarchy.models import HierarchyLevel
from job_position.models import JobPosition
from user_model.models import AdminSettings
from less_hour_deduction.models import LessHourDeduction, LessHourDetails
from HRMS_python import ins_logger
import datetime
import sys, os

class AddWeekOff(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            """To show all date starting from first monday of a month to first monday of second month if weekday exceeded """
            int_month  = request.data.get('intMonth')
            int_year = request.data.get('intYear')
            # int_month = 1
            # int_year =2019
            int_last_day = calendar.monthrange(int_year,int_month)
            #-------------------generating days between first monday and last monday
            dat_first_day = datetime.date(int_year, int_month, 1)
            dat_last_day = datetime.date(int_year, int_month, int_last_day[1])

            if dat_first_day.weekday() == 0:
                dat_first_monday = dat_first_day
            else:
                dat_first_monday = dat_first_day + datetime.timedelta(days=-dat_first_day.weekday(), weeks= 1)

            if dat_last_day.weekday() == 0:
                dat_last_monday = dat_last_day
            else:
                dat_last_monday = dat_last_day + datetime.timedelta(days=-dat_last_day.weekday(), weeks= 1)
            #
            int_dept_id = request.user.userdetails.fk_department_id
            int_desig_id = request.user.userdetails.fk_desig_id

            # int_dept_id = 6
            # int_desig_id = 41
            lst_desig = list(HierarchyLevel.objects.filter(int_status=1, fk_reporting_to_id = int_desig_id,fk_department_id = int_dept_id ).values_list('fk_designation_id',flat = True))

            if request.user.userdetails.fk_desig.vchr_name.upper() =='TERRITORY MANAGER' :
                    lst_desig  = JobPosition.objects.filter(vchr_name__icontains = 'SHOWROOM MANAGER').values_list('pk_bint_id',flat=True)
            lst_phyc_loc =  list(map(int,request.user.userdetails.json_physical_loc))
            lst_employee = list(UserDetails.objects.filter(is_active = True,fk_desig_id__in = lst_desig,fk_department_id = int_dept_id,json_physical_loc__has_any_keys = request.user.userdetails.json_physical_loc).annotate(fullname=Concat('first_name', Value(' '),'vchr_middle_name', Value(' ') ,'last_name'), int_emp_id=Cast(Substr('vchr_employee_code',6), IntegerField())).values('int_emp_id',
                                                                                                                                                                                                                                                                                                                                                              'fullname',
                                                                                                                                                                                                                                                                                                                                                              'fk_desig__vchr_name',
                                                                                                                                                                                                                                                                                                                                                              'fk_branch__vchr_name',
                                                                                                                                                                                                                                                                                                                                                              'fk_branch_id',
                                                                                                                                                                                                                                                                                                                                                              'fk_desig_id',
                                                                                                                                                                                                                                                                                                                                                              'user_ptr_id',
                                                                                                                                                                                                                                                                                                                                                              'vchr_employee_code').order_by('fk_branch_id','fk_desig_id','fullname'))




            # son_physical_loc__has_any_keys
            dct_duty_data = dict(DutyRoster.objects.filter(fk_employee__fk_desig_id__in = lst_desig,int_month = int_month,int_year = int_year,bln_active = True).values_list('fk_employee_id','json_dates'))

            lst_main = []
            for dct_data in lst_employee:
                dct_main = {}
                dct_main['intId'] = dct_data['user_ptr_id']
                dct_main['strName'] = dct_data['fullname']
                dct_main['fk_desig'] = dct_data['fk_desig_id']
                dct_main['designam'] = dct_data['fk_desig__vchr_name']
                dct_main['branch_id'] = dct_data['fk_branch_id']
                dct_main['branch_name'] = dct_data['fk_branch__vchr_name']

                dct_main['lst_dates'] = []
                if (dct_duty_data) and dct_main['intId'] in dct_duty_data.keys():
                    dct_main['lst_dates'] = dct_duty_data[dct_main['intId']]
                dct_main['lst_all_dates'] = []
                dat_temp_first_day = dat_first_monday
                while dat_temp_first_day < dat_last_monday:
                    dct_date = {}
                    dct_date['date'] = dat_temp_first_day
                    dct_date['bln_status'] = False if str(dat_temp_first_day) not in dct_main['lst_dates'] else True
                    dct_date['int_weekday'] = dat_temp_first_day.weekday()
                    dct_main['lst_all_dates'].append(dct_date)
                    dat_temp_first_day += datetime.timedelta(days = 1)
                lst_main.append(dct_main)


            return Response({'status':1,'lst_data':lst_main})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})




    def put(self,request):
        try:
            lst_data = request.data.get('lstData')
            int_employee_id = request.data.get('intEmpId')
            int_month = request.data.get('intMonth')
            int_year = request.data.get('intYear')
            lst_duty_roster = []


            for dct_data in lst_data:
                ins_dup_data = DutyRoster.objects.filter(fk_employee_id = dct_data['intId'],int_month = int_month,int_year = int_year)
                if ins_dup_data:
                    ins_dup_data.update(bln_active = False,fk_updated_id = request.user.id,dat_updated =  datetime.datetime.now())

                if not dct_data['lst_dates']:
                    continue

                ins_dutyroster = DutyRoster(fk_employee_id = dct_data['intId'],
                                            json_dates = dct_data['lst_dates'] ,
                                            int_month = int_month,
                                            int_year = int_year,
                                            bln_active = True,
                                            fk_created_id = request.user.id,
                                            dat_created = datetime.datetime.now())

                lst_duty_roster.append(ins_dutyroster)
            DutyRoster.objects.bulk_create(lst_duty_roster)
            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})

    def patch(self,request):
        try:
            int_dept_id = request.user.userdetails.fk_department_id
            int_desig_id = request.user.userdetails.fk_desig_id
            lst_desig = list(HierarchyLevel.objects.filter(int_status=1, fk_reporting_to_id = int_desig_id ).values_list('fk_designation_id',flat = True))
            int_month = request.data.get('intMonth')
            int_year = request.data.get('intYear')
            lst_data = list(DutyRoster.objects.filter(fk_employee___fk_desig_id__in = lst_desig,int_month = int_month,int_year = int_year,bln_active = True).annotate(fullname=Concat('fk_employee__first_name', Value(' '),'fk_employee__vchr_middle_name', Value(' ') ,'fk_employee__last_name')).values('fk_employee_id',
                                                                                                                                                                                                                                                                                                           'fullname',
                                                                                                                                                                                                                                                                                                           'json_dates',
                                                                                                                                                                                                                                                                                                           'pk_bint_id'))
            return Response({'status':1,'lst_data':lst_data})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


class ViewWeekOff(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            int_dept_id = request.user.userdetails.fk_department_id
            int_desig_id = request.user.userdetails.fk_desig_id
            int_month = request.data.get('intMonth')
            int_year = request.data.get('intYear')


            lst_desig = list(HierarchyLevel.objects.filter(int_status=1, fk_reporting_to_id = int_desig_id,fk_department_id = int_dept_id ).values_list('fk_designation_id',flat = True))
            if request.user.userdetails.fk_desig.vchr_name.upper() =='TERRITORY MANAGER' :
                    lst_desig  = JobPosition.objects.filter(vchr_name__icontains = 'SHOWROOM MANAGER').values_list('pk_bint_id',flat=True)


            #-------------------generating days between first monday and last monday
            int_last_day = calendar.monthrange(int_year,int_month)
            dat_first_day = datetime.date(int_year, int_month, 1)
            dat_last_day = datetime.date(int_year, int_month, int_last_day[1])

            if dat_first_day.weekday() == 0:
                dat_first_monday = dat_first_day
            else:
                dat_first_monday = dat_first_day + datetime.timedelta(days=-dat_first_day.weekday(), weeks= 1)

            if dat_last_day.weekday() == 0:
                dat_last_monday = dat_last_day
            else:
                dat_last_monday = dat_last_day + datetime.timedelta(days=-dat_last_day.weekday(), weeks= 1)

            dct_duty_data = dict(DutyRoster.objects.filter(fk_employee__fk_desig_id__in = lst_desig,int_month = int_month,int_year = int_year,bln_active = True).values_list('fk_employee_id','json_dates'))
            if not dct_duty_data:
                return Response({'status':1,'lst_data':[]})
            lst_employee = list(UserDetails.objects.filter(Q(int_weekoff_type = 1,is_active = True,fk_desig_id__in = lst_desig,fk_department_id = int_dept_id,json_physical_loc__has_any_keys = request.user.userdetails.json_physical_loc)|Q(user_ptr_id = request.user.id )).annotate(fullname=Concat('first_name', Value(' '),'vchr_middle_name', Value(' ') ,'last_name'), int_emp_id=Cast(Substr('vchr_employee_code',6), IntegerField())).values('int_emp_id',
                                                                                                                                                                                                                                                                                                                                                                                 'fullname',
                                                                                                                                                                                                                                                                                                                                                                                 'user_ptr_id',
                                                                                                                                                                                                                                                                                                                                                                                 'vchr_employee_code').exclude(int_weekoff_type = 0).order_by('fk_branch_id','fullname'))

            lst_main = []
            for dct_data in lst_employee:
                dct_main = {}
                dct_main['intId'] = dct_data['user_ptr_id']
                dct_main['strName'] = dct_data['fullname']
                dct_main['lst_dates'] = []
                if dct_main['intId'] in dct_duty_data.keys():
                    dct_main['lst_dates'] = dct_duty_data[dct_main['intId']]
                dct_main['lst_all_dates'] = []
                dat_temp_first_day = dat_first_monday
                while dat_temp_first_day < dat_last_monday:
                    dct_date = {}
                    dct_date['date'] = dat_temp_first_day
                    dct_date['bln_status'] = False if str(dat_temp_first_day) not in dct_main['lst_dates'] else True
                    dct_date['int_weekday'] = dat_temp_first_day.weekday()
                    dct_main['lst_all_dates'].append(dct_date)
                    dat_temp_first_day += datetime.timedelta(days = 1)
                lst_main.append(dct_main)


            return Response({'status':1,'lst_data':lst_main})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


class ListEmployee(APIView):
    permission_classes = [AllowAny]

    def get(self,request):
        try:
            """List Employees"""
            int_dept_id = request.user.userdetails.fk_department_id
            int_desig_id = request.user.userdetails.fk_desig_id
            lst_desig = list(HierarchyLevel.objects.filter(int_status=1, fk_reporting_to_id = int_desig_id ).values_list('fk_designation_id',flat = True))
            # lst_desig = get_data(int_dept_id, int_desig_id, [])


            lst_employee = list(UserDetails.objects.filter(is_active = True,fk_desig_id__in = lst_desig,int_weekoff_type =1).annotate(fullname=Concat('first_name', Value(' '),'vchr_middle_name', Value(' ') ,'last_name'), int_emp_id=Cast(Substr('vchr_employee_code',6), IntegerField())).values('int_emp_id',
                                                                                                                                                                                                                     'fullname','vchr_employee_code',
                                                                                                                                                                                                                     'firstname','last_name',
                                                                                                                                                                                                                     'username','bint_phone',
                                                                                                                                                                                                                     'vchr_email','dat_doj',
                                                                                                                                                                                                                     'dat_dob','vchr_gender',
                                                                                                                                                                                                                     'fk_department__vchr_name',
                                                                                                                                                                                                                     'fk_category__vchr_name',
                                                                                                                                                                                                                     'fk_branch__vchr_name',
                                                                                                                                                                                                                     'fk_brand__vchr_brand_name',
                                                                                                                                                                                                                     'fk_company__vchr_name',
                                                                                                                                                                                                                     'fk_desig__vchr_name','vchr_level',
                                                                                                                                                                                                                     'vchr_grade','user_ptr_id').order_by('-int_emp_id'))

            return Response({'status':1,'lst_employee':lst_employee})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


class WeekoffApprove(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            ins_weekoff = WeekoffLeave.objects.filter(int_status = 2).annotate(intWeekoffId=F('pk_bint_id'),
                                                    strFullName=Concat('fk_employee__first_name', Value(' '),
                                                    Case(When(fk_employee__vchr_middle_name=None, then=F('fk_employee__last_name')),
                                                    default=Concat('fk_employee__vchr_middle_name', Value(' '), 'fk_employee__last_name'),
                                                    output_field=CharField()), output_field=CharField()), strEMPCode=F('fk_employee__vchr_employee_code'),
                                                    datFrom=Func(F('dat_from'), Value('dd-MM-yyyy'), function='to_char', output_field=CharField()),
                                                    datTo=Func(F('dat_to'), Value('dd-MM-yyyy'), function='to_char', output_field=CharField())).values(
                                                    'intWeekoffId', 'strFullName', 'strEMPCode', 'datFrom', 'datTo')
            lst_weekoff = list(ins_weekoff)
            return Response({'status':1,'lst_employee':lst_weekoff})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})

    def post(self, request):
        try:
            if request.data.get('lstId') and request.user.userdetails.fk_department.vchr_name.upper() == 'HR & ADMIN':
                ins_weekoff_leave = WeekoffLeave.objects.filter(pk_bint_id__in=request.data.get('lstId'))
                for ins_weekoff in ins_weekoff_leave:
                    dat_from = ins_weekoff.dat_from
                    while dat_from < ins_weekoff.dat_to + datetime.timedelta(days=1):
                        dur_calendar = calendar.monthrange(dat_from.year, dat_from.month)
                        int_month = dat_from.month
                        int_year = dat_from.year
                        ins_admin = AdminSettings.objects.filter(vchr_code='PAYROLL_PERIOD',bln_enabled=True,fk_company_id=ins_weekoff.fk_employee.fk_company_id).values('vchr_value', 'int_value').first()
                        if ins_admin and ins_admin['int_value'] != 0:
                            if int(ins_admin['vchr_value'][0]) <= dat_from.day:
                                dat_next_month = datetime.datetime.strptime(str(int_year)+'-'+str(int_month)+'-'+str(int(ins_admin['vchr_value'][0])),'%Y-%m-%d')+datetime.timedelta(days=dur_calendar[1]-int(ins_admin['vchr_value'][0])+1)
                                int_month = dat_next_month.month
                                int_year = dat_next_month.year
                        ins_dutyroster = DutyRoster.objects.filter(fk_employee_id = ins_weekoff.fk_employee_id, int_month = int_month, int_year = int_year, bln_active = True)
                        if ins_dutyroster:
                            lst_weekoff = ins_dutyroster.last().json_dates
                            if dat_from.strftime('%Y-%m-%d') not in lst_weekoff:
                                lst_weekoff.append(dat_from.strftime('%Y-%m-%d'))
                                ins_dutyroster.update(json_dates=lst_weekoff)
                        else:
                            DutyRoster.objects.create(fk_employee_id=ins_weekoff.fk_employee_id, json_dates=[dat_from.strftime('%Y-%m-%d')], int_month=int_month, int_year=int_year, bln_active=True, fk_created=request.user, dat_created=datetime.datetime.now())
                        ins_deduction = LessHourDeduction.objects.filter(fk_employee_id=ins_weekoff.fk_employee_id, int_year=int_year, int_month=int_month).first()
                        if ins_deduction:
                            ins_details = LessHourDetails.objects.filter(fk_master_id=ins_deduction.pk_bint_id, dat_less_hour__date=dat_from).first()
                            if ins_details:
                                ins_deduction.dur_time = ins_deduction.dur_time - ins_details.dur_less_hour
                                ins_deduction.save()
                                ins_details.delete()
                        dat_from += datetime.timedelta(days=1)
                ins_weekoff_leave.update(int_status=3, fk_verified_id=request.user.id, dat_verified=datetime.datetime.now())
            else:
                return Response({'status':0,'reason':'Permission Denied', 'message':'Permission Only for H.R department'})
            return Response({'status':1,'message':'successfully verified'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})

    def patch(self, request):
        try:
            if request.data.get('lstId') and request.user.userdetails.fk_department.vchr_name.upper() == 'HR & ADMIN':
                WeekoffLeave.objects.filter(pk_bint_id__in=request.data.get('lstId')).update(int_status=-1, fk_verified_id=request.user.id, dat_verified=datetime.datetime.now())
            else:
                return Response({'status':0,'reason':'Permission Denied', 'message':'Permission Only for H.R department'})
            return Response({'status':1,'message':'Successfully Rejected'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})
