from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from shift_schedule.models import ShiftSchedule, ShiftExemption
from django.db.models import Q, F, Value, Sum , Case, When, CharField, Func, IntegerField,CharField
from django.db.models.functions import Concat, Cast, Substr
from django.contrib.postgres.fields.jsonb import KeyTransform
from userdetails.models import UserDetails
from department.models import Department
from branch.models import Branch
from job_position.models import JobPosition
from datetime import datetime, date, timedelta
from POS import ins_logger
import traceback
import sys, os
# Create your views here.

class AddShift(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        try:
            """Add shift"""
            if request.data.get('strTimeShiftRangeType') == 'monthly':
                int_type = 1
            elif request.data.get('strTimeShiftRangeType') == 'weekly':
                int_type = 2
            else:
                int_type = 0
            if request.data.get('blnTimeShift') == True:
                time_fllday = timedelta(hours=request.data.get('timeFullDay'))
            else:
                time_fllday = request.data.get('timeFullDay')
            ins_shift = ShiftSchedule.objects.create(vchr_name = request.data.get('strName'),
                                                    vchr_code = request.data.get('strCode'),
                                                    bln_night = request.data.get('blnNight'),
                                                    time_shift_from = request.data.get('timeShiftfrom'),
                                                    time_shift_to = request.data.get('timeShiftTo'),
                                                    time_break_from = request.data.get('timeBreakFrom'),
                                                    time_break_to = request.data.get('timeBreakTo'),
                                                    time_break_hrs = request.data.get('timeBreakHrs'),
                                                    time_shed_hrs = request.data.get('timeShedHrs'),
                                                    time_full_day = time_fllday,
                                                    time_half_day = request.data.get('timeHalfDay'),
                                                    bln_allowance = request.data.get('blnAllowance'),
                                                    dbl_allowance_amt = request.data.get('dblAllowance'),
                                                    vchr_remark = request.data.get('strRemark'),
                                                    int_status = 1,
                                                    fk_created_id =request.user.id,
                                                    dat_created = datetime.now(),
                                                    bln_time_shift = request.data.get('blnTimeShift'),
                                                    int_shift_type = int_type)

            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})

    def put(self,request):
        try:
            """Update Shift"""
            if request.data.get('strTimeShiftRangeType') == 'monthly':
                int_type = 1
            elif request.data.get('strTimeShiftRangeType') == 'weekly':
                int_type = 2
            else:
                int_type = 0
            if request.data.get('blnTimeShift') == True:
                time_fllday = timedelta(hours=request.data.get('timeFullDay'))
            else:
                time_fllday = request.data.get('timeFullDay')
            ins_shift = ShiftSchedule.objects.filter(pk_bint_id = int(request.data.get("intId"))).update(vchr_name = request.data.get('strName'),
                                                                                                        vchr_code = request.data.get('strCode'),
                                                                                                        bln_night = request.data.get('blnNight'),
                                                                                                        time_shift_from = request.data.get('timeShiftfrom'),
                                                                                                        time_shift_to = request.data.get('timeShiftTo'),
                                                                                                        time_break_from = request.data.get('timeBreakFrom'),
                                                                                                        time_break_to = request.data.get('timeBreakTo'),
                                                                                                        time_break_hrs = request.data.get('timeBreakHrs'),
                                                                                                        time_shed_hrs = request.data.get('timeShedHrs'),
                                                                                                        time_full_day = time_fllday,
                                                                                                        time_half_day = request.data.get('timeHalfDay'),
                                                                                                        bln_allowance = request.data.get('blnAllowance'),
                                                                                                        dbl_allowance_amt = request.data.get('dblAllowance'),
                                                                                                        vchr_remark = request.data.get('strRemark'),
                                                                                                        fk_updated_id = request.user.id,
                                                                                                        dat_updated = datetime.now(),
                                                                                                        bln_time_shift = request.data.get('blnTimeShift'),
                                                                                                        int_shift_type = int_type)

            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})

    def get(self,request):
        pass
        try:
            """View shift"""
            int_id = request.GET.get('id')
            lst_shift_shedule =  list(ShiftSchedule.objects.filter(pk_bint_id = int_id).annotate(str_shift_type = Case(When(Q(int_shift_type = 0), then = Value('daily')), When(Q(int_shift_type = 1), then = Value('weekly')),When(Q(int_shift_type = 2), then = Value('monthly')), output_field = CharField())).values('vchr_name','vchr_code',
                                                                                        'bln_night','time_shift_from',
                                                                                        'time_shift_to','time_break_from',
                                                                                        'time_break_to','time_break_hrs',
                                                                                        'time_shed_hrs','time_full_day',
                                                                                        'time_half_day','bln_allowance',
                                                                                        'dbl_allowance_amt','vchr_remark',
                                                                                        'dat_created','pk_bint_id','bln_time_shift','str_shift_type'))

            lst_data = []
            for data in lst_shift_shedule:
                dct_data = {}
                dct_data['vchr_name'] = data['vchr_name']
                dct_data['vchr_code'] = data['vchr_code']
                dct_data['bln_night'] = data['bln_night']
                dct_data['time_shift_from'] = data['time_shift_from']
                dct_data['time_shift_to'] = data['time_shift_to']
                dct_data['time_break_from'] = data['time_break_from']
                dct_data['time_break_to'] = data['time_break_to']
                if data['time_break_hrs']:
                    dct_data['time_break_hrs'] = str(int(data['time_break_hrs'].total_seconds()//3600)).zfill(2) + ':' +str((data['time_break_hrs'].seconds//60)%60).zfill(2)
                if data['time_shed_hrs']:
                    dct_data['time_shed_hrs'] = str(int(data['time_shed_hrs'].total_seconds()//3600)).zfill(2) + ':' +str((data['time_shed_hrs'].seconds//60)%60).zfill(2)
                if data['time_half_day']:
                    dct_data['time_half_day'] = str(int(data['time_half_day'].total_seconds()//3600)).zfill(2) + ':' +str((data['time_half_day'].seconds//60)%60).zfill(2)
                dct_data['bln_allowance'] = data['bln_allowance']
                dct_data['dbl_allowance_amt'] = data['dbl_allowance_amt']
                dct_data['vchr_remark'] = data['vchr_remark']
                dct_data['dat_created'] = data['dat_created']
                dct_data['bln_time_shift'] = data['bln_time_shift']
                dct_data['str_shift_type'] = data['str_shift_type']
                dct_data['pk_bint_id'] = data['pk_bint_id']
                if data['time_full_day']:
                    dct_data['time_full_day'] = str(int(data['time_full_day'].total_seconds()//3600)).zfill(2) + ':' +str((data['time_full_day'].seconds//60)%60).zfill(2)
                lst_data.append(dct_data)
            return Response({'status':1,'lst_shift_shedule':lst_data})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})
    def patch(self,request):
        pass
        try:
            """View shift"""
            int_id = request.data.get('id')
            ins_shift_shedule =  ShiftSchedule.objects.filter(pk_bint_id = int_id).update(int_status = -1)

            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


class ListShift(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            """List shift"""
            ins_shift_shedule =  ShiftSchedule.objects.filter(int_status = 1).values('vchr_name','vchr_code',
                                                                                        'bln_night','time_shift_from',
                                                                                        'time_shift_to','time_break_from',
                                                                                        'time_break_to','time_break_hrs',
                                                                                        'time_shed_hrs','time_full_day',
                                                                                        'time_half_day','bln_allowance',
                                                                                        'dbl_allowance_amt','vchr_remark',
                                                                                        'dat_created','pk_bint_id','bln_time_shift').order_by('-pk_bint_id')


            lst_data = []
            for data in ins_shift_shedule:
                dct_data = {}
                dct_data['vchr_name'] = data['vchr_name']
                dct_data['vchr_code'] = data['vchr_code']
                dct_data['bln_night'] = data['bln_night']
                dct_data['time_shift_from'] = data['time_shift_from']
                dct_data['time_shift_to'] = data['time_shift_to']
                dct_data['time_break_from'] = data['time_break_from']
                dct_data['time_break_to'] = data['time_break_to']
                if data['time_break_hrs']:
                    dct_data['time_break_hrs'] = str(int(data['time_break_hrs'].total_seconds()//3600)).zfill(2) + ':' +str((data['time_break_hrs'].seconds//60)%60).zfill(2)
                if data['bln_time_shift'] == True:
                    dct_data['time_shed_hrs'] = str(int(data['time_full_day'].total_seconds()//3600)).zfill(2) + ':' +str((data['time_full_day'].seconds//60)%60).zfill(2)
                else:
                    dct_data['time_shed_hrs'] = str(int(data['time_shed_hrs'].total_seconds()//3600)).zfill(2) + ':' +str((data['time_shed_hrs'].seconds//60)%60).zfill(2)
                if data['time_half_day']:
                    dct_data['time_half_day'] = str(int(data['time_half_day'].total_seconds()//3600)).zfill(2) + ':' +str((data['time_half_day'].seconds//60)%60).zfill(2)
                dct_data['bln_allowance'] = data['bln_allowance']
                dct_data['dbl_allowance_amt'] = data['dbl_allowance_amt']
                dct_data['vchr_remark'] = data['vchr_remark']
                dct_data['dat_created'] = data['dat_created']
                dct_data['pk_bint_id'] = data['pk_bint_id']
                lst_data.append(dct_data)
            return Response({'status':1,'lst_shift_shedule':lst_data})
            # lst_shift_shedule = list(ins_shift_shedule)
            #
            # return Response({'status':1,'lst_shift_shedule' :lst_shift_shedule})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


class ShiftExemptionAPI(APIView):
    def post(self,request):
        try:
            date_from = request.data.get('datFrom')
            date_to = request.data.get('datTo')
            date_start_obj = datetime.strptime(date_from, '%Y-%m-%d')
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            int_type = None
            if request.data.get('strType') == 'Individual':
                int_type = 0
            elif request.data.get('strType') == 'Department':
                int_type = 1
            elif request.data.get('strType') == 'Designation':
                int_type = 2
            elif request.data.get('strType') == 'Branch':
                int_type = 3
            ins_user_data = UserDetails.objects.annotate(full_name=Concat('first_name', Value(' '),
                                        Case(When(vchr_middle_name = None, then=F('last_name')),
                                        default=Concat('vchr_middle_name', Value(' '), 'last_name'),
                                        output_field = CharField()), output_field = CharField()),
                                        int_emp_id=Cast(Substr('vchr_employee_code',6), IntegerField())).filter(is_active=True).values(
                                        'id','username','full_name','vchr_employee_code','fk_department_id','fk_branch_id',
                                        'fk_desig_id','fk_department__vchr_name','fk_branch__vchr_name','fk_desig__vchr_name')
            if request.data.get('lstDeptId'):
                ins_user_data = ins_user_data.filter(fk_department_id__in = request.data.get('lstDeptId'))
            if request.data.get('lstDesigId'):
                ins_user_data = ins_user_data.filter(fk_desig_id__in = request.data.get('lstDesigId'))
            if request.data.get('lstBranchId'):
                ins_user_data = ins_user_data.filter(fk_branch_id__in = request.data.get('lstBranchId'))
            if request.data.get('lstEmpId'):
                ins_user_data = ins_user_data.filter(user_ptr_id__in = request.data.get('lstEmpId'))
            lst_department = list(ins_user_data.values_list('fk_department_id', flat = True).distinct())
            lst_desig = list(ins_user_data.values_list('fk_desig_id', flat = True).distinct())
            lst_branch = list(ins_user_data.values_list('fk_branch_id', flat = True).distinct())
            lst_usr_ids = list(ins_user_data.values_list('user_ptr_id', flat = True))

            ins_exemption =  ShiftExemption.objects.annotate(int_type_mode = KeyTransform('int_type', 'json_type_ids'),
                                lst_type_ids = KeyTransform('lst_type_ids', 'json_type_ids'),
                                lst_emp_ids = KeyTransform('lst_emp_id', 'json_type_ids'),
                                int_punch_mode = KeyTransform('int_type', 'json_punch_emps'),
                                int_punch_ids = KeyTransform('lst_type_ids', 'json_punch_emps'),
                                int_punch_emp_ids = KeyTransform('lst_emp_id', 'json_punch_emps'),
                                int_exclude_type = KeyTransform('int_type', 'json_exclude'),
                                lst_exclude_type = KeyTransform('lst_type', 'json_exclude'),
                                lst_exclude_day_type = KeyTransform('lst_day_type', 'json_exclude')).filter(
                                Q(int_type = 0, lst_type_ids__has_any_keys = lst_usr_ids) | Q(
                                int_type__in = [1,2,3], int_type_mode = 1, lst_emp_ids__has_any_keys = lst_usr_ids) | Q(
                                int_type = 1, int_type_mode = 0, lst_type_ids__has_any_keys = lst_department) | Q(
                                int_type = 2, int_type_mode = 0, lst_type_ids__has_any_keys = lst_desig) | Q(
                                int_type = 3, int_type_mode = 0, lst_type_ids__has_any_keys = lst_branch),
                                dat_start__lte = date_to_obj, dat_end__gte = date_start_obj,int_status = 1).values('int_type', 'int_type_mode', 'lst_type_ids', 'lst_emp_ids')
            lst_user_ids = []
            if ins_exemption:
                for ins_data in ins_exemption:
                    if ins_data['int_type'] == 0 or ins_data['int_type_mode'] == 1:
                        lst_user_ids.extend([int(int_id) for int_id in ins_data['lst_emp_ids']])
                    elif ins_data['int_type'] == 1:
                        lst_user_ids.extend(list(UserDetails.objects.filter(is_active = True, fk_department_id__in = ins_data['lst_type_ids']).values_list('user_ptr_id', flat = True)))
                    elif ins_data['int_type'] == 2:
                        lst_user_ids.extend(list(UserDetails.objects.filter(is_active = True, fk_desig_id__in = ins_data['lst_type_ids']).values_list('user_ptr_id', flat = True)))
                    elif ins_data['int_type'] == 3:
                        lst_user_ids.extend(list(UserDetails.objects.filter(is_active = True, fk_branch_id__in = ins_data['lst_type_ids']).values_list('user_ptr_id', flat = True)))
            json_emp_id = list(set(lst_user_ids))
            lst_user = []
            lst_exempt_id =[]
            for ins_data in ins_user_data.order_by('int_emp_id'):
                dct_data = {}
                if ins_data['id'] in json_emp_id:
                    dct_data['blnChecked'] = True
                    lst_exempt_id.append(ins_data['id'])
                else:
                    dct_data['blnChecked'] = False
                dct_data['intId'] = ins_data['id']
                dct_data['strUserCode'] = ins_data['username'].upper()
                dct_data['strEMPCode'] = ins_data['vchr_employee_code'].upper()
                dct_data['strUserName'] = ins_data['full_name'].title()
                dct_data['intDeptId'] = ins_data['fk_department_id']
                dct_data['strDptName'] =  ins_data['fk_department__vchr_name']
                dct_data['intBranchId'] = ins_data['fk_branch_id']
                dct_data['strBranchName'] = ins_data['fk_branch__vchr_name']
                dct_data['intDesigId'] = ins_data['fk_desig_id']
                dct_data['strDesgName'] = ins_data['fk_desig__vchr_name']
                lst_user.append(dct_data)
            return Response({'status':1,'data':lst_user,'lst_exempt_id':lst_exempt_id})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})

    def put(self,request):
         try:
            date_from = request.data.get('datFrom')
            date_to = request.data.get('datTo')
            date_start_obj = datetime.strptime(date_from, '%Y-%m-%d')
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            lst_ids = []
            if request.data.get('strType') == 'Individual':
                int_type_id = 0
                lst_ids = [str(int_id) for int_id in request.data.get('lstExemptEmpId')]
            elif request.data.get('strType') == 'Department':
                int_type_id = 1
                lst_ids = request.data.get('lstDeptId')
            elif request.data.get('strType') == 'Designation':
                int_type_id = 2
                lst_ids = request.data.get('lstDesigId')
            elif request.data.get('strType') == 'Branch':
                int_type_id = 3
                lst_ids = request.data.get('lstBranchId')
            lst_exemptemp_id = [str(int_id) for int_id in request.data.get('lstExemptEmpId')]
            lst_exempted_id = [str(int_id) for int_id in request.data.get('lstExemptedEmpId')]
            ins_exemped_usrs = UserDetails.objects.filter(user_ptr_id__in = lst_exempted_id)
            lst_exempt_dept = list(ins_exemped_usrs.values_list('fk_department_id', flat = True).distinct())
            lst_exempt_desig = list(ins_exemped_usrs.values_list('fk_desig_id', flat = True).distinct())
            lst_exempt_branch = list(ins_exemped_usrs.values_list('fk_branch_id', flat = True).distinct())
            if not request.data.get('blnAllChecked') or int_type_id == 0:
                lst_usr_ids = request.data.get('lstExemptEmpId')
            elif request.data.get('blnAllChecked') and int_type_id == 1:
                lst_usr_ids = list(UserDetails.objects.filter(fk_department_id__in = lst_ids, is_active = True).exclude(user_ptr_id__in = lst_exempted_id).values_list('user_ptr_id',flat = True))
            elif request.data.get('blnAllChecked') and int_type_id == 2:
                lst_usr_ids = list(UserDetails.objects.filter(fk_desig_id__in = lst_ids, is_active = True).exclude(user_ptr_id__in = lst_exempted_id).values_list('user_ptr_id',flat = True))
            elif request.data.get('blnAllChecked') and int_type_id == 3:
                lst_usr_ids = list(UserDetails.objects.filter(fk_branch_id__in = lst_ids, is_active = True).exclude(user_ptr_id__in = lst_exempted_id).values_list('user_ptr_id',flat = True))
            ins_exemption =  ShiftExemption.objects.annotate(int_type_mode = KeyTransform('int_type', 'json_type_ids'),
                                lst_type_ids = KeyTransform('lst_type_ids', 'json_type_ids'),
                                lst_emp_ids = KeyTransform('lst_emp_id', 'json_type_ids'),
                                lst_exclude_ids = KeyTransform('lst_exclude_ids', 'json_type_ids'),
                                int_punch_mode = KeyTransform('int_type', 'json_punch_emps'),
                                int_punch_ids = KeyTransform('lst_type_ids', 'json_punch_emps'),
                                int_punch_emp_ids = KeyTransform('lst_emp_id', 'json_punch_emps'),
                                int_exclude_type = KeyTransform('int_type', 'json_exclude'),
                                lst_exclude_type = KeyTransform('lst_type', 'json_exclude'),
                                lst_exclude_day_type = KeyTransform('lst_day_type', 'json_exclude')).filter(
                                Q(int_type = int_type_id, int_type_mode = 0, lst_type_ids__has_any_keys = lst_ids) |
                                Q(int_type = int_type_id, int_type_mode = 1, lst_emp_ids__has_any_keys = lst_usr_ids),
                                dat_start__lte = date_to_obj, dat_end__gte = date_start_obj,int_status = 1).exclude(
                                Q(lst_exclude_ids__has_any_keys = lst_exempted_id) |
                                Q(int_type = 1, int_type_mode = 0, lst_type_ids__has_any_keys = lst_exempt_dept) |
                                Q(int_type = 2, int_type_mode = 0, lst_type_ids__has_any_keys = lst_exempt_desig) |
                                Q(int_type = 3, int_type_mode = 0, lst_type_ids__has_any_keys = lst_exempt_branch))
            if ins_exemption:
                return Response({'status':0,'message':'Already shift exempted for some employees'})

            type_ids = {'int_type':0, 'lst_type_ids':[], 'lst_emp_id':[], 'lst_exclude_ids':[]}
            if request.data.get('blnAllChecked') == True and int_type_id != 0:
                type_ids['int_type'] = 0
                type_ids['lst_type_ids'] = lst_ids
                type_ids['lst_emp_id'] = []
                if lst_exempted_id:
                    type_ids['lst_exclude_ids'] = lst_exempted_id
            else:
                type_ids['int_type'] = 1
                type_ids['lst_type_ids'] = lst_ids
                type_ids['lst_emp_id'] = lst_exemptemp_id

            punch_emp = {'int_type':0, 'lst_type_ids':[], 'lst_emp_id':[], 'lst_exclude_ids':[]}
            if request.data.get('blnAllChecked') == True and int_type_id != 0:
                punch_emp['int_type'] = 0
                punch_emp['lst_type_ids'] = lst_ids
                punch_emp['lst_emp_id'] = []
                punch_emp['lst_exclude_ids'] = []
                if lst_exempted_id:
                    punch_emp['lst_exclude_ids'] = lst_exempted_id
            else:
                punch_emp['int_type'] = 1
                punch_emp['lst_type_ids'] = lst_ids
                punch_emp['lst_emp_id'] = lst_exemptemp_id
                punch_emp['lst_exclude_ids'] = []

            exclude = {'int_type':None, 'lst_type':[], 'lst_day_type':[]}
            if request.data.get('strExcludeType') == 'day':
                exclude['int_type'] = 1
                exclude['lst_type'] = request.data.get('lstExludeDay')
                exclude['lst_day_type'] = request.data.get('strExDayType')
            elif request.data.get('strExcludeType') == 'date':
                exclude['int_type'] = 0
                exclude['lst_type'] = request.data.get('strExcludeDate')

            ins_exp = ShiftExemption(dat_start = request.data.get('datFrom'),
                                    dat_end =  request.data.get('datTo') if request.data.get('datTo') else None,
                                    dat_created = datetime.now(),
                                    fk_created_id = request.user.userdetails.user_ptr_id,
                                    json_punch_emps = punch_emp,
                                    json_exclude = exclude,
                                    int_type = int_type_id,
                                    json_type_ids = type_ids,
                                    int_status = 1)
            ins_exp.save()
            return Response({'status':1})
         except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})
    def patch(self, request):
        try:
            int_id = request.data.get('intId')
            int_emp_id = request.data.get('intEmpId')
            rst_exemption = ShiftExemption.objects.annotate(
                                                int_type_mode = KeyTransform('int_type', 'json_type_ids'),
                                                lst_type_ids = KeyTransform('lst_type_ids', 'json_type_ids'),
                                                lst_emp_ids = KeyTransform('lst_emp_id', 'json_type_ids'),
                                                lst_exclude_ids = KeyTransform('lst_exclude_ids', 'json_type_ids'),
                                                int_punch_mode = KeyTransform('int_type', 'json_punch_emps'),
                                                int_punch_ids = KeyTransform('lst_type_ids', 'json_punch_emps'),
                                                int_punch_emp_ids = KeyTransform('lst_emp_id', 'json_punch_emps'),
                                                int_punch_exclude_ids = KeyTransform('lst_exclude_ids', 'json_punch_emps'),
                                                int_exclude_type = KeyTransform('int_type', 'json_exclude'),
                                                lst_exclude_type = KeyTransform('lst_type', 'json_exclude'),
                                                lst_exclude_day_type = KeyTransform('lst_day_type', 'json_exclude')).filter(pk_bint_id = int_id).annotate( strGroupMode = Case(
                                                When(int_type = 0 , then = Value('Employee')),
                                                When(int_type = 1 , then = Value('Department')),
                                                When(int_type = 2 , then = Value('Designation')),
                                                When(int_type = 3 , then = Value('Branch')), output_field = CharField())).filter(pk_bint_id=int_id).values(
                                                'pk_bint_id','strGroupMode', 'int_type', 'int_type_mode',
                                                'lst_type_ids', 'lst_emp_ids', 'lst_exclude_ids', 'int_punch_mode', 'int_punch_ids',
                                                'int_punch_emp_ids','lst_exclude_ids','dat_start','dat_end','int_punch_exclude_ids',
                                                'int_exclude_type','lst_exclude_type','lst_exclude_day_type').first()

            lst_emp = []
            lst_exp_emp = []
            lst_type_id = []
            if rst_exemption['int_type'] == 0:
                for data in rst_exemption['lst_emp_ids']:
                    if data == str(int_emp_id):
                        continue
                    lst_emp.append(str(data))
                for data in rst_exemption['lst_type_ids']:
                    if data == str(int_emp_id):
                        continue
                    lst_type_id.append(str(data))
            else:
                if rst_exemption['int_type_mode'] == 1:
                    for data in rst_exemption['lst_emp_ids']:
                        if data == str(int_emp_id):
                            continue
                        lst_emp.append(str(data))
                else:
                    if rst_exemption['lst_exclude_ids']:
                        for data in rst_exemption['lst_exclude_ids']:
                            lst_exp_emp.append(str(data))
                    lst_exp_emp.append(int_emp_id)
            ShiftExemption.objects.filter(pk_bint_id = int_id).update(int_status = -1)

            type_ids = {'int_type':0, 'lst_type_ids':[], 'lst_emp_id':[], 'lst_exclude_ids':[]}
            type_ids['int_type'] = rst_exemption['int_type_mode']
            type_ids['lst_type_ids'] = lst_type_id if lst_type_id else rst_exemption['lst_type_ids']
            type_ids['lst_emp_id'] = lst_emp if lst_emp else rst_exemption['lst_emp_ids']
            type_ids['lst_exclude_ids'] = lst_exp_emp if lst_exp_emp else rst_exemption['lst_exclude_ids']

            punch_emp = {'int_type':0, 'lst_type_ids':[], 'lst_emp_id':[], 'lst_exclude_ids':[]}
            punch_emp['int_type'] = rst_exemption['int_punch_mode']
            punch_emp['lst_type_ids'] = rst_exemption['int_punch_ids']
            punch_emp['lst_emp_id'] = lst_emp if lst_emp else rst_exemption['int_punch_emp_ids']
            punch_emp['lst_exclude_ids'] = lst_exp_emp if lst_exp_emp else rst_exemption['int_punch_exclude_ids']

            exclude = {'int_type':None, 'lst_type':[], 'lst_day_type':[]}
            exclude['int_type'] = rst_exemption['int_exclude_type']
            exclude['lst_type'] = rst_exemption['lst_exclude_type']
            exclude['lst_day_type'] = rst_exemption['lst_exclude_day_type']

            ins_exp = ShiftExemption(dat_start = rst_exemption['dat_start'],
                                    dat_end =  rst_exemption['dat_end'],
                                    dat_created = datetime.now(),
                                    fk_created_id = request.user.userdetails.user_ptr_id,
                                    json_punch_emps = punch_emp,
                                    json_exclude = exclude,
                                    int_type = rst_exemption['int_type'],
                                    json_type_ids = type_ids,
                                    int_status = 1)
            ins_exp.save()
            int_id = ins_exp.pk_bint_id
            return Response({'status':1,'intId':int_id})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})



class ShiftExemptionList(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            dat_selected = datetime.strptime(request.data.get('datSelected'),'%Y-%m-%d').date() if request.data.get('datSelected') else date.today()
            lst_emp_id = request.data.get('lstEmpId')
            int_count = 1
            dat_tmp = datetime.strptime(str(dat_selected.year).zfill(4)+'-'+str(dat_selected.month).zfill(2)+'-01', '%Y-%m-%d').date()
            while(dat_tmp <= dat_selected):
                if dat_tmp.weekday() == 6:
                    int_count += 1
                dat_tmp += timedelta(days=1)

            rst_exemption = ShiftExemption.objects.annotate(
                        int_type_mode = KeyTransform('int_type', 'json_type_ids'),
                        lst_type_ids = KeyTransform('lst_type_ids', 'json_type_ids'),
                        lst_emp_ids = KeyTransform('lst_emp_id', 'json_type_ids'),
                        lst_exclude_ids = KeyTransform('lst_exclude_ids', 'json_type_ids'),
                        int_punch_mode = KeyTransform('int_type', 'json_punch_emps'),
                        int_punch_ids = KeyTransform('lst_type_ids', 'json_punch_emps'),
                        int_punch_emp_ids = KeyTransform('lst_emp_id', 'json_punch_emps'),
                        int_exclude_type = KeyTransform('int_type', 'json_exclude'),
                        lst_exclude_type = KeyTransform('lst_type', 'json_exclude'),
                        lst_exclude_day_type = KeyTransform('lst_day_type', 'json_exclude'))
            if dat_selected:
                rst_exemption = rst_exemption.filter(int_status = 1, dat_start__lte = dat_selected, dat_end__gte = dat_selected).exclude(
                        Q(int_exclude_type = 0, lst_exclude_type__has_any_keys = [datetime.strftime(dat_selected, '%Y-%m-%d')])|
                        Q(int_exclude_type = 1, lst_exclude_type__has_any_keys = [dat_selected.strftime('%A').upper()],
                        lst_exclude_day_type__has_any_keys=[str(int_count)]))
            if lst_emp_id:
                ins_employee = UserDetails.objects.filter(user_ptr_id__in = lst_emp_id).values('fk_desig_id','fk_department_id','fk_branch_id')
                lst_department = list(ins_employee.values_list('fk_department_id', flat = True).distinct())
                lst_desig = list(ins_employee.values_list('fk_desig_id', flat = True).distinct())
                lst_branch = list(ins_employee.values_list('fk_branch_id', flat = True).distinct())
                rst_exemption = rst_exemption.filter(Q(int_type = 0, lst_emp_ids__has_any_keys = lst_emp_id) | Q(
                            int_type = 1, int_type_mode = 0, lst_type_ids__has_any_keys = lst_department) | Q(
                            int_type = 2, int_type_mode = 0, lst_type_ids__has_any_keys = lst_desig) | Q(
                            int_type = 3, int_type_mode = 0, lst_type_ids__has_any_keys = lst_branch) | Q(
                            int_type__in = [1, 2, 3], int_type_mode = 1, lst_emp_ids__in = lst_emp_id,int_status = 1))

            rst_exemption = rst_exemption.annotate(datStart = Func(F('dat_start'), Value('DD-MON-YYYY'), function='to_char'),
                        datEnd = Func(F('dat_end'), Value('DD-MON-YYYY'), function='to_char'), strGroupMode = Case(
                        When(int_type = 0 , then = Value('Individual')),
                        When(int_type = 1 , then = Value('Department')),
                        When(int_type = 2 , then = Value('Designation')),
                        When(int_type = 3 , then = Value('Branch')), output_field = CharField())).values(
                        'pk_bint_id', 'datStart', 'datEnd', 'strGroupMode', 'int_type', 'int_type_mode',
                        'lst_type_ids', 'lst_emp_ids', 'int_punch_mode', 'int_punch_ids', 'int_punch_emp_ids')
            lst_data = []
            for ins_data in rst_exemption:
                dct_data = {}
                dct_data['intId'] = ins_data['pk_bint_id']
                dct_data['datStart'] = ins_data['datStart']
                dct_data['datEnd'] = ins_data['datEnd']
                dct_data['strGroupMode'] = ins_data['strGroupMode']
                dct_data['strTypeData'] = ''
                if ins_data['int_type'] == 0:
                    lst_user = list(UserDetails.objects.filter(user_ptr_id__in=ins_data['lst_emp_ids']).values_list('vchr_employee_code',flat=True)[:3])
                    dct_data['strTypeData'] = ', '.join(lst_user[:2]) + (', '.join(lst_user[2:]) and '...')
                elif ins_data['int_type'] == 1:
                    lst_dept = list(Department.objects.filter(pk_bint_id__in=ins_data['lst_type_ids']).values_list('vchr_name',flat=True)[:2])
                    dct_data['strTypeData'] = ', '.join(lst_dept[:2])
                    if len(dct_data['strTypeData'])>17:
                        dct_data['strTypeData'] = dct_data['strTypeData'][:17]+'...'
                elif ins_data['int_type'] == 2:
                    lst_desig = list(JobPosition.objects.filter(pk_bint_id__in=ins_data['lst_type_ids']).values_list('vchr_name',flat=True)[:3])
                    dct_data['strTypeData'] = ', '.join(lst_desig[:2])
                    if len(dct_data['strTypeData'])>17:
                        dct_data['strTypeData'] = dct_data['strTypeData'][:17]+'...'
                elif ins_data['int_type'] == 3:
                    lst_branch = list(Branch.objects.filter(pk_bint_id__in=ins_data['lst_type_ids']).values_list('vchr_name',flat=True)[:3])
                    dct_data['strTypeData'] = ', '.join(lst_branch[:2])
                    if len(dct_data['strTypeData'])>17:
                        dct_data['strTypeData'] = dct_data['strTypeData'][:17]+'...'

                lst_data.append(dct_data)
            return Response({'status':1,'data' :lst_data})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})

    def put(self, request):
        try:
            int_id = request.data.get('intId')
            rst_exemption = ShiftExemption.objects.annotate(
                        int_type_mode = KeyTransform('int_type', 'json_type_ids'),
                        lst_type_ids = KeyTransform('lst_type_ids', 'json_type_ids'),
                        lst_emp_ids = KeyTransform('lst_emp_id', 'json_type_ids'),
                        lst_exclude_ids = KeyTransform('lst_exclude_ids', 'json_type_ids'),
                        int_punch_mode = KeyTransform('int_type', 'json_punch_emps'),
                        int_punch_ids = KeyTransform('lst_type_ids', 'json_punch_emps'),
                        int_punch_emp_ids = KeyTransform('lst_emp_id', 'json_punch_emps'),
                        int_exclude_type = KeyTransform('int_type', 'json_exclude'),
                        lst_exclude_type = KeyTransform('lst_type', 'json_exclude'),
                        lst_exclude_day_type = KeyTransform('lst_day_type', 'json_exclude')).filter(pk_bint_id = int_id).annotate(
                        datStart = Func(F('dat_start'), Value('DD-MON-YYYY'), function='to_char'),
                        datEnd = Func(F('dat_end'), Value('DD-MON-YYYY'), function='to_char'), strGroupMode = Case(
                        When(int_type = 0 , then = Value('Employee')),
                        When(int_type = 1 , then = Value('Department')),
                        When(int_type = 2 , then = Value('Designation')),
                        When(int_type = 3 , then = Value('Branch')), output_field = CharField())).values(
                        'pk_bint_id', 'datStart', 'datEnd', 'strGroupMode', 'int_type', 'int_type_mode',
                        'lst_type_ids', 'lst_emp_ids', 'lst_exclude_ids', 'int_punch_mode', 'int_punch_ids', 'int_punch_emp_ids').first()
            dct_data = {}
            dct_data['intId'] = rst_exemption['pk_bint_id']
            dct_data['datStart'] = rst_exemption['datStart']
            dct_data['datEnd'] = rst_exemption['datEnd']
            dct_data['strGroupMode'] = rst_exemption['strGroupMode']
            dct_data['lstTypeName'] = []
            dct_data['lstEmpData'] = []
            if rst_exemption['int_type'] == 0:
                dct_data['lstEmpData'] = list(UserDetails.objects.filter(user_ptr_id__in=rst_exemption['lst_emp_ids']).annotate(
                                        intEmpId = F('user_ptr_id'), strEmpCode = F('vchr_employee_code'), strName = Concat('first_name', Value(' '),
                                                                                Case(When(vchr_middle_name=None, then=F('last_name')),
                                                                                default=Concat('vchr_middle_name', Value(' '), 'last_name'),
                                                                                output_field=CharField()), output_field=CharField()),
                                        strDepartment = F('fk_department__vchr_name'), strDesignation = F('fk_desig__vchr_name'),
                                        strBranch = F('fk_branch__vchr_name')).values('intEmpId', 'strEmpCode', 'strName', 'strDepartment', 'strBranch'))
            elif rst_exemption['int_type'] == 1:
                dct_data['lstTypeName'] = list(Department.objects.filter(pk_bint_id__in = rst_exemption['lst_type_ids']).annotate(intId = F('pk_bint_id'), strName = F('vchr_name')).values('intId', 'strName'))
                if rst_exemption['int_type_mode'] == 0:
                    dct_data['lstEmpData'] = list(UserDetails.objects.filter(is_active = True, fk_department_id__in=rst_exemption['lst_type_ids']).exclude(user_ptr_id__in = rst_exemption['lst_exclude_ids']).annotate(
                                            intEmpId = F('user_ptr_id'), strEmpCode = F('vchr_employee_code'), strName = Concat('first_name', Value(' '),
                                                                                    Case(When(vchr_middle_name=None, then=F('last_name')),
                                                                                    default=Concat('vchr_middle_name', Value(' '), 'last_name'),
                                                                                    output_field=CharField()), output_field=CharField()),
                                            strDepartment = F('fk_department__vchr_name'), strDesignation = F('fk_desig__vchr_name'),
                                            strBranch = F('fk_branch__vchr_name')).values('intEmpId', 'strEmpCode', 'strName', 'strDepartment', 'strBranch'))
            elif rst_exemption['int_type'] == 2:
                dct_data['lstTypeName'] = list(JobPosition.objects.filter(pk_bint_id__in = rst_exemption['lst_type_ids']).annotate(intId = F('pk_bint_id'), strName = F('vchr_name')).values('intId', 'strName'))
                if rst_exemption['int_type_mode'] == 0:
                    dct_data['lstEmpData'] = list(UserDetails.objects.filter(is_active = True, fk_desig_id__in=rst_exemption['lst_type_ids']).exclude(user_ptr_id__in = rst_exemption['lst_exclude_ids']).annotate(
                                            intEmpId = F('user_ptr_id'), strEmpCode = F('vchr_employee_code'), strName = Concat('first_name', Value(' '),
                                                                                    Case(When(vchr_middle_name=None, then=F('last_name')),
                                                                                    default=Concat('vchr_middle_name', Value(' '), 'last_name'),
                                                                                    output_field=CharField()), output_field=CharField()),
                                            strDepartment = F('fk_department__vchr_name'), strDesignation = F('fk_desig__vchr_name'),
                                            strBranch = F('fk_branch__vchr_name')).values('intEmpId', 'strEmpCode', 'strName', 'strDepartment', 'strBranch'))
            elif rst_exemption['int_type'] == 3:
                dct_data['lstTypeName'] = list(Branch.objects.filter(pk_bint_id__in = rst_exemption['lst_type_ids']).annotate(intId = F('pk_bint_id'), strName = F('vchr_name')).values('intId', 'strName'))
                if rst_exemption['int_type_mode'] == 0:
                    dct_data['lstEmpData'] = list(UserDetails.objects.filter(is_active = True, fk_branch_id__in=rst_exemption['lst_type_ids']).exclude(user_ptr_id__in = rst_exemption['lst_exclude_ids']).annotate(
                                            intEmpId = F('user_ptr_id'), strEmpCode = F('vchr_employee_code'), strName = Concat('first_name', Value(' '),
                                                                                    Case(When(vchr_middle_name=None, then=F('last_name')),
                                                                                    default=Concat('vchr_middle_name', Value(' '), 'last_name'),
                                                                                    output_field=CharField()), output_field=CharField()),
                                            strDepartment = F('fk_department__vchr_name'), strDesignation = F('fk_desig__vchr_name'),
                                            strBranch = F('fk_branch__vchr_name')).values('intEmpId', 'strEmpCode', 'strName', 'strDepartment', 'strBranch'))

            if rst_exemption['int_type'] in [1, 2, 3] and rst_exemption['int_type_mode'] == 1:
                dct_data['lstEmpData'] = list(UserDetails.objects.filter(user_ptr_id__in=rst_exemption['lst_emp_ids']).exclude(user_ptr_id__in = rst_exemption['lst_exclude_ids']).annotate(
                                        intEmpId = F('user_ptr_id'), strEmpCode = F('vchr_employee_code'), strName = Concat('first_name', Value(' '),
                                                                                Case(When(vchr_middle_name=None, then=F('last_name')),
                                                                                default=Concat('vchr_middle_name', Value(' '), 'last_name'),
                                                                                output_field=CharField()), output_field=CharField()),
                                        strDepartment = F('fk_department__vchr_name'), strDesignation = F('fk_desig__vchr_name'),
                                        strBranch = F('fk_branch__vchr_name')).values('intEmpId', 'strEmpCode', 'strName', 'strDepartment', 'strBranch'))
            return Response({'status':1,'data' :dct_data})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})
    def patch(self,request):
         try:
             int_id = request.data.get('intId')
             ShiftExemption.objects.filter(pk_bint_id = int_id).update(int_status = -1)
             return Response({'status':1})
         except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})
