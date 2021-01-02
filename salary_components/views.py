
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.views import APIView
from salary_components.models import SalaryComponents
from django.db.models import Q
from POS import ins_logger
import traceback
import sys, os

class AddSalaryComponents(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            """Add salary_component"""
            # import pdb; pdb.set_trace()
            ins_dup_salary_component = SalaryComponents.objects.filter((Q(vchr_code = request.data.get("strCode")) | Q(vchr_name = request.data.get("strName"))),bln_active = True)
            if ins_dup_salary_component:
                return Response({'status':0,'message':'Salary Code Already Exists'})

            if  SalaryComponents.objects.filter(int_order = request.data.get("intOrder"),bln_active = True,int_type = request.data.get("intType") ):
                return Response({'status':0,'message':'Order Number Already Exists'})


            ins_salary_component = SalaryComponents.objects.create(vchr_code = request.data.get("strCode"),
                                                                   vchr_name = request.data.get("strName"),
                                                                   vchr_remarks = request.data.get("strRemarks"),
                                                                   int_order = request.data.get("intOrder"),
                                                                   bln_exclude = request.data.get("blnExclude"),
                                                                   bln_active = True,
                                                                   bln_fixed_allowance = request.data.get('blnFixedAllowance'),
                                                                   int_type = request.data.get("intType"))

            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})

    def put(self,request):
        try:
            """Update SalaryComponents"""
            # import pdb; pdb.set_trace()
            int_salary_component_id = request.data.get("intAllowanceId")
            str_code = request.data.get("strCode")
            str_name = request.data.get("strName")

            ins_dup_salary_component = SalaryComponents.objects.filter((Q(vchr_code = str_code) | Q(vchr_name = str_name)),bln_active = True).exclude(pk_bint_id = int(int_salary_component_id))

            if ins_dup_salary_component:
                return Response({'status':0,'message':'Salary Code Already Exists'})

            if  SalaryComponents.objects.filter(int_order = request.data.get("intOrder"),bln_active = True,int_type = request.data.get("intType")).exclude(pk_bint_id = int(int_salary_component_id)):
                return Response({'status':0,'message':'Order Number Already Exists'})

            ins_salary_component = SalaryComponents.objects.filter(pk_bint_id = int_salary_component_id).update(vchr_code = request.data.get("strCode"),
                                                                                                                vchr_name = request.data.get("strName"),
                                                                                                                vchr_remarks = request.data.get("strRemarks"),
                                                                                                                int_order = request.data.get("intOrder"),
                                                                                                                bln_exclude = request.data.get("blnExclude"),
                                                                                                                bln_fixed_allowance = request.data.get('blnFixedAllowance'))
            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})

    def get(self,request):
        try:
            """View SalaryComponents"""
            int_salary_component_id  = request.GET.get("id")
            if int_salary_component_id:
                lst_salary_component = list(SalaryComponents.objects.filter(pk_bint_id = int(int_salary_component_id)).values('pk_bint_id','vchr_code','vchr_name','int_order','vchr_remarks','bln_exclude','bln_fixed_allowance','int_type'))


            elif request.GET.get("type"):
                """List SalaryComponents"""
                #if type = 0 list allowance if type = 1 list Deductions
                lst_salary_component = list(SalaryComponents.objects.filter(int_type = int(request.GET.get("type")),bln_active = True).values('pk_bint_id','vchr_code','vchr_name','int_order','bln_exclude','bln_fixed_allowance','int_type').order_by('-int_order'))

            return Response({'status':1,'lst_salary_component':lst_salary_component})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})
    def patch(self,request):
        try:
            """Delete SalaryComponents"""
            int_salary_component_id  = request.data.get("intId")
            ins_salary_component = SalaryComponents.objects.filter(pk_bint_id = int(int_salary_component_id)).update(bln_active = False)
            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})
