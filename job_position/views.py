from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from job_position.models import JobPosition
from states.models import Location

from territory.models import Territory
# from zone.models import Zone
from company.models import Company
from POS import ins_logger
import traceback
import sys, os
from django.db.models.functions import Concat, Substr, Cast
from django.db.models import F, Q, Value, IntegerField
class AddJobPosition(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            """Add Job Position"""
            # import pdb; pdb.set_trace()
            int_company_id = Company.objects.filter().values().first()['pk_bint_id']
            ins_dup_job = JobPosition.objects.filter(vchr_name = request.data.get("strDesignationName"),bln_active = True)
            if ins_dup_job:
                return Response({'status':0,'reason':'Job Position Already Exists'})




            ins_job = JobPosition.objects.create(vchr_name = request.data.get("strDesignationName"),
                                                        fk_department_id = request.data.get("intDepartmentId"),
                                                        int_area_type = request.data.get("intApplyTo"),
                                                        json_area_id = request.data.get("lstAreaId"),
                                                        fk_company_id = int_company_id,
                                                        dbl_experience = request.data.get("fltExp"),
                                                        json_qualification = request.data.get("lstQualifications"),
                                                        vchr_age_limit = request.data.get("strAgeLimit"),
                                                        json_desc = request.data.get("lstDesc"),
                                                        int_notice_period = request.data.get('intNoticePeriod'),
                                                        bln_active = True)

            return Response({'status':1,'message':'Designation successfully created'})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})


    def put(self,request):
        try:
            """Update Job Position"""
            # import pdb; pdb.set_trace()
            int_job_id  = request.data.get("intJobId")

            ins_dup_job = JobPosition.objects.filter(vchr_name = request.data.get("strDesignationName"),bln_active = True).exclude(pk_bint_id = int_job_id)
            if ins_dup_job:
                return Response({'status':0,'reason':'Job Position Already Exists'})


            ins_job_position = JobPosition.objects.filter(pk_bint_id = int_job_id).update(vchr_name = request.data.get("strDesignationName"),
                                                                                          fk_department_id = request.data.get("intDepartmentId"),
                                                                                          int_area_type = request.data.get("intApplyTo"),
                                                                                          json_area_id = request.data.get("lstAreaId"),
                                                                                          dbl_experience = request.data.get("fltExp"),
                                                                                          json_qualification = request.data.get("lstQualifications"),
                                                                                          vchr_age_limit = request.data.get("strAgeLimit"),
                                                                                          txt_desc = request.data.get("strDesc"),
                                                                                          int_notice_period =request.data.get('intNoticePeriod'),
                                                                                          json_desc = request.data.get("lstDesc"))
            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})

    def patch(self,request):
        try:
            """Delete JobPosition"""

            int_job_id = request.data.get("intJobId")
            JobPosition.objects.filter(pk_bint_id = int_job_id).update(bln_active = False)
            return Response({'status':1})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})

    def get(self,request):
        try:
            """view Job Position"""
            # import pdb; pdb.set_trace()
            # int_company_id = request.user.userdetails.fk_company_id

            if request.GET.get('id'):
                int_id = int(request.GET.get('id'))

                lst_job_position = list(JobPosition.objects.filter(pk_bint_id = int_id,bln_active = True).annotate(int_age_to = Cast(Substr('vchr_age_limit',4,6), IntegerField()),int_age_from = Cast(Substr('vchr_age_limit',1,2), IntegerField())).values('pk_bint_id',
                                                                                                                                                                                                                                                             'vchr_name',
                                                                                                                                                                                                                                                             'fk_department__vchr_name',
                                                                                                                                                                                                                                                             'int_age_from','int_age_to',
                                                                                                                                                                                                                                                             'int_area_type','json_area_id',
                                                                                                                                                                                                                                                             'fk_department_id', 'dbl_experience',
                                                                                                                                                                                                                                                             'json_qualification', 'vchr_age_limit',
                                                                                                                                                                                                                                                             'txt_desc','int_notice_period','json_desc','bln_brand'))
                #getting area name from json_area_id
                #
                if lst_job_position:
                    lst_area_names = []
                    lst_area_id = lst_job_position[0]['json_area_id']
                    if lst_area_id:
                        if lst_job_position[0]['int_area_type'] == 0:
                            #state
                            lst_area_names = list(State.objects.filter(pk_bint_id__in = lst_area_id).values('vchr_name'))
                        elif lst_job_position[0]['int_area_type'] == 1:
                            #territory
                            lst_area_names  = list(Territory.objects.filter(pk_bint_id__in = lst_area_id).values('vchr_name'))
                        else:
                            #zone
                            lst_area_names = list(Zone.objects.filter(pk_bint_id__in = lst_area_id).values('vchr_name'))
                        lst_job_position[0].update({'lst_area_names':lst_area_names})

            else:
                """List Job Position"""
                if request.GET.get('intDeptId') and int(request.GET.get('intDeptId'))!=0:
                    lst_job_position = list(JobPosition.objects.filter(bln_active = True,fk_department_id=int(request.GET.get('intDeptId'))).values('pk_bint_id','vchr_name','fk_department__vchr_name','int_area_type','fk_department_id','bln_brand').order_by('vchr_name'))
                else:
                    lst_job_position = list(JobPosition.objects.filter(bln_active = True).values('pk_bint_id','vchr_name','fk_department__vchr_name','int_area_type','fk_department_id','bln_brand').order_by('vchr_name'))

            return Response({'status':1,'lst_job_position':lst_job_position})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})

class JobPositionFilter(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:

            int_dept_id = request.data.get('intDepartmentId')
            # import pdb; pdb.set_trace()
            """List Job Position"""
            ins_job_position = JobPosition.objects.filter(bln_active = True)
            ins_job_position = ins_job_position.filter(fk_department_id = int_dept_id ) if int_dept_id else ins_job_position
            lst_job_position  = list(ins_job_position.values('pk_bint_id','vchr_name','fk_department__vchr_name','int_area_type','fk_department_id','bln_brand').order_by('vchr_name'))

            return Response({'status':1,'lst_job_position':lst_job_position})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})
    def put(self,request):
        try:
            lst_dept_id = request.data.get('lstDepartmentId')
            ins_job_position = JobPosition.objects.filter(bln_active = True)
            if lst_dept_id:
                ins_job_position = ins_job_position.filter(fk_department_id__in = lst_dept_id )
            lst_job_position  = list(ins_job_position.values('pk_bint_id','vchr_name','fk_department__vchr_name','int_area_type','fk_department_id','bln_brand').order_by('vchr_name'))
            return Response({'status':1,'lst_job_position':lst_job_position})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            ins_logger.logger.error(e,extra={'details':'line no: ' + str(exc_tb.tb_lineno),'user': 'user_id:' + str(request.user.id)})
            return Response({'status':0,'reason':str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)})
