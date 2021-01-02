from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.views import APIView
from salary_advance.models import SalaryAdvance
from datetime import datetime
from POS import ins_logger
import traceback
import sys, os
class AddSalaryAdvanceDetails(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            """Add """
            if request.user.is_staff or request.user.is_superuser:
                return Response({'status':0,'reason':"Super Users do not have permission"})
            ins_cash_advance = SalaryAdvance.objects.create (fk_employee_id = request.user.id,
                                                           dbl_amount = request.data.get("intAmount"),
                                                           vchr_purpose = request.data.get("strPurpose"),
                                                           int_month = request.data.get("intMonth"),
                                                           int_year = request.data.get("intYear"),
                                                           dat_created = datetime.now(),
                                                           bln_active = True,
                                                           int_status = 1)
            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})

    def put(self,request):
        try:
            """edit """
            if request.user.is_staff or request.user.is_superuser:
                return Response({'status':0,'reason':"Super Users do not have permission"})
            int_id = request.data.get("int_id")
            ins_cash_advance = SalaryAdvance.objects.filter(pk_bint_id = int_id).update(dbl_amount = request.data.get("intAmount"),
                                                                                        vchr_purpose = request.data.get("strPurpose"),
                                                                                        int_month = request.data.get("intMonth"),
                                                                                        int_year = request.data.get("intYear"),
                                                                                        dat_created = datetime.now())
            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})
    def patch(self,request):
        try:
            """delete"""
            int_id =  request.data.get("int_id")
            SalaryAdvance.objects.filter(pk_bint_id = int_id).update(bln_active = False)

            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})

    def get(self,request):
        try:
            """list of request user made"""
            lst_cash_advance_details = list(SalaryAdvance.objects.filter(fk_employee_id = request.user.id,bln_active = True).values('fk_employee_id',
                                                                                                                              'int_status',
                                                                                                                              'fk_employee__username',
                                                                                                                              'fk_employee__first_name',
                                                                                                                              'fk_employee__last_name',
                                                                                                                              'dbl_amount','vchr_purpose',
                                                                                                                              'int_month','int_year',
                                                                                                                              'dat_created','pk_bint_id').order_by('-dat_created'))
            return Response({'status':1,'lst_data':lst_cash_advance_details})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})

class SalaryAdvanceApproval(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            """Aprrove/Reject the cash advance request made by any user"""
            if not request.user.is_superuser and not request.user.userdetails.fk_desig.vchr_name.upper() in('SR. HR MANAGER'):
                return Response({'status':0,'reason':'No Permission'})
            int_id = request.data.get("intId")
            # import pdb; pdb.set_trace()
            SalaryAdvance.objects.filter(pk_bint_id = int_id).update(int_status = request.data.get("intStatus"),
                                                                   vchr_remarks = request.data.get("strRemarks"),
                                                                   dat_approval = datetime.now(),
                                                                   fk_approved_id = request.user.id)
            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})
    def get(self,request):
        try:
            """list of all request to be Approved/Rejected"""
            lst_cash_advance_details = list(SalaryAdvance.objects.filter(int_status = 1,bln_active = True).values('fk_employee_id',
                                                                                                                'fk_employee__username',
                                                                                                                'fk_employee__first_name',
                                                                                                                'fk_employee__last_name',
                                                                                                                'dbl_amount','vchr_purpose',
                                                                                                                'int_month','int_year',
                                                                                                                'dat_created','pk_bint_id','vchr_remarks').order_by('-dat_approval','dat_created',))
            return Response({'status':1,'lst_data':lst_cash_advance_details})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})
