from django.shortcuts import render

# Create your views here.
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from professional_tax.models import ProfessionalTax,PtPeriod
from POS import ins_logger
import traceback
import sys, os
from django.db.models import Q

class ProfessionalTaxAdd(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            """Add Tax"""
            ins_department = ProfessionalTax.objects.create(dbl_from_amt = request.data.get("intIncomeFrom"),
                                                            dbl_to_amt = request.data.get("intIncomeTo"),
                                                            dbl_tax = request.data.get("intIncomeTax"),
                                                            fk_period_id = request.data.get("intPeriodId"),
                                                            bln_active = True)

            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


    def put(self,request):
        try:
            """Edit Tax"""
            int_id = request.data.get('intId')
            ins_professional_tax = ProfessionalTax.objects.filter(pk_bint_id = int(int_id)).update(dbl_from_amt = request.data.get("intIncomeFrom"),
                                                                                             dbl_to_amt = request.data.get("intIncomeTo"),
                                                                                             dbl_tax = request.data.get("intIncomeTax"),
                                                                                             fk_period_id = request.data.get("intPeriodId"))

            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})

    def get(self,request):
        try:
            """view"""
            int_id = request.GET.get('intId')
            if int_id:
                lst_tax = list(ProfessionalTax.objects.filter(pk_bint_id = int(int_id)).values('pk_bint_id',
                                                                                               'dbl_from_amt',
                                                                                               'dbl_to_amt',
                                                                                               'dbl_tax',
                                                                                               'fk_period_id',
                                                                                               'fk_period__vchr_period_name'))
                return Response({'status':1,"lst_tax":lst_tax})
            else:
                """list"""
                lst_tax = list(ProfessionalTax.objects.filter(bln_active = True).values('dbl_from_amt',
                                                                                        'dbl_to_amt',
                                                                                        'dbl_tax',
                                                                                        'pk_bint_id',
                                                                                        'fk_period_id',
                                                                                        'fk_period__vchr_period_name'))
                return Response({'status':1,"lst_tax":lst_tax})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})
    def patch(self,request):
        try:
            """Delete Tax"""
            int_id = request.data.get('intId')
            ins_professional_tax = ProfessionalTax.objects.filter(pk_bint_id = int(int_id)).update(bln_active = False)

            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})

class PtPeriodList(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            lst_period = list(PtPeriod.objects.filter(bln_active = True).values('pk_bint_id',
                                                                                'vchr_period_name'))
            return Response({'status':1,"lst_period":lst_period})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


class UpdatePtPeriod(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try :
            rst_data = PtPeriod.objects.filter(bln_active = True).values()
            return Response({"status":1,"data":rst_data})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


    def post(self,request):
        try:

            rst_data = request.data
            if rst_data['intFrom'] < rst_data['intTo']:
                month_range = list(range(rst_data['intFrom'],rst_data['intTo']+1))
            else:
                month_range = list(range(rst_data['intFrom'],13))+list(range(1,rst_data['intTo']+1))
            if rst_data['intDeduction'] in month_range :
                existing_data = PtPeriod.objects.filter(Q(int_month_from__in = month_range) | Q(int_month_to__in = month_range),bln_active=True).exclude(pk_bint_id = rst_data["pk_bint_id"])
                if existing_data :
                    return Response({"status":0,"data":"Selected month range already exists"})
                else :
                    # UPDATE
                    if rst_data["pk_bint_id"]:
                        PtPeriod.objects.filter(pk_bint_id = rst_data["pk_bint_id"]).update(vchr_period_name = rst_data["strName"],
                                                                                            int_month_from = rst_data["intFrom"],
                                                                                            int_month_to = rst_data["intTo"],
                                                                                            int_deduct_month = rst_data["intDeduction"]
                                                                                            )
                        return Response({"status":1})

                    # ADD
                    else:
                        ins_ptperiode = PtPeriod.objects.create(vchr_period_name = rst_data["strName"],
                                                                int_month_from = rst_data["intFrom"],
                                                                int_month_to = rst_data["intTo"],
                                                                int_deduct_month = rst_data["intDeduction"],
                                                                bln_active = True
                                                                )
                        ins_ptperiode.save()
                        return Response({"status":1})
            else:
                return Response({"status":0,"data":"Deduction month should be between from month and to month "})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})

    def put(self,request):
        try:

            PtPeriod.objects.filter(pk_bint_id = request.data.get("pk_bint_id")).update(bln_active = False)
            return Response({"status":1})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})
