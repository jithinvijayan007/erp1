from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.views import APIView
from django.db.models import Q, F
from salary_struct.models import SalaryStructure,PfandEsiStructure
from salary_components.models import SalaryComponents
from POS import ins_logger
from datetime import datetime, date
import traceback
import sys, os
import calendar

# Create your views here.
class AddSalaryStruct(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        """adding salary_struct"""

        try:
            str_name = request.data.get('vchrName')
            flt_bp_da = request.data.get('dbl_bp_da')
            flt_da = request.data.get('dbl_da')
            flt_da_per = request.data.get('dbl_da_per')
            dct_rules = request.data.get('json_rules')
            ins_duplicate = SalaryStructure.objects.filter(vchr_name = str_name , bln_active = True).values('pk_bint_id')

            if ins_duplicate:
                return Response({'status':0,'message': 'code already exists'})
            else:
                ins_group = SalaryStructure.objects.create(vchr_name = str_name,
                                                           dbl_bp_da = flt_bp_da,
                                                           dbl_da = flt_da,
                                                           dbl_bp_da_per = flt_da_per,
                                                           json_rules = json.loads(dct_rules)
                                                           )
                return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})

    def get(self,request):
        """View Salary Structure"""
        try:

            if request.data.get('intSalaryStructId'):
                lst_salary_struct = list(SalaryStructure.objects.filter(bln_active = True,pk_bint_id = request.data.get('intSalaryStructId')).values('vchr_name',
                                                                                                                                            'dbl_bp_da',
                                                                                                                                            'dbl_da',
                                                                                                                                            'dbl_bp_da_per',
                                                                                                                                            'json_rules',
                                                                                                                                            'pk_bint_id'))

            else:
                """List SalaryStructure"""
                lst_salary_struct = list(SalaryStructure.objects.filter(bln_active = True).values('vchr_name',
                                                                                                  'dbl_bp_da',
                                                                                                  'dbl_da',
                                                                                                  'json_rules',
                                                                                                  'pk_bint_id').order_by('-pk_bint_id'))

            return Response({'status':1, 'lst_salary_struct' : lst_salary_struct})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


    def put(self,request):
        """Update Salary Structure"""
        try:
            str_name = request.data.get('vchrName')
            flt_bp_da = request.data.get('dbl_bp_da')
            flt_da = request.data.get('dbl_da')
            flt_da_per = request.data.get('dbl_da_per')
            dct_rules = request.data.get('json_rules')
            int_id = request.data.get('intId')
            ins_duplicate = SalaryStructure.objects.filter(vchr_name = str_name , bln_active = True).values('pk_bint_id').exclude(pk_bint_id = intId)
            if ins_duplicate:
                return Response({'status':0,'message': 'code already exists'})
            else:
                ins_group = SalaryStructure.objects.filter(pk_bint_id = int_id ).update(vchr_name= str_name,
                                                                                        dbl_bp_da = flt_bp_da,
                                                                                        dbl_da = flt_dbl_da,
                                                                                        dbl_da_per = flt_da_per,
                                                                                        json_rules = json.laods(dct_rules)
                                                                                       )
            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})

    def patch(self,request):
        """Delete Salary Structure"""
        try:
            int_salary_struct_id = request.data.get('intSalaryStructId')
            ins_group = SalaryStructure.objects.filter(pk_bint_id = int_salary_struct_id).update(bln_active = False)
            return Response({'status':1})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


class SalaryStructureList(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        try:


            """List Salary Structure"""
            # int_company_id = request.user.userdetails.fk_company_id
            lst_salary_struct = list(SalaryStructure.objects.filter(bln_active = True).values('pk_bint_id','vchr_name',
                                                                                              'dbl_bp_da','dbl_da','dbl_bp_da_per','json_rules').order_by('-pk_bint_id'))

            return Response({'status':1,'lst_salary_struct':lst_salary_struct})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


class ComponentsList(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            ins_sal_com = SalaryComponents.objects.filter(bln_active = True, bln_exclude = False).values('pk_bint_id','vchr_name', 'vchr_code','int_order', 'bln_fixed_allowance','int_type')
            if not ins_sal_com:
                return Response({'status':0,'message': 'No Data'})
            lst_allowance = []
            lst_fixed_allowance = []
            lst_deduction = []
            dct_data = {}
            for data in ins_sal_com:
                if data['int_type'] == 0:
                    lst_allowance.append(data)
                    if  data['bln_fixed_allowance']:
                        lst_fixed_allowance.append(data)
                else:
                    lst_deduction.append(data)
            dct_data.update({'allowance':lst_allowance,'fixed_allowance':lst_fixed_allowance,'deduction':lst_deduction})

            return Response({'status':1,'dct_data':dct_data})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


class PFandESIstruct(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        try:
            intId = request.GET.get('intId')
            if intId:
                lst_data = PfandEsiStructure.objects.filter(pk_bint_id = intId).values('pk_bint_id',
                                                                                        'int_start_month',
                                                                                        'int_start_year',
                                                                                        'int_end_month',
                                                                                        'int_end_year',
                                                                                        'vchr_type',
                                                                                        'dbl_empy_share',
                                                                                        'dbl_empr_share').order_by('pk_bint_id')
                lst_pf = []
                for data in lst_data:
                    dct_data = {}
                    dct_data['intId'] = data['pk_bint_id']
                    dct_data['strType'] = data['vchr_type']
                    dct_data['fltEmpleShare'] = data['dbl_empy_share']
                    dct_data['fltEmplrShare'] = data['dbl_empr_share']
                    dct_data['intStartMonthYear'] = str(data['int_start_month'])+"-"+str(data['int_start_year'])
                    if data['int_end_month']:
                        dct_data['intEndMonthYear'] = str(data['int_end_month'])+"-"+str(data['int_end_year'])
                    lst_pf.append(dct_data)
                return Response({'status':1,'data':lst_pf})
            else:
                lst_data = PfandEsiStructure.objects.values('pk_bint_id',
                                                            'int_start_month',
                                                            'int_start_year',
                                                            'int_end_month',
                                                            'int_end_year',
                                                            'vchr_type',
                                                            'dbl_empy_share',
                                                            'dbl_empr_share').order_by('pk_bint_id')


                lst_pf = []
                for data in lst_data:
                    dct_data = {}
                    dct_data['intId'] = data['pk_bint_id']
                    dct_data['strType'] = data['vchr_type']
                    dct_data['fltEmpleShare'] = data['dbl_empy_share']
                    dct_data['fltEmplrShare'] = data['dbl_empr_share']
                    dct_data['intStartMonthYear'] = str(data['int_start_month'])+"-"+str(data['int_start_year'])
                    if data['int_end_month']:
                        dct_data['intEndMonthYear'] = str(data['int_end_month'])+"-"+str(data['int_end_year'])
                    lst_pf.append(dct_data)
                return Response({'status':1,'data':lst_pf})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})

    def post(self,request):
        try:
            str_type = request.data.get('strType')
            flt_emple_share = request.data.get('fltEmpleShare')
            flt_emplr_share = request.data.get('fltEmplrShare')
            int_start_month = None
            int_start_year = None
            if request.data.get('intStartMonthYear'):
                int_start_month = int(request.data.get('intStartMonthYear').split('-')[0])
                int_start_year = int(request.data.get('intStartMonthYear').split('-')[1])
            int_end_month = None
            int_end_year = None
            if request.data.get('intEndMonthYear'):
                int_end_month = int(request.data.get('intEndMonthYear').split('-')[0])
                int_end_year = int(request.data.get('intEndMonthYear').split('-')[1])
                if datetime.strptime(request.data.get('intStartMonthYear'),'%m-%Y') > datetime.strptime(request.data.get('intEndMonthYear'),'%m-%Y'):
                # if int_start_year > int_end_year:
                    return Response({'status':0,'message':'Check the date'})
                # else:
                #     if int_start_month > int_end_month:
                #         return Response({'status':0,'message':'Check the date'})

            lst_data = PfandEsiStructure.objects.filter(vchr_type = str_type).values('int_start_month','int_start_year','int_end_month','int_end_year','vchr_type').order_by('-pk_bint_id').first()
            if lst_data:
                if lst_data['int_end_year']:
                    if lst_data['int_end_year'] < int_start_year:
                        PfandEsiStructure.objects.create(int_start_month = int_start_month,
                                                int_start_year = int_start_year,
                                                int_end_month = int_end_month,
                                                int_end_year = int_end_year,
                                                vchr_type = str_type,
                                                dbl_empy_share = flt_emple_share,
                                                dbl_empr_share = flt_emplr_share)
                        return Response({'status':1,'reason':'Success'})
                    elif lst_data['int_end_year'] == int_start_year:
                        if lst_data['int_end_month'] < int_start_month:
                            PfandEsiStructure.objects.create(int_start_month = int_start_month,
                                                int_start_year = int_start_year,
                                                int_end_month = int_end_month,
                                                int_end_year = int_end_year,
                                                vchr_type = str_type,
                                                dbl_empy_share = flt_emple_share,
                                                dbl_empr_share = flt_emplr_share)
                            return Response({'status':1,'message':'Success'})
                        else:
                            return Response({'status':0,'message':'Start Date is overlaped'})
                    else:
                        return Response({'status':0,'message':'Start Date is overlaped'})
                else:
                    return Response({'status':0,'message':'Update To Date for the last updation'})
            else:
                PfandEsiStructure.objects.create(int_start_month = int_start_month,
                                            int_start_year = int_start_year,
                                            int_end_month = int_end_month,
                                            int_end_year = int_end_year,
                                            vchr_type = str_type,
                                            dbl_empy_share = flt_emple_share,
                                            dbl_empr_share = flt_emplr_share)

                return Response({'status':1,'message':'Success'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})
    def put(self,request):
        try:
            int_id = request.data.get('intId')
            str_type = request.data.get('strType')
            flt_emple_share = request.data.get('fltEmpleShare')
            flt_emplr_share = request.data.get('fltEmplrShare')
            int_start_month = None
            int_start_year = None
            int_end_month = None
            int_end_year = None
            if request.data.get('intStartMonthYear'):
                int_start_month = int(request.data.get('intStartMonthYear').split('-')[0])
                int_start_year = int(request.data.get('intStartMonthYear').split('-')[1])

            if request.data.get('intEndMonthYear'):
                int_end_month = int(request.data.get('intEndMonthYear').split('-')[0])
                int_end_year = int(request.data.get('intEndMonthYear').split('-')[1])
                if int_start_year > int_end_year:
                    return Response({'status':0,'message':'Check the date'})
                else:
                    if int_start_month > int_end_month:
                        return Response({'status':0,'message':'Check the date'})

            lst_data = PfandEsiStructure.objects.filter(vchr_type = str_type, pk_bint_id__lt= int_id).values('int_start_month','int_start_year','int_end_month','int_end_year','vchr_type').order_by('-pk_bint_id').first()
            lst_details = PfandEsiStructure.objects.filter(vchr_type = str_type, pk_bint_id__gt= int_id).values('int_start_month','int_start_year','int_end_month','int_end_year','vchr_type').order_by('pk_bint_id').first()

            if lst_data:
                if lst_data['int_end_year']:
                    if lst_details:
                        if lst_details['int_start_year'] > int_end_year:
                            if lst_data['int_end_year'] < int_start_year:
                                PfandEsiStructure.objects.filter(pk_bint_id = int_id).update(int_start_month = int_start_month,
                                                                                            int_start_year = int_start_year,
                                                                                            int_end_month = int_end_month,
                                                                                            int_end_year = int_end_year,
                                                                                            dbl_empy_share = flt_emple_share,
                                                                                            dbl_empr_share = flt_emplr_share)
                                return Response({'status':1,'message':'Success'})
                            elif lst_data['int_end_year'] == int_start_year:
                                if lst_data['int_end_month'] < int_start_month:
                                    PfandEsiStructure.objects.filter(pk_bint_id = int_id).update(int_start_month = int_start_month,
                                                        int_start_year = int_start_year,
                                                        int_end_month = int_end_month,
                                                        int_end_year = int_end_year,
                                                        dbl_empy_share = flt_emple_share,
                                                        dbl_empr_share = flt_emplr_share)
                                    return Response({'status':1,'message':'Success'})
                                else:
                                    return Response({'status':0,'message':'Start Date is overlaped'})
                            else:
                                return Response({'status':0,'message':'Start Date is overlaped'})
                        elif lst_details['int_start_year'] == int_end_year:
                            if lst_details['int_start_month'] > int_end_month:
                                if lst_data['int_end_year'] < int_start_year:
                                    PfandEsiStructure.objects.filter(pk_bint_id = int_id).update(int_start_month = int_start_month,
                                                                                            int_start_year = int_start_year,
                                                                                            int_end_month = int_end_month,
                                                                                            int_end_year = int_end_year,
                                                                                            dbl_empy_share = flt_emple_share,
                                                                                            dbl_empr_share = flt_emplr_share)
                                    return Response({'status':1,'message':'Success'})
                                elif lst_data['int_end_year'] == int_start_year:
                                    if lst_data['int_end_month'] < int_start_month:
                                        PfandEsiStructure.objects.filter(pk_bint_id = int_id).update(int_start_month = int_start_month,
                                                            int_start_year = int_start_year,
                                                            int_end_month = int_end_month,
                                                            int_end_year = int_end_year,
                                                            dbl_empy_share = flt_emple_share,
                                                            dbl_empr_share = flt_emplr_share)
                                        return Response({'status':1,'message':'Success'})
                                    else:
                                        return Response({'status':0,'message':'Start Date Month is overlaped'})
                                else:
                                    return Response({'status':0,'message':'Start Date is overlaped'})
                            else:
                                return Response({'status':0,'message':'End Date is overlaped'})
                        else:
                            return Response({'status':0,'message':'End Date is overlaped'})
                    else:
                        if lst_data['int_end_year'] < int_start_year:
                            PfandEsiStructure.objects.filter(pk_bint_id = int_id).update(int_start_month = int_start_month,
                                                                                        int_start_year = int_start_year,
                                                                                        int_end_month = int_end_month,
                                                                                        int_end_year = int_end_year,
                                                                                        dbl_empy_share = flt_emple_share,
                                                                                        dbl_empr_share = flt_emplr_share)
                            return Response({'status':1,'message':'Success'})
                        elif lst_data['int_end_year'] == int_start_year:
                            if lst_data['int_end_month'] < int_start_month:
                                PfandEsiStructure.objects.filter(pk_bint_id = int_id).update(int_start_month = int_start_month,
                                                    int_start_year = int_start_year,
                                                    int_end_month = int_end_month,
                                                    int_end_year = int_end_year,
                                                    dbl_empy_share = flt_emple_share,
                                                    dbl_empr_share = flt_emplr_share)
                                return Response({'status':1,'message':'Success'})
                            else:
                                return Response({'status':0,'message':'Start Date is overlaped'})
                        else:
                            return Response({'status':0,'message':'Start Date is overlaped'})

                else:
                    return Response({'status':0,'message':'Update the last end date'})
            else:
                if lst_details:
                    if lst_details['int_start_year'] > int_end_year:
                        PfandEsiStructure.objects.filter(pk_bint_id = int_id).update(int_start_month = int_start_month,
                                                                                    int_start_year = int_start_year,
                                                                                    int_end_month = int_end_month,
                                                                                    int_end_year = int_end_year,
                                                                                    dbl_empy_share = flt_emple_share,
                                                                                    dbl_empr_share = flt_emplr_share)
                        return Response({'status':1,'message':'Success'})
                    elif lst_details['int_start_year'] == int_end_year:
                        if lst_details['int_start_month'] > int_end_month:
                            PfandEsiStructure.objects.filter(pk_bint_id = int_id).update(int_start_month = int_start_month,
                                                                                    int_start_year = int_start_year,
                                                                                    int_end_month = int_end_month,
                                                                                    int_end_year = int_end_year,
                                                                                    dbl_empy_share = flt_emple_share,
                                                                                    dbl_empr_share = flt_emplr_share)
                            return Response({'status':1,'message':'Success'})
                        else:
                            return Response({'status':0,'message':'End Date Month is overlaped'})
                    else:
                        return Response({'status':0,'message':'End Date Year is overlaped'})
                else:

                    PfandEsiStructure.objects.filter(pk_bint_id = int_id).update(int_start_month = int_start_month,
                                                int_start_year = int_start_year,
                                                int_end_month = int_end_month,
                                                int_end_year = int_end_year,
                                                dbl_empy_share = flt_emple_share,
                                                dbl_empr_share = flt_emplr_share)

                    return Response({'status':1,'message':'Success'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


class CurrentESIandPF(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            str_type = request.data.get('strType','ESI')
            dat_today = date.today()
            dct_data = {}
            dct_data = PfandEsiStructure.objects.filter(Q(int_start_year__lte=dat_today.year, int_start_month__lte=dat_today.month, int_end_year__isnull=True, int_end_month__isnull=True) | Q(int_start_year__lte=dat_today.year, int_start_month__lte=dat_today.month, int_end_year__gte=dat_today.year, int_end_month__gte=dat_today.month), vchr_type = str_type).annotate(strType=F('vchr_type'), fltEmpleShare=F('dbl_empy_share'), fltEmplrShare=F('dbl_empr_share')).values('strType', 'fltEmpleShare', 'fltEmplrShare').first()
            return Response({'status':1,'message':'Success','data':dct_data})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


class chengeStruct(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        try:
            ins_data =  SalaryStructure.objects.filter(bln_active = True).values('pk_bint_id','vchr_name','dbl_bp_da','dbl_bp_da_per','dbl_da','json_rules').order_by('vchr_name')
            return Response({'status':1,'lstData':ins_data})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})
    def post(self, request):
        try:
            str_name = request.data.get('strSlabName')
            int_id = request.data.get('intSlabId')
            int_bp_da = None
            per_bp_da = None
            if request.data.get('strCalcType') == 'percentage':
                per_bp_da = request.data.get('intBpda')
            else:
                int_bp_da = request.data.get('intBpda')
            ins_details = SalaryStructure.objects.filter(pk_bint_id = int_id).values('vchr_name','dbl_bp_da','dbl_bp_da_per','dbl_da','json_rules').first()
            dct_rules =  ins_details['json_rules']
            dct_json_rules = {}
            dct_json_rules['SA'] = dct_rules['SA']
            dct_json_rules['WA'] = request.data.get('strWA')
            dct_json_rules['CCA'] = request.data.get('strCCA')
            dct_json_rules['HRA'] = request.data.get('strHRA')
            dct_rules['Allowances']['WWF'] = request.data.get('intAllownceWWF')
            dct_json_rules['Allowances'] = dct_rules['Allowances']
            dct_rules['Deductions']['WWF'] = request.data.get('intDeductionWWF')
            dct_json_rules['Deductions'] = dct_rules['Deductions']
            ins_struct = SalaryStructure.objects.create(vchr_name = str_name,
                                                       dbl_bp_da = int_bp_da,
                                                       dbl_bp_da_per = per_bp_da,
                                                       json_rules = dct_json_rules,
                                                       bln_active = True)
            SalaryStructure.objects.filter(pk_bint_id = int_id).update(bln_active = False)
            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})

    def put(self, request):
        try:
            today = date.today()
            int_month_year =  datetime.strftime(today,'%m-%y')
            int_month = int(int_month_year.split('-')[0])
            int_year = int(int_month_year.split('-')[1]) + 2000
            str_name = request.data.get('strSlabName')
            ins_duplicate = SalaryStructure.objects.filter(vchr_name = str_name , bln_active = True).values('pk_bint_id')
            if ins_duplicate:
                return Response({'status':0,'message': 'code already exists'})
            dct_json_rules = {}
            Allowances = {}
            Deductions = {}
            int_bp_da = None
            per_bp_da = None
            dct_struct = {data['vchr_type']:{'ER':data['dbl_empr_share'], 'EE':data['dbl_empy_share']} for data in PfandEsiStructure.objects.filter(Q(int_end_month__isnull=True, int_end_year__isnull=True) | Q(int_end_month__gte=int_month, int_end_year__gte=int_year), int_start_month__lte=int_month, int_start_year__lte=int_year).values('vchr_type', 'dbl_empr_share', 'dbl_empy_share')}

            dct_json_rules['SA'] = True
            dct_json_rules['WA'] = request.data.get('strWA')
            dct_json_rules['CCA'] = request.data.get('strCCA')
            dct_json_rules['HRA'] = request.data.get('strHRA')
            Allowances['MI'] = True
            if dct_struct and dct_struct.get('PF'):
                Allowances['PF'] = dct_struct['PF']['ER']
            else:
                Allowances['PF'] = 13
            if dct_struct and dct_struct.get('ESI'):
                Allowances['ESI'] = dct_struct['ESI']['ER']
            else:
                Allowances['ESI']= 3.25
            Allowances['WWF'] = request.data.get('intAllownceWWF')
            Allowances['Gratuity'] = "BP+DA/26*15/12"
            dct_json_rules['Allowances'] = Allowances
            if dct_struct and dct_struct.get('PF'):
                Deductions['PF'] = dct_struct['PF']['EE']
            else:
                Deductions['PF'] = 12
            if dct_struct and dct_struct.get('ESI'):
                Deductions['ESI'] = dct_struct['ESI']['EE']
            else:
                Deductions['ESI'] = .75
            Deductions['TDS'] = True
            Deductions['WWF'] = request.data.get('intDeductionWWF')
            dct_json_rules['Deductions'] = Deductions
            if request.data.get('strCalcType') == 'percentage':
                per_bp_da = request.data.get('intBpda')
            else:
                int_bp_da = request.data.get('intBpda')
            ins_struct = SalaryStructure.objects.create(vchr_name = str_name,
                                                       dbl_bp_da = int_bp_da,
                                                       dbl_bp_da_per = per_bp_da,
                                                       json_rules = dct_json_rules,
                                                       bln_active = True)
            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})
